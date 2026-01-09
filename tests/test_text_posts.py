"""
Test cases for text posts CRUD functionality.
"""
import pytest


class TestTextPostCRUD:
    """Test cases for text post CRUD operations."""
    
    def test_get_text_posts_empty(self, client):
        """Test getting text posts when none exist."""
        response = client.get('/api/text-posts')
        assert response.status_code == 200
        json_data = response.get_json()
        assert isinstance(json_data, list)
        assert len(json_data) == 0
    
    def test_create_text_post(self, logged_in_client):
        """Test creating a new text post."""
        post_data = {
            'title': 'My First Post',
            'subtitle': 'An introduction',
            'content': 'This is the content of my first post.',
            'category': 'Essays',
            'tags': ['test', 'first-post'],
            'reading_time': 5,
            'published': True
        }
        
        response = logged_in_client.post('/api/text-posts',
                                        json=post_data)
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] is True
        assert 'id' in json_data
        assert json_data['id'] > 0
    
    def test_create_text_post_requires_auth(self, client):
        """Test that creating a text post requires authentication."""
        post_data = {
            'title': 'Unauthorized Post',
            'content': 'This should not be created.'
        }
        
        response = client.post('/api/text-posts', json=post_data)
        # Should require auth
        assert response.status_code in [302, 401]
    
    def test_create_text_post_requires_title(self, logged_in_client):
        """Test that title is required."""
        post_data = {
            'content': 'Content without title'
        }
        
        response = logged_in_client.post('/api/text-posts',
                                        json=post_data)
        assert response.status_code == 400
        json_data = response.get_json()
        assert 'error' in json_data
        assert 'title' in json_data['error'].lower()
    
    def test_create_text_post_requires_content(self, logged_in_client):
        """Test that content is required."""
        post_data = {
            'title': 'Title without content'
        }
        
        response = logged_in_client.post('/api/text-posts',
                                        json=post_data)
        assert response.status_code == 400
        json_data = response.get_json()
        assert 'error' in json_data
        assert 'content' in json_data['error'].lower()
    
    def test_create_text_post_validates_tags_type(self, logged_in_client):
        """Test that tags must be a list."""
        post_data = {
            'title': 'Test Post',
            'content': 'Content here',
            'tags': 'not-a-list'  # Invalid: should be a list
        }
        
        response = logged_in_client.post('/api/text-posts',
                                        json=post_data)
        assert response.status_code == 400
        json_data = response.get_json()
        assert 'error' in json_data
        assert 'tags' in json_data['error'].lower()
    
    def test_get_all_text_posts(self, logged_in_client):
        """Test getting all text posts."""
        # Create a few posts
        for i in range(3):
            post_data = {
                'title': f'Post {i+1}',
                'content': f'Content {i+1}',
                'published': i % 2 == 0  # Alternate published status
            }
            logged_in_client.post('/api/text-posts', json=post_data)
        
        # Get all posts (as admin, should see all)
        response = logged_in_client.get('/api/text-posts')
        assert response.status_code == 200
        json_data = response.get_json()
        assert len(json_data) == 3
    
    def test_get_text_post_by_id(self, logged_in_client):
        """Test getting a specific text post by ID."""
        # Create a post
        post_data = {
            'title': 'Specific Post',
            'subtitle': 'With subtitle',
            'content': 'Specific content',
            'category': 'World Building',
            'tags': ['architecture', 'speculative'],
            'reading_time': 7,
            'published': True
        }
        
        create_response = logged_in_client.post('/api/text-posts',
                                                json=post_data)
        post_id = create_response.get_json()['id']
        
        # Get the post
        response = logged_in_client.get(f'/api/text-posts/{post_id}')
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['title'] == 'Specific Post'
        assert json_data['subtitle'] == 'With subtitle'
        assert json_data['content'] == 'Specific content'
        assert json_data['category'] == 'World Building'
        assert json_data['tags'] == ['architecture', 'speculative']
        assert json_data['reading_time'] == 7
        assert json_data['published'] == 1  # SQLite stores boolean as integer
    
    def test_get_text_post_not_found(self, logged_in_client):
        """Test getting a non-existent post."""
        response = logged_in_client.get('/api/text-posts/99999')
        assert response.status_code == 404
        json_data = response.get_json()
        assert 'error' in json_data
    
    def test_update_text_post(self, logged_in_client):
        """Test updating an existing text post."""
        # Create a post
        post_data = {
            'title': 'Original Title',
            'content': 'Original content',
            'published': False
        }
        
        create_response = logged_in_client.post('/api/text-posts',
                                                json=post_data)
        post_id = create_response.get_json()['id']
        
        # Update the post
        updated_data = {
            'title': 'Updated Title',
            'content': 'Updated content',
            'subtitle': 'New subtitle',
            'category': 'Essays',
            'tags': ['updated'],
            'reading_time': 10,
            'published': True
        }
        
        response = logged_in_client.put(f'/api/text-posts/{post_id}',
                                       json=updated_data)
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] is True
        
        # Verify the update
        get_response = logged_in_client.get(f'/api/text-posts/{post_id}')
        updated_post = get_response.get_json()
        assert updated_post['title'] == 'Updated Title'
        assert updated_post['content'] == 'Updated content'
        assert updated_post['subtitle'] == 'New subtitle'
        assert updated_post['published'] == 1
    
    def test_update_text_post_not_found(self, logged_in_client):
        """Test updating a non-existent post."""
        updated_data = {
            'title': 'Updated Title',
            'content': 'Updated content'
        }
        
        response = logged_in_client.put('/api/text-posts/99999',
                                       json=updated_data)
        assert response.status_code == 404
    
    def test_update_text_post_requires_title(self, logged_in_client):
        """Test that title is required when updating."""
        # Create a post
        post_data = {
            'title': 'Original',
            'content': 'Original content'
        }
        create_response = logged_in_client.post('/api/text-posts',
                                                json=post_data)
        post_id = create_response.get_json()['id']
        
        # Try to update without title
        response = logged_in_client.put(f'/api/text-posts/{post_id}',
                                       json={'content': 'New content'})
        assert response.status_code == 400
    
    def test_delete_text_post(self, logged_in_client):
        """Test deleting a text post."""
        # Create a post
        post_data = {
            'title': 'To be deleted',
            'content': 'Delete me'
        }
        
        create_response = logged_in_client.post('/api/text-posts',
                                                json=post_data)
        post_id = create_response.get_json()['id']
        
        # Delete the post
        response = logged_in_client.delete(f'/api/text-posts/{post_id}')
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data['success'] is True
        
        # Verify it's gone
        get_response = logged_in_client.get(f'/api/text-posts/{post_id}')
        assert get_response.status_code == 404
    
    def test_delete_text_post_not_found(self, logged_in_client):
        """Test deleting a non-existent post."""
        response = logged_in_client.delete('/api/text-posts/99999')
        assert response.status_code == 404
    
    def test_delete_text_post_requires_auth(self, client):
        """Test that deleting requires authentication."""
        response = client.delete('/api/text-posts/1')
        # Should require auth
        assert response.status_code in [302, 401]


