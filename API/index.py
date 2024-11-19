import os
import re
import json
import docx  # For DOCX analysis
import PyPDF2  # For PDF analysis
import pdfplumber  # For analyzing fonts and sizes in PDFs
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure upload and reports folders
UPLOAD_FOLDER = 'uploads/'
REPORTS_FOLDER = 'reports/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REPORTS_FOLDER'] = REPORTS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

# Helper function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Helper function to check APA style
APA_REGEX = r"^[A-Z][a-z]+, ([A-Z]\. )*(\(\d{4}\).*|[A-Z]\.[A-Z]\. \(\d{4}\))"

def check_apa_style(reference):
    return bool(re.match(APA_REGEX, reference.strip()))

# Helper function to analyze files
def analyze_file(filepath, filename):
    try:
        file_extension = filename.rsplit('.', 1)[1].lower()
        results = []

        if file_extension == 'pdf':
            with pdfplumber.open(filepath) as pdf:
                text = ''.join(page.extract_text() or '' for page in pdf.pages)
                results.append({"page_count": f"Document has {len(pdf.pages)} pages."})

                # Check for font and title case issues
                font_issues = []
                for i, page in enumerate(pdf.pages):
                    for char in page.chars:
                        font_name = char.get('fontname', '')
                        font_size = char.get('size', 0)
                        if 'Times' not in font_name or font_size != 12:
                            font_issues.append({
                                "page": i + 1,
                                "issue": "Font is not Times New Roman 12pt",
                                "font": font_name,
                                "size": font_size
                            })
                if font_issues:
                    results.append({"font_issues": font_issues})

        elif file_extension == 'docx':
            text = "\n".join([p.text for p in docx.Document(filepath).paragraphs])

        else:
            return {"error": "Unsupported file format"}

        # Perform further text analysis
        abstract_match = re.search(r"\babstract\b[:\-]?\s*(.*?)\n\n", text, re.IGNORECASE | re.DOTALL)
        if abstract_match:
            abstract_text = abstract_match.group(1).strip()
            word_count = len(abstract_text.split())
            if word_count > 500:
                results.append({"abstract_length": f"Abstract exceeds 500 words: {word_count} words."})

        # APA reference check
        references_match = re.search(r'\b(references|bibliography)\b', text, re.IGNORECASE)
        if references_match:
            references_start = references_match.start()
            references_text = text[references_start:].split('\n')[1:]
            references = [line.strip() for line in references_text if line.strip()]
            apa_results = [
                {"reference": ref, "apa_compliance": check_apa_style(ref)}
                for ref in references
            ]
            results.append({"apa_compliance_results": apa_results})

        # Save analysis report
        report_name = f"{filename.rsplit('.', 1)[0]}_analysis.json"
        report_path = os.path.join(REPORTS_FOLDER, report_name)
        with open(report_path, 'w') as report_file:
            json.dump(results, report_file, indent=4)

        return {"message": "Analysis completed successfully", "results": results, "report": report_name}

    except Exception as e:
        return {"error": f"Failed to analyze file: {str(e)}"}

# Route for file upload and analysis
@app.route('/api/upload', methods=['POST'])
def upload_file():
    try:
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

        # Analyze the uploaded file
        analysis = analyze_file(filepath, filename)

        if 'error' in analysis:
            return jsonify({"message": analysis['error']}), 500

        return jsonify({"message": analysis['message'], "results": analysis['results'], "report": analysis['report']}), 200

    except Exception as e:
        return jsonify({"message": f"Failed to upload file: {str(e)}"}), 500

# Route to fetch the report
@app.route('/api/report/<filename>', methods=['GET'])
def get_report(filename):
    try:
        report_path = os.path.join(app.config['REPORTS_FOLDER'], filename)
        if os.path.exists(report_path):
            return send_file(report_path)
        return jsonify({"message": "Report not found"}), 404
    except Exception as e:
        return jsonify({"message": f"Error fetching report: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
