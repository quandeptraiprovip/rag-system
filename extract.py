import fitz  # PyMuPDF
import os
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

def bbox_overlap(b1, b2, tol=3):
    # "tol" để cho phép block chạm nhẹ vào bảng
    x0, y0, x1, y1 = b1
    a0, a1, a2, a3 = b2
    return not (x1 < a0 - tol or x0 > a2 + tol or y1 < a1 - tol or y0 > a3 + tol)


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

# def clean_text(text):
#     text = re.sub(r'\n+', '\n', text)             # remove multiple newlines
#     text = re.sub(r'\s+', ' ', text)              # compress whitespace
#     text = text.replace("\x00", "")               # remove null chars
#     return text.strip()

def clean_text(text):
    text = text.replace("\x00", "")
    text = re.sub(r'\n{3,}', '\n\n', text)   # giữ đoạn văn
    text = re.sub(r'[ \t]+', ' ', text)      # chỉ xóa space dư
    return text.strip()


SECTION_PATTERN = re.compile(
    r'^(\d+\.|[IVX]+\.)?\s*'
    r'(ABSTRACT|INTRODUCTION|RELATED WORK|PROPOSED (METHOD|APPROACH)|METHODS|'
    r'METHODOLOGY|EXPERIMENTS?|EXPERIMENT DESIGN|ACCURACY ASSESSMENT|EXPERIMENTAL RESULTS?|RESULTS?|RESULTS AND DISCUSSION|'
    r'DISCUSSION|CONCLUSION|CONCLUSIONS|REFERENCES)\s*$',
    re.I
)


def split_by_sections(text):
    lines = text.split("\n")
    sections = []
    current_section = "unknown"
    buffer = ""

    for line in lines:
        l = line.strip()

        if SECTION_PATTERN.match(l):
            if buffer.strip():
                sections.append({
                    "section": current_section,
                    "text": buffer.strip()
                })

            current_section = l
            buffer = ""
        else:
            buffer += line + "\n"

    if buffer.strip():
        sections.append({
            "section": current_section,
            "text": buffer.strip()
        })

    return sections


def chunk_for_rag(sections, pdf_name,
                  chunk_size=500,
                  chunk_overlap=100):
    """
    sections = output của split_by_sections()
    return: list các chunks để đưa vào embedding
    """

    chunks = []

    for sec in sections:
        section_name = sec["section"]
        text = sec["text"]

        words = text.split()
        step = chunk_size - chunk_overlap

        for i in range(0, len(words), step):
            chunk_words = words[i:i + chunk_size]
            chunk_text = " ".join(chunk_words)

            chunk_with_meta = f"""
                            SOURCE: {pdf_name}
                            SECTION: {section_name}

                            {chunk_text}
                            """.strip()

            chunks.append({
                "source": pdf_name,
                "section": section_name,
                "text": chunk_with_meta
            })

    return chunks



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
        # print(figure_bboxes)

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
    return final_text

import fitz
import re

def extract_title_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    page = doc[0]

    blocks = page.get_text("dict")["blocks"]

    title_candidates = []

    for block in blocks:
        if block["type"] != 0:
            continue

        for line in block["lines"]:
            for span in line["spans"]:
                text = span["text"].strip()

                if len(text) < 10:
                    continue

                # ❌ Bỏ dòng arXiv
                if "arxiv" in text.lower():
                    continue

                # ❌ Bỏ email, url, ngày tháng
                if re.search(r"\d{1,2}\s+\w+\s+\d{4}", text):
                    continue

                if "http" in text.lower():
                    continue

                title_candidates.append((span["size"], text))

    if not title_candidates:
        return "untitled"

    # Sắp theo font size giảm dần, text dài hơn được ưu tiên
    title_candidates = sorted(
        title_candidates,
        key=lambda x: (x[0], len(x[1])),
        reverse=True
    )

    return title_candidates[0][1]


def get_all_pdfs(root_folder):
    pdfs = []
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            if file.lower().endswith(".pdf"):
                pdfs.append(os.path.join(root, file))
    return pdfs


# ví dụ
files = get_all_pdfs("research")
print(len(files))

save_path = "/Users/minh10hd/Downloads/rag/text/"

for file in files:

    text = extract_text_from_pdf(file, save_path)
    sections = split_by_sections(text)

    print(len(sections))
    for s in sections:
        print(s["section"])

    name = extract_title_from_pdf("/Users/minh10hd/Downloads/rag/research/1810.01733v3.pdf")
    chunks = chunk_for_rag(sections, name)
print(chunks[0]["text"])
    

# text = extract_text_from_pdf("/Users/minh10hd/Downloads/rag/text/1810.01733v3.txt", save_path)
# sections = split_by_sections(text)

# # print(len(sections))
# for s in sections:
#     print(s["section"])