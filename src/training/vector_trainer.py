import os
import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List
from sklearn.preprocessing import MultiLabelBinarizer, OneHotEncoder, StandardScaler
from src.config.settings import settings
from src.config.feature_weights import FEATURE_WEIGHTS
from src.utils.logger import logger


class VectorTrainer:
    def __init__(self):
        self.team_encoder = MultiLabelBinarizer()
        self.security_encoder = MultiLabelBinarizer()
        self.topics_encoder = MultiLabelBinarizer()
        self.tags_encoder = MultiLabelBinarizer()
        self.technologies_encoder = MultiLabelBinarizer()
        self.tools_encoder = MultiLabelBinarizer()
        self.related_domains_encoder = MultiLabelBinarizer()
        self.learning_path_encoder = MultiLabelBinarizer()
        self.domain_encoder = OneHotEncoder(sparse_output=False)
        self.scaler = StandardScaler()

    def validate_dataset(self, data: List[Dict[str, Any]]) -> bool:
        """
        Validates the dataset structure and required fields.
        """
        logger.info("Validating dataset schema and contents...")
        required_fields = {
            "id": str,
            "title": str,
            "domain": str,
            "team": list,
            "securityType": list,
            "difficulty": str,
            "difficultyScore": (int, float),
            "price": (int, float),
            "popularityScore": (int, float),
        }
        for idx, item in enumerate(data):
            # Check fields and types
            for field, expected_type in required_fields.items():
                if field not in item:
                    logger.error(
                        f"Validation failed: Product at index {idx} is missing required field '{field}'"
                    )
                    return False
                val = item[field]
                if not isinstance(val, expected_type):
                    logger.error(
                        f"Validation failed: Product ID '{item.get('id', idx)}' "
                        f"has invalid type for '{field}'. Expected {expected_type}, got {type(val)}"
                    )
                    return False
            # Check difficulty levels
            if item["difficulty"] not in ["beginner", "intermediate", "advanced"]:
                logger.error(
                    f"Validation failed: Product ID '{item['id']}' has invalid difficulty value '{item['difficulty']}'"
                )
                return False
        logger.info(
            f"Dataset validation successful. Total validated products: {len(data)}"
        )
        return True

    def train_and_save(self) -> Tuple[np.ndarray, pd.DataFrame]:
        """
        Executes raw dataset loading, validation, encoding, weighting, stacking, and artifact saving.
        """
        logger.info("Starting feature engineering and vector generation...")
        # Load dataset
        if not os.path.exists(settings.RAW_DATASET_PATH):
            raise FileNotFoundError(
                f"Raw dataset not found at: {settings.RAW_DATASET_PATH}"
            )
        with open(settings.RAW_DATASET_PATH, "r", encoding="utf-8") as f:
            products = json.load(f)
        # Validate dataset
        if not self.validate_dataset(products):
            raise ValueError("Dataset validation failed. Training aborted.")
        df = pd.DataFrame(products)
        # Encode categorical/multilabel lists
        team_features = self.team_encoder.fit_transform(df["team"])
        security_features = self.security_encoder.fit_transform(df["securityType"])
        topics_features = self.topics_encoder.fit_transform(df["internalTopics"])
        tags_features = self.tags_encoder.fit_transform(df["tags"])
        technologies_features = self.technologies_encoder.fit_transform(
            df["technologies"]
        )
        tools_features = self.tools_encoder.fit_transform(df["tools"])
        related_domains_features = self.related_domains_encoder.fit_transform(
            df["relatedDomains"]
        )
        learning_path_features = self.learning_path_encoder.fit_transform(
            df["learningPath"]
        )
        # Encode single value domain (One Hot)
        domain_features = self.domain_encoder.fit_transform(df[["domain"]])
        # Scale numeric features
        numeric_cols = ["difficultyScore", "price", "popularityScore"]
        scaled_numeric = self.scaler.fit_transform(df[numeric_cols])
        # Apply weights
        weighted_team = team_features * FEATURE_WEIGHTS["team"]
        weighted_security = security_features * FEATURE_WEIGHTS["securityType"]
        weighted_topics = topics_features * FEATURE_WEIGHTS["internalTopics"]
        weighted_tags = tags_features * FEATURE_WEIGHTS["tags"]
        weighted_technologies = technologies_features * FEATURE_WEIGHTS["technologies"]
        weighted_tools = tools_features * FEATURE_WEIGHTS["tools"]
        weighted_related_domains = (
            related_domains_features * FEATURE_WEIGHTS["relatedDomains"]
        )
        weighted_learning_path = (
            learning_path_features * FEATURE_WEIGHTS["learningPath"]
        )
        weighted_domain = domain_features * FEATURE_WEIGHTS["domain"]
        weighted_numeric = scaled_numeric.copy()
        weighted_numeric[:, 0] *= FEATURE_WEIGHTS["difficultyScore"]
        weighted_numeric[:, 1] *= FEATURE_WEIGHTS["price"]
        weighted_numeric[:, 2] *= FEATURE_WEIGHTS["popularityScore"]
        # Stack features
        combined_features = np.hstack(
            [
                weighted_team,
                weighted_security,
                weighted_topics,
                weighted_tags,
                weighted_technologies,
                weighted_tools,
                weighted_related_domains,
                weighted_learning_path,
                weighted_domain,
                weighted_numeric,
            ]
        )
        logger.info(
            f"Generated vectors with combined feature shape: {combined_features.shape}"
        )
        # Save artifacts
        os.makedirs(settings.MODELS_DIR, exist_ok=True)
        os.makedirs(settings.PROCESSED_DATA_DIR, exist_ok=True)
        np.save(settings.PRODUCT_VECTORS_PATH, combined_features)
        df.to_json(settings.METADATA_PATH, orient="records", indent=2)
        df.to_json(settings.CLEANED_PRODUCTS_PATH, orient="records", indent=2)
        # Dump encoders
        joblib.dump(
            self.team_encoder, os.path.join(settings.MODELS_DIR, "team_encoder.pkl")
        )
        joblib.dump(
            self.security_encoder,
            os.path.join(settings.MODELS_DIR, "security_encoder.pkl"),
        )
        joblib.dump(
            self.topics_encoder, os.path.join(settings.MODELS_DIR, "topics_encoder.pkl")
        )
        joblib.dump(
            self.tags_encoder, os.path.join(settings.MODELS_DIR, "tags_encoder.pkl")
        )
        joblib.dump(
            self.technologies_encoder,
            os.path.join(settings.MODELS_DIR, "technologies_encoder.pkl"),
        )
        joblib.dump(
            self.tools_encoder, os.path.join(settings.MODELS_DIR, "tools_encoder.pkl")
        )
        joblib.dump(
            self.related_domains_encoder,
            os.path.join(settings.MODELS_DIR, "related_domains_encoder.pkl"),
        )
        joblib.dump(
            self.learning_path_encoder,
            os.path.join(settings.MODELS_DIR, "learning_path_encoder.pkl"),
        )
        joblib.dump(
            self.domain_encoder, os.path.join(settings.MODELS_DIR, "domain_encoder.pkl")
        )
        joblib.dump(self.scaler, os.path.join(settings.MODELS_DIR, "scaler.pkl"))
        logger.info(
            "Saved product vectors, encoders, metadata, and cleaned outputs successfully."
        )
        return combined_features, df
