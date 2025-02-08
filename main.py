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
            Name="/AIEval/OPENAI_API_KEY", WithDecryption=True
        )
        OPENAI_API_KEY = response["Parameter"]["Value"]
    return OPENAI_API_KEY


def lambda_handler(event, context):
    # Define CORS headers
    cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }

    # Handle preflight OPTIONS request
    if event.get("httpMethod", "") == "OPTIONS":
        return {"statusCode": 200, "headers": cors_headers, "body": ""}

    try:
        # Parse the input JSON from the request body
        body = json.loads(event.get("body", "{}"))
        word = body.get("word")
        sentence = body.get("sentence")

        if not word or not sentence:
            return {
                "statusCode": 400,
                "headers": cors_headers,
                "body": json.dumps(
                    {"error": "Both 'word' and 'sentence' parameters are required."}
                ),
            }

        # Retrieve the OpenAI API key from SSM
        openai_api_key = get_openai_api_key()

        # Initialize the OpenAI client
        client = OpenAI(api_key=openai_api_key)

        # Construct the prompt
        prompt = (
            f"Evaluate the usage of the word '{word}' in the following sentence: \"{sentence}\". "
            "Return a JSON with two fields: 'correct' (a boolean) and 'explanation' (a string explaining your decision)."
        )

        # Call the OpenAI API using gpt-3.5-turbo
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a grammar and usage evaluator. Respond only with valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )

        answer_text = response.choices[0].message.content.strip()
        try:
            answer_json = json.loads(answer_text)
        except json.JSONDecodeError as e:
            # If we can't parse the JSON, create a structured response
            answer_json = {
                "correct": False,
                "explanation": f"Could not parse OpenAI response: {str(e)}. Response was: {answer_text}",
            }

        return {
            "statusCode": 200,
            "headers": cors_headers,
            "body": json.dumps(answer_json),
        }
    except Exception as e:
        print(f"Error: {str(e)}")  # This will log to CloudWatch
        return {
            "statusCode": 500,
            "headers": cors_headers,
            "body": json.dumps({"error": str(e)}),
        }
