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
