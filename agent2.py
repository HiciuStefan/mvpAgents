from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI


load_dotenv()

def generate_business_insights(template: str) -> str:
    llm = AzureChatOpenAI(
        temperature=0,
        api_version="2025-01-01-preview",
        azure_deployment="gpt-35-turbo-vasi"
    )

    prompt = f""""{template}"Reply:"""
    
    try:
        response = llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        print(f"Error generating the answer: {e}")
        return "Thank you for sharing your thoughts!"

if __name__=="__main__":
    print("Running...")
    print(generate_business_insights(template_path = "client_prompt_template.txt"))
