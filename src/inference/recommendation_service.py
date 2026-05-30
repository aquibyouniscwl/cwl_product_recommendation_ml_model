from collections import defaultdict
from typing import List, Dict, Any, Optional
from src.models.loader import ModelLoader
from src.inference.similarity_service import SimilarityService
from src.inference.rerank_service import RerankService
from src.inference.ai_rerank_service import AIRerankService
from src.inference.validation_service import ValidationService
from src.config.constants import ML_RERANK_WEIGHT, AI_RERANK_WEIGHT
from src.utils.logger import logger

class RecommendationService:
    def __init__(self):
        self.model_loader = ModelLoader()
        self.similarity_service = SimilarityService()
        self.rerank_service = RerankService()
        self.ai_rerank_service = AIRerankService()
        self.validation_service = ValidationService()

    def get_recommendations(
        self,
        cart_products: List[str],
        enrolled_products: Optional[List[str]] = None,
        top_k: int = 10
    ) -> Dict[str, Any]:
        """
        Coordinates the entire recommendation process for user cart and enrollment profiles.
        """
        if enrolled_products is None:
            enrolled_products = []

        all_user_products = cart_products + enrolled_products
        logger.info(f"Generating recommendations for cart={cart_products}, enrolled={enrolled_products}")

        # Ensure models are loaded once
        self.model_loader.load_all()

        # Step 1: Retrieve similarity candidate scores
        aggregated_scores = defaultdict(float)
        
        for pid in all_user_products:
            similar_items = self.similarity_service.get_similar_products(pid, top_k=top_k)
            for item in similar_items:
                rec_id = item["id"]
                # Skip already owned/cart products
                if rec_id in all_user_products:
                    continue
                aggregated_scores[rec_id] += item["score"]

        # Sort aggregated similarity scores
        sorted_similarity = sorted(
            aggregated_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Retrieve metadata for user products
        cart_products_metadata = []
        for pid in cart_products:
            meta = self.model_loader.get_product_metadata(pid)
            if meta:
                cart_products_metadata.append(meta)

        enrolled_products_metadata = []
        for pid in enrolled_products:
            meta = self.model_loader.get_product_metadata(pid)
            if meta:
                enrolled_products_metadata.append(meta)

        # Build candidate profiles with attributes
        candidates = []
        for rec_id, score in sorted_similarity:
            rec_meta = self.model_loader.get_product_metadata(rec_id)
            if not rec_meta:
                continue

            candidates.append({
                "id": rec_meta["id"],
                "title": rec_meta["title"],
                "domain": rec_meta["domain"],
                "difficulty": rec_meta["difficulty"],
                
                # ML aggregated score
                "aggregated_score": round(score, 4),
                
                # Semantic metadata for overlap matching
                "internalTopics": rec_meta.get("internalTopics", []),
                "technologies": rec_meta.get("technologies", []),
                "tools": rec_meta.get("tools", []),
                "tags": rec_meta.get("tags", []),
                "securityType": rec_meta.get("securityType", []),
                "learningPath": rec_meta.get("learningPath", []),
                "popularityScore": rec_meta.get("popularityScore", 50)
            })

        # Step 2: Apply semantic rule-based reranking boosts/penalties
        reranked_candidates = self.rerank_service.rerank_recommendations(
            recommendations=candidates,
            cart_products_metadata=cart_products_metadata,
            enrolled_products_metadata=enrolled_products_metadata
        )

        # Select Top K candidates
        top_candidates = reranked_candidates[:top_k]

        if not top_candidates:
            logger.info("No candidates generated for recommendations.")
            return {
                "recommendations": [],
                "llm_validation": {
                    "validated_recommendations": [],
                    "overall_explanation": "No recommendation candidates generated."
                },
                "ai_reranking": {
                    "reranked_recommendations": []
                }
            }

        # Step 3: Run AI adjustment scores using Groq
        ai_rerank_output = self.ai_rerank_service.ai_rerank_recommendations(
            recommendations=top_candidates,
            cart_products=cart_products_metadata,
            enrolled_products=enrolled_products_metadata
        )

        # Map AI adjustments to candidates
        ai_score_map = {}
        for item in ai_rerank_output.get("reranked_recommendations", []):
            ai_score_map[item["title"]] = {
                "ai_adjustment_score": item.get("ai_adjustment_score", 0.0),
                "ai_reason": item.get("reason", "")
            }

        # Combine ML rerank and AI adjustment scores into final hybrid score
        for rec in top_candidates:
            ai_data = ai_score_map.get(rec["title"], {})
            ai_adj = ai_data.get("ai_adjustment_score", 0.0)
            
            rec["ai_adjustment_score"] = round(ai_adj, 4)
            rec["ai_reason"] = ai_data.get("ai_reason", "")
            
            # Hybrid combined score
            final_score = (rec["reranked_score"] * ML_RERANK_WEIGHT) + (ai_adj * AI_RERANK_WEIGHT)
            rec["final_score"] = round(final_score, 4)

        # Re-sort candidates by hybrid final_score desc
        top_candidates = sorted(
            top_candidates,
            key=lambda x: x["final_score"],
            reverse=True
        )

        # Step 4: Perform final LLM Validation and Path explanation
        llm_output = self.validation_service.validate_and_explain_recommendations(
            cart_products=cart_products_metadata,
            enrolled_products=enrolled_products_metadata,
            recommendations=top_candidates
        )

        return {
            "recommendations": top_candidates,
            "llm_validation": llm_output,
            "ai_reranking": ai_rerank_output
        }
