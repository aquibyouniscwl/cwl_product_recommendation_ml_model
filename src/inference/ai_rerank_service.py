import json
from typing import List, Dict, Any
from groq import Groq
from src.config.settings import settings
from src.utils.helpers import clean_and_parse_json
from src.utils.logger import logger

class AIRerankService:
    def __init__(self):
        # Initialized with settings values
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
        self.temperature = settings.AI_RERANK_TEMPERATURE

    def ai_rerank_recommendations(
        self,
        recommendations: List[Dict[str, Any]],
        cart_products: List[Dict[str, Any]],
        enrolled_products: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Submits candidate recommendations to Groq Llama-3 for AI adjustment scores and rationale.
        """
        # Build context
        context = {
            "cart_products": cart_products,
            "enrolled_products": enrolled_products,
            "recommendations": recommendations
        }

        # prompt template (retained identically to keep intelligence intact)
        prompt = f"""
You are an elite cybersecurity learning-path intelligence engine.

Your job is NOT to recommend generic courses.

Your job is to think like:
- a senior red team mentor
- a cloud offensive security architect
- an advanced cyber training advisor

You must analyze:

1. realistic offensive/defensive progression
2. specialization continuity
3. semantic topic overlap
4. attack-chain continuity
5. cloud attack-path progression
6. infrastructure adjacency
7. operational maturity
8. realistic cyber career progression
9. reduction of duplicate learning outcomes
10. advanced learner alignment

VERY IMPORTANT:

Prioritize:
- deep specialization continuity
- offensive operational progression
- realistic attack-chain evolution
- advanced cloud offensive paths
- infrastructure progression
- cross-domain offensive adjacency

Avoid:
- generic beginner recommendations
- popularity-only scoring
- weak domain-only matching
- repetitive learning outcomes
- shallow recommendations

IMPORTANT SCORING RULES:

0.0 - 0.5
Weak recommendation

0.6 - 1.0
Moderate recommendation

1.1 - 1.5
Strong recommendation

1.6 - 2.0
Exceptional specialization continuity

VERY IMPORTANT:

Your explanation MUST reference:
- attack paths
- offensive concepts
- operational progression
- cloud pivoting
- infrastructure adjacency
- semantic continuity
- realistic skill evolution

BAD EXAMPLE:
"High popularity score"

GOOD EXAMPLE:
"Extends multi-cloud offensive attack-path progression through IAM abuse, cloud pivoting, and cross-provider persistence techniques."

RETURN ONLY VALID JSON.

NO MARKDOWN.
NO EXTRA TEXT.
VERY IMPORTANT:

You MUST return scoring for EVERY recommendation.
Do NOT skip any recommendation.
Every recommendation must contain:
- title
- ai_adjustment_score
- reason

RETURN FORMAT:

{{
    "reranked_recommendations": [

        {{
            "title": "...",

            "ai_adjustment_score": 1.7,

            "reason": "..."
        }}
    ]
}}

DATA:
{json.dumps(context, indent=2)}
"""
        logger.info("Requesting Groq AI adjustments for recommendations...")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an elite cybersecurity recommendation intelligence engine."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature
            )

            content = response.choices[0].message.content
            logger.info("Successfully received Groq AI adjustment response.")
            
            # Clean and parse response via utility helper
            return clean_and_parse_json(content)

        except Exception as e:
            logger.error(f"Error calling Groq for AI reranking: {str(e)}")
            return {
                "reranked_recommendations": [],
                "error": str(e),
                "raw_response": getattr(locals().get('response'), 'choices', [None])[0].message.content if 'response' in locals() else ""
            }
