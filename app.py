from flask import Flask, request, jsonify, render_template
from pdf2image import convert_from_path
from pytesseract import pytesseract
import pandas as pd
import openai
import os
import cv2
import numpy as np
import json
import logging
import re
from PIL import Image

# Flask initialization
app = Flask(__name__)
UPLOAD_FOLDER = './uploads'
PROCESSED_FOLDER = './processed'
OUTPUT_FILE = './output/data.csv'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Explicit paths for Poppler and Tesseract
POPPLER_PATH = os.path.join(os.getcwd(), "poppler-24.08.0", "Library", "bin") 
TESSERACT_PATH = os.path.join(os.getcwd(), "tesseract-ocr-5.5", "tesseract.exe") 
pytesseract.tesseract_cmd = TESSERACT_PATH

# OpenAI API key (set as environment variable or directly here - not recommended for production)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('./output', exist_ok=True)

# Logging setup
logging.basicConfig(level=logging.DEBUG)

# Status tracking
process_status = []


def update_status(message):
    """Update processing status."""
    process_status.append(message)


def pdf_to_images(file_path):
    """Convert a PDF to images."""
    try:
        images = convert_from_path(file_path, dpi=200, poppler_path=POPPLER_PATH)
        return images
    except Exception as e:
        logging.error(f"Error converting PDF to images: {e}")
        return []


def preprocess_image(image):
    """Preprocess image for better OCR accuracy."""
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    return thresh


def run_ocr_on_image(image):
    """Run OCR using Tesseract on an image."""
    try:
        processed_image = preprocess_image(image)
        text = pytesseract.image_to_string(Image.fromarray(processed_image), lang='eng')
        return text
    except Exception as e:
        logging.error(f"Error during OCR: {e}")
        return ""


def extract_data(text):
    """Extract relevant fields from text using regex."""
    return {
        "Payment to": re.search(r'Payment to:\s*(.*)', text).group(1) if re.search(r'Payment to:\s*(.*)', text) else None,
        "Payment Date": re.search(r'Payment date:\s*(.*)', text).group(1) if re.search(r'Payment date:\s*(.*)', text) else None,
        "Payment Number": re.search(r'Payment number:\s*(.*)', text).group(1) if re.search(r'Payment number:\s*(.*)', text) else None,
        "Total Amount Charged": re.search(r'Total Amount Charged:\s*\$([\d,]+\.\d{2})', text).group(1) if re.search(r'Total Amount Charged:\s*\$([\d,]+\.\d{2})', text) else None,
        "Total Contracted Amount": re.search(r'Total Contracted Amount:\s*\$([\d,]+\.\d{2})', text).group(1) if re.search(r'Total Contracted Amount:\s*\$([\d,]+\.\d{2})', text) else None,
        "Amount Eligible for Coverage": re.search(r'Amount Eligible for Coverage:\s*\$([\d,]+\.\d{2})', text).group(1) if re.search(r'Amount Eligible for Coverage:\s*\$([\d,]+\.\d{2})', text) else None,
        "Patient Name": re.search(r'Patient Name:\s*(.*)', text).group(1) if re.search(r'Patient Name:\s*(.*)', text) else None,
        "Patient ID": re.search(r'Patient ID:\s*(.*)', text).group(1) if re.search(r'Patient ID:\s*(.*)', text) else None,
        "Service Provider ID": re.search(r'Service Provider ID:\s*(.*)', text).group(1) if re.search(r'Service Provider ID:\s*(.*)', text) else None,
    }


def calculate_field_accuracy(structured_data):
    """Calculate accuracy for each field."""
    field_accuracies = {field: (1 if value else 0) for field, value in structured_data.items()}
    return field_accuracies


