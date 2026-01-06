import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral"

def classify_query(query: str) -> bool:
    prompt = f"""
You are a query classifier for a RAG system.

Decide whether the question requires document retrieval.

Return JSON only.

Rules:
- use_retrieval = true if the query refers to specific documents, papers, sections, or private knowledge
- use_retrieval = false if general knowledge is enough

User query:
"{query}"

Example:
{{"use_retrieval": true, "reason": "Refers to a specific paper"}}
"""

    r = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0}
        },
        timeout=300
    )

    raw = r.json().get("response", "").strip()

    try:
        data = json.loads(raw)
        print(data)
        return bool(data.get("use_retrieval", True))
    except Exception:
        # an toàn: nếu parse fail → assume cần retrieval
        return True

print(classify_query("architecture of resnet"))