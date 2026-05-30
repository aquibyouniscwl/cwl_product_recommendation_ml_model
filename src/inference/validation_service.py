import json
from typing import List, Dict, Any
from groq import Groq
from src.config.settings import settings
from src.utils.helpers import clean_and_parse_json
from src.utils.logger import logger

class ValidationService:
    def __init__(self):
        # Fetch configurations from Settings
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
        self.temperature = settings.VALIDATION_TEMPERATURE

    def build_user_profile(
        self,
        cart_products: List[Dict[str, Any]],
        enrolled_products: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Structures the user profile data format for the LLM request.
        """
        profile = {
            "cartProducts": [],
            "enrolledProducts": []
        }

        for product in cart_products:
            profile["cartProducts"].append({
                "title": product["title"],
                "domain": product["domain"],
                "difficulty": product["difficulty"],
                "topics": product.get("internalTopics", []),
                "securityType": product.get("securityType", []),
                "technologies": product.get("technologies", []),
                "tags": product.get("tags", [])
            })

        for product in enrolled_products:
            profile["enrolledProducts"].append({
                "title": product["title"],
                "domain": product["domain"],
                "difficulty": product["difficulty"],
                "topics": product.get("internalTopics", []),
                "securityType": product.get("securityType", []),
                "technologies": product.get("technologies", []),
                "tags": product.get("tags", [])
            })

        return profile

    def build_recommendation_context(self, recommendations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Formats candidate recommendations for LLM context.
        """
        context = []
        for rec in recommendations:
            context.append({
                "title": rec["title"],
                "domain": rec["domain"],
                "difficulty": rec["difficulty"],
                "topics": rec.get("internalTopics", []),
                "securityType": rec.get("securityType", []),
                "technologies": rec.get("technologies", []),
                "tags": rec.get("tags", []),
                "score": rec["reranked_score"]
            })
        return context

    def validate_and_explain_recommendations(
        self,
        cart_products: List[Dict[str, Any]],
        enrolled_products: List[Dict[str, Any]],
        recommendations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validates recommended paths and outputs a holistic explanation via Groq.
        """
        user_profile = self.build_user_profile(cart_products, enrolled_products)
        recommendation_context = self.build_recommendation_context(recommendations)

        prompt = f"""
You are an elite cybersecurity recommendation intelligence engine.

Your role:
- validate ML recommendations
- identify weak recommendations
- prioritize realistic learning progression
- prioritize specialization continuity
- prioritize offensive/defensive alignment
- prioritize semantic topic overlap
- avoid unrelated beginner recommendations
- preserve realistic cyber learning paths

IMPORTANT RULES:
- Return ONLY valid raw JSON
- Do NOT use markdown
- Do NOT wrap response in ```json
- Do NOT explain outside JSON
- Return ONLY the requested structure

USER PROFILE:
{json.dumps(user_profile, indent=2)}

ML RECOMMENDATIONS:
{json.dumps(recommendation_context, indent=2)}

RETURN THIS EXACT JSON STRUCTURE:

{{
    "validated_recommendations": [
        {{
            "title": "Course Name",
            "reason": "Why this recommendation is relevant",
            "confidence_score": 9.4
        }}
    ],

    "overall_explanation":
    "Holistic explanation of the recommendation strategy."
}}
"""
        logger.info("Submitting recommendations for validation and path explanation...")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a cybersecurity recommendation intelligence engine."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature
            )

            content = response.choices[0].message.content
            logger.info("Successfully received validation and explanation response.")
            return clean_and_parse_json(content)

        except Exception as e:
            logger.error(f"Error calling Groq for recommendation validation: {str(e)}")
            # Fallback logic mirroring the exact fallback logic from original rag_explainer
            return {
                "validated_recommendations": [
                    {
                        "title": rec["title"],
                        "reason": "Fallback recommendation validation.",
                        "confidence_score": round(rec["reranked_score"], 2)
                    }
                    for rec in recommendations
                ],
                "overall_explanation": f"LLM parsing failed. Error: {str(e)}"
            }
