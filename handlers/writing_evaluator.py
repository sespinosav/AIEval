import json
import boto3
from openai import OpenAI

# Create a global SSM client and cache for the API key
ssm_client = boto3.client("ssm")
OPENAI_API_KEY = None


def get_openai_api_key():
    global OPENAI_API_KEY
    if OPENAI_API_KEY is None:
        response = ssm_client.get_parameter(
            Name="/EnglishLearning/OPENAI_API_KEY", WithDecryption=True
        )
        OPENAI_API_KEY = response["Parameter"]["Value"]
    return OPENAI_API_KEY


def lambda_handler(event, context):
    cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }

    if event.get("httpMethod", "") == "OPTIONS":
        return {"statusCode": 200, "headers": cors_headers, "body": ""}

    try:
        # Parse the input JSON
        body = json.loads(event.get("body", "{}"))
        original_article = body.get("article")
        user_summary = body.get("summary")

        if not original_article or not user_summary:
            return {
                "statusCode": 400,
                "headers": cors_headers,
                "body": json.dumps(
                    {"error": "Both 'article' and 'summary' parameters are required."}
                ),
            }

        # Retrieve the OpenAI API key
        openai_api_key = get_openai_api_key()
        client = OpenAI(api_key=openai_api_key)

        # Construct the evaluation prompt
        prompt = (
            f"Evaluate the following summary of an article based on three categories:\n\n"
            f"Original Article:\n{original_article}\n\n"
            f"User's Summary:\n{user_summary}\n\n"
            f"Provide an evaluation in JSON format with the following structure:\n"
            "{\n"
            "  'grammar_spelling': {'score': 0-100, 'feedback': 'detailed feedback'},\n"
            "  'understanding': {'score': 0-100, 'feedback': 'detailed feedback'},\n"
            "  'coherence': {'score': 0-100, 'feedback': 'detailed feedback'}\n"
            "}"
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an English writing evaluator. Provide detailed, "
                    "constructive feedback in JSON format.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )

        evaluation = json.loads(response.choices[0].message.content.strip())

        return {
            "statusCode": 200,
            "headers": cors_headers,
            "body": json.dumps(evaluation),
        }
    except Exception as e:
        print(f"Error: {str(e)}")  # This will log to CloudWatch
        return {
            "statusCode": 500,
            "headers": cors_headers,
            "body": json.dumps({"error": str(e)}),
        }
