import sys
from src.training.pipeline import TrainingPipeline
from src.utils.logger import logger


def main():
    """
    Orchestrator script to execute offline retraining.
    Run via: python train.py
    """
    try:
        pipeline = TrainingPipeline()
        pipeline.run(train_clustering=True, n_clusters=3)
    except Exception as e:
        logger.error(f"Training pipeline run failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
