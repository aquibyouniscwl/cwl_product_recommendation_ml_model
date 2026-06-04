import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from src.config.settings import settings
from src.utils.logger import logger


class SimilarityTrainer:
    def train_and_save(self, vectors: np.ndarray) -> np.ndarray:
        """
        Calculates pairwise cosine similarity from the stacked features vectors and saves the matrix.
        """
        logger.info("Starting cosine similarity calculations...")
        similarity_matrix = cosine_similarity(vectors)
        logger.info(
            f"Similarity matrix calculated with shape: {similarity_matrix.shape}"
        )
        np.save(settings.SIMILARITY_MATRIX_PATH, similarity_matrix)
        logger.info(f"Saved similarity matrix to: {settings.SIMILARITY_MATRIX_PATH}")
        return similarity_matrix
