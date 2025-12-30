"""
Test cases for basic Flask application functionality and configuration.
"""
import pytest


class TestAppConfiguration:
    """Test cases for Flask app configuration."""
    
    def test_app_exists(self, app):
        """Test that the Flask app is created."""
        assert app is not None
    
    def test_app_is_testing(self, app):
        """Test that app is in testing mode."""
        assert app.config['TESTING'] is True
    
    def test_upload_folder_configured(self, app):
        """Test that upload folder is configured."""
        # In the original app, UPLOAD_FOLDER is a module-level variable, not in config
        import app as app_module
        assert app_module.UPLOAD_FOLDER is not None
        assert isinstance(app_module.UPLOAD_FOLDER, str)


class TestBasicRoutes:
    """Test cases for basic application routes."""
    
    def test_index_route(self, client):
        """Test that index route works."""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_api_upload_route_exists(self, client):
        """Test that upload API route exists."""
        # POST is the correct method, we just want to verify route exists
        import io
        data = {
            'image': (io.BytesIO(b'test'), 'test.png')
        }
        response = client.post('/api/upload',
                              data=data,
                              content_type='multipart/form-data')
        # Should get 200 (success) or 302 (redirect to login), not 404 (route not found)
        # Upload now requires authentication, so 302 is expected for unauthenticated requests
        assert response.status_code in [200, 302]
    
    def test_api_images_route_exists(self, client):
        """Test that images API route exists."""
        response = client.get('/api/images')
        assert response.status_code == 200
    
    def test_404_for_invalid_route(self, client):
        """Test that invalid routes return 404."""
        response = client.get('/this-route-does-not-exist')
        assert response.status_code == 404


class TestAllowedFileExtensions:
    """Test cases for file extension validation."""
    
    def test_allowed_file_function(self, app):
        """Test the allowed_file helper function."""
        from app import allowed_file
        
        # Valid extensions
        assert allowed_file('image.png') is True
        assert allowed_file('photo.jpg') is True
        assert allowed_file('photo.jpeg') is True
        assert allowed_file('animation.gif') is True
        assert allowed_file('modern.webp') is True
        
        # Invalid extensions
        assert allowed_file('document.txt') is False
        assert allowed_file('script.js') is False
        assert allowed_file('data.json') is False
        assert allowed_file('file.pdf') is False
        assert allowed_file('program.exe') is False
    
    def test_allowed_file_case_insensitive(self, app):
        """Test that file extension check is case insensitive."""
        from app import allowed_file
        
        assert allowed_file('IMAGE.PNG') is True
        assert allowed_file('Photo.JPG') is True
        assert allowed_file('Image.JpEg') is True
        assert allowed_file('ANIMATION.GIF') is True
        assert allowed_file('modern.WEBP') is True
    
    def test_allowed_file_no_extension(self, app):
        """Test files without extensions."""
        from app import allowed_file
        
        assert allowed_file('noextension') is False
        assert allowed_file('') is False
    
    def test_allowed_file_multiple_dots(self, app):
        """Test files with multiple dots in name."""
        from app import allowed_file
        
        assert allowed_file('my.image.file.png') is True
        assert allowed_file('archive.tar.gz') is False
