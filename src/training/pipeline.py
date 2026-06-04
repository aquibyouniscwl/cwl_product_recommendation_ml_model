from src.training.vector_trainer import VectorTrainer
from src.training.similarity_trainer import SimilarityTrainer
from src.training.clustering_trainer import ClusteringTrainer
from src.models.registry import ModelRegistry
from src.utils.logger import logger


class TrainingPipeline:
    def __init__(self):
        self.vector_trainer = VectorTrainer()
        self.similarity_trainer = SimilarityTrainer()
        self.clustering_trainer = ClusteringTrainer()

    def run(self, train_clustering: bool = True, n_clusters: int = 3) -> None:
        """
        Executes the full offline training flow sequentially.
        """
        logger.info("========================================")
        logger.info("STARTING OFFLINE TRAINING PIPELINE")
        logger.info("========================================")
        try:
            # 1. Preprocess & Feature Engineering & Save
            vectors, df = self.vector_trainer.train_and_save()
            # 2. Compute similarity & Save
            self.similarity_trainer.train_and_save(vectors)
            # 3. Optionally fit clustering model & Save
            if train_clustering:
                self.clustering_trainer.train_and_save(vectors, n_clusters=n_clusters)
            # 4. Save metadata
            ModelRegistry.save_run_metadata(
                vector_shape=list(vectors.shape),
                total_products=len(df),
                has_clustering=train_clustering,
            )
            logger.info("========================================")
            logger.info("OFFLINE TRAINING PIPELINE COMPLETED")
            logger.info("========================================")
        except Exception as e:
            logger.error(f"Training pipeline execution failed: {str(e)}")
            raise e
