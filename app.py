from flask import Flask, request, jsonify, send_file, render_template
import requests
import os
import io  

app = Flask(__name__)

@app.route('/')
def serve_frontend():
    return render_template('index.html')

@app.route('/get-fit-file', methods=['POST'])
def get_fit_file():
    url = "https://www.8020endurance.com/wp-content/library/run/RRe1.FIT"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        file_stream = io.BytesIO(response.content)
        return send_file(
            file_stream,
            mimetype="application/octet-stream",
            as_attachment=True,
            download_name="RRe1.FIT"  # Updated parameter name
        )
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch file: {str(e)}"}), 500
    
    
@app.route('/process-fit-file', methods=['POST'])
def process_fit_file():
    data = request.json
    file_name = data['fileName']
    base64_data = data['data']
    return jsonify({'processed': True, 'fileName': file_name})

if __name__ == '__main__':
    app.run(debug=True)