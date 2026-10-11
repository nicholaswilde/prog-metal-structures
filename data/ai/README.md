# Progressive Metal AI Training Corpora & Benchmark Suite

This directory contains curated machine learning datasets formatted for Large Language Model (LLM) instruction fine-tuning, Retrieval-Augmented Generation (RAG) vector embeddings, and evaluation benchmarking across progressive metal musical architectures.

---

## Files in this Dataset

### 1. `prog_metal_sft.jsonl` (142 conversation pairs)
- **Format**: JSON Lines, ChatML / OpenAI message format (`messages`).
- **Use Case**: Supervised Fine-Tuning (SFT) for music analysis, meter prediction, and metric complexity reasoning.
- **Record Structure**:
  ```json
  {
    "messages": [
      {"role": "system", "content": "You are an expert computational musicologist specializing in progressive metal rhythm, odd-meter structures, tempo modulations, and musical architecture."},
      {"role": "user", "content": "Analyze the metric complexity of 'Dance of Eternity' by Dream Theater."},
      {"role": "assistant", "content": "..."}
    ],
    "category": "metric_complexity",
    "track_id": "dream_theater_dance_of_eternity"
  }
  ```

### 2. `prog_metal_knowledge_corpus.jsonl` (58 documents)
- **Format**: JSON Lines, structured markdown documents with metadata.
- **Use Case**: Vector database ingestion (Chroma, Qdrant, Pinecone), BM25 hybrid search, and semantic RAG retrieval.
- **Record Structure**:
  ```json
  {
    "id": "prog_doc_dream_theater_dance_of_eternity",
    "title": "Dance of Eternity by Dream Theater — Structural Analysis",
    "text": "# Dance of Eternity — Dream Theater\n\n**Total Measures**: 127...",
    "metadata": {
      "track_id": "dream_theater_dance_of_eternity",
      "artist": "Dream Theater",
      "metric_entropy": 2.45
    }
  }
  ```

### 3. `prog_metal_benchmark_suite.jsonl` (232 evaluation questions)
- **Format**: JSON Lines, question and ground-truth answer pairs with evaluation strategy.
- **Use Case**: Evaluating model domain understanding, factual recall of meter progressions, and hallucination rates.
- **Record Structure**:
  ```json
  {
    "id": "prog_bench_001",
    "category": "unique_meters_count",
    "question": "How many unique time signatures are used in 'Dance of Eternity' by Dream Theater?",
    "golden_answer": "8",
    "eval_type": "exact_match"
  }
  ```
