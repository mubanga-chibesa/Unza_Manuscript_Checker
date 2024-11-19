from flask import Flask, request, jsonify

app = Flask(__name__)

# Route for file upload
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"message": "No file part in the request"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No file selected"}), 400

    # Process the uploaded file (Placeholder logic)
    file_content = file.read()  # Read file content
    analysis_results = {"filename": file.filename, "size": len(file_content)}

    return jsonify({"message": "File processed successfully", "results": analysis_results})

# For Vercel serverless
def handler(event, context):
    from flask import Response
    from werkzeug.middleware.dispatcher import DispatcherMiddleware
    from werkzeug.serving import run_simple

    if event.get('source') == 'serverless':
        # Adapt Flask to work with Vercel
        app.wsgi_app = DispatcherMiddleware(app)
        response = Response.from_app(app, event)
        return response(environ=event['rawPath'], start_response=context)
    else:
        run_simple('localhost', 5000, app)
