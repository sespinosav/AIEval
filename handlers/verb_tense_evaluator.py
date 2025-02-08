from dataclasses import dataclass
from typing import Dict, Any, Optional
import logging
import json
from openai.types.chat import ChatCompletion
from base_handler import BaseLambdaHandler, ValidationError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


@dataclass
class TenseAnalysisRequest:
    """Request data for tense analysis."""

    verb_tense: str
    sentence: str


class TenseAnalysisHandler(BaseLambdaHandler[TenseAnalysisRequest, Dict[str, Any]]):
    """Handler for verb tense analysis requests."""

    def validate_request(self, body: Dict[str, Any]) -> TenseAnalysisRequest:
        """Validates tense analysis request."""
        if not isinstance(body.get("verb_tense"), str):
            raise ValidationError("'verb_tense' must be a string")
        if not isinstance(body.get("sentence"), str):
            raise ValidationError("'sentence' must be a string")
        if not body["verb_tense"].strip() or not body["sentence"].strip():
            raise ValidationError("'verb_tense' and 'sentence' cannot be empty")

        return TenseAnalysisRequest(
            verb_tense=body["verb_tense"].strip(), sentence=body["sentence"].strip()
        )

    def process_request(self, request: TenseAnalysisRequest) -> Dict[str, Any]:
        """Processes tense analysis request using OpenAI API."""
        try:
            response: ChatCompletion = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a tense evaluator. Respond only with valid JSON.",
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Evaluate whether the following sentence correctly uses the '{request.verb_tense}' tense: "
                            f"\"{request.sentence}\". Return a JSON with two fields: 'correct' (a boolean) and "
                            "'explanation' (a string explaining your decision)."
                        ),
                    },
                ],
                temperature=0.7,
            )

            answer_text = response.choices[0].message.content.strip()
            return json.loads(answer_text)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI response: {answer_text}")
            return {
                "correct": False,
                "explanation": f"Invalid response format from language model: {str(e)}",
            }


# Lambda handler function
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    handler = TenseAnalysisHandler()
    return handler.handle(event, context)
