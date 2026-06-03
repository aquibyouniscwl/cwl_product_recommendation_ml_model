import os

from pathlib import Path

from dotenv import load_dotenv


# =====================================================
# LOAD ENV VARIABLES
# =====================================================

load_dotenv()


# =====================================================
# SETTINGS
# =====================================================

class Settings:

    # -------------------------------------------------
    # BASE DIRECTORY
    # -------------------------------------------------

    BASE_DIR = Path.cwd()

    # -------------------------------------------------
    # DATA DIRECTORIES
    # -------------------------------------------------

    DATA_DIR = BASE_DIR / "data"

    RAW_DATA_DIR = DATA_DIR / "raw"

    PROCESSED_DATA_DIR = DATA_DIR / "processed"

    # -------------------------------------------------
    # MODEL DIRECTORY
    # -------------------------------------------------

    MODELS_DIR = BASE_DIR / "models"

    # -------------------------------------------------
    # RAW DATASET
    # -------------------------------------------------

    RAW_DATASET_PATH = os.getenv(

        "RAW_DATASET_PATH",

        str(
            RAW_DATA_DIR
            / "products_dataset.json"
        )
    )

    # -------------------------------------------------
    # PROCESSED DATA
    # -------------------------------------------------

    CLEANED_PRODUCTS_PATH = str(

        PROCESSED_DATA_DIR
        / "cleaned_products.json"
    )

    # -------------------------------------------------
    # MODEL FILES
    # -------------------------------------------------

    PRODUCT_VECTORS_PATH = str(

        MODELS_DIR
        / "product_vectors.npy"
    )

    SIMILARITY_MATRIX_PATH = str(

        MODELS_DIR
        / "similarity_matrix.npy"
    )

    METADATA_PATH = str(

        MODELS_DIR
        / "metadata.json"
    )

    KMEANS_MODEL_PATH = str(

        MODELS_DIR
        / "kmeans_model.pkl"
    )

    # -------------------------------------------------
    # API CONFIGURATION
    # -------------------------------------------------

    API_HOST = os.getenv(

        "API_HOST",

        "0.0.0.0"
    )

    API_PORT = int(

        os.getenv(
            "API_PORT",
            "8000"
        )
    )


# =====================================================
# SETTINGS INSTANCE
# =====================================================

settings = Settings()