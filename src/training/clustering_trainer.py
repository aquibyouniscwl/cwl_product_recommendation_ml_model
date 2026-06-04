import joblib
import numpy as np
from sklearn.cluster import KMeans
from src.config.settings import settings
from src.utils.logger import logger


class ClusteringTrainer:
    def train_and_save(self, vectors: np.ndarray, n_clusters: int = 3) -> KMeans:
        """
        Trains a KMeans clustering model on features and saves the model.
        """
        logger.info(
            f"Starting KMeans clustering training with n_clusters={n_clusters}..."
        )
        # Instantiate and fit KMeans
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        kmeans.fit(vectors)
        logger.info(
            f"KMeans model trained. Cluster centers shape: {kmeans.cluster_centers_.shape}"
        )
        # Save KMeans model
        joblib.dump(kmeans, settings.KMEANS_MODEL_PATH)
        logger.info(f"Saved KMeans clustering model to: {settings.KMEANS_MODEL_PATH}")
        return kmeans
