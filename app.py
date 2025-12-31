import os
import time
import random
from flask import Flask, request, jsonify, send_from_directory, redirect, url_for, session, render_template_string
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import init_db, verify_user, get_user_by_id, save_image_metadata, get_all_images
from models import create_community_image, get_all_community_images, get_community_image_by_id
from models import update_community_image, delete_community_image

# Configure app to serve static files from htdocs
app = Flask(__name__, static_folder='htdocs')

# Secret key configuration
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    # Generate a random secret key for development
    import secrets
    SECRET_KEY = secrets.token_hex(32)
    print("WARNING: Using auto-generated SECRET_KEY. Set SECRET_KEY environment variable in production!")

app.config['SECRET_KEY'] = SECRET_KEY

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
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB in bytes

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

    # Validate required fields
    if not username or not password:
        return jsonify({'success': False, 'error': 'Username and password are required'}), 400

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

# Community Images CRUD API
@app.route('/api/community-images', methods=['GET'])
def get_community_images():
    """Get all community images"""
    images = get_all_community_images()
    return jsonify(images)

@app.route('/api/community-images/<int:image_id>', methods=['GET'])
def get_community_image(image_id):
    """Get a single community image by ID"""
    image = get_community_image_by_id(image_id)
    if image:
        return jsonify(image)
    return jsonify({'error': 'Image not found'}), 404

@app.route('/api/community-images', methods=['POST'])
@login_required
def create_community_image_api():
    """Create a new community image gallery item"""
    saved_filenames = []
    try:
        # Get form data
        title = request.form.get('title', '').strip()
        caption = request.form.get('caption', '')
        description = request.form.get('description', '')
        
        # Validate title
        if not title:
            return jsonify({'error': 'Title is required'}), 400
        
        # Handle multiple file uploads
        files = request.files.getlist('images')
        
        if not files or len(files) == 0:
            return jsonify({'error': 'At least one image is required'}), 400
        
        if len(files) > 9:
            return jsonify({'error': 'Maximum 9 images allowed'}), 400
        
        # Process and save files
        for file in files:
            if file and file.filename and allowed_file(file.filename):
                # Check file size
                file.seek(0, os.SEEK_END)
                file_size = file.tell()
                file.seek(0)
                
                if file_size > MAX_FILE_SIZE:
                    return jsonify({'error': f'File {file.filename} exceeds 20MB limit'}), 400
                
                # Generate unique filename
                ext = file.filename.rsplit('.', 1)[1].lower()
                unique_name = f"community-{int(time.time())}-{random.randint(1000, 9999)}.{ext}"
                
                file.save(os.path.join(UPLOAD_FOLDER, unique_name))
                saved_filenames.append(unique_name)
            elif file and file.filename:
                return jsonify({'error': f'Invalid file type: {file.filename}'}), 400
        
        if not saved_filenames:
            return jsonify({'error': 'No valid images uploaded'}), 400
        
        # Save to database
        image_id = create_community_image(title, caption, description, saved_filenames)
        
        return jsonify({
            'success': True,
            'id': image_id,
            'images': saved_filenames
        })
    
    except Exception as e:
        # Clean up any files that were saved before the error to avoid orphaned uploads
        for filename in saved_filenames:
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except OSError:
                # If cleanup fails, log but preserve the original error context
                pass
        return jsonify({'error': str(e)}), 500

@app.route('/api/community-images/<int:image_id>', methods=['PUT'])
@login_required
def update_community_image_api(image_id):
    """Update an existing community image"""
    try:
        # Check if image exists
        existing_image = get_community_image_by_id(image_id)
        if not existing_image:
            return jsonify({'error': 'Image not found'}), 404
        
        # Get form data
        title = request.form.get('title', '').strip()
        caption = request.form.get('caption', '')
        description = request.form.get('description', '')
        
        if not title:
            return jsonify({'error': 'Title is required'}), 400
        
        # Check if new images are being uploaded
        files = request.files.getlist('images')
        
        if files and files[0].filename:
            # New images provided
            if len(files) > 9:
                return jsonify({'error': 'Maximum 9 images allowed'}), 400
            
            # Process and save new files first
            saved_filenames = []
            for file in files:
                if file and file.filename and allowed_file(file.filename):
                    # Check file size
                    file.seek(0, os.SEEK_END)
                    file_size = file.tell()
                    file.seek(0)
                    
                    if file_size > MAX_FILE_SIZE:
                        return jsonify({'error': f'File {file.filename} exceeds 20MB limit'}), 400
                    
                    ext = file.filename.rsplit('.', 1)[1].lower()
                    unique_name = f"community-{int(time.time())}-{random.randint(1000, 9999)}.{ext}"
                    
                    file.save(os.path.join(UPLOAD_FOLDER, unique_name))
                    saved_filenames.append(unique_name)
            
            if not saved_filenames:
                return jsonify({'error': 'No valid images uploaded'}), 400
            
            # Update database with new images
            update_community_image(image_id, title, caption, description, saved_filenames)
            
            # Only delete old images after successful database update
            for old_filename in existing_image['images']:
                old_path = os.path.join(UPLOAD_FOLDER, old_filename)
                try:
                    if os.path.exists(old_path):
                        os.remove(old_path)
                except OSError:
                    # Log but don't fail if old file deletion fails
                    pass
        else:
            # Keep existing images
            update_community_image(image_id, title, caption, description, existing_image['images'])
        
        return jsonify({'success': True, 'id': image_id})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/community-images/<int:image_id>', methods=['DELETE'])
@login_required
def delete_community_image_api(image_id):
    """Delete a community image"""
    try:
        # Get the image to delete files
        image = get_community_image_by_id(image_id)
        if not image:
            return jsonify({'error': 'Image not found'}), 404
        
        # Delete associated files
        for filename in image['images']:
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
        
        # Delete from database
        delete_community_image(image_id)
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return send_from_directory('htdocs', '404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return send_from_directory('htdocs', '500.html'), 500

if __name__ == '__main__':
    # Initialize database on startup
    init_db()
    print("Server running at http://localhost:5000")
    app.run(debug=True, port=5000)
