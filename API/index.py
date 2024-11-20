import os
import re
import json
import docx
import pdfplumber
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = Flask(__name__)
CORS(app)

# Configure upload and reports folders for serverless environments
UPLOAD_FOLDER = '/tmp/uploads'
REPORTS_FOLDER = '/tmp/reports'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REPORTS_FOLDER'] = REPORTS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

# Helper function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to check APA style compliance
APA_REGEX = r"^[A-Z][a-z]+, ([A-Z]\. )*(\(\d{4}\).*|[A-Z]\.[A-Z]\. \(\d{4}\))"

def check_apa_style(reference):
    return bool(re.match(APA_REGEX, reference.strip()))

def extract_and_check_references(text):
    section_match = re.search(r'\b(references|bibliography)\b', text, re.IGNORECASE)
    if not section_match:
        return {"message": "No references or bibliography section found."}

    references = []
    for line in text[section_match.end():].split("\n"):
        line = line.strip()
        if line and not re.match(r'^[A-Z ]+$', line):
            references.append(line)

    is_ordered = references == sorted(references, key=lambda x: x.lower())
    compliance_results = [
        {"reference": ref, "apa_check": "APA compliant" if check_apa_style(ref) else "Not APA compliant"}
        for ref in references
    ]

    return {
        "reference_order_check": "References are in alphabetical order." if is_ordered else "References are NOT in alphabetical order.",
        "apa_compliance": compliance_results
    }

# Function to extract text from files
def extract_text_from_docx(filepath):
    try:
        doc = docx.Document(filepath)
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)
    except Exception as e:
        raise Exception(f"Failed to extract text from DOCX: {str(e)}")

def extract_text_from_pdf(filepath):
    try:
        with pdfplumber.open(filepath) as pdf:
            return ''.join(page.extract_text() or '' for page in pdf.pages)
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")

# Function to analyze the file
def analyze_file(filepath, filename):
    try:
        file_extension = filename.rsplit('.', 1)[1].lower()
        results = []

        if file_extension == 'pdf':
            with pdfplumber.open(filepath) as pdf:
                text = ''.join(page.extract_text() or '' for page in pdf.pages)
                results.append({"page_count": len(pdf.pages)})

        elif file_extension == 'docx':
            text = extract_text_from_docx(filepath)

        else:
            return {"error": "Unsupported file format"}

        # Perform analysis tasks
        abstract_match = re.search(r"\babstract\b[:\-]?\s*(.*?)\n\n", text, re.IGNORECASE | re.DOTALL)
        if abstract_match:
            abstract_text = abstract_match.group(1).strip()
            word_count = len(abstract_text.split())
            if word_count > 500:
                results.append({"abstract_length_check": f"Abstract exceeds 500 words: {word_count}"})

        references_results = extract_and_check_references(text)
        if references_results:
            results.append(references_results)

        report_name = f"{filename.rsplit('.', 1)[0]}_analysis.json"
        report_path = os.path.join(REPORTS_FOLDER, report_name)
        with open(report_path, 'w') as report_file:
            json.dump(results, report_file, indent=4)

        return {"message": "Analysis completed successfully", "results": results, "report": report_name}

    except Exception as e:
        return {"error": f"Failed to analyze file: {str(e)}"}

# Flask routes
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"message": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"message": "File type not allowed"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    analysis = analyze_file(filepath, filename)
    if 'error' in analysis:
        return jsonify({"message": analysis['error']}), 500

    return jsonify({"message": analysis['message'], "results": analysis['results'], "report": analysis['report']}), 200

@app.route('/api/report/<filename>', methods=['GET'])
def get_report(filename):
    report_path = os.path.join(app.config['REPORTS_FOLDER'], filename)
    if os.path.exists(report_path):
        return send_file(report_path)
    return jsonify({"message": "Report not found"}), 404

# Adapt Flask for Vercel
def handler(event, context):
    return DispatcherMiddleware(app)
