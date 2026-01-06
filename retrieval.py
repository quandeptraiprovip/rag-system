
from sentence_transformers import SentenceTransformer
import faiss
from query_parser import extract_filters_from_query
from extract_keyword import extract_keywords_bert
from query import expand_query

model = SentenceTransformer("all-mpnet-base-v2")

index = faiss.read_index("papers.index")

print("Vector dimension:", index.d)
print("Total vectors:", index.ntotal)
print("Index type:", type(index))

import pickle

with open("metadata.pkl", "rb") as f:
    chunks = pickle.load(f)

# # Sau khi search
# for idx in I[0]:
#     print(chunks[idx]["text"])



def retrieve_with_expansion(
    query,
    model,
    index,
    chunks,
    top_k=5,
    filters=None,
    enable_dynamic_filter=True,
    enable_expansion=True,
    alpha=0.7,
    beta=0.25,
    section_bonus_weight=0.1
):
    """
    Hybrid RAG retrieval with:
    - FAISS semantic search
    - Query expansion
    - Soft keyword + section boosting
    - Guaranteed non-empty fallback
    """

    # ---------- QUERY EXPANSION ----------
    queries = [query]
    if enable_expansion:
        try:
            queries += expand_query(query)
        except Exception:
            pass

    # ---------- DYNAMIC KEYWORDS / SECTION ----------
    dynamic_filters = {}
    if enable_dynamic_filter:
        try:
            raw = extract_keywords_bert(query)
            if isinstance(raw, list):
                dynamic_filters = {"keywords": raw, "section": None}
            elif isinstance(raw, dict):
                dynamic_filters = raw
        except Exception:
            dynamic_filters = {}

    query_keywords = set(
        map(str.lower, dynamic_filters.get("keywords", []))
    )

    seen = set()
    candidates = []

    # ---------- MAIN RETRIEVAL ----------
    for q in queries:
        q_emb = model.encode([q], convert_to_numpy=True).astype("float32")
        distances, indices = index.search(q_emb, top_k * 10)

        for idx, dist in zip(indices[0], distances[0]):
            chunk = chunks[idx]

            chunk_id = (
                chunk["source"],
                chunk["section"],
                chunk["text"][:100]
            )

            if chunk_id in seen:
                continue

            # ---------- STATIC FILTER ----------
            if filters:
                if filters.source and chunk["source"] != filters.source:
                    continue
                if filters.section and chunk["section"] != filters.section:
                    continue

            # ---------- SEMANTIC SCORE ----------
            semantic_score = float(1.0 / (1.0 + dist))

            # ---------- KEYWORD SCORE ----------
            chunk_keywords = set(
                map(str.lower, chunk.get("keywords", []))
            )
            if query_keywords and chunk_keywords:
                keyword_score = float(
                    len(query_keywords & chunk_keywords) / len(query_keywords)
                )
            else:
                keyword_score = 0.0

            # ---------- SECTION BONUS ----------
            section_bonus = 0.0
            if dynamic_filters.get("section"):
                if dynamic_filters["section"].lower() in chunk["section"].lower():
                    section_bonus = section_bonus_weight

            # ---------- HYBRID SCORE ----------
            hybrid_score = float(
                alpha * semantic_score +
                beta * keyword_score +
                section_bonus
            )

            seen.add(chunk_id)

            candidates.append({
                "hybrid_score": hybrid_score,
                "semantic_score": semantic_score,
                "keyword_score": keyword_score,
                "query_used": q,
                "source": chunk["source"],
                "section": chunk["section"],
                "keywords": chunk.get("keywords", []),
                "text": chunk["text"]
            })

    # ---------- FALLBACK (NEVER EMPTY) ----------
    if not candidates:
        q_emb = model.encode([query], convert_to_numpy=True).astype("float32")
        distances, indices = index.search(q_emb, top_k)

        for idx, dist in zip(indices[0], distances[0]):
            score = float(1.0 / (1.0 + dist))
            chunk = chunks[idx]

            candidates.append({
                "hybrid_score": score,
                "semantic_score": score,
                "keyword_score": 0.0,
                "query_used": query,
                "source": chunk["source"],
                "section": chunk["section"],
                "keywords": chunk.get("keywords", []),
                "text": chunk["text"]
            })

    # ---------- SORT & RETURN ----------
    candidates.sort(key=lambda x: x["hybrid_score"], reverse=True)
    return candidates[:top_k]








# question = "structure of resnet?"

# auto_filters = extract_filters_from_query(question)
# res = retrieve(question, model, index, chunks, filters=auto_filters)

# for r in res:
#     print(r["source"])