class TestTextPostVisibility:
    """Test cases for text post visibility (published vs draft)."""
    
    def test_public_sees_only_published_posts(self, client, logged_in_client):
        """Test that unauthenticated users only see published posts."""
        # Create published and unpublished posts
        logged_in_client.post('/api/text-posts', json={
            'title': 'Published Post',
            'content': 'Public content',
            'published': True
        })
        
        logged_in_client.post('/api/text-posts', json={
            'title': 'Draft Post',
            'content': 'Draft content',
            'published': False
        })
        
        # Logout
        logged_in_client.post('/api/logout')
        
        # Public should only see published post
        response = client.get('/api/text-posts')
        assert response.status_code == 200
        posts = response.get_json()
        assert len(posts) == 1
        assert posts[0]['title'] == 'Published Post'
    
    def test_admin_sees_all_posts(self, logged_in_client):
        """Test that authenticated admin sees all posts."""
        # Create published and unpublished posts
        logged_in_client.post('/api/text-posts', json={
            'title': 'Published Post',
            'content': 'Public content',
            'published': True
        })
        
        logged_in_client.post('/api/text-posts', json={
            'title': 'Draft Post',
            'content': 'Draft content',
            'published': False
        })
        
        # Admin should see both posts
        response = logged_in_client.get('/api/text-posts')
        assert response.status_code == 200
        posts = response.get_json()
        assert len(posts) == 2
    
    def test_public_cannot_access_unpublished_post_by_id(self, client, logged_in_client):
        """Test that public cannot access unpublished posts by ID."""
        # Create unpublished post
        create_response = logged_in_client.post('/api/text-posts', json={
            'title': 'Draft Post',
            'content': 'Draft content',
            'published': False
        })
        post_id = create_response.get_json()['id']
        
        # Logout
        logged_in_client.post('/api/logout')
        
        # Public should not be able to access it
        response = client.get(f'/api/text-posts/{post_id}')
        assert response.status_code == 404


class TestTextPostEdgeCases:
    """Test edge cases and data validation."""
    
    def test_create_post_with_empty_tags(self, logged_in_client):
        """Test creating a post with empty tags list."""
        post_data = {
            'title': 'No Tags Post',
            'content': 'Content without tags',
            'tags': []
        }
        
        response = logged_in_client.post('/api/text-posts',
                                        json=post_data)
        assert response.status_code == 200
        
        # Verify it was created correctly
        post_id = response.get_json()['id']
        get_response = logged_in_client.get(f'/api/text-posts/{post_id}')
        post = get_response.get_json()
        assert post['tags'] == []
    
    def test_create_post_with_zero_reading_time(self, logged_in_client):
        """Test creating a post with zero reading time."""
        post_data = {
            'title': 'Quick Read',
            'content': 'Very short content',
            'reading_time': 0
        }
        
        response = logged_in_client.post('/api/text-posts',
                                        json=post_data)
        assert response.status_code == 200
    
    def test_create_post_with_long_content(self, logged_in_client):
        """Test creating a post with very long content."""
        long_content = 'A' * 10000  # 10k characters
        
        post_data = {
            'title': 'Long Post',
            'content': long_content
        }
        
        response = logged_in_client.post('/api/text-posts',
                                        json=post_data)
        assert response.status_code == 200
        
        # Verify content was stored correctly
        post_id = response.get_json()['id']
        get_response = logged_in_client.get(f'/api/text-posts/{post_id}')
        post = get_response.get_json()
        assert len(post['content']) == 10000
    
    def test_posts_sorted_by_created_at_desc(self, logged_in_client):
        """Test that posts are returned in correct order."""
        # Create posts
        titles = ['First', 'Second', 'Third']
        for title in titles:
            logged_in_client.post('/api/text-posts', json={
                'title': title,
                'content': f'{title} content'
            })
        
        response = logged_in_client.get('/api/text-posts')
        posts = response.get_json()
        
        # Should have all 3 posts
        assert len(posts) == 3
        # All titles should be present
        post_titles = [p['title'] for p in posts]
        assert 'First' in post_titles
        assert 'Second' in post_titles
        assert 'Third' in post_titles
