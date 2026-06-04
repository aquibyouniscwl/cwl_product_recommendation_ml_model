from collections import defaultdict
from typing import List, Dict, Any, Optional
import json
import time

from src.models.loader import ModelLoader
from src.inference.similarity_service import SimilarityService
from src.inference.rerank_service import RerankService

from src.cache.cache_service import (
    get_cache,
    set_cache,
    CACHE_ENABLED,
)

from src.cache.cache_utils import generate_cache_key
from src.cache.lru_cache_service import lru_cache_service

from src.analytics.pattern_analytics import pattern_analytics

from src.utils.logger import logger


# =====================================================
# RECOMMENDATION SERVICE
# =====================================================
class RecommendationService:

    def __init__(self):
        self.model_loader = ModelLoader()
        self.similarity_service = SimilarityService()
        self.rerank_service = RerankService()

    # =================================================
    # MAIN RECOMMENDATION PIPELINE
    # =================================================
    def get_recommendations(
        self,
        cart_products: List[str],
        enrolled_products: Optional[List[str]] = None,
        top_k: int = 10,
    ) -> Dict[str, Any]:

        # -------------------------------------------------
        # HANDLE EMPTY ENROLLED PRODUCTS
        # -------------------------------------------------
        if enrolled_products is None:
            enrolled_products = []

        # =================================================
        # TRACK ALL REQUESTS
        # =================================================
        try:
            pattern_analytics.track_request_pattern(
                cart_products,
                enrolled_products,
            )
        except Exception as e:
            logger.error(
                f"Pattern tracking failed: {e}"
            )

        # -------------------------------------------------
        # USER PRODUCTS
        # -------------------------------------------------
        all_user_products = (
            cart_products + enrolled_products
        )

        logger.info(
            f"Generating recommendations "
            f"for cart={cart_products}, "
            f"enrolled={enrolled_products}"
        )
        start_time = time.perf_counter()

        # =================================================
        # CACHE KEY
        # =================================================
        cache_key = generate_cache_key(
            cart_products,
            enrolled_products,
            top_k,
        )

        # =================================================
        # STEP 0A — LRU CACHE CHECK
        # =================================================
        lru_result = lru_cache_service.get_from_lru(
            cache_key
        )

        if lru_result is not None:

            logger.info(
                f"LRU cache hit: {cache_key}"
            )

            lru_result["cache_status"] = "lru_hit"
            lru_result["cache_key"] = cache_key

            lru_stats = (
                lru_cache_service.get_lru_stats()
            )

            lru_result["lru_hits"] = (
                lru_stats["lru_hits"]
            )

            lru_result["lru_misses"] = (
                lru_stats["lru_misses"]
            )

            try:
                pattern_analytics.auto_save()
            except Exception:
                pass
            elapsed = time.perf_counter() - start_time

            logger.info(
                f"Request completed in {elapsed:.6f}s "
                f"(LRU HIT)"
            )
            return lru_result

        # =================================================
        # STEP 0B — REDIS CACHE CHECK
        # =================================================
        if CACHE_ENABLED:

            cached_response = get_cache(
                cache_key
            )

            if cached_response:

                logger.info(
                    f"Redis cache hit: {cache_key}"
                )

                cached_data = json.loads(
                    cached_response
                )

                cached_data["cache_status"] = "hit"
                cached_data["cache_key"] = cache_key

                # Promote to LRU
                lru_cache_service.store_in_lru(
                    cache_key,
                    cached_data.copy(),
                )

                lru_stats = (
                    lru_cache_service.get_lru_stats()
                )

                cached_data["lru_hits"] = (
                    lru_stats["lru_hits"]
                )

                cached_data["lru_misses"] = (
                    lru_stats["lru_misses"]
                )

                try:
                    pattern_analytics.auto_save()
                except Exception:
                    pass
                elapsed = time.perf_counter() - start_time

                logger.info(
                    f"Request completed in {elapsed:.6f}s "
                    f"(REDIS HIT)"
                )
                return cached_data

            logger.info(
                f"Redis cache miss: {cache_key}"
            )

        # -------------------------------------------------
        # LOAD MODELS
        # -------------------------------------------------
        self.model_loader.load_all()

        # =================================================
        # STEP 1 — SIMILARITY RETRIEVAL
        # =================================================
        aggregated_scores = defaultdict(float)

        for product_id in all_user_products:

            similar_products = (
                self.similarity_service
                .get_similar_products(
                    product_id,
                    top_k=top_k,
                )
            )

            for item in similar_products:

                recommendation_id = item["id"]

                if recommendation_id in all_user_products:
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
            reverse=True,
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

            candidates.append(
                {
                    "id": rec_meta["id"],
                    "title": rec_meta["title"],
                    "domain": rec_meta["domain"],
                    "difficulty": rec_meta["difficulty"],
                    "aggregated_score": round(score, 4),
                    "internalTopics": rec_meta.get("internalTopics", []),
                    "technologies": rec_meta.get("technologies", []),
                    "tools": rec_meta.get("tools", []),
                    "tags": rec_meta.get("tags", []),
                    "securityType": rec_meta.get("securityType", []),
                    "learningPath": rec_meta.get("learningPath", []),
                    "relatedDomains": rec_meta.get("relatedDomains", []),
                    "team": rec_meta.get("team", []),
                    "popularityScore": rec_meta.get("popularityScore", 50),
                    "difficultyScore": rec_meta.get("difficultyScore", 1),
                    "price": rec_meta.get("price", 0),
                }
            )

        # =================================================
        # STEP 5 — SEMANTIC RERANKING
        # =================================================
        reranked_candidates = (
            self.rerank_service
            .rerank_recommendations(
                recommendations=candidates,
                cart_products_metadata=cart_products_metadata,
                enrolled_products_metadata=enrolled_products_metadata,
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
        # TRACK RECOMMENDATION PATTERNS
        # =================================================
        recommendation_ids = [
            r["id"]
            for r in final_recommendations
        ]

        try:

            pattern_analytics.track_recommendation_pattern(
                cart_products,
                enrolled_products,
                recommendation_ids,
            )

            pattern_analytics.auto_save()

        except Exception as e:

            logger.error(
                f"Pattern analytics failed: {e}"
            )

        # =================================================
        # FINAL RESPONSE
        # =================================================
        lru_stats = (
            lru_cache_service.get_lru_stats()
        )

        result = {
            "recommendations":
                final_recommendations,

            "cache_status":
                "miss",

            "cache_key":
                cache_key,

            "lru_hits":
                lru_stats["lru_hits"],

            "lru_misses":
                lru_stats["lru_misses"],
        }

        # =================================================
        # STORE IN REDIS CACHE
        # =================================================
        if CACHE_ENABLED:

            set_cache(
                cache_key,
                json.dumps(result),
                ttl=3600,
            )

            logger.info(
                f"Stored recommendations "
                f"in Redis cache: "
                f"{cache_key}"
            )

        # =================================================
        # STORE IN LRU CACHE
        # =================================================
        lru_cache_service.store_in_lru(
            cache_key,
            result.copy(),
        )
        elapsed = time.perf_counter() - start_time

        logger.info(
            f"Request completed in {elapsed:.6f}s "
            f"(CACHE MISS)"
        )
        return result