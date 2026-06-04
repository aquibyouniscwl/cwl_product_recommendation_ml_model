import os
import json
import joblib
import numpy as np
from typing import Dict
from typing import Any
from typing import Optional
from typing import List
from src.config.settings import settings
from src.utils.logger import logger


# =====================================================
# MODEL LOADER (SINGLETON)
# =====================================================
class ModelLoader:
    _instance = None

    # =================================================
    # SINGLETON INSTANCE
    # =================================================
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    # =================================================
    # INITIALIZE
    # =================================================
    def __init__(self):
        if self._initialized:
            return
        # -------------------------------------------------
        # MODEL ARTIFACTS
        # -------------------------------------------------
        self.similarity_matrix = None
        self.product_vectors = None
        self.metadata = None
        self.kmeans_model = None
        self.encoders = {}
        self.product_id_to_index = {}
        self._initialized = True

    # =================================================
    # LOAD ALL MODELS
    # =================================================
    def load_all(self, force: bool = False) -> None:
        # -------------------------------------------------
        # AVOID RELOADING
        # -------------------------------------------------
        if self.similarity_matrix is not None and not force:
            logger.info("Models already loaded.")
            return
        logger.info("========================================")
        logger.info("LOADING MODEL REGISTRY")
        logger.info("========================================")
        # =================================================
        # 1. LOAD SIMILARITY MATRIX
        # =================================================
        if os.path.exists(settings.SIMILARITY_MATRIX_PATH):
            self.similarity_matrix = np.load(settings.SIMILARITY_MATRIX_PATH)
            logger.info("Similarity matrix loaded.")
        else:
            logger.warning("Similarity matrix not found.")
        # =================================================
        # 2. LOAD PRODUCT VECTORS
        # =================================================
        if os.path.exists(settings.PRODUCT_VECTORS_PATH):
            self.product_vectors = np.load(settings.PRODUCT_VECTORS_PATH)
            logger.info("Product vectors loaded.")
        else:
            logger.warning("Product vectors not found.")
        # =================================================
        # 3. LOAD METADATA
        # =================================================
        if os.path.exists(settings.METADATA_PATH):
            with open(settings.METADATA_PATH, "r", encoding="utf-8") as file:
                self.metadata = json.load(file)
            logger.info("Metadata loaded.")
            # ---------------------------------------------
            # CREATE FAST LOOKUP
            # ---------------------------------------------
            self.product_id_to_index = {
                product["id"]: index for index, product in enumerate(self.metadata)
            }
            logger.info("Product ID mapping created.")
        else:
            logger.warning("Metadata not found.")
        # =================================================
        # 4. LOAD ENCODERS
        # =================================================
        encoder_names = [
            "team_encoder",
            "security_encoder",
            "topics_encoder",
            "tags_encoder",
            "technologies_encoder",
            "tools_encoder",
            "related_domains_encoder",
            "learning_path_encoder",
            "domain_encoder",
            "scaler",
        ]
        for encoder_name in encoder_names:
            encoder_path = os.path.join(settings.MODELS_DIR, f"{encoder_name}.pkl")
            if os.path.exists(encoder_path):
                self.encoders[encoder_name] = joblib.load(encoder_path)
                logger.info(f"{encoder_name} loaded.")
            else:
                logger.warning(f"{encoder_name} missing.")
        # =================================================
        # 5. LOAD KMEANS MODEL
        # =================================================
        if os.path.exists(settings.KMEANS_MODEL_PATH):
            self.kmeans_model = joblib.load(settings.KMEANS_MODEL_PATH)
            logger.info("KMeans model loaded.")
        else:
            logger.warning("KMeans model not found.")
        logger.info("Model registry loading complete.")

    # =================================================
    # GET PRODUCT METADATA
    # =================================================
    def get_product_metadata(self, product_id: str) -> Optional[Dict[str, Any]]:
        if self.metadata is None:
            return None
        product_index = self.product_id_to_index.get(product_id)
        if product_index is None:
            return None
        return self.metadata[product_index]
