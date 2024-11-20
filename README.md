# EOB Processing and Query System

This project automates the extraction and querying of data from Explanation of Benefits (EOB) documents. It uses **OCR (Tesseract)** for extracting text from uploaded files and **GPT-4** to answer user queries in natural language. The system is built with **Flask**, **JavaScript**, and integrates a dynamic query system.

---

## Features

- **File Upload**: Upload multiple EOB PDF documents for processing.
- **OCR Processing**: Extract structured data like payment details, patient information, and service provider details using Tesseract OCR.
- **Dynamic Query System**: Ask natural language questions about the extracted data using GPT-4.
- **Real-time Status Updates**: View the status of document processing.
- **User-Friendly Interface**: A simple, clean UI for file uploads and querying.

---

## Tech Stack

- **Backend**: Flask, Tesseract OCR, OpenAI GPT-4
- **Frontend**: HTML, CSS, JavaScript
- **Storage**: Processed data is stored in a CSV file for querying.

---

## Installation

1. **Clone the Repository**  
   Clone the repository to your local machine:
   ```bash
   git clone https://github.com/your-repo/EOB-Processing-System.git
   cd EOB-Processing-System
2.  **Install Dependencies**  
    Install the required Python dependencies:
    ```bash
    pip install -r requirements.txt
3.  Install Tesseract OCR: Download and install Tesseract from Tesseract's official site.  
    Install Poppler: Install Poppler for PDF to image conversion:
    On Ubuntu: sudo apt install poppler-utils
    On macOS: brew install poppler
    On Windows: Download Poppler for Windows.
    Set Up OpenAI API
    Get your API key from OpenAI and add it to your environment:

    ```bash
    export OPENAI_API_KEY="your-api-key"

## Usage
1.  **Upload EOB Files**  
    Navigate to the "Upload Files" section in the web interface.
    Select one or more EOB PDF documents and click "Upload."
    Monitor the real-time status updates as the backend processes the documents.
2.  **Query the Data**
    Enter a query in the input box in the "Query" section, such as:
    1.  "What is the highest medical bill?"
    2.  "List all payments made after September 2024."
    Submit the query and view the response from GPT-4.
