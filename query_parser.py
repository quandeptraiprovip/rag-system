import json
from schemas import MetadataFilter
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral"

def extract_filters_from_query(query: str) -> MetadataFilter:
    prompt = f"""
You are an information extraction system.

Extract metadata filters from the user query.
Return JSON only.

Fields:
- source (string or null)
- section (string or null)

User query:
"{query}"

Example output:
{{"source": null, "section": "Architecture"}}
"""

    r = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0
            }
        },
        timeout=30
    )

    raw = r.json().get("response", "").strip()

    try:
        data = json.loads(raw)
        return MetadataFilter(
            source=data.get("source"),
            section=data.get("section")
        )
    except Exception:
        # fallback an toàn
        return MetadataFilter()

print(extract_filters_from_query("what is resnet"))