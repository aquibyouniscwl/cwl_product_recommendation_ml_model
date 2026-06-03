from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.routes import router

from src.models.loader import ModelLoader

from src.utils.logger import logger


# =====================================================
# FASTAPI LIFESPAN
# =====================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    # -------------------------------------------------
    # LOAD ML MODELS ON STARTUP
    # -------------------------------------------------

    logger.info(
        "Loading ML recommendation models..."
    )

    ModelLoader().load_all()

    logger.info(
        "All ML models loaded successfully."
    )

    yield

    # -------------------------------------------------
    # SHUTDOWN
    # -------------------------------------------------

    logger.info(
        "Recommendation engine shutting down..."
    )


# =====================================================
# CREATE FASTAPI APP
# =====================================================

app = FastAPI(

    title="CWL Recommendation Engine",

    version="1.0.0",

    description="""
ML-powered cybersecurity recommendation engine.

Features:
- Cosine similarity recommendations
- KMeans clustering
- Weighted semantic reranking
- Multi-product cart intelligence
- Learning path continuity
- Offensive / defensive alignment
""",

    lifespan=lifespan
)


# =====================================================
# REGISTER ROUTES
# =====================================================

app.include_router(router)


# =====================================================
# HEALTH CHECK
# =====================================================

@app.get("/")

def health_check():

    return {

        "status": "running",

        "service": "recommendation-engine"
    }