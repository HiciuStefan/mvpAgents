# openai_integration.py
import openai
import os

# Set up for Azure OpenAI
openai.api_type = "azure"
openai.api_base = "https://openai-vasi.openai.azure.com/openai/deployments/gpt-35-turbo-vasi/chat/completions?api-version=2025-01-01-preview" #os.environ.get("AZURE_OPENAI_API_BASE")  # e.g., "https://your-resource-name.openai.azure.com/"
openai.api_version = "2023-03-15-preview"  # or the appropriate API version
openai.api_key = "ACYhswv9bdG9HLSwegzWBaepqA7mKYn3mQtHqU3hiTJzzbRO9qyOJQQJ99BEACfhMk5XJ3w3AAABACOGp1TG"#os.environ.get("AZURE_OPENAI_API_KEY")

def generate_marketing_strategy(input_text):
    prompt = (
        "Based on the following marketing input details, generate a detailed marketing campaign strategy. "
        "Include suggestions for campaign duration and post ideas (for social media, blogs, etc.):\n\n"
        f"{input_text}\n\nStrategy:"
    )
    try:
        response = openai.Completion.create(
            engine="your-deployment-name",  # In Azure, you refer to your deployed model by its name
            prompt=prompt,
            max_tokens=500,
            temperature=0.7
        )
    except Exception as e:
        return f"Error calling Azure OpenAI API: {e}"
    
    strategy = response.choices[0].text.strip()
    return strategy
