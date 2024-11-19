import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = '/tmp/uploads'  # Use /tmp for serverless compatibility
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

# Helper function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

        # Mock analysis for simplicity
        analysis_result = {
            "filename": filename,
            "status": "success",
            "message": "File analyzed successfully",
            "analysis": {"line_count": 100, "word_count": 500}  # Replace with actual analysis
        }

        return jsonify({"message": "File processed successfully", "results": analysis_result}), 200

    except Exception as e:
        return jsonify({"message": f"Failed to process file: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
