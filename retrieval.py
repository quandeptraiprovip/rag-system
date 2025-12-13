
from sentence_transformers import SentenceTransformer
import faiss

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


def retrieve(query, model, index, chunks, top_k=5):

    q_emb = model.encode([query], convert_to_numpy=True).astype("float32")

    distances, indices = index.search(q_emb, top_k)

    results = []
    for idx, dist in zip(indices[0], distances[0]):

        chunk = chunks[idx]

        results.append({
            "score": float(dist),
            "source": chunk["source"],
            "section": chunk["section"],
            "text": chunk["text"]
        })

    return results


# question = "structure of resnet?"


# res = retrieve(question, model, index, chunks)

# for r in res:
#     print(r["source"])

