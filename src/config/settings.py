import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    # Base directories
    BASE_DIR: Path = Path(os.getcwd())
    
    # Data & Models paths
    RAW_DATASET_PATH: str = os.getenv(
        "RAW_DATASET_PATH",
        str(BASE_DIR / "data" / "raw" / "products_dataset.json")
    )
    PROCESSED_DATA_DIR: str = os.getenv(
        "PROCESSED_DATA_DIR",
        str(BASE_DIR / "data" / "processed")
    )
    MODELS_DIR: str = os.getenv(
        "MODELS_DIR",
        str(BASE_DIR / "models")
    )

    # API Configuration
    HOST: str = os.getenv("API_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("API_PORT", "8000"))

    # Groq Settings
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv(
        "GROQ_MODEL",
        "llama-3.3-70b-versatile"
    )
    AI_RERANK_TEMPERATURE: float = float(
        os.getenv("AI_RERANK_TEMPERATURE", "0.1")
    )
    VALIDATION_TEMPERATURE: float = float(
        os.getenv("VALIDATION_TEMPERATURE", "0.2")
    )

    @property
    def similarity_matrix_path(self) -> str:
        return os.path.join(self.MODELS_DIR, "similarity_matrix.npy")

    @property
    def product_vectors_path(self) -> str:
        return os.path.join(self.MODELS_DIR, "product_vectors.npy")

    @property
    def metadata_path(self) -> str:
        return os.path.join(self.MODELS_DIR, "metadata.json")

    @property
    def kmeans_model_path(self) -> str:
        return os.path.join(self.MODELS_DIR, "kmeans_model.pkl")

    @property
    def cleaned_products_path(self) -> str:
        return os.path.join(
            self.PROCESSED_DATA_DIR,
            "cleaned_products.json"
        )

# Instantiate singleton settings
settings = Settings()
