# Adaptive Agentic RAG — multi-service image (Streamlit + MCP API)
# Python 3.12 for Chroma compatibility; use 3.14 base if you prefer FAISS-only.
FROM python:3.12-slim

WORKDIR /app

# System deps for PDF and optional native libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies first (better layer cache)
COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY adaptive_rag ./adaptive_rag

# Non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Persistence dir (mount volume here)
ENV VECTOR_STORE_PATH=/app/data/vector_store

# Default: run Streamlit (override in compose for MCP service)
EXPOSE 8501
CMD ["streamlit", "run", "adaptive_rag/app/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
