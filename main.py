from fastapi import FastAPI
from schemas import QueryRequest
from retrieval import retrieve
from sentence_transformers import SentenceTransformer
import faiss, pickle

app = FastAPI()

model = SentenceTransformer("all-mpnet-base-v2")
index = faiss.read_index("papers.index")

with open("metadata.pkl", "rb") as f:
    chunks = pickle.load(f)

@app.post("/retrieve")
def retrieve_api(req: QueryRequest):
    return retrieve(req.question, model, index, chunks, req.top_k)
