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
        "Access-Control-Allow-Methods": "GET,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }

    if event.get("httpMethod", "") == "OPTIONS":
        return {"statusCode": 200, "headers": cors_headers, "body": ""}

    try:
        # Retrieve the OpenAI API key
        openai_api_key = get_openai_api_key()
        client = OpenAI(api_key=openai_api_key)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
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
                        "Write a short-length article (two paragraphs) about a general topic in the world. "
                        "The article should be informative and engaging, suitable for English learning purposes. "
                        "Format the response using structured text with clear sections, headings, and bold or italicized keywords. "
                        "Use Markdown or another structured text format to enhance readability."
                    ),
                },
            ],
            temperature=0.9,
            max_tokens=400,  # Aproximadamente 300 palabras
        )

        article = response.choices[0].message.content.strip()

        return {
            "statusCode": 200,
            "headers": cors_headers,
            "body": json.dumps({"article": article}),
        }
    except Exception as e:
        print(f"Error: {str(e)}")  # This will log to CloudWatch
        return {
            "statusCode": 500,
            "headers": cors_headers,
            "body": json.dumps({"error": str(e)}),
        }
