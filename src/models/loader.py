import os
import json
import joblib
import numpy as np
from typing import Dict, Any, Optional, List
from src.config.settings import settings
from src.utils.logger import logger

class ModelLoader:
    _instance: Optional['ModelLoader'] = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ModelLoader, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self.similarity_matrix: Optional[np.ndarray] = None
        self.metadata: Optional[List[Dict[str, Any]]] = None
        self.product_vectors: Optional[np.ndarray] = None
        self.kmeans_model: Optional[Any] = None
        self.encoders: Dict[str, Any] = {}
        self.product_id_to_index: Dict[str, int] = {}
        self._initialized = True

    def load_all(self, force: bool = False) -> None:
        """
        Loads all model assets and encoders into memory.
        If force=True, reloads even if already loaded.
        """
        if self.similarity_matrix is not None and not force:
            logger.info("Models already loaded in memory.")
            return

        logger.info("========================================")
        logger.info("LOADING CENTRALIZED MODEL REGISTRY")
        logger.info("========================================")

        # 1. Load Similarity Matrix
        sim_path = settings.similarity_matrix_path
        if os.path.exists(sim_path):
            self.similarity_matrix = np.load(sim_path)
            logger.info(f"Loaded similarity matrix from {sim_path}")
        else:
            logger.warning(f"Similarity matrix not found at {sim_path}")

        # 2. Load Product Vectors
        vec_path = settings.product_vectors_path
        if os.path.exists(vec_path):
            self.product_vectors = np.load(vec_path)
            logger.info(f"Loaded product vectors from {vec_path}")
        else:
            logger.warning(f"Product vectors not found at {vec_path}")

        # 3. Load Metadata
        meta_path = settings.metadata_path
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
            logger.info(f"Loaded product metadata from {meta_path}")
            
            # Recreate product_id_to_index mapping
            self.product_id_to_index = {
                product["id"]: idx for idx, product in enumerate(self.metadata)
            }
            logger.info("Product ID mapping created successfully.")
        else:
            logger.warning(f"Metadata not found at {meta_path}")

        # 4. Load Encoders
        encoder_names = [
            "team_encoder", "security_encoder", "topics_encoder",
            "tags_encoder", "technologies_encoder", "tools_encoder",
            "related_domains_encoder", "learning_path_encoder",
            "domain_encoder", "scaler"
        ]
        
        for name in encoder_names:
            enc_path = os.path.join(settings.MODELS_DIR, f"{name}.pkl")
            if os.path.exists(enc_path):
                self.encoders[name] = joblib.load(enc_path)
                logger.info(f"Loaded encoder '{name}' from {enc_path}")
            else:
                logger.warning(f"Encoder file '{name}' not found at {enc_path}")

        # 5. Load KMeans Model
        kmeans_path = settings.kmeans_model_path
        if os.path.exists(kmeans_path):
            self.kmeans_model = joblib.load(kmeans_path)
            logger.info(f"Loaded KMeans clustering model from {kmeans_path}")
        else:
            logger.info("KMeans clustering model not found (optional).")

        logger.info("Centralized model loading complete.\n")

    def get_product_metadata(self, product_id: str) -> Optional[Dict[str, Any]]:
        """
        O(1) lookup of metadata by product ID.
        """
        if not self.metadata:
            return None
        idx = self.product_id_to_index.get(product_id)
        if idx is not None and idx < len(self.metadata):
            return self.metadata[idx]
        return None
