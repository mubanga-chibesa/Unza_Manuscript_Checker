from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import PyPDF2  # For PDF analysis
import pdfplumber  # For analyzing fonts and sizes in PDFs
import re  # For APA style regex matching
import docx  # For DOCX analysis
from flask_cors import CORS
import json

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Folder paths for uploaded files and reports
UPLOAD_FOLDER = 'uploads/'
REPORTS_FOLDER = 'reports/'

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REPORTS_FOLDER'] = REPORTS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

# Function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# APA regex pattern
APA_REGEX = r"^[A-Z][a-z]+, ([A-Z]\. )*(\(\d{4}\).*|[A-Z]\.[A-Z]\. \(\d{4}\))"

# Function to check if a reference is in APA style
def check_apa_style(reference):
    return bool(re.match(APA_REGEX, reference.strip()))

# Function to extract and check references or bibliography
def extract_and_check_references(text):
    # Search for "References" or "Bibliography"
    section_match = re.search(r'\b(references|bibliography)\b', text, re.IGNORECASE)
    if not section_match:
        return {"message": "No references or bibliography section found."}

    # Extract the text starting from the section
    section_start = section_match.start()
    references_text = text[section_start:].split("\n")[1:]  # Skip the section title

    # Stop processing if we encounter a new section title (uppercase text or keywords like "Appendix")
    references = []
    for line in references_text:
        line = line.strip()
        if not line:
            continue  # Skip empty lines
        if re.match(r'^[A-Z ]+$', line) and len(line.split()) > 1:  # New section title (all uppercase, multiple words)
            break
        references.append(line)

    if not references:
        return {"message": "No references found after the section title."}

    # Check alphabetical order
    is_ordered = references == sorted(references, key=lambda x: x.lower())
    reference_order_result = "References are in alphabetical order." if is_ordered else "References are NOT in alphabetical order."

    # Check APA compliance for each reference
    apa_compliance_results = [
        {
            "reference": ref,
            "apa_check": "APA compliant" if check_apa_style(ref) else "Not APA compliant"
        }
        for ref in references
    ]

    return {
        "reference_order_check": reference_order_result,
        "apa_compliance": apa_compliance_results
    }

# Function to check if text is in title case
def is_title_case(text):
    words = text.split()
    return all(word.istitle() or word.lower() in ['a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor', 'on', 'at', 'to', 'by'] for word in words)

# Function to extract text from DOCX
def extract_text_from_docx(filepath):
    try:
        doc = docx.Document(filepath)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    except Exception as e:
        raise Exception(f"Failed to extract text from DOCX: {str(e)}")

# Function to extract text from PDF
def extract_text_from_pdf(filepath):
    try:
        with pdfplumber.open(filepath) as pdf:
            return ''.join(page.extract_text() or '' for page in pdf.pages)
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")

# Function to check abstract length
def check_abstract_length(text):
    abstract_match = re.search(r"\babstract\b[:\-]?\s*(.*?)\n\n", text, re.IGNORECASE | re.DOTALL)
    if abstract_match:
        abstract_text = abstract_match.group(1).strip()
        word_count = len(abstract_text.split())
        if word_count > 500:
            return {"message": f"Abstract exceeds 500 words: {word_count} words."}
        return None
    else:
        return {"message": "Abstract not found in the document."}

# Function to check tables and diagrams for source mention and percent usage
def check_tables_diagrams_and_percent_usage(text):
    results = []

    # Look for tables or diagrams by specific keywords like "Table" or "Diagram"
    tables_and_diagrams = re.findall(r"(Table|Diagram|Figure)\s*\d+", text)

    for table_or_diagram in tables_and_diagrams:
        # Check if a source is mentioned beneath the table or diagram
        source_check = "No source stated beneath" if "source" not in text.lower() else None

        # Check for percentage usage in text
        percent_word_check = "The word 'percent' was NOT used" if "percent" not in text.lower() else None

        # Check for '%' symbol usage in tables
        percent_symbol_check = "'%' symbol for percent was NOT used" if "%" not in text else None

        # If any issue is detected, add it to the results
        if source_check or percent_word_check or percent_symbol_check:
            results.append({
                "table_or_diagram": table_or_diagram,
                "source_check": source_check,
                "percent_word_check": percent_word_check,
                "percent_symbol_check": percent_symbol_check
            })

    # Return None if no issues are found
    return results if results else None

# Function to check font properties in PDFs
def check_font_properties(pdf):
    font_issues = []
    for i, page in enumerate(pdf.pages):
        text = page.extract_text() or ""
        font_data = page.chars

        if i > 0:  # Skip first page for title case check
            for line in text.split('\n'):
                if line.strip() and not is_title_case(line.strip()):
                    font_issues.append({"page": i + 1, "issue": "Title not in title case", "text": line.strip()})

        for char in font_data:
            font_name = char.get('fontname', '')
            font_size = char.get('size', 0)

            # Check for Times New Roman and font size 12
            if 'Times' not in font_name or font_size != 12:
                font_issues.append({"page": i + 1, "issue": "Font is not Times New Roman 12pt", "font": font_name, "size": font_size})

    return font_issues if font_issues else None

# Function to analyze the file
def analyze_file(filepath, filename):
    try:
        file_extension = filename.rsplit('.', 1)[1].lower()
        if file_extension == 'pdf':
            with pdfplumber.open(filepath) as pdf:
                # Check for page count
                page_count = len(pdf.pages)
                page_result = f"Document has {page_count} pages."
                results = [{"page_check": page_result}]

                # Font and title case check
                font_issues = check_font_properties(pdf)
                if font_issues:
                    results.append({"font_and_title_issues": font_issues})

            text = extract_text_from_pdf(filepath)

        elif file_extension == 'docx':
            text = extract_text_from_docx(filepath)
            results = []

        else:
            return {"error": "Unsupported file format"}

        # Abstract length check
        abstract_result = check_abstract_length(text)
        if abstract_result:
            results.append(abstract_result)

        # References check
        reference_results = extract_and_check_references(text)
        if reference_results:
            results.append(reference_results)

        # Tables and diagrams check
        tables_and_diagrams_results = check_tables_diagrams_and_percent_usage(text)
        if tables_and_diagrams_results:
            results.extend(tables_and_diagrams_results)

        # Save results as a text file
        report_name = f"{filename.rsplit('.', 1)[0]}_analysis.txt"
        analysis_file_path = os.path.join(REPORTS_FOLDER, report_name)
        with open(analysis_file_path, "w") as f:
            for result in results:
                f.write(json.dumps(result, indent=4) + "\n")

        return {"message": "File analyzed successfully", "results": results, "report": report_name}
    except Exception as e:
        return {"error": f"Failed to analyze file: {str(e)}"}

        return {"message": "File analyzed successfully", "results": results, "report": report_name}
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
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Analyze file
        analysis = analyze_file(file_path, filename)

        if 'error' in analysis:
            return jsonify({"message": analysis['error']}), 500

        return jsonify({"message": analysis['message'], "report": analysis["report"], "results": analysis["results"]}), 200

    except Exception as e:
        return jsonify({"message": f"Failed to upload file: {str(e)}"}), 500

# Route to fetch the report
@app.route('/api/report/<filename>', methods=['GET'])
def get_report(filename):
    try:
        report_path = os.path.join(app.config['REPORTS_FOLDER'], filename)

        if os.path.exists(report_path):
            return send_file(report_path)
        else:
            return jsonify({"message": "Report not found"}), 404
    except Exception as e:
        return jsonify({"message": f"Error fetching report: {str(e)}"}), 500

if __name__ == '__main__':
   app.run(debug=True)







