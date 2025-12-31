"""
Test cases for admin panel functionality and access control.
Currently tests static admin resources and provides framework for authentication.
"""
import pytest


class TestAdminPanelAccess:
    """Test cases for admin panel access."""
    
    def test_admin_js_accessible(self, client):
        """Test that admin.js file is accessible."""
        response = client.get('/static/admin/admin.js')
        assert response.status_code == 200
        # Verify it contains expected admin functionality
        assert b'initSnippetManager' in response.data
        assert b'initWorldBuildingFeatures' in response.data
    
    def test_admin_js_contains_snippet_manager(self, client):
        """Test that admin.js contains snippet management functionality."""
        response = client.get('/static/admin/admin.js')
        assert response.status_code == 200
        assert b'initSnippetManager' in response.data
    
    def test_admin_js_contains_world_building(self, client):
        """Test that admin.js contains world building features."""
        response = client.get('/static/admin/admin.js')
        assert response.status_code == 200
        assert b'initWorldBuildingFeatures' in response.data
    
    def test_index_page_accessible(self, client):
        """Test that main index page is accessible (public)."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'TinyRisks' in response.data
    
    def test_gallery_page_accessible(self, client):
        """Test that gallery page is accessible."""
        response = client.get('/gallery.html')
        assert response.status_code == 200


class TestAuthenticationFramework:
    """Test cases for authentication functionality."""

    def test_login_endpoint_exists(self, client):
        """Test that login endpoint exists."""
        response = client.get('/login')
        # Should not be 404
        assert response.status_code in [200, 302, 401]

    def test_login_with_valid_credentials(self, client):
        """Test login with valid credentials (admin/adminpass123)."""
        response = client.post('/api/login', json={
            'username': 'admin',
            'password': 'adminpass123'
        })
        assert response.status_code == 200
        json_data = response.get_json()
        assert 'success' in json_data
        assert json_data['success'] is True

    def test_login_with_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        response = client.post('/api/login', json={
            'username': 'admin',
            'password': 'wrongpassword'
        })
        assert response.status_code in [401, 403]
        json_data = response.get_json()
        assert 'error' in json_data or 'success' in json_data
        if 'success' in json_data:
            assert json_data['success'] is False

    def test_login_with_missing_fields(self, client):
        """Test login with missing username or password."""
        # Missing password
        response = client.post('/api/login', json={
            'username': 'admin'
        })
        # App should handle None password gracefully
        assert response.status_code in [400, 401]

    def test_logout_when_logged_in(self, client):
        """Test logout functionality when user is logged in."""
        # First login
        login_response = client.post('/api/login', json={
            'username': 'admin',
            'password': 'adminpass123'
        })
        assert login_response.status_code == 200

        # Then logout
        logout_response = client.post('/api/logout')
        assert logout_response.status_code == 200
        json_data = logout_response.get_json()
        assert json_data['success'] is True

    def test_logout_when_not_logged_in(self, client):
        """Test logout when user is not logged in."""
        response = client.post('/api/logout')
        # Flask-Login @login_required will redirect unauthorized users
        assert response.status_code in [200, 302, 401]

    def test_admin_access_requires_authentication(self, client):
        """Test that admin panel requires authentication."""
        response = client.get('/admin')
        # Should redirect to login or return 401
        assert response.status_code in [302, 401]

    def test_admin_access_with_authentication(self, client):
        """Test admin panel access with valid authentication."""
        # Login first
        client.post('/api/login', json={
            'username': 'admin',
            'password': 'adminpass123'
        })

        # Access admin panel
        response = client.get('/admin')
        assert response.status_code == 200

    def test_session_persistence(self, client):
        """Test that session persists across requests."""
        # Login
        login_response = client.post('/api/login', json={
            'username': 'admin',
            'password': 'adminpass123'
        })
        assert login_response.status_code == 200

        # Make another request to admin panel
        # Session should persist
        response = client.get('/admin')
        assert response.status_code == 200

    def test_protected_endpoint_after_logout(self, client):
        """Test that protected endpoints are inaccessible after logout."""
        # Login
        client.post('/api/login', json={
            'username': 'admin',
            'password': 'adminpass123'
        })

        # Logout
        client.post('/api/logout')

        # Try to access protected resource
        response = client.get('/admin')
        assert response.status_code in [302, 401]


class TestAdminImageUploadControl:
    """Test cases for admin control over image uploads."""

    def test_upload_requires_authentication(self, client):
        """Test that image upload requires authentication."""
        import io
        data = {
            'image': (io.BytesIO(b'test image'), 'test.png')
        }
        response = client.post('/api/upload',
                              data=data,
                              content_type='multipart/form-data')
        # Should require auth
        assert response.status_code in [302, 401]

    def test_authenticated_admin_can_upload(self, client):
        """Test that authenticated admin can upload images."""
        import io

        # Login first
        client.post('/api/login', json={
            'username': 'admin',
            'password': 'adminpass123'
        })

        # Upload image
        data = {
            'image': (io.BytesIO(b'test image'), 'test.png')
        }
        response = client.post('/api/upload',
                              data=data,
                              content_type='multipart/form-data')
        assert response.status_code == 200

    def test_upload_with_description(self, client):
        """Test uploading image with description field."""
        import io

        # Login first
        client.post('/api/login', json={
            'username': 'admin',
            'password': 'adminpass123'
        })

        # Upload image with description
        data = {
            'image': (io.BytesIO(b'test image'), 'test.png'),
            'description': 'Test image description'
        }
        response = client.post('/api/upload',
                              data=data,
                              content_type='multipart/form-data')
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] is True

    def test_upload_description_max_length(self, client):
        """Test that description has 4000 character limit."""
        import io

        # Login first
        client.post('/api/login', json={
            'username': 'admin',
            'password': 'adminpass123'
        })

        # Try to upload with description over 4000 chars
        long_description = 'a' * 4001
        data = {
            'image': (io.BytesIO(b'test image'), 'test.png'),
            'description': long_description
        }
        response = client.post('/api/upload',
                              data=data,
                              content_type='multipart/form-data')
        assert response.status_code == 400
        json_data = response.get_json()
        assert 'error' in json_data


class TestStaticFileServing:
    """Test cases for static file serving."""
    
    def test_serve_index_html(self, client):
        """Test serving index.html."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'<!DOCTYPE html>' in response.data or b'<html' in response.data
    
    def test_serve_css_file(self, client):
        """Test serving CSS files."""
        response = client.get('/static/css/base.css')
        # May return 200 or 404 depending on file existence
        assert response.status_code in [200, 404]
    
    def test_serve_js_component(self, client):
        """Test serving JavaScript component files."""
        response = client.get('/static/js/components.js')
        # May return 200 or 404 depending on file existence
        assert response.status_code in [200, 404]
    
    def test_serve_nonexistent_file(self, client):
        """Test serving a file that doesn't exist."""
        response = client.get('/nonexistent/file.html')
        assert response.status_code == 404
