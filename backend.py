# @title Libraries and Packages Imports
!apt-get install -y poppler-utils
!pip install --upgrade deepdoctection
!pip install tensorflow
!pip install torch
!apt-get install -y tesseract-ocr
!pip install pdfplumber
!pip install pdf2image
!pip install flask flask-cors

# Import libraries
import deepdoctection as dd
from pdf2image import convert_from_path
from pathlib import Path
from matplotlib import pyplot as plt
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration for file uploads
UPLOAD_FOLDER = 'uploads'  # Directory to save uploaded files
ALLOWED_EXTENSIONS = {'pdf', 'docx'}  # Allowed file extensions
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Example GET endpoint
@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify(message='Hello from the backend!')

# Example POST endpoint
@app.route('/api/data', methods=['POST'])
def receive_data():
    data = request.json
    name = data.get('name', 'Unknown')
    return jsonify(message=f'Hello, {name}!')

# Endpoint to handle file uploads from the front end
@app.route('/api/upload', methods=['POST'])
def upload_file():
    # Check if a file is part of the request
    if 'file' not in request.files:
        return jsonify(message='No file part in the request'), 400

    file = request.files['file']

    # Check if a file was submitted
    if file.filename == '':
        return jsonify(message='No file selected'), 400

    # Check if the file is allowed
    if file and allowed_file(file.filename):
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Save the file to the upload folder
        file.save(file_path)

        # Convert PDF to a list of images (one per page)
        pages = convert_from_path(file_path, dpi=300)

        # Check if the document pages are less than 150
        if len(pages) >= 150:
            response_message = "The document has 150 or more pages."
        else:
            response_message = "The document has fewer than 150 pages."

        # Analyze the uploaded PDF
        results = analyze_pdf(file_path)

        # Return the analysis result
        return jsonify(message=response_message, analysis_results=results), 200

    else:
        return jsonify(message='File type not allowed'), 400

# Function to analyze the PDF file
def analyze_pdf(pdf_path):
    # Convert PDF to a list of images (one per page)
    pages = convert_from_path(pdf_path, dpi=300)
    results = []

    # Process each page image using the analyzer
    analyzer = dd.get_dd_analyzer(config_overwrite=["LANGUAGE='eng'"])
    for i, page_image in enumerate(pages):
        # Convert the PIL image to a format compatible with deepdoctection
        page_image_path = Path(f"page_{i}.png")
        page_image.save(page_image_path)  # Save the image to a unique path for each page

        # Analyze the image
        analysis_result = analyzer.analyze(path=pdf_path, page_number=i+1)
        results.append(analysis_result)
        print(f"Analysis result for page {i}:", analysis_result)

        # Additional checks for abstract and font size
        if 'font_size' in analysis_result:
            font_size = analysis_result['font_size']
            print(f"Page {i} font size:", font_size)

            if font_size != 12:
                print(f"Warning: Page {i} does not have the correct font size. Expected 12pt.")
        else:
            print(f"Font size information not available for page {i}.")

        if 'abstract' in analysis_result:
            abstract_content = analysis_result['abstract']
            abstract_length_chars = len(abstract_content) if isinstance(abstract_content, str) else len(" ".join(abstract_content))
            print(f"Abstract length: {abstract_length_chars} characters")

    return results

# Run the Flask app
if __name__ == '__main__':
    # Create the upload folder if it doesn't exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    app.run(port=3000)
