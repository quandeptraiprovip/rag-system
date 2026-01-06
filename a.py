import requests

def ollama_generate(prompt, model="mistral"):
    r = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        },
        timeout=300
    )
    return r.json()["response"]

print(ollama_generate("hello"))
