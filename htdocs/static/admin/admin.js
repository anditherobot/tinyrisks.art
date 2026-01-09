document.addEventListener('DOMContentLoaded', () => {
    // --- State & Elements ---
    const elements = {
        tabs: {
            create: document.getElementById('tab-create'),
            library: document.getElementById('tab-library'),
            posts: document.getElementById('tab-posts')
        },
        panels: {
            create: document.getElementById('panel-create'),
            library: document.getElementById('panel-library'),
            posts: document.getElementById('panel-posts')
        },
        form: document.getElementById('editorForm'),
        inputs: {
            id: document.getElementById('editingId'),
            title: document.getElementById('title'),
            caption: document.getElementById('caption'),
            desc: document.getElementById('description'),
            images: document.getElementById('images'),
            fileStatus: document.getElementById('fileStatus')
        },
        preview: document.getElementById('mdPreview'),
        lists: {
            recent: document.getElementById('recentList'),
            library: document.getElementById('libraryGrid'),
            posts: document.getElementById('postsGrid')
        },
        btns: {
            save: document.getElementById('saveBtn'),
            cancel: document.getElementById('cancelBtn'),
            logout: document.getElementById('logoutBtn')
        },
        status: document.getElementById('statusMsg'),
        // Text post elements
        postModal: document.getElementById('postModal'),
        postForm: document.getElementById('postForm'),
        postInputs: {
            id: document.getElementById('postEditingId'),
            title: document.getElementById('postTitle'),
            subtitle: document.getElementById('postSubtitle'),
            category: document.getElementById('postCategory'),
            tags: document.getElementById('postTags'),
            readingTime: document.getElementById('postReadingTime'),
            content: document.getElementById('postContent'),
            published: document.getElementById('postPublished')
        },
        postPreview: document.getElementById('postPreview'),
        postStatus: document.getElementById('postStatusMsg'),
        postSaveBtn: document.getElementById('postSaveBtn'),
        postModalTitle: document.getElementById('postModalTitle')
    };

    // --- Init ---
    loadData();
    setupMarkdownPreview();
    setupPostEditor();
    
    // --- Event Listeners ---
    elements.btns.logout.addEventListener('click', handleLogout);
    elements.form.addEventListener('submit', handleFormSubmit);
    elements.btns.cancel.addEventListener('click', resetForm);
    elements.inputs.images.addEventListener('change', updateFileStatus);
    elements.postForm.addEventListener('submit', handlePostFormSubmit);

    // Global access for onclick handlers in HTML
    window.switchTab = switchTab;
    window.editItem = editItem;
    window.deleteItem = deleteItem;
    window.createNewPost = createNewPost;
    window.editPost = editPost;
    window.deletePost = deletePost;
    window.closePostModal = closePostModal;

    // --- Core Functions ---

    function switchTab(tabName) {
        // Toggle Buttons
        Object.values(elements.tabs).forEach(btn => btn.classList.remove('active'));
        if(elements.tabs[tabName]) elements.tabs[tabName].classList.add('active');

        // Toggle Panels
        Object.values(elements.panels).forEach(p => p.classList.remove('active'));
        if(elements.panels[tabName]) elements.panels[tabName].classList.add('active');

        if(tabName === 'library') loadData(); // Refresh data when opening library
        if(tabName === 'posts') loadPosts(); // Refresh posts when opening posts tab
    }

    function setupMarkdownPreview() {
        const updatePreview = () => {
            const raw = elements.inputs.desc.value;
            elements.preview.innerHTML = marked.parse(raw);
        };
        elements.inputs.desc.addEventListener('input', updatePreview);
        // Initial call
        updatePreview(); 
    }

    async function loadData() {
        try {
            const res = await fetch('/api/community-images');
            const data = await res.json();
            
            renderRecentList(data);
            renderLibraryGrid(data);
        } catch (err) {
            console.error("Failed to load data", err);
        }
    }

    // --- Rendering ---

    function renderRecentList(items) {
        const recent = items.slice(0, 5);
        elements.lists.recent.innerHTML = recent.map(item => `
            <li class="recent-item" onclick="editItem(${item.id})">
                ${escapeHtml(item.title)}
            </li>
        `).join('') || '<li class="recent-item">No posts yet</li>';
    }

    function renderLibraryGrid(items) {
        if (items.length === 0) {
            elements.lists.library.innerHTML = '<p style="padding:1rem">No items found.</p>';
            return;
        }

        elements.lists.library.innerHTML = items.map(item => {
            const thumb = item.images[0] ? `/static/uploads/${item.images[0]}` : ''; // Placeholder logic could go here
            return `
            <div class="library-item">
                <img src="${thumb}" class="lib-thumb" loading="lazy" alt="Thumbnail">
                <div style="font-weight:bold;margin-bottom:auto">${escapeHtml(item.title)}</div>
                <div style="font-size:0.8rem;color:var(--muted)">${item.images.length} images</div>
                <div class="action-bar">
                    <button class="btn-sm" onclick="editItem(${item.id})">Edit</button>
                    <button class="btn-sm btn-danger" onclick="deleteItem(${item.id})">Delete</button>
                </div>
            </div>
            `;
        }).join('');
    }

    // --- CRUD Operations ---

    async function handleFormSubmit(e) {
        e.preventDefault();
        
        const id = elements.inputs.id.value;
        const isEdit = !!id;
        const formData = new FormData(elements.form);

        // Validation for new posts
        if (!isEdit && elements.inputs.images.files.length === 0) {
            showStatus('Please select at least one image.', 'error');
            return;
        }

        setStatus('Saving...', 'neutral');
        elements.btns.save.disabled = true;

        try {
            const url = isEdit ? `/api/community-images/${id}` : '/api/community-images';
            const method = isEdit ? 'PUT' : 'POST';

            const res = await fetch(url, { method, body: formData });
            const json = await res.json();

            if (res.ok) {
                showStatus(isEdit ? 'Updated!' : 'Published!', 'success');
                resetForm();
                loadData(); // Refresh lists
                // Optional: Switch to library to see result? Or stay to create more.
                // switchTab('library'); 
            } else {
                throw new Error(json.error || 'Operation failed');
            }
        } catch (err) {
            showStatus(err.message, 'error');
        } finally {
            elements.btns.save.disabled = false;
        }
    }

    async function deleteItem(id) {
        if(!confirm('Permanently delete this project?')) return;
        
        try {
            const res = await fetch(`/api/community-images/${id}`, { method: 'DELETE' });
            if (res.ok) {
                loadData();
            } else {
                alert('Failed to delete');
            }
        } catch (err) {
            console.error(err);
        }
    }

    function editItem(id) {
        // 1. Fetch details (to get full description etc if not in list view)
        fetch(`/api/community-images/${id}`)
            .then(res => res.json())
            .then(item => {
                // 2. Populate Form
                elements.inputs.id.value = item.id;
                elements.inputs.title.value = item.title;
                elements.inputs.caption.value = item.caption || '';
                elements.inputs.desc.value = item.description || '';
                
                // 3. UI Updates
                elements.inputs.images.required = false; // Not required on edit
                elements.btns.save.textContent = 'Update Project';
                elements.btns.cancel.style.display = 'inline-block';
                elements.inputs.fileStatus.textContent = `${item.images.length} existing images (Upload new to replace/add)`;
                
                // 4. Trigger Preview Update
                elements.inputs.desc.dispatchEvent(new Event('input'));
                
                // 5. Switch Tab
                switchTab('create');
            })
            .catch(err => console.error("Edit fetch failed", err));
    }

    function resetForm() {
        elements.form.reset();
        elements.inputs.id.value = '';
        elements.btns.save.textContent = 'Publish Project';
        elements.btns.cancel.style.display = 'none';
        elements.inputs.images.required = true;
        elements.inputs.fileStatus.textContent = 'No files selected';
        elements.inputs.desc.dispatchEvent(new Event('input')); // clear preview
        setStatus('', 'neutral');
    }

    // --- Helpers ---

    function updateFileStatus() {
        const count = elements.inputs.images.files.length;
        elements.inputs.fileStatus.textContent = count > 0 ? `${count} file(s) selected` : 'No files selected';
    }

    async function handleLogout() {
        await fetch('/api/logout', { method: 'POST' });
        window.location.href = '/login';
    }

    function setStatus(msg, type) {
        const el = elements.status;
        el.textContent = msg;
        el.style.color = type === 'error' ? 'var(--error)' : type === 'success' ? 'var(--success)' : 'var(--muted)';
    }

    function showStatus(msg, type) {
        setStatus(msg, type);
        setTimeout(() => setStatus('', 'neutral'), 3000);
    }

    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // --- Text Post Functions ---

    function setupPostEditor() {
        const updatePostPreview = () => {
            const raw = elements.postInputs.content.value;
            elements.postPreview.innerHTML = marked.parse(raw);
        };
        elements.postInputs.content.addEventListener('input', updatePostPreview);
    }

    async function loadPosts() {
        try {
            const res = await fetch('/api/text-posts');
            const data = await res.json();
            renderPostsGrid(data);
        } catch (err) {
            console.error("Failed to load posts", err);
            elements.lists.posts.innerHTML = '<p style="padding:1rem;color:var(--error)">Failed to load posts</p>';
        }
    }

    function renderPostsGrid(posts) {
        if (posts.length === 0) {
            elements.lists.posts.innerHTML = '<p style="padding:1rem">No posts yet. Create your first one!</p>';
            return;
        }

        elements.lists.posts.innerHTML = posts.map(post => {
            const statusBadge = post.published ? 
                '<span style="padding:4px 8px;background:var(--accent);color:white;border-radius:4px;font-size:0.75rem">Published</span>' :
                '<span style="padding:4px 8px;background:var(--muted);color:var(--bg);border-radius:4px;font-size:0.75rem">Draft</span>';
            
            const excerpt = post.content.substring(0, 100) + (post.content.length > 100 ? '...' : '');
            
            return `
            <div class="library-item">
                <div style="font-weight:bold;margin-bottom:0.5rem">${escapeHtml(post.title)}</div>
                ${post.subtitle ? `<div style="font-size:0.9rem;color:var(--accent);font-style:italic;margin-bottom:0.5rem">${escapeHtml(post.subtitle)}</div>` : ''}
                <div style="font-size:0.85rem;color:var(--muted);margin-bottom:0.5rem">${escapeHtml(excerpt)}</div>
                <div style="font-size:0.75rem;color:var(--muted);margin-bottom:auto">
                    ${post.category || 'Uncategorized'} • ${post.reading_time || 0} min read
                </div>
                <div style="margin-top:0.5rem">${statusBadge}</div>
                <div class="action-bar">
                    <button class="btn-sm" onclick="editPost(${post.id})">Edit</button>
                    <button class="btn-sm btn-danger" onclick="deletePost(${post.id})">Delete</button>
                </div>
            </div>
            `;
        }).join('');
    }

    function createNewPost() {
        resetPostForm();
        elements.postModal.style.display = 'block';
        elements.postModalTitle.textContent = 'New Text Post';
    }

    function closePostModal() {
        elements.postModal.style.display = 'none';
        resetPostForm();
    }

    async function editPost(id) {
        try {
            const res = await fetch(`/api/text-posts/${id}`);
            const post = await res.json();
            
            // Populate form
            elements.postInputs.id.value = post.id;
            elements.postInputs.title.value = post.title;
            elements.postInputs.subtitle.value = post.subtitle || '';
            elements.postInputs.category.value = post.category || '';
            elements.postInputs.tags.value = Array.isArray(post.tags) ? post.tags.join(', ') : '';
            elements.postInputs.readingTime.value = post.reading_time || 0;
            elements.postInputs.content.value = post.content;
            elements.postInputs.published.checked = post.published === 1;
            
            // Update preview
            elements.postInputs.content.dispatchEvent(new Event('input'));
            
            // Show modal
            elements.postModalTitle.textContent = 'Edit Text Post';
            elements.postModal.style.display = 'block';
        } catch (err) {
            console.error("Failed to load post for editing", err);
            alert('Failed to load post');
        }
    }

    async function handlePostFormSubmit(e) {
        e.preventDefault();
        
        const id = elements.postInputs.id.value;
        const isEdit = !!id;
        
        // Parse tags from comma-separated string
        const tagsString = elements.postInputs.tags.value.trim();
        const tags = tagsString ? tagsString.split(',').map(t => t.trim()).filter(t => t) : [];
        
        const postData = {
            title: elements.postInputs.title.value.trim(),
            subtitle: elements.postInputs.subtitle.value.trim(),
            category: elements.postInputs.category.value,
            tags: tags,
            reading_time: parseInt(elements.postInputs.readingTime.value) || 0,
            content: elements.postInputs.content.value.trim(),
            published: elements.postInputs.published.checked
        };
        
        setPostStatus('Saving...', 'neutral');
        elements.postSaveBtn.disabled = true;
        
        try {
            const url = isEdit ? `/api/text-posts/${id}` : '/api/text-posts';
            const method = isEdit ? 'PUT' : 'POST';
            
            const res = await fetch(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(postData)
            });
            
            const json = await res.json();
            
            if (res.ok) {
                showPostStatus(isEdit ? 'Post updated!' : 'Post created!', 'success');
                setTimeout(() => {
                    closePostModal();
                    loadPosts(); // Refresh post list
                }, 1000);
            } else {
                throw new Error(json.error || 'Operation failed');
            }
        } catch (err) {
            showPostStatus(err.message, 'error');
        } finally {
            elements.postSaveBtn.disabled = false;
        }
    }

    async function deletePost(id) {
        if(!confirm('Permanently delete this post?')) return;
        
        try {
            const res = await fetch(`/api/text-posts/${id}`, { method: 'DELETE' });
            if (res.ok) {
                loadPosts();
            } else {
                alert('Failed to delete post');
            }
        } catch (err) {
            console.error(err);
            alert('Failed to delete post');
        }
    }

    function resetPostForm() {
        elements.postForm.reset();
        elements.postInputs.id.value = '';
        elements.postInputs.content.dispatchEvent(new Event('input')); // Clear preview
        setPostStatus('', 'neutral');
    }

    function setPostStatus(msg, type) {
        elements.postStatus.textContent = msg;
        elements.postStatus.style.color = type === 'error' ? 'var(--error)' : type === 'success' ? 'var(--success)' : 'var(--muted)';
    }

    function showPostStatus(msg, type) {
        setPostStatus(msg, type);
        setTimeout(() => setPostStatus('', 'neutral'), 3000);
    }
});