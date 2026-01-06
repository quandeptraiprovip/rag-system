from fastapi import FastAPI
from schemas import QueryRequest
from retrieval import retrieve_with_expansion
from sentence_transformers import SentenceTransformer
import faiss, pickle
from query_parser import extract_filters_from_query
from query_classify import classify_query

app = FastAPI()

# global resources
model = None
index = None
chunks = None


@app.on_event("startup")
def startup():
    global model, index, chunks

    print("🚀 Loading RAG resources...")

    model = SentenceTransformer("all-mpnet-base-v2")
    index = faiss.read_index("papers.index")

    with open("metadata.pkl", "rb") as f:
        chunks = pickle.load(f)

    print("✅ RAG system ready")


@app.post("/retrieve")
def retrieve_api(req: QueryRequest):
    if classify_query(req.question):
        auto_filters = extract_filters_from_query(req.question)
        return retrieve_with_expansion(
            query=req.question,
            model=model,
            index=index,
            chunks=chunks,
            top_k=req.top_k,
            filters=auto_filters
        )
    else:
        # answer = generate_direct(query)
        print("khong lien quan")


