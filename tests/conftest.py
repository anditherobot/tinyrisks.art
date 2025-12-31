import os
import sys
import pytest
import tempfile

# Add the parent directory to the path so we can import app
# This is a common pattern for test discovery in Flask applications
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create a temporary directory for uploads during testing
    test_upload_folder = tempfile.mkdtemp()

    # Create a temporary database for testing
    test_db_fd, test_db_path = tempfile.mkstemp()

    # Update the UPLOAD_FOLDER and database in the app configuration
    flask_app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key-for-sessions',
        'WTF_CSRF_ENABLED': False,  # Disable CSRF for testing
    })

    # Directly modify the UPLOAD_FOLDER and DATABASE_PATH used by the app
    import app as app_module
    import models

    original_upload_folder = app_module.UPLOAD_FOLDER
    original_db_path = models.DATABASE_PATH

    app_module.UPLOAD_FOLDER = test_upload_folder
    models.DATABASE_PATH = test_db_path

    # Initialize the test database
    models.init_db()

    yield flask_app

    # Restore original paths and cleanup
    app_module.UPLOAD_FOLDER = original_upload_folder
    models.DATABASE_PATH = original_db_path

    import shutil
    if os.path.exists(test_upload_folder):
        shutil.rmtree(test_upload_folder)

    # Close and remove test database
    os.close(test_db_fd)
    os.unlink(test_db_path)

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

@pytest.fixture
def logged_in_client(client):
    """A test client that is already logged in as admin."""
    client.post('/api/login', json={
        'username': 'admin',
        'password': 'adminpass123'
    })
    return client
