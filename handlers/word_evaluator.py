from dataclasses import dataclass
from typing import Dict, Any, Optional
import json
import logging
from openai.types.chat import ChatCompletion
from base_handler import BaseLambdaHandler, ValidationError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


@dataclass
class WordUsageRequest:
    """Request data for word usage evaluation."""

    word: str
    sentence: str


class WordUsageHandler(BaseLambdaHandler[WordUsageRequest, Dict[str, Any]]):
    """Handler for evaluating word usage in sentences."""

    def validate_request(self, body: Dict[str, Any]) -> WordUsageRequest:
        """
        Validates word usage evaluation request.

        Args:
            body: The request body dictionary

        Returns:
            WordUsageRequest object

        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(body.get("word"), str):
            raise ValidationError("'word' must be a string")
        if not isinstance(body.get("sentence"), str):
            raise ValidationError("'sentence' must be a string")

        word = body["word"].strip()
        sentence = body["sentence"].strip()

        if not word:
            raise ValidationError("'word' cannot be empty")
        if not sentence:
            raise ValidationError("'sentence' cannot be empty")

        return WordUsageRequest(word=word, sentence=sentence)

    def process_request(self, request: WordUsageRequest) -> Dict[str, Any]:
        """
        Processes word usage evaluation request using OpenAI API.

        Args:
            request: The validated request object

        Returns:
            Dictionary containing evaluation results
        """
        try:
            response: ChatCompletion = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a grammar and usage evaluator. Respond only with valid JSON.",
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Evaluate the usage of the word '{request.word}' in the following sentence: "
                            f"\"{request.sentence}\". Return a JSON with two fields: 'correct' (a boolean) "
                            "and 'explanation' (a string explaining your decision)."
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
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            raise


# Lambda handler function
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    handler = WordUsageHandler()
    return handler.handle(event, context)
