import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral"   # hoặc "llama3"

def expand_query(query: str, n: int = 3) -> list[str]:
    prompt = f"""
You are a query expansion system.

Generate {n} alternative search queries
that are semantically similar to the input.

Return JSON only.

Format:
{{"queries": ["...", "...", "..."]}}

Query:
"{query}"
"""

    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }

    resp = requests.post(OLLAMA_URL, json=payload)
    data = resp.json()

    try:
        parsed = json.loads(data["response"])
        return parsed["queries"]
    except Exception:
        return []
    
print(expand_query("structure of resnet", 3))


def retrieve_with_expansion(query, model, index, chunks, top_k=5):
    expanded = expand_query(query)
    queries = [query] + expanded

    all_results = []

    for q in queries:
        q_emb = model.encode([q], convert_to_numpy=True).astype("float32")
        distances, indices = index.search(q_emb, top_k)

        for idx, dist in zip(indices[0], distances[0]):
            chunk = chunks[idx]
            all_results.append({
                "score": float(dist),
                "source": chunk["source"],
                "section": chunk["section"],
                "text": chunk["text"]
            })

    # sort + deduplicate
    all_results = sorted(all_results, key=lambda x: x["score"])
    seen = set()
    final = []

    for r in all_results:
        key = (r["source"], r["section"], r["text"][:50])
        if key not in seen:
            seen.add(key)
            final.append(r)
        if len(final) >= top_k:
            break

    return final