def reprocess_with_gpt4(text):
    """Reprocess text using GPT-4."""
    prompt = f"""
    Extract the following fields from this text and return them as a JSON object:
    {{
        "Payment to": <value>,
        "Payment Date": <value>,
        "Payment Number": <value>,
        "Total Amount Charged": <value>,
        "Total Contracted Amount": <value>,
        "Amount Eligible for Coverage": <value>,
        "Patient Name": <value>,
        "Patient ID": <value>,
        "Service Provider ID": <value>
    }}

    If any field is missing or not found, set its value to null.

    Text:
    {text}
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        content = response['choices'][0]['message']['content']
        return json.loads(content)
    except Exception as e:
        logging.error(f"Error during GPT-4 processing: {e}")
        return {}


def consolidate_data(all_data):
    """Consolidate data from multiple pages into a single JSON object."""
    consolidated = {
        "Payment to": None,
        "Payment Date": None,
        "Payment Number": None,
        "Total Amount Charged": None,
        "Total Contracted Amount": None,
        "Amount Eligible for Coverage": None,
        "Patient Name": None,
        "Patient ID": None,
        "Service Provider ID": None,
    }

    for page_data in all_data:
        for key, value in page_data.items():
            if value and not consolidated[key]:
                consolidated[key] = value

    return consolidated


def save_to_csv(data):
    """Save extracted data to a CSV file."""
    df = pd.DataFrame([data])  # Create a DataFrame for the new data
    try:
        if not os.path.exists(OUTPUT_FILE) or os.stat(OUTPUT_FILE).st_size == 0:
            # If file doesn't exist or is empty, write headers
            df.to_csv(OUTPUT_FILE, index=False)
        else:
            # Append to existing file without writing headers again
            existing_df = pd.read_csv(OUTPUT_FILE)
            combined_df = pd.concat([existing_df, df])
            combined_df.to_csv(OUTPUT_FILE, index=False)
    except Exception as e:
        logging.error(f"Error saving to CSV: {e}")



@app.route('/')
def home():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    files = request.files.getlist("files")
    results = []
    global process_status
    process_status = []

    for file in files:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        update_status(f"Processing file: {file.filename}")
        images = pdf_to_images(file_path)

        all_page_data = []
        for idx, image in enumerate(images):
            text = run_ocr_on_image(image)
            page_data = extract_data(text)

            # Calculate field-wise accuracy
            field_accuracies = calculate_field_accuracy(page_data)
            update_status(f"Page {idx + 1} field accuracies: {field_accuracies}")

            # Use GPT-4 for any missing fields
            if any(value == 0 for value in field_accuracies.values()):
                update_status(f"Using GPT-4 for missing fields on page {idx + 1}...")
                page_data = reprocess_with_gpt4(text)

            all_page_data.append(page_data)

        consolidated_data = consolidate_data(all_page_data)
        save_to_csv(consolidated_data)
        results.append(consolidated_data)

    return jsonify(results)


@app.route('/status', methods=['GET'])
def status():
    return jsonify(process_status)

@app.route('/query', methods=['POST'])
def query_data():
    """Handle queries using GPT-4 based on the consolidated EOB data."""
    try:
        # Check if the consolidated CSV exists and is not empty
        if not os.path.exists(OUTPUT_FILE) or os.stat(OUTPUT_FILE).st_size == 0:
            return jsonify({"error": "No data available to query. Upload and process a file first."}), 400

        # Load data from the CSV file
        df = pd.read_csv(OUTPUT_FILE)

        # Convert the data into a JSON-like string for GPT-4
        data_json = df.to_dict(orient="records")

        # Extract the query from the request
        user_query = request.json.get("query", "").strip()
        if not user_query:
            return jsonify({"error": "No query provided."}), 400

        # Build the GPT-4 prompt
        prompt = f"""
        You are a data analyst. Here is the structured data extracted from Explanation of Benefits (EOB) documents:
        
        {data_json}

        Answer the following query based on this data:
        {user_query}
        """

        # Send the prompt to GPT-4
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )

        # Log the raw GPT-4 response for debugging
        logging.debug(f"GPT-4 Full Response: {response}")

        # Extract the answer
        answer = response['choices'][0]['message']['content'].strip()
        logging.debug(f"GPT-4 Extracted Answer: {answer}")

        # Return the extracted answer
        return jsonify({"query": user_query, "answer": answer})

    except Exception as e:
        logging.error(f"Error processing query: {e}")
        return jsonify({"error": "An error occurred while processing the query."}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
