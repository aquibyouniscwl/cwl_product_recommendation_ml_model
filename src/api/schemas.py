from pydantic import BaseModel
from typing import List
from typing import Optional


# =====================================================
# REQUEST SCHEMA
# =====================================================
class RecommendationRequest(BaseModel):
    # -------------------------------------------------
    # PRODUCTS IN USER CART
    # -------------------------------------------------
    cartProducts: List[str]
    # -------------------------------------------------
    # OPTIONAL ENROLLED PRODUCTS
    # -------------------------------------------------
    enrolledProducts: Optional[List[str]] = []
    # -------------------------------------------------
    # NUMBER OF RECOMMENDATIONS
    # -------------------------------------------------
    topK: Optional[int] = 10


# =====================================================
# RECOMMENDATION ITEM
# =====================================================
class RecommendationItem(BaseModel):
    # -------------------------------------------------
    # BASIC PRODUCT INFO
    # -------------------------------------------------
    id: str
    title: str
    domain: str
    difficulty: str
    # -------------------------------------------------
    # ML SCORES
    # -------------------------------------------------
    aggregated_score: float
    reranked_score: float
    # -------------------------------------------------
    # SEMANTIC METADATA
    # -------------------------------------------------
    internalTopics: Optional[List[str]] = []
    technologies: Optional[List[str]] = []
    tools: Optional[List[str]] = []
    tags: Optional[List[str]] = []
    securityType: Optional[List[str]] = []
    learningPath: Optional[List[str]] = []
    relatedDomains: Optional[List[str]] = []
    team: Optional[List[str]] = []
    # -------------------------------------------------
    # NUMERICAL FEATURES
    # -------------------------------------------------
    popularityScore: Optional[int] = 0
    difficultyScore: Optional[int] = 0
    price: Optional[int] = 0


# =====================================================
# FINAL RESPONSE
# =====================================================
class RecommendationResponse(BaseModel):
    # -------------------------------------------------
    # RECOMMENDATIONS
    # -------------------------------------------------
    recommendations: List[RecommendationItem]
    # -------------------------------------------------
    # CACHE METADATA
    # -------------------------------------------------
    cache_status: str
    cache_key: str
