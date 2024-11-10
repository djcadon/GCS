from flask import Flask, request, jsonify, send_file
from GSlice import create_obj, create_gif  # Ensure GSlice.py is in the same directory
import os
import io

app = Flask(__name__)

# Ensure uploads and processed folders exist
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return send_file('templates/home.html')  # Serves the home page

@app.route('/result')
def result():
    return send_file('templates/slice.html')  # Serves the result page

@app.route('/about')
def about():
    return send_file('templates/about.html')  # Serves the about page


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        # Process the file to get .obj and .gif contents
        obj_content = create_obj(file_path)
        gif_buffer = create_gif(file_path)

        # Store processed files
        obj_path = os.path.join(PROCESSED_FOLDER, 'model.obj')
        gif_path = os.path.join(PROCESSED_FOLDER, 'model_animation.gif')

        with open(obj_path, 'w') as f:
            f.write(obj_content)

        gif_buffer.seek(0)
        with open(gif_path, 'wb') as f:
            f.write(gif_buffer.read())

        # Send paths to frontend as response
        return jsonify({
            "obj": f"/processed/model.obj",
            "gif": f"/processed/model_animation.gif"
        })

@app.route('/processed/<path:filename>')
def download_file(filename):
    return send_file(os.path.join(PROCESSED_FOLDER, filename))

if __name__ == "__main__":
    app.run(host = '0.0.0.0')
