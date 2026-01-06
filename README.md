# PDF - RAG Systems

This project provides a robust workflow to **extract text from scientific PDF papers**, preprocess it, and prepare it for **Retrieval-Augmented Generation (RAG) systems**. It is designed to handle tables, figures, and vector graphics commonly found in research papers.

---

## Features

- **Table Extraction & Normalization**
  - Uses `pdfplumber` to detect and extract tables from PDFs.
  - Converts tables to a consistent `list-of-lists` format, preserving rows and columns.
  - Normalizes table data for easier insertion into text for RAG pipelines.

- **Figure Detection & Removal**
  - Detects figures using:
    - Vector graphics (`page.get_drawings()`)
    - Tables (page.find_tables().tables)
  - Removes figure blocks from text to reduce noise in extracted content.

- **Text Cleaning**
  - Removes null characters and unnecessary newlines.
  - Optionally compresses whitespace for embedding quality.
  - Keeps table structure intact when needed.

- **Integration**
  - Replaces detected tables in the text while maintaining document layout.
  - Returns clean text ready for ingestion into a RAG system.

---

## Metadata

Each document chunk is stored with lightweight, structured metadata to support precise retrieval, filtering, and tracing.

Metadata fields:
source – Original document name (PDF / file ID)
section – Section or heading the chunk belongs to
keywords – Key terms extracted from the chunk (for filtering & query expansion)
text – Chunk content used for embedding and retrieval

---

## Tokenizer
In this project, Sentence Transformers are used to convert text chunks into dense vector representations (embeddings) for RAG. Although Sentence Transformers do not perform tokenization in the traditional NLP sense (like splitting text into subwords), they internally handle tokenization and encoding, then transform entire sentences or paragraphs into fixed-size vectors in a semantic space.

- **Why Sentence Transformer?**
  - Captures semantic meaning, not just keywords
  - Better for semantic search and retrieval tasks
  - Optimized for cosine / dot-product similarity
  - Easy to integrate with FAISS / vector databases
- **Models for RAG**
  |Model|Dim|Characteristics|
  |:---|:---|:---|
  |all-MiniLM-L6-v2|384|Fast, Light, The most common|
  |all-MiniLM-L12-v2|384|More accuracy then L6|
  |all-mpnet-base-v2|768|Much more accuracy but slow|

---

## Vector database
- **HNSW (Hierarchical Nevigable Small World)**: is a multi-layer graph structure used for fast Approximate Nearest Neighbor (ANN) search.
  - It's one of the fastest and most accurate ANN algorithms and is widely used in modern vector databases (Faiss, Qdrant, Milvus, Pinecone, Weaviate).
  - HNSW builds a multi-level small-world graph. Upper layers allow fast navigation, and lower layers improve precision. Search starts from the top and descends greedily toward the nearest vector.
- **Faiss (Facebook AI Similarity Search)*:* is a high-performance library for dense vector similarity search and clustering, developed by Meta AI.

|VectorDB|Note|
|:--|:--|
|Pinecone|Managed, easy to start|
|Weaviate|great hybrid search, open source|
|Milvus|High scale, popular in interprise|
---

## LLM Model

Using Ollama for query expansion. 

|Tiêu chí|	mistral|	llama3|
|:--|:--|:--|
|Quy mô|	~7B	8B| (LLaMA 3.1: 8B / 70B)
|Speed|	⚡ Very fast|	🐢 a bit slower|
|RAM|	~4–6 GB|	~6–8 GB|
|Instruction following|	Good|	Very good|
|Reasoning|	Khá	|Tốt hơn|
|RAG / QA	|Tốt	|Rất tốt|
|Phân tích query	|OK|	Rất mạnh|
|Dùng laptop|	✅	|⚠️ cần RAM|


**Mistral** phù hợp khi:
- Expand query
- Extract metadata
- Rewrite question
- Keyword extraction
- Query routing
- Semantic caching key

**LLaMA3** phù hợp khi:
- Multi-hop reasoning
- Legal / technical QA
- Tổng hợp nhiều chunk
- RAG-Fusion / ReAct-RAG
- Generate the long sentence.

**LLaMA3:**
- Ít hallucinate hơn
- Hiểu context sâu hơn
- Trả lời giống GPT-4 hơn

---
## Retrieval
- **Query Classification**
- **Hybrid Search**
- **Reranking**
---

## Techniques
- **Query Transformation**
- **Context Optimization**
---

## Evaluation
---


