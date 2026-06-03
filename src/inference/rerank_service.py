from collections import defaultdict

from typing import List
from typing import Dict
from typing import Any
from typing import Optional

from src.config.constants import (
    DOMAIN_BOOSTS,
    PROGRESSION_MAP,
    SAME_DOMAIN_BOOST,
    SECURITY_ALIGNMENT_BOOST,
    TOPIC_OVERLAP_BOOST,
    LEARNING_PATH_BOOST,
    CLOUD_SPECIALIZATION_BOOST,
    DIFFICULTY_PROGRESSION_BOOST,
    POPULARITY_BOOST,
    DIVERSITY_PENALTY,
    DEFAULT_POPULARITY_SCORE
)


# =====================================================
# RERANK SERVICE
# =====================================================

class RerankService:


    # =================================================
    # SEMANTIC OVERLAP SCORE
    # =================================================

    def semantic_overlap_score(

        self,

        recommendation: Dict[str, Any],

        user_product: Dict[str, Any]

    ) -> float:

        score = 0.0

        # -------------------------------------------------
        # INTERNAL TOPICS
        # -------------------------------------------------

        rec_topics = set(

            recommendation.get(
                "internalTopics",
                []
            )
        )

        user_topics = set(

            user_product.get(
                "internalTopics",
                []
            )
        )

        topic_overlap = len(

            rec_topics.intersection(
                user_topics
            )
        )

        score += (
            topic_overlap
            *
            TOPIC_OVERLAP_BOOST
            *
            0.10
        )

        # -------------------------------------------------
        # TECHNOLOGIES
        # -------------------------------------------------

        rec_technologies = set(

            recommendation.get(
                "technologies",
                []
            )
        )

        user_technologies = set(

            user_product.get(
                "technologies",
                []
            )
        )

        technology_overlap = len(

            rec_technologies.intersection(
                user_technologies
            )
        )

        score += (
            technology_overlap
            *
            0.20
        )

        # -------------------------------------------------
        # TOOLS
        # -------------------------------------------------

        rec_tools = set(

            recommendation.get(
                "tools",
                []
            )
        )

        user_tools = set(

            user_product.get(
                "tools",
                []
            )
        )

        tool_overlap = len(

            rec_tools.intersection(
                user_tools
            )
        )

        score += (
            tool_overlap
            *
            0.15
        )

        # -------------------------------------------------
        # TAGS
        # -------------------------------------------------

        rec_tags = set(

            recommendation.get(
                "tags",
                []
            )
        )

        user_tags = set(

            user_product.get(
                "tags",
                []
            )
        )

        tag_overlap = len(

            rec_tags.intersection(
                user_tags
            )
        )

        score += (
            tag_overlap
            *
            0.10
        )

        return score


    # =================================================
    # MAIN RERANKING
    # =================================================

    def rerank_recommendations(

        self,

        recommendations: List[
            Dict[str, Any]
        ],

        cart_products_metadata: List[
            Dict[str, Any]
        ],

        enrolled_products_metadata: Optional[
            List[Dict[str, Any]]
        ] = None

    ) -> List[Dict[str, Any]]:

        # -------------------------------------------------
        # HANDLE EMPTY ENROLLED PRODUCTS
        # -------------------------------------------------

        if enrolled_products_metadata is None:

            enrolled_products_metadata = []

        # -------------------------------------------------
        # USER PRODUCTS
        # -------------------------------------------------

        user_products = (

            cart_products_metadata
            +
            enrolled_products_metadata
        )

        # -------------------------------------------------
        # DOMAIN DIVERSITY TRACKING
        # -------------------------------------------------

        domain_counter = defaultdict(
            int
        )

        reranked = []

        # =================================================
        # PROCESS RECOMMENDATIONS
        # =================================================

        for recommendation in recommendations:

            score = recommendation[
                "aggregated_score"
            ]

            recommendation_domain = (
                recommendation["domain"]
            )

            recommendation_difficulty = (
                recommendation["difficulty"]
            )

            # =================================================
            # 1. SEMANTIC OVERLAP
            # =================================================

            for user_product in user_products:

                score += (
                    self.semantic_overlap_score(

                        recommendation,

                        user_product
                    )
                )

            # =================================================
            # 2. SAME DOMAIN BOOST
            # =================================================

            for user_product in user_products:

                if (

                    recommendation_domain
                    ==
                    user_product.get("domain")

                ):

                    score += (

                        SAME_DOMAIN_BOOST

                        +

                        DOMAIN_BOOSTS.get(
                            recommendation_domain,
                            0.15
                        )
                    )

            # =================================================
            # 3. SECURITY ALIGNMENT
            # =================================================

            for user_product in user_products:

                user_security = set(

                    user_product.get(
                        "securityType",
                        []
                    )
                )

                recommendation_security = set(

                    recommendation.get(
                        "securityType",
                        []
                    )
                )

                overlap = (

                    user_security.intersection(
                        recommendation_security
                    )
                )

                if overlap:

                    score += (
                        SECURITY_ALIGNMENT_BOOST
                    )

            # =================================================
            # 4. LEARNING PROGRESSION
            # =================================================

            recommendation_level = (

                PROGRESSION_MAP.get(
                    recommendation_difficulty,
                    1
                )
            )

            for user_product in user_products:

                user_level = (

                    PROGRESSION_MAP.get(

                        user_product.get(
                            "difficulty"
                        ),

                        1
                    )
                )

                # Same Level

                if recommendation_level == user_level:

                    score += 0.15

                # Natural Progression

                elif (

                    recommendation_level
                    ==
                    user_level + 1

                ):

                    score += (
                        DIFFICULTY_PROGRESSION_BOOST
                    )

                # Too Difficult

                elif (

                    recommendation_level
                    >
                    user_level + 1

                ):

                    score -= 0.25

            # =================================================
            # 5. LEARNING PATH CONTINUITY
            # =================================================

            for user_product in user_products:

                learning_path = (

                    user_product.get(
                        "learningPath",
                        []
                    )
                )

                if (

                    recommendation["id"]
                    in
                    learning_path

                ):

                    score += (
                        LEARNING_PATH_BOOST
                    )

            # =================================================
            # 6. CLOUD SPECIALIZATION
            # =================================================

            for user_product in user_products:

                if (

                    user_product.get("domain")
                    ==
                    "cloud-security"

                    and

                    recommendation_domain
                    ==
                    "cloud-security"

                ):

                    score += (
                        CLOUD_SPECIALIZATION_BOOST
                    )

            # =================================================
            # 7. GENERIC BEGINNER PENALTY
            # =================================================

            if (

                recommendation_domain
                ==
                "blue-team"

                and

                recommendation_difficulty
                ==
                "beginner"

            ):

                score -= 0.15

            # =================================================
            # 8. DIVERSITY CONTROL
            # =================================================

            domain_counter[
                recommendation_domain
            ] += 1

            if (

                domain_counter[
                    recommendation_domain
                ] > 3

            ):

                score -= DIVERSITY_PENALTY

            # =================================================
            # 9. POPULARITY BOOST
            # =================================================

            popularity = recommendation.get(

                "popularityScore",

                DEFAULT_POPULARITY_SCORE
            )

            popularity_score = (

                (popularity / 100)
                *
                POPULARITY_BOOST
            )

            score += popularity_score

            # =================================================
            # 10. SCORE NORMALIZATION
            # =================================================

            if score < 0:

                score = 0.0

            # =================================================
            # SAVE FINAL SCORE
            # =================================================

            recommendation[
                "reranked_score"
            ] = round(score, 4)

            reranked.append(
                recommendation
            )

        # =================================================
        # FINAL SORTING
        # =================================================

        reranked = sorted(

            reranked,

            key=lambda x: x[
                "reranked_score"
            ],

            reverse=True
        )

        return reranked