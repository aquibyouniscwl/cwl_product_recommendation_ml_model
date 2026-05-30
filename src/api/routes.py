from fastapi import APIRouter, Depends
from src.api.schemas import RecommendationRequest, RecommendationResponse
from src.inference.recommendation_service import RecommendationService

router = APIRouter()

# Dependency injection helper
def get_recommendation_service() -> RecommendationService:
    return RecommendationService()

@router.post(
    "/recommend",
    response_model=RecommendationResponse,
    summary="Get course recommendations",
    description="Generates AI-powered hybrid recommendations for a user based on their cart and enrolled courses."
)
def recommend_products(
    request: RecommendationRequest,
    service: RecommendationService = Depends(get_recommendation_service)
):
    """
    HTTP POST endpoint to generate cybersecurity course recommendations.
    """
    result = service.get_recommendations(
        cart_products=request.cartProducts,
        enrolled_products=request.enrolledProducts,
        top_k=request.topK
    )
    return result
