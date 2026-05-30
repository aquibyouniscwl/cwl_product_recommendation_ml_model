from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.api.routes import router
from src.models.loader import ModelLoader
from src.utils.logger import logger

# FastAPI lifespan for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Centralized model loading at startup
    logger.info("FastAPI starting up: loading all ML models and encoders into memory...")
    ModelLoader().load_all()
    yield
    logger.info("FastAPI shutting down...")

app = FastAPI(
    title="CWL Recommendation Engine",
    version="1.0.0",
    description="""
AI-powered cybersecurity course recommendation engine.

Features:
- ML similarity recommendations
- Semantic reranking
- Multi-product cart intelligence
- LLM validation
- AI recommendation explanations
""",
    lifespan=lifespan
)

# Register application routes
app.include_router(router)

# Health check endpoint
@app.get("/")
def health_check():
    return {
        "status": "running",
        "service": "recommendation-engine"
    }