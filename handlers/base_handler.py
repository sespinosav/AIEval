import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, TypeVar, Generic
from dataclasses import dataclass
import boto3
from botocore.exceptions import ClientError
from openai import OpenAI


# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Type variable for request/response body types
RequestT = TypeVar("RequestT")
ResponseT = TypeVar("ResponseT")

MODEL = "gpt-4o-mini"


class ConfigError(Exception):
    """Custom exception for configuration-related errors."""

    pass


class ValidationError(Exception):
    """Custom exception for input validation errors."""

    pass


@dataclass
class APIGatewayEvent:
    """Structured representation of API Gateway event."""

    http_method: str
    body: Optional[str]
    headers: Dict[str, str]

    @classmethod
    def from_dict(cls, event: Dict[str, Any]) -> "APIGatewayEvent":
        return cls(
            http_method=event.get("httpMethod", ""),
            body=event.get("body"),
            headers=event.get("headers", {}),
        )


class APIGatewayResponse:
    """Helper class to create consistent API Gateway responses."""

    CORS_HEADERS = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }

    @staticmethod
    def success(body: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "statusCode": 200,
            "headers": APIGatewayResponse.CORS_HEADERS,
            "body": json.dumps(body),
        }

    @staticmethod
    def error(status_code: int, message: str) -> Dict[str, Any]:
        return {
            "statusCode": status_code,
            "headers": APIGatewayResponse.CORS_HEADERS,
            "body": json.dumps({"error": message}),
        }

    @staticmethod
    def options() -> Dict[str, Any]:
        return {
            "statusCode": 200,
            "headers": APIGatewayResponse.CORS_HEADERS,
            "body": "",
        }


class SSMParameterStore:
    """Manages AWS Systems Manager Parameter Store interactions."""

    def __init__(self):
        self.client = boto3.client("ssm")
        self._parameters: Dict[str, str] = {}

    def get_parameter(self, name: str) -> str:
        """
        Retrieves a parameter from SSM Parameter Store with caching.

        Args:
            name: The parameter name

        Returns:
            The parameter value

        Raises:
            ConfigError: If the parameter cannot be retrieved
        """
        if name not in self._parameters:
            try:
                response = self.client.get_parameter(Name=name, WithDecryption=True)
                self._parameters[name] = response["Parameter"]["Value"]
            except ClientError as e:
                logger.error(f"Failed to retrieve parameter {name} from SSM: {str(e)}")
                raise ConfigError(f"Failed to retrieve parameter: {name}") from e

        return self._parameters[name]


class BaseLambdaHandler(ABC, Generic[RequestT, ResponseT]):
    """
    Base class for Lambda handlers with common functionality.

    Type Parameters:
        RequestT: The type of the request body
        ResponseT: The type of the response body
    """

    def __init__(self):
        self.ssm = SSMParameterStore()
        self._openai_client: Optional[OpenAI] = None
        self._model: str = MODEL

    @property
    def openai_client(self) -> OpenAI:
        """Lazy initialization of OpenAI client."""
        if self._openai_client is None:
            api_key = self.ssm.get_parameter("/EnglishLearning/OPENAI_API_KEY")
            self._openai_client = OpenAI(api_key=api_key)
        return self._openai_client

    @property
    def model(self) -> OpenAI:
        return self._model

    @abstractmethod
    def validate_request(self, body: Dict[str, Any]) -> RequestT:
        """
        Validates and converts the request body to the request type.

        Args:
            body: The raw request body dictionary

        Returns:
            The validated request object

        Raises:
            ValidationError: If validation fails
        """
        pass

    @abstractmethod
    def process_request(self, request: RequestT) -> ResponseT:
        """
        Processes the validated request.

        Args:
            request: The validated request object

        Returns:
            The response object
        """
        pass

    def handle(self, event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """
        Main handler method for Lambda function.

        Args:
            event: The Lambda event object
            context: The Lambda context object

        Returns:
            API Gateway response dictionary
        """
        api_event = APIGatewayEvent.from_dict(event)

        # Handle OPTIONS request
        if api_event.http_method == "OPTIONS":
            return APIGatewayResponse.options()

        try:
            # Parse and validate input
            try:
                body = json.loads(api_event.body or "{}")
                request = self.validate_request(body)
            except (json.JSONDecodeError, ValidationError) as e:
                return APIGatewayResponse.error(400, str(e))

            # Process the request
            response = self.process_request(request)

            return APIGatewayResponse.success(response)

        except ConfigError as e:
            return APIGatewayResponse.error(500, str(e))
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return APIGatewayResponse.error(
                500, "An unexpected error occurred. Please try again later."
            )
