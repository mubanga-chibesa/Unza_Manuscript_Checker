from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"message": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No file selected"}), 400

    # Example file processing (expand this with your logic)
    file_content = file.read()
    analysis_results = {
        "filename": file.filename,
        "size": len(file_content),
        "message": "Analysis completed successfully"
    }

    return jsonify({"message": "File processed successfully", "results": analysis_results})
