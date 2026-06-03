from fastapi import APIRouter
from fastapi import Depends

from src.api.schemas import (
    RecommendationRequest,
    RecommendationResponse
)

from src.inference.recommendation_service import (
    RecommendationService
)


# =====================================================
# CREATE ROUTER
# =====================================================

router = APIRouter()


# =====================================================
# DEPENDENCY INJECTION
# =====================================================

def get_recommendation_service():

    return RecommendationService()


# =====================================================
# RECOMMENDATION ENDPOINT
# =====================================================

@router.post(

    "/recommend",

    response_model=RecommendationResponse,

    summary="Get cybersecurity course recommendations",

    description="""
Generates ML-powered cybersecurity recommendations
based on cart products and enrolled products.
"""
)

def recommend_products(

    request: RecommendationRequest,

    service: RecommendationService = Depends(
        get_recommendation_service
    )

):

    # -------------------------------------------------
    # GENERATE RECOMMENDATIONS
    # -------------------------------------------------

    result = service.get_recommendations(

        cart_products=
        request.cartProducts,

        enrolled_products=
        request.enrolledProducts,

        top_k=
        request.topK
    )

    # -------------------------------------------------
    # RETURN RESPONSE
    # -------------------------------------------------

    return result