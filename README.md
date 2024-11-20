EOB Processing and Query System
This project automates the extraction and querying of data from Explanation of Benefits (EOB) documents. It uses OCR (Tesseract) for extracting text from uploaded files and GPT-4 to answer user queries in natural language. The system is built with Flask, JavaScript, and integrates a dynamic query system.

Features
File Upload: Upload multiple EOB PDF documents for processing.
OCR Processing: Extract structured data like payment details, patient information, and service provider details using Tesseract OCR.
Dynamic Query System: Ask natural language questions about the extracted data using GPT-4.
Real-time Status Updates: View the status of document processing.
User-Friendly Interface: A simple, clean UI for file uploads and querying.
Tech Stack
Backend: Flask, Tesseract OCR, OpenAI GPT-4
Frontend: HTML, CSS, JavaScript
Storage: Processed data is stored in a CSV file for querying.
Installation
Clone the Repository

bash
Copy code
git clone https://github.com/your-repo/EOB-Processing-System.git
cd EOB-Processing-System
Install Dependencies

Python dependencies:
bash
Copy code
pip install -r requirements.txt
Install Tesseract OCR and add it to your system PATH.
Install Poppler for PDF to image conversion.
Set Up OpenAI API

Get your API key from OpenAI.
Add it to your environment:
bash
Copy code
export OPENAI_API_KEY="your-api-key"
Run the Application

bash
Copy code
python app.py
The app will run on http://127.0.0.1:5000.

Usage
Upload EOB Files

Go to the "Upload Files" section, select one or more EOB PDFs, and click "Upload."
Monitor the real-time status updates as the files are processed.
Query the Data

Enter any natural language query in the "Query" box, such as:
"What is the highest medical bill?"
"List all payments made after September 2024."
The system will return an answer based on the extracted data.
File Structure
app.py: Backend logic for file upload, OCR processing, and GPT-4 query handling.
static/js/scripts.js: Handles frontend interactivity for file uploads and queries.
static/css/styles.css: Styles for the user interface.
templates/index.html: Frontend HTML for the web app.
output/consolidated_eob.csv: Stores extracted data for querying.
Requirements
Python 3.8+
Tesseract OCR
Poppler for PDF processing
OpenAI GPT-4 API key
Example Queries
"What is the highest medical bill?"
"List all patients whose medical bill exceeded $500."
"How many payments were made to CHOICE DENTAL?"
