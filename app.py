from flask import Flask, render_template, request
from pathlib import Path

app = Flask(__name__)

def load_template(template_path):
    with open(template_path, 'r', encoding='utf-8') as file:
        return file.read()

def fill_template(template, context):
    for key, value in context.items():
        template = template.replace(f"{{{{{key}}}}}", value)
    return template


if __name__ == "__main__":
    app.run(debug=True)
