from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import re
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lazy import to avoid hanging on startup
_rag_engine = None

def get_rag_engine():
    global _rag_engine
    if _rag_engine is None:
        try:
            from rag_engine import ask
            _rag_engine = ask
            logger.info("RAG engine loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load RAG engine: {e}")
            raise
    return _rag_engine

app = FastAPI(title="Second Brain API")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QuestionRequest(BaseModel):
    question: str

class FlashcardResponse(BaseModel):
    question: str
    answer: str

@app.get("/")
def root():
    return {"message": "Second Brain API is running"}

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    try:
        ask = get_rag_engine()
        # Run in executor to avoid blocking, with timeout
        loop = asyncio.get_event_loop()
        answer = await asyncio.wait_for(
            loop.run_in_executor(None, ask, request.question),
            timeout=60.0  # 60 second timeout
        )
        return {"answer": answer}
    except asyncio.TimeoutError:
        logger.error("Request timed out after 60 seconds")
        raise HTTPException(status_code=504, detail="Request timed out. The AI model may be taking too long to respond.")
    except Exception as e:
        logger.error(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/flashcards")
async def generate_flashcards():
    try:
        ask = get_rag_engine()
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(None, ask, "Generate 10 flashcards as JSON array with 'question' and 'answer'."),
            timeout=60.0
        )
        # Extract JSON array inside optional code fences
        cleaned = re.search(r"\[.*\]", response, re.DOTALL)
        if cleaned:
            response_json = cleaned.group(0)
        else:
            response_json = response
        
        cards = json.loads(response_json)
        return {"cards": cards}
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Request timed out. The AI model may be taking too long to respond.")
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Could not parse model output as JSON: {str(e)}")
    except Exception as e:
        logger.error(f"Error generating flashcards: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    """Check if the API and dependencies are ready"""
    try:
        ask = get_rag_engine()
        return {
            "status": "healthy",
            "rag_engine": "loaded"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "RAG engine failed to load. Check if Ollama is running and .env is configured."
        }

