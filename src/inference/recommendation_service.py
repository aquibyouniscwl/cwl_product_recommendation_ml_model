from collections import defaultdict

from typing import List
from typing import Dict
from typing import Any
from typing import Optional

from src.models.loader import ModelLoader

from src.inference.similarity_service import (
    SimilarityService
)

from src.inference.rerank_service import (
    RerankService
)

from src.utils.logger import logger


# =====================================================
# RECOMMENDATION SERVICE
# =====================================================

class RecommendationService:

    def __init__(self):

        self.model_loader = ModelLoader()

        self.similarity_service = (
            SimilarityService()
        )

        self.rerank_service = (
            RerankService()
        )


    # =================================================
    # MAIN RECOMMENDATION PIPELINE
    # =================================================

    def get_recommendations(

        self,

        cart_products: List[str],

        enrolled_products: Optional[
            List[str]
        ] = None,

        top_k: int = 10

    ) -> Dict[str, Any]:

        # -------------------------------------------------
        # HANDLE EMPTY ENROLLED PRODUCTS
        # -------------------------------------------------

        if enrolled_products is None:

            enrolled_products = []

        # -------------------------------------------------
        # USER PRODUCTS
        # -------------------------------------------------

        all_user_products = (

            cart_products
            +
            enrolled_products
        )

        logger.info(

            f"Generating recommendations "
            f"for cart={cart_products}, "
            f"enrolled={enrolled_products}"

        )

        # -------------------------------------------------
        # LOAD MODELS
        # -------------------------------------------------

        self.model_loader.load_all()

        # =================================================
        # STEP 1 — SIMILARITY RETRIEVAL
        # =================================================

        aggregated_scores = defaultdict(
            float
        )

        for product_id in all_user_products:

            similar_products = (

                self.similarity_service
                .get_similar_products(

                    product_id,

                    top_k=top_k
                )
            )

            for item in similar_products:

                recommendation_id = item["id"]

                # -----------------------------------------
                # SKIP EXISTING PRODUCTS
                # -----------------------------------------

                if (
                    recommendation_id
                    in
                    all_user_products
                ):

                    continue

                aggregated_scores[
                    recommendation_id
                ] += item["score"]

        # =================================================
        # STEP 2 — SORT SIMILARITY SCORES
        # =================================================

        sorted_similarity = sorted(

            aggregated_scores.items(),

            key=lambda x: x[1],

            reverse=True
        )

        # =================================================
        # STEP 3 — LOAD USER PRODUCT METADATA
        # =================================================

        cart_products_metadata = []

        for product_id in cart_products:

            metadata = (

                self.model_loader
                .get_product_metadata(
                    product_id
                )
            )

            if metadata:

                cart_products_metadata.append(
                    metadata
                )

        enrolled_products_metadata = []

        for product_id in enrolled_products:

            metadata = (

                self.model_loader
                .get_product_metadata(
                    product_id
                )
            )

            if metadata:

                enrolled_products_metadata.append(
                    metadata
                )

        # =================================================
        # STEP 4 — BUILD CANDIDATE PROFILES
        # =================================================

        candidates = []

        for rec_id, score in sorted_similarity:

            rec_meta = (

                self.model_loader
                .get_product_metadata(
                    rec_id
                )
            )

            if not rec_meta:

                continue

            candidates.append({

                # -----------------------------------------
                # BASIC INFO
                # -----------------------------------------

                "id":
                rec_meta["id"],

                "title":
                rec_meta["title"],

                "domain":
                rec_meta["domain"],

                "difficulty":
                rec_meta["difficulty"],

                # -----------------------------------------
                # ML SCORES
                # -----------------------------------------

                "aggregated_score":
                round(score, 4),

                # -----------------------------------------
                # SEMANTIC METADATA
                # -----------------------------------------

                "internalTopics":
                rec_meta.get(
                    "internalTopics",
                    []
                ),

                "technologies":
                rec_meta.get(
                    "technologies",
                    []
                ),

                "tools":
                rec_meta.get(
                    "tools",
                    []
                ),

                "tags":
                rec_meta.get(
                    "tags",
                    []
                ),

                "securityType":
                rec_meta.get(
                    "securityType",
                    []
                ),

                "learningPath":
                rec_meta.get(
                    "learningPath",
                    []
                ),

                "relatedDomains":
                rec_meta.get(
                    "relatedDomains",
                    []
                ),

                "team":
                rec_meta.get(
                    "team",
                    []
                ),

                # -----------------------------------------
                # NUMERICAL FEATURES
                # -----------------------------------------

                "popularityScore":
                rec_meta.get(
                    "popularityScore",
                    50
                ),

                "difficultyScore":
                rec_meta.get(
                    "difficultyScore",
                    1
                ),

                "price":
                rec_meta.get(
                    "price",
                    0
                )
            })

        # =================================================
        # STEP 5 — SEMANTIC RERANKING
        # =================================================

        reranked_candidates = (

            self.rerank_service
            .rerank_recommendations(

                recommendations=
                candidates,

                cart_products_metadata=
                cart_products_metadata,

                enrolled_products_metadata=
                enrolled_products_metadata
            )
        )

        # =================================================
        # STEP 6 — FINAL TOP K
        # =================================================

        final_recommendations = (
            reranked_candidates[:top_k]
        )

        logger.info(

            f"Generated "
            f"{len(final_recommendations)} "
            f"recommendations."

        )

        # =================================================
        # FINAL RESPONSE
        # =================================================

        return {

            "recommendations":
            final_recommendations
        }