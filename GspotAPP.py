from flask import Flask, render_template, request, send_from_directory
import os
import re
from werkzeug.utils import secure_filename
import Gspot

app = Flask(__name__)

# Set the upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'gcode'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Helper function to check file extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route for the main page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle file upload and conversion
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Process the G-code file and generate OBJ and GIF (use your existing functions here)
        obj_file, gif_file = gcode_to_obj_with_animation(filepath)

        # Send the generated files to the user
        return render_template('download.html', obj_file=obj_file, gif_file=gif_file)

# Route to download the generated files
@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Function for G-code to OBJ and GIF (use your existing code here)
def gcode_to_obj_with_animation(gcode_file):
    # Generate output files with the same base name but with .obj and .gif extensions
    obj_file = f"{base_name}.obj"
    gif_file = f"{base_name}.gif"
    # Run your existing code to create these files
    return obj_file, gif_file

if __name__ == '__main__':
    app.run(debug=True)
