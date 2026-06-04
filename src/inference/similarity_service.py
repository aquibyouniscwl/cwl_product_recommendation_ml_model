from typing import List
from typing import Dict
from typing import Any
import numpy as np
from src.models.loader import ModelLoader
from src.utils.logger import logger


# =====================================================
# SIMILARITY SERVICE
# =====================================================
class SimilarityService:
    # =================================================
    # INITIALIZE
    # =================================================
    def __init__(self):
        self.model_loader = ModelLoader()

    # =================================================
    # GET SIMILAR PRODUCTS
    # =================================================
    def get_similar_products(
        self, product_id: str, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        # -------------------------------------------------
        # ENSURE MODELS ARE LOADED
        # -------------------------------------------------
        self.model_loader.load_all()
        # -------------------------------------------------
        # FETCH LOADED ARTIFACTS
        # -------------------------------------------------
        similarity_matrix = self.model_loader.similarity_matrix
        metadata = self.model_loader.metadata
        product_id_to_index = self.model_loader.product_id_to_index
        # -------------------------------------------------
        # VALIDATE LOADED MODELS
        # -------------------------------------------------
        if similarity_matrix is None:
            logger.error("Similarity matrix not loaded.")
            return []
        if metadata is None:
            logger.error("Metadata not loaded.")
            return []
        # -------------------------------------------------
        # VALIDATE PRODUCT ID
        # -------------------------------------------------
        if product_id not in product_id_to_index:
            logger.warning(f"Product ID '{product_id}' not found.")
            return []
        # -------------------------------------------------
        # FETCH PRODUCT INDEX
        # -------------------------------------------------
        product_index = product_id_to_index[product_id]
        # -------------------------------------------------
        # GET SIMILARITY SCORES
        # -------------------------------------------------
        similarity_scores = similarity_matrix[product_index]
        # -------------------------------------------------
        # SORT HIGHEST SIMILARITIES
        # -------------------------------------------------
        sorted_indices = np.argsort(similarity_scores)[::-1]
        # -------------------------------------------------
        # BUILD RECOMMENDATIONS
        # -------------------------------------------------
        recommendations = []
        for index in sorted_indices:
            # ---------------------------------------------
            # SKIP SAME PRODUCT
            # ---------------------------------------------
            if index == product_index:
                continue
            product_metadata = metadata[index]
            recommendations.append(
                {
                    "id": product_metadata["id"],
                    "title": product_metadata["title"],
                    "score": round(float(similarity_scores[index]), 4),
                    "domain": product_metadata["domain"],
                    "difficulty": product_metadata["difficulty"],
                }
            )
            # ---------------------------------------------
            # LIMIT TOP K
            # ---------------------------------------------
            if len(recommendations) >= top_k:
                break
        # -------------------------------------------------
        # RETURN RESULTS
        # -------------------------------------------------
        return recommendations
