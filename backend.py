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
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import PyPDF2  # For PDF analysis
import docx    # For DOCX analysis
from pathlib import Path
from pdf2image import convert_from_path
import matplotlib.pyplot as plt
import json

app = Flask(__name__)

# Folder paths for uploaded files and reports
UPLOAD_FOLDER = 'uploads/'
REPORTS_FOLDER = 'reports/'

# Create necessary folders if they don't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(REPORTS_FOLDER):
    os.makedirs(REPORTS_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REPORTS_FOLDER'] = REPORTS_FOLDER

# Max file size set to 16 MB
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

# Function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Analyze PDF file (this includes the PDF analysis you provided)
def analyze_pdf(filepath):
    try:
        results = []
        pdf_path = Path(filepath)

        # Convert PDF to images (one per page)
        pages = convert_from_path(pdf_path, dpi=300)

        # Check if the document pages are less than 150
        if len(pages) >= 150:
            print("The document has 150 or more pages.")
            results.append({"page_check": "The document has 150 or more pages."})
        else:
            print("The document has fewer than 150 pages.")
            results.append({"page_check": "The document has fewer than 150 pages."})

        # Loop through each page and analyze
        for i, page_image in enumerate(pages):
            # Save each page image
            page_image_path = Path(f"page_{i}.png")
            page_image.save(page_image_path)

            # Analyze the page (simulating the analysis here)
            analysis_result = {"font_size": 12, "abstract": "Sample abstract"}  # Simulated analysis

            results.append(analysis_result)
            print(f"Analysis result for page {i}:", analysis_result)

            # Check font size
            if 'font_size' in analysis_result:
                font_size = analysis_result['font_size']
                if font_size != 12:
                    print(f"Warning: Page {i} does not have the correct font size. Expected 12pt.")
                    results.append({"font_check": f"Page {i} does not have the correct font size. Expected 12pt."})

            # Check for abstract content
            if 'abstract' in analysis_result:
                abstract_content = analysis_result['abstract']
                abstract_length_chars = len(abstract_content)

                if isinstance(abstract_content, list):
                    abstract_length_pages = len(abstract_content)
                    abstract_text_combined = " ".join(abstract_content)
                    abstract_length_chars = len(abstract_text_combined)
                else:
                    abstract_length_pages = 1

                if abstract_length_pages == 1 or abstract_length_chars == 300:
                    results.append({"abstract_check": "The abstract meets the requirement."})
                    print("The abstract meets the requirement of being one page long or exactly 300 characters.")
                else:
                    results.append({"abstract_check": "The abstract does not meet the requirement."})
                    print("Warning: The abstract does not meet the requirement.")
            else:
                results.append({"abstract_check": f"Abstract content not found on page {i}."})

        # Save results as a JSON file
        analysis_file = os.path.join(REPORTS_FOLDER, "analysis_results.json")
        with open(analysis_file, "w") as f:
            json.dump(results, f, indent=4)

        return {"message": "PDF analyzed successfully", "results": results, "report": analysis_file}
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return {"error": f"Failed to process PDF: {str(e)}"}

# Route for file upload and analysis
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"message": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"message": "No file selected"}), 400

    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            print(f"File saved to {file_path}")

            # Analyze the file based on its type
            if filename.lower().endswith('.pdf'):
                analysis = analyze_pdf(file_path)
            elif filename.lower().endswith('.docx'):
                analysis = {"message": "DOCX analysis is not implemented in this example."}  # Placeholder for DOCX analysis
            else:
                return jsonify({"message": "Unsupported file format"}), 400

            # If there was an error during analysis, return it
            if 'error' in analysis:
                return jsonify({"message": analysis['error']}), 500

            return jsonify({"message": analysis['message'], "report": analysis["report"], "results": analysis["results"]}), 200
        except Exception as e:
            print(f"Error uploading file: {str(e)}")
            return jsonify({"message": f"Failed to upload file: {str(e)}"}), 500
    else:
        return jsonify({"message": "File type not allowed"}), 400

# Route to fetch the report
@app.route('/api/report/<filename>', methods=['GET'])
def get_report(filename):
    report_path = os.path.join(app.config['REPORTS_FOLDER'], filename)

    if os.path.exists(report_path):
        return send_file(report_path)
    else:
        return jsonify({"message": "Report not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
