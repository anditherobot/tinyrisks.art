import os
import sys
import pytest
import tempfile

# Add the parent directory to the path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create a temporary directory for uploads during testing
    test_upload_folder = tempfile.mkdtemp()
    
    # Update the UPLOAD_FOLDER in the app configuration
    flask_app.config.update({
        'TESTING': True,
    })
    
    # Directly modify the UPLOAD_FOLDER path used by the app
    import app as app_module
    original_upload_folder = app_module.UPLOAD_FOLDER
    app_module.UPLOAD_FOLDER = test_upload_folder
    
    yield flask_app
    
    # Restore original upload folder and cleanup
    app_module.UPLOAD_FOLDER = original_upload_folder
    import shutil
    if os.path.exists(test_upload_folder):
        shutil.rmtree(test_upload_folder)

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()
