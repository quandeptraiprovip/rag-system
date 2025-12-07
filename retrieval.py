
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


question = "How does the proposed method improve accuracy?"

query_embedding = model.encode([question]).astype("float32")

k = 5  # top 5 relevant chunks
distances, indices = index.search(query_embedding, k)

for idx in indices[0]:
    print(chunks[idx]["section"])
    print(chunks[idx]["text"][:300])
    print("-" * 30)
