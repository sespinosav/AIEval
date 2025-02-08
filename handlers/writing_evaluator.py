import re
import json
import logging
from dataclasses import dataclass
from typing import Dict, Any, Optional

from base_handler import BaseLambdaHandler, ValidationError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


@dataclass
class SummaryEvaluationRequest:
    """
    Request data for article summary evaluation.

    Attributes:
        article (str): The original article text.
        summary (str): The user-provided summary.
    """

    article: str
    summary: str


class SummaryEvaluationHandler(
    BaseLambdaHandler[SummaryEvaluationRequest, Dict[str, Any]]
):
    """
    Handler for evaluating a user's summary against an original article using OpenAI.
    """

    def validate_request(self, body: Dict[str, Any]) -> SummaryEvaluationRequest:
        """
        Validates the incoming request body.

        Args:
            body: The request body dictionary.

        Returns:
            A SummaryEvaluationRequest object with the validated data.

        Raises:
            ValidationError: If any of the required fields are missing or empty.
        """
        if not isinstance(body.get("article"), str):
            raise ValidationError("'article' must be a string")
        if not isinstance(body.get("summary"), str):
            raise ValidationError("'summary' must be a string")

        article = body.get("article", "").strip()
        summary = body.get("summary", "").strip()

        if not article:
            raise ValidationError("'article' cannot be empty")
        if not summary:
            raise ValidationError("'summary' cannot be empty")

        return SummaryEvaluationRequest(article=article, summary=summary)

    def process_request(self, request: SummaryEvaluationRequest) -> Dict[str, Any]:
        """
        Processes the summary evaluation request by constructing the prompt, calling the OpenAI API,
        and parsing the response.

        Args:
            request: The validated SummaryEvaluationRequest object.

        Returns:
            A dictionary containing the evaluation results.

        Raises:
            Exception: If the response from OpenAI cannot be parsed.
        """
        try:
            prompt = (
                f"Evaluate the following summary of an article based on two categories:\n\n"
                f"Original Article:\n{request.article}\n\n"
                f"User's Summary:\n{request.summary}\n\n"
                "Provide an evaluation with this structure:\n"
                "Grammar & Spelling: (0-100), Feedback: <your feedback>\n"
                "Coherence: (0-100), Feedback: <your feedback>"
            )

            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI writing evaluator. Respond strictly following the required format.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
            )

            evaluation_text = response.choices[0].message.content.strip()

            # Extract evaluation details using regex
            grammar_match = re.search(
                r"Grammar & Spelling: (\d+), Feedback: (.+)", evaluation_text
            )
            coherence_match = re.search(
                r"Coherence: (\d+), Feedback: (.+)", evaluation_text
            )

            if not grammar_match or not coherence_match:
                logger.error(f"Could not parse evaluation results: {evaluation_text}")
                raise Exception("Could not parse evaluation results.")

            evaluation_result = {
                "grammar_spelling": {
                    "score": int(grammar_match.group(1)),
                    "feedback": grammar_match.group(2).strip(),
                },
                "coherence": {
                    "score": int(coherence_match.group(1)),
                    "feedback": coherence_match.group(2).strip(),
                },
            }
            return evaluation_result

        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            raise


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda entry point.

    Instantiates the SummaryEvaluationHandler and delegates the event handling.
    """
    handler = SummaryEvaluationHandler()
    return handler.handle(event, context)
