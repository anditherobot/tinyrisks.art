import os
import time
import random
from flask import Flask, request, jsonify, send_from_directory

# Configure app to serve static files from htdocs
app = Flask(__name__, static_folder='htdocs')

# Configuration
UPLOAD_FOLDER = os.path.join(app.static_folder, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return send_from_directory('htdocs', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('htdocs', path)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file and allowed_file(file.filename):
        # Generate unique filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_name = f"img-{int(time.time())}-{random.randint(1000, 9999)}.{ext}"
        
        file.save(os.path.join(UPLOAD_FOLDER, unique_name))
        
        return jsonify({
            'success': True, 
            'file': unique_name,
            'url': f'/static/uploads/{unique_name}'
        })
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/api/images', methods=['GET'])
def list_images():
    images = []
    if os.path.exists(UPLOAD_FOLDER):
        for filename in os.listdir(UPLOAD_FOLDER):
            if allowed_file(filename):
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                images.append({
                    'url': f'/static/uploads/{filename}',
                    'time': os.path.getmtime(filepath)
                })
    
    # Sort by newest first
    images.sort(key=lambda x: x['time'], reverse=True)
    return jsonify(images)

if __name__ == '__main__':
    print("Server running at http://localhost:5000")
    app.run(debug=True, port=5000)
