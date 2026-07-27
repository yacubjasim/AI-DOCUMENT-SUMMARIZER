from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
from google import genai
from PyPDF2 import PdfReader

# Load API key
load_dotenv()

client = genai.Client(api_key=os.getenv("AQ.Ab8RN6KGQmlpnazFIY3jHJIS7tLx6yGP-R1hGQK0gI1ZiJ-Piw"))

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/summarize", methods=["POST"])
def summarize():

    if "pdf" not in request.files:
        return "No PDF uploaded."

    file = request.files["pdf"]

    if file.filename == "":
        return "No file selected."

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    # Read PDF
    reader = PdfReader(filepath)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    if text.strip() == "":
        return "Could not read any text from the PDF."

    prompt = f"""
You are an expert document summarizer.

Read the following document and summarize it in simple English.

Return the output in exactly this format:

# 📄 Document Title

## 📌 Overview
(2-3 sentences)

## ⭐ Key Points
- Point 1
- Point 2
- Point 3
- Point 4
- Point 5

## 📝 Important Details
- Detail 1
- Detail 2
- Detail 3

## ✅ Conclusion
(2-3 sentences)

Document:
{text}
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    summary = response.text

    return render_template("index.html", summary=summary)


if __name__ == "__main__":
    app.run(debug=True)
