import os
import json
import datetime

from typing import Dict
from typing import Any

from src.config.settings import (
    settings
)

from src.utils.logger import (
    logger
)


# =====================================================
# MODEL REGISTRY
# =====================================================

class ModelRegistry:


    # =================================================
    # GET TRAINING METADATA
    # =================================================

    @staticmethod

    def get_metadata() -> Dict[str, Any]:

        metadata_path = os.path.join(

            settings.MODELS_DIR,

            "train_run_metadata.json"
        )

        # -------------------------------------------------
        # CHECK FILE EXISTS
        # -------------------------------------------------

        if not os.path.exists(
            metadata_path
        ):

            logger.warning(
                "Training metadata not found."
            )

            return {}

        # -------------------------------------------------
        # LOAD METADATA
        # -------------------------------------------------

        with open(

            metadata_path,

            "r",

            encoding="utf-8"

        ) as file:

            metadata = json.load(
                file
            )

        logger.info(
            "Training metadata loaded."
        )

        return metadata


    # =================================================
    # SAVE TRAINING METADATA
    # =================================================

    @staticmethod

    def save_run_metadata(

        vector_shape: list,

        total_products: int,

        has_clustering: bool

    ) -> None:

        # -------------------------------------------------
        # CREATE MODELS DIRECTORY
        # -------------------------------------------------

        os.makedirs(

            settings.MODELS_DIR,

            exist_ok=True
        )

        metadata_path = os.path.join(

            settings.MODELS_DIR,

            "train_run_metadata.json"
        )

        # -------------------------------------------------
        # BUILD METADATA
        # -------------------------------------------------

        metadata = {

            "trained_at":

            datetime.datetime.utcnow()
            .isoformat(),

            "vector_shape":
            vector_shape,

            "total_products":
            total_products,

            "has_clustering_model":
            has_clustering
        }

        # -------------------------------------------------
        # SAVE METADATA
        # -------------------------------------------------

        with open(

            metadata_path,

            "w",

            encoding="utf-8"

        ) as file:

            json.dump(

                metadata,

                file,

                indent=2
            )

        logger.info(
            "Training metadata saved."
        )