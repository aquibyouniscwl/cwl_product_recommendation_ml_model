from pydantic import BaseModel
from typing import List, Optional, Dict, Any

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

    enrolledProducts: Optional[
        List[str]
    ] = []

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
    # AI RERANKING
    # -------------------------------------------------

    ai_adjustment_score: Optional[
        float
    ] = 0

    final_score: Optional[
        float
    ] = 0

    ai_reason: Optional[
        str
    ] = ""

    # -------------------------------------------------
    # SEMANTIC METADATA
    # -------------------------------------------------

    internalTopics: Optional[
        List[str]
    ] = []

    technologies: Optional[
        List[str]
    ] = []

    tools: Optional[
        List[str]
    ] = []

    tags: Optional[
        List[str]
    ] = []

    securityType: Optional[
        List[str]
    ] = []

    learningPath: Optional[
        List[str]
    ] = []

    popularityScore: Optional[
        int
    ] = 0

# =====================================================
# LLM VALIDATION
# =====================================================

class LLMValidation(BaseModel):

    validated_recommendations: List[
        Dict[str, Any]
    ]

    overall_explanation: str

# =====================================================
# FINAL RESPONSE
# =====================================================

class RecommendationResponse(BaseModel):

    recommendations: List[
        RecommendationItem
    ]

    llm_validation: LLMValidation

    ai_reranking: Dict[
        str,
        Any
    ]