Geometric Code Slicer
Geometric Code Slicer is a web-based tool for converting G-code files into 3D models and animations, making it easier for users to visualize and analyze geometric code (G-code) from various 3D printing and CNC applications. This project was developed for [Hackathon Name], focused on creating innovative solutions for file processing and visualization.

🚀 Features
G-Code Upload: Simple drag-and-drop upload for G-code files.
G-Code Slicing: Converts G-code into .obj (3D model) and .gif (animated preview).
Downloadable Outputs: Get processed 3D models and animations instantly.
Real-time Progress Bar: Visual indication of file processing status.
📂 Directory Structure
/templates: Contains HTML templates for the home, result, and about pages.
/uploads: Directory for uploaded files.
/processed: Stores processed .obj and .gif files.
/static/images: Static assets like the logo and icons.
🛠️ Tech Stack
Frontend: HTML, CSS, JavaScript (with Tailwind CSS for styling)
Backend: Flask (Python)
3D Processing: GSlice.py handles G-code to .obj and .gif conversion.
⚙️ Setup & Installation
Prerequisites
Python 3.7+
pip for Python package management
Flask and flask-cors for backend and CORS handling
