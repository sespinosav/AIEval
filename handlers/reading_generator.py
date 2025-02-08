import json
import boto3
import random
from openai import OpenAI

# Create a global SSM client and cache for the API key
ssm_client = boto3.client("ssm")
OPENAI_API_KEY = None

# Constant: List of 20 random topics
TOPICS = [
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
        # Retrieve OpenAI API key
        openai_api_key = get_openai_api_key()
        client = OpenAI(api_key=openai_api_key)

        # Select a random topic from the list
        selected_topic = random.choice(TOPICS)

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
                        f"Write a short-length article (two paragraphs) about the topic: **{selected_topic}**. "
                        "The article should be informative and engaging, suitable for English learning purposes. "
                        "Format the response using structured text with clear sections, headings, and bold or italicized keywords. "
                        "Use Markdown or another structured text format to enhance readability."
                    ),
                },
            ],
            temperature=0.9,
            max_tokens=320,
        )

        article = response.choices[0].message.content.strip()

        return {
            "statusCode": 200,
            "headers": cors_headers,
            "body": json.dumps({"topic": selected_topic, "article": article}),
        }
    except Exception as e:
        print(f"Error: {str(e)}")  # This will log to CloudWatch
        return {
            "statusCode": 500,
            "headers": cors_headers,
            "body": json.dumps({"error": str(e)}),
        }
