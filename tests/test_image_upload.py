"""
Test cases for image upload and retrieval functionality.
Tests the /api/upload and /api/images endpoints.
"""
import io
import os
import pytest
from werkzeug.datastructures import FileStorage


class TestImageUpload:
    """Test cases for image upload functionality."""
    
    def test_upload_valid_image(self, client, app):
        """Test successful upload of a valid image file."""
        # Create a fake image file
        data = {
            'image': (io.BytesIO(b'fake image content'), 'test_image.png')
        }
        
        response = client.post('/api/upload', 
                              data=data,
                              content_type='multipart/form-data')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] is True
        assert 'file' in json_data
        assert 'url' in json_data
        assert json_data['file'].endswith('.png')
        assert json_data['url'].startswith('/static/uploads/')
    
    def test_upload_jpg_image(self, client, app):
        """Test uploading a JPG image."""
        data = {
            'image': (io.BytesIO(b'fake jpg content'), 'photo.jpg')
        }
        
        response = client.post('/api/upload',
                              data=data,
                              content_type='multipart/form-data')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] is True
        assert json_data['file'].endswith('.jpg')
    
    def test_upload_jpeg_image(self, client, app):
        """Test uploading a JPEG image."""
        data = {
            'image': (io.BytesIO(b'fake jpeg content'), 'photo.jpeg')
        }
        
        response = client.post('/api/upload',
                              data=data,
                              content_type='multipart/form-data')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] is True
        assert json_data['file'].endswith('.jpeg')
    
    def test_upload_gif_image(self, client, app):
        """Test uploading a GIF image."""
        data = {
            'image': (io.BytesIO(b'GIF89a'), 'animation.gif')
        }
        
        response = client.post('/api/upload',
                              data=data,
                              content_type='multipart/form-data')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] is True
        assert json_data['file'].endswith('.gif')
    
    def test_upload_webp_image(self, client, app):
        """Test uploading a WEBP image."""
        data = {
            'image': (io.BytesIO(b'fake webp content'), 'modern.webp')
        }
        
        response = client.post('/api/upload',
                              data=data,
                              content_type='multipart/form-data')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] is True
        assert json_data['file'].endswith('.webp')
    
    def test_upload_no_file_part(self, client):
        """Test upload request with no file part."""
        response = client.post('/api/upload',
                              data={},
                              content_type='multipart/form-data')
        
        assert response.status_code == 400
        json_data = response.get_json()
        assert 'error' in json_data
        assert json_data['error'] == 'No file part'
    
    def test_upload_empty_filename(self, client):
        """Test upload with empty filename."""
        data = {
            'image': (io.BytesIO(b'content'), '')
        }
        
        response = client.post('/api/upload',
                              data=data,
                              content_type='multipart/form-data')
        
        assert response.status_code == 400
        json_data = response.get_json()
        assert 'error' in json_data
        assert json_data['error'] == 'No selected file'
    
    def test_upload_invalid_file_type_txt(self, client):
        """Test upload with invalid file type (.txt)."""
        data = {
            'image': (io.BytesIO(b'text content'), 'document.txt')
        }
        
        response = client.post('/api/upload',
                              data=data,
                              content_type='multipart/form-data')
        
        assert response.status_code == 400
        json_data = response.get_json()
        assert 'error' in json_data
        assert json_data['error'] == 'Invalid file type'
    
    def test_upload_invalid_file_type_pdf(self, client):
        """Test upload with invalid file type (.pdf)."""
        data = {
            'image': (io.BytesIO(b'%PDF-1.4'), 'document.pdf')
        }
        
        response = client.post('/api/upload',
                              data=data,
                              content_type='multipart/form-data')
        
        assert response.status_code == 400
        json_data = response.get_json()
        assert 'error' in json_data
        assert json_data['error'] == 'Invalid file type'
    
    def test_upload_invalid_file_type_exe(self, client):
        """Test upload with invalid file type (.exe)."""
        data = {
            'image': (io.BytesIO(b'MZ'), 'malware.exe')
        }
        
        response = client.post('/api/upload',
                              data=data,
                              content_type='multipart/form-data')
        
        assert response.status_code == 400
        json_data = response.get_json()
        assert 'error' in json_data
        assert json_data['error'] == 'Invalid file type'
    
    def test_upload_creates_unique_filenames(self, client):
        """Test that multiple uploads create unique filenames."""
        data1 = {
            'image': (io.BytesIO(b'image1'), 'same_name.png')
        }
        data2 = {
            'image': (io.BytesIO(b'image2'), 'same_name.png')
        }
        
        response1 = client.post('/api/upload',
                               data=data1,
                               content_type='multipart/form-data')
        response2 = client.post('/api/upload',
                               data=data2,
                               content_type='multipart/form-data')
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        file1 = response1.get_json()['file']
        file2 = response2.get_json()['file']
        
        # Filenames should be different even though original name was same
        assert file1 != file2
        assert file1 != 'same_name.png'
        assert file2 != 'same_name.png'
    
    def test_upload_file_case_insensitive_extension(self, client):
        """Test that file extensions are case-insensitive."""
        data = {
            'image': (io.BytesIO(b'fake content'), 'IMAGE.PNG')
        }
        
        response = client.post('/api/upload',
                              data=data,
                              content_type='multipart/form-data')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] is True
        # Extension should be lowercase in the saved filename
        assert json_data['file'].endswith('.png')


class TestImageListing:
    """Test cases for image listing functionality."""
    
    def test_list_images_empty(self, client):
        """Test listing images when no images have been uploaded."""
        response = client.get('/api/images')
        
        assert response.status_code == 200
        json_data = response.get_json()
        assert isinstance(json_data, list)
        assert len(json_data) == 0
    
    def test_list_images_after_upload(self, client, app):
        """Test listing images after uploading one."""
        # Upload an image first
        data = {
            'image': (io.BytesIO(b'test image'), 'test.png')
        }
        upload_response = client.post('/api/upload',
                                     data=data,
                                     content_type='multipart/form-data')
        assert upload_response.status_code == 200
        
        # Now list images
        list_response = client.get('/api/images')
        assert list_response.status_code == 200
        
        json_data = list_response.get_json()
        assert isinstance(json_data, list)
        assert len(json_data) == 1
        assert 'url' in json_data[0]
        assert 'time' in json_data[0]
    
    def test_list_images_multiple_uploads(self, client, app):
        """Test listing multiple uploaded images."""
        # Upload multiple images
        for i in range(3):
            data = {
                'image': (io.BytesIO(f'image{i}'.encode()), f'test{i}.png')
            }
            response = client.post('/api/upload',
                                  data=data,
                                  content_type='multipart/form-data')
            assert response.status_code == 200
        
        # List all images
        list_response = client.get('/api/images')
        assert list_response.status_code == 200
        
        json_data = list_response.get_json()
        assert len(json_data) == 3
        
        # Verify all have required fields
        for image in json_data:
            assert 'url' in image
            assert 'time' in image
    
    def test_list_images_sorted_by_newest(self, client, app):
        """Test that images are sorted by newest first."""
        import time
        
        # Upload images with slight delay
        for i in range(3):
            data = {
                'image': (io.BytesIO(f'image{i}'.encode()), f'test{i}.png')
            }
            client.post('/api/upload',
                       data=data,
                       content_type='multipart/form-data')
            time.sleep(0.01)  # Small delay to ensure different timestamps
        
        # List images
        response = client.get('/api/images')
        json_data = response.get_json()
        
        # Verify sorting (newest first)
        for i in range(len(json_data) - 1):
            assert json_data[i]['time'] >= json_data[i + 1]['time']
