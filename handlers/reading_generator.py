from dataclasses import dataclass
from typing import Dict, Any, Optional, List
import random
from openai.types.chat import ChatCompletion
from base_handler import BaseLambdaHandler, ValidationError


@dataclass
class ArticleGeneratorRequest:
    """Request data for article generation."""

    # Empty for now as we don't take any input parameters
    pass


class ArticleGeneratorHandler(
    BaseLambdaHandler[ArticleGeneratorRequest, Dict[str, Any]]
):
    """Handler for generating random topic articles."""

    # List of available topics
    TOPICS: List[str] = [
        "The impact of artificial intelligence on daily life",
        "How climate change affects our planet",
        "The importance of learning a second language",
        "The benefits of regular exercise",
        "How to improve your time management skills",
        "The history and significance of space exploration",
        "The effects of social media on mental health",
        "Why sleep is essential for a healthy life",
        "The role of technology in education",
        "The power of positive thinking",
        "How music influences our emotions",
        "The importance of recycling and waste management",
        "The future of electric vehicles",
        "How to build healthy eating habits",
        "The benefits of reading books regularly",
        "The science behind human emotions",
        "The cultural impact of globalization",
        "How mindfulness can improve your daily life",
        "The evolution of the internet and its influence",
        "The significance of renewable energy sources",
    ]

    def validate_request(self, body: Dict[str, Any]) -> ArticleGeneratorRequest:
        """
        Validates the request. For this handler, we don't need any input parameters
        as we generate random topics.
        """
        return ArticleGeneratorRequest()

    def process_request(self, request: ArticleGeneratorRequest) -> Dict[str, Any]:
        """Generates an article about a random topic using OpenAI API."""
        selected_topic = random.choice(self.TOPICS)

        try:
            response: ChatCompletion = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a creative and engaging English article generator, specializing in making learning fun and memorable. "
                            "Craft compelling, well-structured content that captivates the reader, using vivid examples, analogies, and storytelling techniques. "
                            "Your writing should feel dynamic and immersive, sparking curiosity and making complex topics easy to grasp."
                        ),
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Write a short-length article (two paragraphs) about the topic: **{selected_topic}**. "
                            "The article should be informative and engaging, suitable for English learning purposes. "
                            "Format the response using structured text with clear sections, headings, and bold or italicized keywords. "
                            "Use Markdown or another structured text format to enhance readability."
                        ),
                    },
                ],
                temperature=0.9,
                max_tokens=300,
            )

            article = response.choices[0].message.content.strip()

            return {"topic": selected_topic, "article": article}

        except Exception as e:
            logger.error(f"Failed to generate article: {str(e)}")
            raise


# Lambda handler function
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    handler = ArticleGeneratorHandler()
    return handler.handle(event, context)
