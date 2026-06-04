import json
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.api.routes import router
from src.models.loader import ModelLoader
from src.inference.recommendation_service import RecommendationService
from src.analytics.pattern_analytics import pattern_analytics
from src.cache.cache_service import set_cache, CACHE_ENABLED
from src.utils.logger import logger

# =====================================================
# CONFIG
# =====================================================
POPULAR_PATTERN_LIMIT = 100


# =====================================================
# FASTAPI LIFESPAN
# =====================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # -------------------------------------------------
    # LOAD ML MODELS ON STARTUP
    # -------------------------------------------------
    logger.info("Loading ML recommendation models...")
    ModelLoader().load_all()
    logger.info("All ML models loaded successfully.")
    # -------------------------------------------------
    # LOAD PATTERN ANALYTICS
    # -------------------------------------------------
    pattern_analytics.load_pattern_analytics()
    # -------------------------------------------------
    # PRELOAD POPULAR PATTERNS INTO REDIS
    # -------------------------------------------------
    if CACHE_ENABLED:
        preload_popular_patterns()
    yield
    # -------------------------------------------------
    # SAVE ANALYTICS ON SHUTDOWN
    # -------------------------------------------------
    pattern_analytics.save_pattern_analytics()
    # -------------------------------------------------
    # SHUTDOWN
    # -------------------------------------------------
    logger.info("Recommendation engine shutting down...")


# =====================================================
# PRELOAD POPULAR PATTERNS
# =====================================================
def preload_popular_patterns():
    top_patterns = pattern_analytics.get_top_patterns(limit=POPULAR_PATTERN_LIMIT)
    if not top_patterns:
        logger.info("No popular patterns found to preload.")
        return
    service = RecommendationService()
    preloaded_count = 0
    for entry in top_patterns:
        pattern = entry["pattern"]
        try:
            # Parse pattern key back into cart/enrolled lists
            # Format: "cart:product_1|product_2::enrolled:product_3"
            parts = pattern.split("::")
            cart_part = parts[0].replace("cart:", "")
            enrolled_part = parts[1].replace("enrolled:", "") if len(parts) > 1 else ""
            cart_products = [p for p in cart_part.split("|") if p]
            enrolled_products = [p for p in enrolled_part.split("|") if p]
            if not cart_products:
                continue
            # Generate recommendations and store in Redis
            result = service.get_recommendations(
                cart_products=cart_products,
                enrolled_products=enrolled_products,
                top_k=10,
            )
            preloaded_count += 1
        except Exception as e:
            logger.warning(f"Failed to preload pattern '{pattern}': {e}")
            continue
    logger.info(f"Loaded Top {preloaded_count} Recommendation Patterns")


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
- LRU in-process caching
- Request pattern analytics
""",
    lifespan=lifespan,
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
    return {"status": "running", "service": "recommendation-engine"}
