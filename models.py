import sqlite3
import os
import json
import logging
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Configure logging
logger = logging.getLogger(__name__)

DATABASE_PATH = 'tinyrisks.db'

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

def get_db_connection():
    """Create and return database connection"""
    conn = sqlite3.connect(DATABASE_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode for better concurrency
    conn.execute('PRAGMA journal_mode=WAL')
    return conn

def init_db():
    """Initialize database schema and seed default user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    
    # Create images table to store metadata and descriptions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            description TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create community_images table for gallery CRUD
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS community_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            caption TEXT,
            description TEXT,
            images TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create text_posts table for writing/blog CRUD
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS text_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            subtitle TEXT,
            content TEXT NOT NULL,
            category TEXT,
            tags TEXT,
            reading_time INTEGER,
            published BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Seed default user: admin/adminpass123
    try:
        password_hash = generate_password_hash('adminpass123')
        cursor.execute(
            'INSERT INTO users (username, password_hash) VALUES (?, ?)',
            ('admin', password_hash)
        )
        conn.commit()
        print("Database initialized and default user 'admin' created")
    except sqlite3.IntegrityError:
        # User already exists
        print("Database already initialized")
    
    conn.close()

def verify_user(username, password):
    """Verify user credentials"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT id, username, password_hash FROM users WHERE username = ?',
        (username,)
    )
    
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data and check_password_hash(user_data['password_hash'], password):
        return User(id=user_data['id'], username=user_data['username'])
    return None

def get_user_by_id(user_id):
    """Get user by ID for Flask-Login"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, username FROM users WHERE id = ?', (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data:
        return User(id=user_data['id'], username=user_data['username'])
    return None

def save_image_metadata(filename, description):
    """Save image metadata to database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'INSERT INTO images (filename, description) VALUES (?, ?)',
        (filename, description)
    )
    conn.commit()
    conn.close()

def get_all_images():
    """Get all images with metadata"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM images ORDER BY uploaded_at DESC')
    images = cursor.fetchall()
    conn.close()
    
    return images

# Community Images CRUD operations
def create_community_image(title, caption, description, images):
    """Create a new community image gallery item"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Store images as JSON array
    images_json = json.dumps(images)
    
    cursor.execute(
        'INSERT INTO community_images (title, caption, description, images) VALUES (?, ?, ?, ?)',
        (title, caption, description, images_json)
    )
    conn.commit()
    image_id = cursor.lastrowid
    conn.close()
    
    return image_id

def get_all_community_images():
    """Get all community images"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM community_images ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    
    # Convert to list of dicts and parse JSON images
    images = []
    for row in rows:
        img = dict(row)
        try:
            img['images'] = json.loads(img['images'])
        except (json.JSONDecodeError, TypeError) as e:
            # Handle corrupted JSON data gracefully
            logger.warning(f"Failed to parse images JSON for item {img.get('id')}: {e}")
            img['images'] = []
        images.append(img)
    
    return images

def get_community_image_by_id(image_id):
    """Get a single community image by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM community_images WHERE id = ?', (image_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        img = dict(row)
        try:
            img['images'] = json.loads(img['images'])
        except (json.JSONDecodeError, TypeError) as e:
            # Handle corrupted JSON data gracefully
            logger.warning(f"Failed to parse images JSON for item {img.get('id')}: {e}")
            img['images'] = []
        return img
    return None

def update_community_image(image_id, title, caption, description, images):
    """Update an existing community image"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    images_json = json.dumps(images)
    
    cursor.execute(
        '''UPDATE community_images 
           SET title = ?, caption = ?, description = ?, images = ?, 
               updated_at = CURRENT_TIMESTAMP 
           WHERE id = ?''',
        (title, caption, description, images_json, image_id)
    )
    conn.commit()
    conn.close()

def delete_community_image(image_id):
    """Delete a community image"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM community_images WHERE id = ?', (image_id,))
    conn.commit()
    conn.close()

# Text Posts CRUD operations
def create_text_post(title, subtitle, content, category, tags, reading_time, published=False):
    """Create a new text post"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Store tags as JSON array if provided
    tags_json = json.dumps(tags) if tags else None
    
    cursor.execute(
        '''INSERT INTO text_posts (title, subtitle, content, category, tags, reading_time, published) 
           VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (title, subtitle, content, category, tags_json, reading_time, published)
    )
    conn.commit()
    post_id = cursor.lastrowid
    conn.close()
    
    return post_id

def get_all_text_posts(published_only=False):
    """Get all text posts"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if published_only:
        cursor.execute('SELECT * FROM text_posts WHERE published = 1 ORDER BY created_at DESC')
    else:
        cursor.execute('SELECT * FROM text_posts ORDER BY created_at DESC')
    
    rows = cursor.fetchall()
    conn.close()
    
    # Convert to list of dicts and parse JSON tags
    posts = []
    for row in rows:
        post = dict(row)
        try:
            post['tags'] = json.loads(post['tags']) if post['tags'] else []
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"Failed to parse tags JSON for post {post.get('id')}: {e}")
            post['tags'] = []
        posts.append(post)
    
    return posts

def get_text_post_by_id(post_id):
    """Get a single text post by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM text_posts WHERE id = ?', (post_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        post = dict(row)
        try:
            post['tags'] = json.loads(post['tags']) if post['tags'] else []
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"Failed to parse tags JSON for post {post.get('id')}: {e}")
            post['tags'] = []
        return post
    return None

def update_text_post(post_id, title, subtitle, content, category, tags, reading_time, published):
    """Update an existing text post"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    tags_json = json.dumps(tags) if tags else None
    
    cursor.execute(
        '''UPDATE text_posts 
           SET title = ?, subtitle = ?, content = ?, category = ?, tags = ?, 
               reading_time = ?, published = ?, updated_at = CURRENT_TIMESTAMP 
           WHERE id = ?''',
        (title, subtitle, content, category, tags_json, reading_time, published, post_id)
    )
    conn.commit()
    conn.close()

def delete_text_post(post_id):
    """Delete a text post"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM text_posts WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()
