import sqlite3
import os
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE_PATH = 'tinyrisks.db'

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

def get_db_connection():
    """Create and return database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
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
    
    # Seed default user: captain/bateau
    try:
        password_hash = generate_password_hash('bateau')
        cursor.execute(
            'INSERT INTO users (username, password_hash) VALUES (?, ?)',
            ('captain', password_hash)
        )
        conn.commit()
        print("✓ Database initialized and default user 'captain' created")
    except sqlite3.IntegrityError:
        # User already exists
        print("✓ Database already initialized")
    
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
