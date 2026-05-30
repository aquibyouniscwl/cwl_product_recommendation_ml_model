from typing import List, Dict, Any
import numpy as np
from src.models.loader import ModelLoader
from src.utils.logger import logger

class SimilarityService:
    def __init__(self):
        self.model_loader = ModelLoader()

    def get_similar_products(self, product_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Given a product_id, retrieves the most similar products using the similarity matrix from ModelLoader.
        """
        # Ensure model registry is loaded in memory
        self.model_loader.load_all()

        similarity_matrix = self.model_loader.similarity_matrix
        metadata = self.model_loader.metadata
        product_id_to_index = self.model_loader.product_id_to_index

        if similarity_matrix is None or metadata is None:
            logger.error("Similarity matrix or metadata is not loaded.")
            return []

        if product_id not in product_id_to_index:
            logger.warning(f"Product ID '{product_id}' not found in metadata index.")
            return []

        product_index = product_id_to_index[product_id]
        similarity_scores = similarity_matrix[product_index]

        # Sort indices by highest similarity score
        sorted_indices = np.argsort(similarity_scores)[::-1]

        recommendations = []
        for idx in sorted_indices:
            # Skip the query product itself
            if idx == product_index:
                continue

            recommendations.append({
                "id": metadata[idx]["id"],
                "title": metadata[idx]["title"],
                "score": float(similarity_scores[idx]),
                "domain": metadata[idx]["domain"],
                "difficulty": metadata[idx]["difficulty"]
            })

            if len(recommendations) >= top_k:
                break

        return recommendations
