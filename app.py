from flask import Flask, render_template, request
from pathlib import Path
from agent2 import generate_business_insights

app = Flask(__name__)

def load_template(template_path):
    with open(template_path, 'r', encoding='utf-8') as file:
        return file.read()

def fill_template(template, context):
    for key, value in context.items():
        template = template.replace(f"{{{{{key}}}}}", value)
    return template

@app.route('/', methods=['GET', 'POST'])
def index():
    filled_prompt = ""
    if request.method == 'POST':
        # Collect user inputs from the form
        context_data = {
            "recent_emails_summary": request.form.get("recent_emails_summary", ""),
            "tweet_summary": request.form.get("tweet_summary", ""),
            "financial_summary": request.form.get("financial_summary", ""),
            "contract_summary": request.form.get("contract_summary", ""),
            "specific_info": request.form.get("specific_info", "")
        }

        # Load and fill the prompt template
        if request.form.get("specific_info", "")=="":
            template = load_template("client_prompt_template.txt")
        else:
            template = load_template("user_prompt_template.txt")

        filled_prompt = fill_template(template, context_data)
        
    response = generate_business_insights(filled_prompt)

    return render_template("index.html", result=response)

if __name__ == "__main__":
    app.run(debug=True)
