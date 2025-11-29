import fitz  # PyMuPDF
import os
import pdfplumber
from pprint import pformat
import re

def normalize_table_to_list(raw_table, min_nonempty_cells=1):
    """
    Chuẩn hóa bảng pdfplumber, tách các row theo '\n', trả về list of lists.
    
    Args:
        raw_table: list of lists, output từ pdfplumber.extract_tables()
        min_nonempty_cells: bảng có ít hơn số cell có dữ liệu -> bỏ qua
        
    Returns:
        list of lists chuẩn hóa, hoặc None nếu bảng rỗng
    """
    # Bỏ qua bảng rỗng
    nonempty_cells = sum(1 for row in raw_table for cell in row if cell not in (None,''))
    if nonempty_cells < min_nonempty_cells:
        return None
    
    header = raw_table[0]
    data_rows = raw_table[1:]
    normalized_rows = [header]  # giữ header đầu tiên
    
    for row in data_rows:
        # pad row nếu ít cột hơn header
        if len(row) < len(header):
            row += [''] * (len(header) - len(row))
        
        # tách cell theo '\n'
        split_cells = [str(cell).split('\n') if cell not in (None,'') else [''] for cell in row]
        max_len = max(len(c) for c in split_cells)
        
        # tạo từng sub-row
        for i in range(max_len):
            sub_row = [c[i] if i < len(c) else '' for c in split_cells]
            normalized_rows.append(sub_row)
    
    return pformat(normalized_rows)

def is_table_empty(table):
    """
    Kiểm tra bảng rỗng: nếu tất cả cell là '' hoặc None -> True
    """
    for row in table:
        for cell in row:
            if cell not in (None, ''):
                return False
    return True

# with pdfplumber.open("/Users/minh10hd/Downloads/rag/research/1810.01733v3.pdf") as pdf:
#     for page_number, page in enumerate(pdf.pages, start=1):
#         tables = page.extract_tables()

#         # print(f"Page {page_number}: {len(tables)} tables found")

#         for idx, table in enumerate(tables):
#             if is_table_empty(table):
#                 # print(f"Page {page_number} Table {idx+1} → bỏ qua (rỗng)")
#                 continue
#             # print(f"\nTable {idx+1}:")
#             for row in table:
#                 # print(row)
#                 ...

def bbox_overlap(b1, b2, tol=3):
    # "tol" để cho phép block chạm nhẹ vào bảng
    x0, y0, x1, y1 = b1
    a0, a1, a2, a3 = b2
    return not (x1 < a0 - tol or x0 > a2 + tol or y1 < a1 - tol or y0 > a3 + tol)

def detect_all_figure_bboxes(page):
    raw = page.get_text("rawdict")
    bboxes = []

    # 1) ảnh
    # for b in raw["blocks"]:
    #     if b["type"] == 1:
    #         bboxes.append(tuple(b["bbox"]))

    # 2) vector graphics (biểu đồ)
    for b in raw["blocks"]:
        if b["type"] == 4:
            bboxes.append(tuple(b["bbox"]))

    return bboxes





def normalize_table(raw_table):
    """Convert list-of-lists to your preferred format ['a','b'] per row."""
    out = []
    for row in raw_table:
        out.append(str(row))
    return "\n".join(out)

def detect_vector_figures(page):
    """
    Detect vector graphics (line, plot, chart) using page.get_drawings()
    Returns list of bboxes (x0, y0, x1, y1)
    """
    vector_bboxes = []
    for draw in page.get_drawings():
        bbox = draw["rect"]
        vector_bboxes.append((bbox.x0, bbox.y0, bbox.x1, bbox.y1))
    return vector_bboxes

def clean_text(text):
    text = re.sub(r'\n+', '\n', text)             # remove multiple newlines
    # text = re.sub(r'\s+', ' ', text)              # compress whitespace
    text = text.replace("\x00", "")               # remove null chars
    return text.strip()

def extract_text_from_pdf(path, save_path):
    pdf_filename = os.path.basename(path)
    base_name = os.path.splitext(pdf_filename)[0]
    output_path = save_path + base_name + ".txt"
    doc = fitz.open(path)
    text = ""
    final_text = ""
    for page in doc:
        # 1) lấy bảng
        detected_tables = page.find_tables().tables
        table_blocks = []
        for t in detected_tables:
            extracted = t.extract()   # [[row], [row], ...]
            table_blocks.append({
                "bbox": t.bbox,
                "text": normalize_table_to_list(extracted),
                "used": False  # tránh in 2 lần
            })

        # 2) lấy figure (ảnh + vector + caption)
        # figure_bboxes = detect_all_figure_bboxes(page)
        figure_bboxes = detect_vector_figures(page)
        print(figure_bboxes)

        # 3) lấy text block
        blocks = page.get_text("blocks")  # (x0, y0, x1, y1, text, block_no)

        # 4) xử lý từng block
        for b in blocks:
            block_bbox = b[:4]
            block_text = b[4]

            # --- ưu tiên 1: block thuộc bảng ---
            replaced = False
            for tbl in table_blocks:
                if bbox_overlap(block_bbox, tbl["bbox"]):
                    if not tbl["used"]:
                        final_text += tbl["text"] + "\n"
                        tbl["used"] = True
                    replaced = True
                    break
            if replaced:
                continue  # không xét figure nữa

            # --- ưu tiên 2: block thuộc figure → bỏ ---
            is_figure = any(bbox_overlap(block_bbox, fb) for fb in figure_bboxes)
            if is_figure:
                continue

            # --- nếu không phải bảng và không phải figure → giữ ---
            final_text += block_text + "\n"

    final_text = clean_text(final_text)
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(final_text)
        print(f"✅ Đã lưu văn bản thành công vào: {output_path}")
    except Exception as e:
        print(f"❌ Lỗi khi lưu file: {e}")
    return output_path

print(extract_text_from_pdf("/Users/minh10hd/Downloads/rag/research/1810.01733v3.pdf", "/Users/minh10hd/Downloads/rag/text/"))
# === Ví dụ sử dụng ===
# raw_table_example = [
#     ['Method', 'mAP(%) PR(%)'],
#     ['FS[22]', '66.37 75.0'],
#     ['yolo gd\nyolo ld\nyolo ld+th\nyolo ld+lf\nyolo ld+mc', '66.95 78.89\n74.32 84.75\n75.62 81.55\n76.37 86.56\n74.80 85.28'],
#     ['yolo ld+lf-mc-th(full)', '76.93 85.71'],
# ]

# normalized_list = normalize_table_to_list(raw_table_example)
# for row in normalized_list:
#     print(row)

# doc = fitz.open("/Users/minh10hd/Downloads/rag/research/1810.01733v3.pdf")
# for page_num in range(len(doc)):
#     page = doc[page_num]
#     paths = page.get_drawings() # Extract existing drawings
    
#     print(f"Page {page_num+1} contains {len(paths)} vector graphic paths.")
    
# print(pformat(raw_table_example))