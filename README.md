# PocketForge

PocketForge is an asynchronous, multi-agent AI pipeline that adapts text web-novels into multi-voice audio dramas. It is built completely on free and open-source models and tools, requiring zero paid API keys!

## 🚀 100% Free Architecture

- **Backend framework**: FastAPI, Celery, Redis, and PostgreSQL
- **Vector Database**: Qdrant (using HuggingFace `all-MiniLM-L6-v2` for embeddings)
- **Agent Orchestration**: LangGraph
- **LLM Engine**: Groq API (free tier) or local Ollama (Llama-3 models)
- **Audio Synthesis**: Microsoft Edge-TTS

### How the Pipeline Works

1. **API & Queue**: Users submit raw chapters via FastAPI. Jobs are stored in Postgres as `Pending` and pushed to Celery via Redis.
2. **LangGraph State Machine**: A `Director` agent (small LLM) breaks down the text into speakers. A `ScriptWriter` agent (large LLM) converts the prose to a JSON script, querying Qdrant using RAG (Retrieval-Augmented Generation) to inject specific character Lore/personas into the prompt to prevent hallucinations.
3. **Parallel Audio Synthesis**: The Celery worker parses the JSON script. It concurrently invokes `edge-tts` using `asyncio.gather` for every single line of dialogue, mapping different characters to different distinct voices (e.g. `en-US-ChristopherNeural`, `en-GB-SoniaNeural`).
4. **Byte-level Merging**: Once all individual MP3 chunks are downloaded, PocketForge concatenates the raw MP3 bytes sequentially, skipping heavy FFmpeg processing entirely!
5. **Delivery**: The status updates to `Completed` and FastAPI serves the final `.mp3` directly via a static mount.

## 🛠 Setup & Run

### 1. Environment Configuration
Copy the `.env.example` file to `.env` and configure your API keys (e.g., your free Groq API key).

```bash
cp .env.example .env
```

### 2. Start Infrastructure
Start PostgreSQL, Redis, and Qdrant using Docker Compose:

```bash
docker-compose up -d
```

*(Note: Custom ports are configured in `docker-compose.yml` to prevent conflicts with local database installations).*

### 3. Initialize Python Environment
Install dependencies:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Seed the Vector Database
Populate Qdrant with the character Lore:

```bash
python seed_lore.py
```

### 5. Run the Services
You need two terminals running simultaneously.

**Terminal 1 (FastAPI Server):**
```bash
python -m uvicorn app.main:app --reload
```
Navigate to `http://127.0.0.1:8000/` to access the Frontend UI!

**Terminal 2 (Celery Worker):**
```bash
celery -A app.worker.celery_app worker --loglevel=info --pool=solo
```

## 🧠 Automated Evaluation

An evaluation script is included to test the ScriptWriter agent for hallucinations against the Qdrant lorebook.

Run the evaluator:
```bash
python evaluate.py
```
This script acts as an LLM judge, reading both the vector store context and the generated script, scoring the agent on its adherence to canon lore.
