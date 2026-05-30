import os
import json
import datetime
from typing import Dict, Any
from src.config.settings import settings

class ModelRegistry:
    @staticmethod
    def get_metadata() -> Dict[str, Any]:
        """
        Retrieves training run metadata if available.
        """
        meta_path = os.path.join(settings.MODELS_DIR, "train_run_metadata.json")
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    @staticmethod
    def save_run_metadata(vector_shape: list, total_products: int, has_clustering: bool) -> None:
        """
        Saves training run metadata to models directory.
        """
        os.makedirs(settings.MODELS_DIR, exist_ok=True)
        meta_path = os.path.join(settings.MODELS_DIR, "train_run_metadata.json")
        metadata = {
            "trained_at": datetime.datetime.utcnow().isoformat(),
            "vector_shape": vector_shape,
            "total_products": total_products,
            "has_clustering_model": has_clustering
        }
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
