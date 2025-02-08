import re
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

        # Construct the evaluation prompt using regex format
        prompt = (
            f"Evaluate the following summary of an article based on two categories:\n\n"
            f"Original Article:\n{original_article}\n\n"
            f"User's Summary:\n{user_summary}\n\n"
            f"Provide an evaluation with this structure:\n"
            f"Grammar & Spelling: (0-100), Feedback: <your feedback>\n"
            f"Coherence: (0-100), Feedback: <your feedback>"
        )

        response = client.chat.completions.create(
            model="gpt-4o-mini",
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

        # Extract scores and feedback using regex
        grammar_match = re.search(
            r"Grammar & Spelling: (\d+), Feedback: (.+)", evaluation_text
        )
        coherence_match = re.search(
            r"Coherence: (\d+), Feedback: (.+)", evaluation_text
        )

        if not grammar_match or not coherence_match:
            return {
                "statusCode": 500,
                "headers": cors_headers,
                "body": json.dumps({"error": "Could not parse evaluation results."}),
            }

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

        return {
            "statusCode": 200,
            "headers": cors_headers,
            "body": json.dumps(evaluation_result),
        }
    except Exception as e:
        print(f"Error: {str(e)}")  # Log to CloudWatch
        return {
            "statusCode": 500,
            "headers": cors_headers,
            "body": json.dumps({"error": str(e)}),
        }
