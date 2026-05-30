from collections import defaultdict
from typing import List, Dict, Any, Optional
from src.config.constants import DOMAIN_BOOSTS, PROGRESSION_MAP, DEFAULT_POPULARITY_SCORE

class RerankService:
    def semantic_overlap_score(self, recommendation: Dict[str, Any], user_product: Dict[str, Any]) -> float:
        """
        Calculates similarity overlap score based on topics, technologies, tools, tags, and security types.
        """
        score = 0.0

        # Topic overlap (0.35 weight per overlap)
        rec_topics = set(recommendation.get("internalTopics", []))
        user_topics = set(user_product.get("internalTopics", []))
        score += len(rec_topics.intersection(user_topics)) * 0.35

        # Technologies overlap (0.20 weight per overlap)
        rec_tech = set(recommendation.get("technologies", []))
        user_tech = set(user_product.get("technologies", []))
        score += len(rec_tech.intersection(user_tech)) * 0.20

        # Tools overlap (0.15 weight per overlap)
        rec_tools = set(recommendation.get("tools", []))
        user_tools = set(user_product.get("tools", []))
        score += len(rec_tools.intersection(user_tools)) * 0.15

        # Tags overlap (0.10 weight per overlap)
        rec_tags = set(recommendation.get("tags", []))
        user_tags = set(user_product.get("tags", []))
        score += len(rec_tags.intersection(user_tags)) * 0.10

        # Security Type overlap (0.30 weight per overlap)
        rec_security = set(recommendation.get("securityType", []))
        user_security = set(user_product.get("securityType", []))
        score += len(rec_security.intersection(user_security)) * 0.30

        return score

    def rerank_recommendations(
        self,
        recommendations: List[Dict[str, Any]],
        cart_products_metadata: List[Dict[str, Any]],
        enrolled_products_metadata: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Applies a multi-layered rule-based rerank score adjustment logic to candidate recommendations.
        """
        if enrolled_products_metadata is None:
            enrolled_products_metadata = []

        user_products = cart_products_metadata + enrolled_products_metadata
        domain_counter = defaultdict(int)
        reranked = []

        for rec in recommendations:
            score = rec["aggregated_score"]
            rec_domain = rec["domain"]
            rec_difficulty = rec["difficulty"]

            # 1. Semantic Overlap Score
            for user_product in user_products:
                score += self.semantic_overlap_score(rec, user_product)

            # 2. Same Domain Boost
            for user_product in user_products:
                if rec_domain == user_product["domain"]:
                    score += DOMAIN_BOOSTS.get(rec_domain, 0.15)

            # 3. Offensive / Defensive Alignment
            for user_product in user_products:
                user_security_types = user_product.get("securityType", [])
                rec_security_types = rec.get("securityType", [])
                overlap = set(user_security_types).intersection(set(rec_security_types))
                if overlap:
                    score += 0.30

            # 4. Learning Progression
            rec_level = PROGRESSION_MAP.get(rec_difficulty, 1)
            for user_product in user_products:
                user_level = PROGRESSION_MAP.get(user_product.get("difficulty"), 1)
                if rec_level == user_level:
                    score += 0.15
                elif rec_level == user_level + 1:
                    score += 0.25
                elif rec_level > user_level + 1:
                    score -= 0.20

            # 5. Learning Path Continuity
            for user_product in user_products:
                learning_path = user_product.get("learningPath", [])
                if rec["id"] in learning_path:
                    score += 0.50

            # 6. Cloud Specialization
            for user_product in user_products:
                if user_product.get("domain") == "cloud-security" and rec_domain == "cloud-security":
                    score += 0.35

            # 7. Generic Beginner Penalty
            if rec_domain == "blue-team" and rec_difficulty == "beginner":
                score -= 0.15

            # 8. Diversity Control
            domain_counter[rec_domain] += 1
            if domain_counter[rec_domain] > 3:
                score -= 0.25

            # 9. Popularity Boost
            popularity = rec.get("popularityScore", DEFAULT_POPULARITY_SCORE)
            popularity_boost = (popularity / 100) * 0.05
            score += popularity_boost

            # 10. Score Normalization
            if score < 0:
                score = 0.0

            rec["reranked_score"] = round(score, 4)
            reranked.append(rec)

        # Final Sort by reranked_score desc
        reranked = sorted(
            reranked,
            key=lambda x: x["reranked_score"],
            reverse=True
        )

        return reranked
