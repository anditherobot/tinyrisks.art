"""
Test cases for community image CRUD functionality.
"""
import io


class TestCommunityImageCRUD:
    """Test cases for community image CRUD operations."""

    def test_get_community_images_empty(self, client):
        """Test getting community images when none exist."""
        response = client.get('/api/community-images')
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_create_community_image(self, logged_in_client):
        """Test creating a new community image."""
        data = {
            'title': 'Test Gallery',
            'caption': 'Test Caption',
            'description': 'Test Description',
            'images': [
                (io.BytesIO(b'test image 1'), 'test1.png'),
                (io.BytesIO(b'test image 2'), 'test2.jpg')
            ]
        }
        
        response = logged_in_client.post('/api/community-images',
                                        data=data,
                                        content_type='multipart/form-data')
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] is True
        assert 'id' in json_data
        assert len(json_data['images']) == 2

    def test_create_community_image_requires_auth(self, client):
        """Test that creating community images requires authentication."""
        data = {
            'title': 'Test Gallery',
            'images': [(io.BytesIO(b'test image'), 'test.png')]
        }
        
        response = client.post('/api/community-images',
                             data=data,
                             content_type='multipart/form-data')
        assert response.status_code in [302, 401]

    def test_create_community_image_requires_title(self, logged_in_client):
        """Test that title is required."""
        data = {
            'caption': 'Caption without title',
            'images': [(io.BytesIO(b'test image'), 'test.png')]
        }
        
        response = logged_in_client.post('/api/community-images',
                                        data=data,
                                        content_type='multipart/form-data')
        assert response.status_code == 400
        json_data = response.get_json()
        assert 'error' in json_data

    def test_create_community_image_requires_at_least_one_image(self, logged_in_client):
        """Test that at least one image is required."""
        data = {
            'title': 'Test Gallery'
        }
        
        response = logged_in_client.post('/api/community-images',
                                        data=data,
                                        content_type='multipart/form-data')
        assert response.status_code == 400
        json_data = response.get_json()
        assert 'error' in json_data

    def test_create_community_image_max_9_images(self, logged_in_client):
        """Test that maximum 9 images are allowed."""
        data = {
            'title': 'Test Gallery',
            'images': [(io.BytesIO(b'test image'), f'test{i}.png') for i in range(10)]
        }
        
        response = logged_in_client.post('/api/community-images',
                                        data=data,
                                        content_type='multipart/form-data')
        assert response.status_code == 400
        json_data = response.get_json()
        assert 'error' in json_data
        assert '9' in json_data['error'].lower()

    def test_create_community_image_file_size_limit(self, logged_in_client):
        """Test 20MB file size limit."""
        # Create a file larger than 20MB
        large_file = io.BytesIO(b'x' * (21 * 1024 * 1024))
        data = {
            'title': 'Test Gallery',
            'images': [(large_file, 'large.png')]
        }
        
        response = logged_in_client.post('/api/community-images',
                                        data=data,
                                        content_type='multipart/form-data')
        assert response.status_code == 400
        json_data = response.get_json()
        assert 'error' in json_data
        assert '20mb' in json_data['error'].lower()

    def test_get_all_community_images(self, logged_in_client, client):
        """Test getting all community images."""
        # Create a community image first
        data = {
            'title': 'Test Gallery 1',
            'images': [(io.BytesIO(b'test image'), 'test.png')]
        }
        logged_in_client.post('/api/community-images',
                             data=data,
                             content_type='multipart/form-data')
        
        # Get all images
        response = client.get('/api/community-images')
        assert response.status_code == 200
        json_data = response.get_json()
        assert isinstance(json_data, list)
        assert len(json_data) == 1
        assert json_data[0]['title'] == 'Test Gallery 1'

    def test_get_community_image_by_id(self, logged_in_client, client):
        """Test getting a single community image by ID."""
        # Create a community image
        data = {
            'title': 'Test Gallery',
            'caption': 'Test Caption',
            'images': [(io.BytesIO(b'test image'), 'test.png')]
        }
        create_response = logged_in_client.post('/api/community-images',
                                               data=data,
                                               content_type='multipart/form-data')
        image_id = create_response.get_json()['id']
        
        # Get the image
        response = client.get(f'/api/community-images/{image_id}')
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['title'] == 'Test Gallery'
        assert json_data['caption'] == 'Test Caption'

    def test_get_community_image_not_found(self, client):
        """Test getting a non-existent community image."""
        response = client.get('/api/community-images/999')
        assert response.status_code == 404

    def test_update_community_image(self, logged_in_client):
        """Test updating a community image."""
        # Create a community image
        data = {
            'title': 'Original Title',
            'images': [(io.BytesIO(b'test image'), 'test.png')]
        }
        create_response = logged_in_client.post('/api/community-images',
                                               data=data,
                                               content_type='multipart/form-data')
        image_id = create_response.get_json()['id']
        
        # Update the image
        update_data = {
            'title': 'Updated Title',
            'caption': 'New Caption',
            'description': 'New Description'
        }
        response = logged_in_client.put(f'/api/community-images/{image_id}',
                                       data=update_data,
                                       content_type='multipart/form-data')
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] is True
        
        # Verify the update
        get_response = logged_in_client.get(f'/api/community-images/{image_id}')
        updated_image = get_response.get_json()
        assert updated_image['title'] == 'Updated Title'
        assert updated_image['caption'] == 'New Caption'
        assert updated_image['description'] == 'New Description'

    def test_delete_community_image(self, logged_in_client):
        """Test deleting a community image."""
        # Create a community image
        data = {
            'title': 'To Delete',
            'images': [(io.BytesIO(b'test image'), 'test.png')]
        }
        create_response = logged_in_client.post('/api/community-images',
                                               data=data,
                                               content_type='multipart/form-data')
        image_id = create_response.get_json()['id']
        
        # Delete the image
        response = logged_in_client.delete(f'/api/community-images/{image_id}')
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] is True
        
        # Verify it's deleted
        get_response = logged_in_client.get(f'/api/community-images/{image_id}')
        assert get_response.status_code == 404

    def test_delete_community_image_not_found(self, logged_in_client):
        """Test deleting a non-existent image."""
        response = logged_in_client.delete('/api/community-images/999')
        assert response.status_code == 404


class TestErrorPages:
    """Test cases for error pages."""

    def test_404_error_page(self, client):
        """Test that 404 error page is returned for non-existent routes."""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
        assert b'404' in response.data
        assert b'Page Not Found' in response.data

    def test_404_page_has_back_link(self, client):
        """Test that 404 page has a back to site link."""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
        assert b'Back to Site' in response.data or b'back to site' in response.data.lower()
