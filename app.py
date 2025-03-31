from flask import Flask, request, jsonify, send_file, render_template
import requests
import io
import base64
import os
import tempfile
from fitparse import FitFile

app = Flask(__name__)

# Function to extract workout steps with per-zone durations (from your working code)
def extract_workout_data(file_path):
    durations = []  # Will store [start, end] pairs (either time in minutes or distance in km)
    zones = []
    is_time_based = False
    
    try:
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' not found.")
            return None, None, None
        
        with open(file_path, 'rb') as f:
            fitfile = FitFile(f)
            for record in fitfile.get_messages('workout_step'):
                distance = record.get_value('duration_distance')
                time = record.get_value('duration_time')
                duration_type = record.get_value('duration_type')
                intensity = record.get_value('intensity')
                notes = record.get_value('notes')
                
                # Skip steps without a usable duration (e.g., repeat steps)
                if duration_type == 'repeat_until_steps_cmplt':
                    continue
                
                # Determine if this is time-based or distance-based
                if time is not None and distance is None:
                    duration = time / 60  # Convert seconds to minutes
                    is_time_based = True
                elif distance is not None and time is None:
                    duration = distance / 1000  # Convert meters to kilometers
                    is_time_based = False
                else:
                    continue  # Skip if neither or both are present (ambiguous)
                
                # Map intensity/notes to zone numbers
                if intensity == 'warmup' or intensity == 'cooldown' or (notes and 'Zone 1' in notes):
                    zone = 1
                elif notes and 'Zone 2' in notes:
                    zone = 2
                elif notes and 'Zone 3' in notes:
                    zone = 3
                elif intensity == '4' or (notes and 'Zone 4' in notes):
                    zone = 4
                elif notes and 'Zone 5' in notes:
                    zone = 5
                else:
                    zone = 1  # Default to Zone 1 if unclear
                
                durations.append([0, duration])
                zones.append(zone)
                
        return durations, zones, is_time_based
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None, None

@app.route('/')
def serve_frontend():
    return render_template('index.html')

@app.route('/get-fit-file', methods=['POST'])
def get_fit_file():
    data = request.json
    url = data['url']
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
            download_name=url.split('/')[-1]
        )
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch file: {str(e)}"}), 500

@app.route('/process-fit-file', methods=['POST'])
def process_fit_file():
    try:
        data = request.json
        file_name = data['fileName']
        base64_data = data['data']

        # Decode base64 data back to binary
        binary_data = base64.b64decode(base64_data)

        # Save the binary data to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.fit') as temp_file:
            temp_file.write(binary_data)
            temp_file_path = temp_file.name

        # Process the FIT file using the working function
        durations, zones, is_time_based = extract_workout_data(temp_file_path)

        # Clean up the temporary file
        os.unlink(temp_file_path)

        if durations is None or zones is None:
            return jsonify({'error': 'Failed to process FIT file'}), 500

        # Return the processed data to the frontend
        return jsonify({
            'processed': True,
            'fileName': file_name,
            'durations': durations,
            'zones': zones,
            'isTimeBased': is_time_based
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)