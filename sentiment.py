# from langchain_openai import OpenAI  # Or use HuggingFace for free tier

# llm = OpenAI(temperature=0)  # Set your OpenAI API key in environment variables

# def analyze_sentiment(text):
#     response = llm.invoke(f"Is this text negative or urgent? Reply ONLY with 'negative', 'urgent', or 'neutral': {text}")
#     return response.strip().lower()
# from transformers import pipeline


# # Define the candidate labels you want to classify
# candidate_labels = ["negative", "urgent", "neutral"]

# # Create a zero-shot classification pipeline using facebook/bart-large-mnli
# classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

# def analyze_sentiment(text: str) -> str:
#     result = classifier(text, candidate_labels=candidate_labels)
#     #print(result)  # for debugging purposes: this prints the full result, including scores
#     # The best candidate (with the highest score) is often in result["labels"][0]
#     return result["labels"][0]

import requests
from dotenv import load_dotenv
import os

# Define your API endpoint and your API token from Hugging Face.
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
#load_dotenv(override=True)  # Load environment variables

#API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
API_TOKEN ="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"  # Replace with your actual token.
AZURE_OPENAI_API_KEY="ACYhswv9bdG9HLSwegzWBaepqA7mKYn3mQtHqU3hiTJzzbRO9qyOJQQJ99BEACfhMk5XJ3w3AAABACOGp1TG"
#print(API_TOKEN)

headers = {"Authorization": f"Bearer {API_TOKEN}"}

# Define the candidate labels for classification.
candidate_labels = ["Work", "Urgent", "Invoice", "Contract", "Promo"]

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

def analyze_sentiment(text: str) -> str:
    """
    Uses Hugging Face's hosted Inference API to classify the input text without loading
    the model locally.
    """
    payload = {
        "inputs": text,
        "parameters": {"candidate_labels": candidate_labels}
    }
    result = query(payload)
    #print(result)  # For debugging; displays the full JSON output.
    return result["labels"][0]

    