import os
import time
import random
from flask import Flask, request, jsonify, send_from_directory, redirect, url_for, session, render_template_string
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import init_db, verify_user, get_user_by_id, save_image_metadata, get_all_images

# Configure app to serve static files from htdocs
app = Flask(__name__, static_folder='htdocs')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(int(user_id))

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

@app.route('/login')
def login():
    return send_from_directory('htdocs', 'login.html')

@app.route('/admin')
@login_required
def admin_dashboard():
    return send_from_directory('htdocs', 'admin.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = verify_user(username, password)
    if user:
        login_user(user)
        return jsonify({'success': True, 'redirect': '/admin'})
    
    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
@login_required
def api_logout():
    logout_user()
    return jsonify({'success': True, 'redirect': '/login'})

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('htdocs', path)

@app.route('/api/upload', methods=['POST'])
@login_required
def upload_file():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['image']
    description = request.form.get('description', '')
    
    # Validate description length (max 4000 characters)
    if len(description) > 4000:
        return jsonify({'error': 'Description too long (max 4000 characters)'}), 400
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file and allowed_file(file.filename):
        # Generate unique filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_name = f"img-{int(time.time())}-{random.randint(1000, 9999)}.{ext}"
        
        file.save(os.path.join(UPLOAD_FOLDER, unique_name))
        
        # Save metadata to database
        save_image_metadata(unique_name, description)
        
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
    # Initialize database on startup
    init_db()
    print("Server running at http://localhost:5000")
    app.run(debug=True, port=5000)
