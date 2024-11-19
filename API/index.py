import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# Ensure a directory exists to temporarily store uploaded files
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# File upload and analysis route
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"message": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No file selected"}), 400

    # Save the file temporarily for analysis
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Perform analysis (you can customize this with your logic)
    analysis_results = perform_analysis(file_path)

    # Clean up the file after analysis
    os.remove(file_path)

    return jsonify({
        "message": "File processed successfully",
        "results": analysis_results
    })

# Function to analyze the file
def perform_analysis(file_path):
    # Placeholder for real analysis logic
    # Example: Counting the number of lines in the file
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        return {
            "filename": os.path.basename(file_path),
            "line_count": len(lines),
            "message": "Analysis completed successfully"
        }
    except Exception as e:
        return {"error": str(e), "message": "Failed to analyze the file"}

# Run the app (For local development; ignored in production with Vercel)
if __name__ == '__main__':
    app.run(debug=True)
