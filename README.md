## SecondBrain

Multi-modal RAG knowledge base that ingests PDFs, images, audio, and video from AWS S3, extracts text with Tesseract + Whisper, and exposes a LangChain + FAISS retrieval API via FastAPI with a small React client.

---

## Environment
1. Copy `.env.example` to `.env` inside `backend/`.
2. Fill in `.env` file with your credentials.
3. Install [Ollama](https://ollama.com/download) and pull the embedding model:
   ```bash
   ollama pull gemma:2b
   ```

---

## Backend Setup
```bash
cd SecondBrain
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r backend/requirements.txt

cd backend
uvicorn api:app --reload --port 8000
```
API lives at `http://localhost:8000`.

---

## Frontend Setup
```bash
cd SecondBrain/frontend
npm install
npm run dev
```
Frontend runs at `http://localhost:5173`.
