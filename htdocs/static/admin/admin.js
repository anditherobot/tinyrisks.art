document.addEventListener('DOMContentLoaded', () => {
    // --- State & Elements ---
    const elements = {
        tabs: {
            create: document.getElementById('tab-create'),
            library: document.getElementById('tab-library')
        },
        panels: {
            create: document.getElementById('panel-create'),
            library: document.getElementById('panel-library')
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
            library: document.getElementById('libraryGrid')
        },
        btns: {
            save: document.getElementById('saveBtn'),
            cancel: document.getElementById('cancelBtn'),
            logout: document.getElementById('logoutBtn')
        },
        status: document.getElementById('statusMsg')
    };

    // --- Init ---
    loadData();
    setupMarkdownPreview();
    
    // --- Event Listeners ---
    elements.btns.logout.addEventListener('click', handleLogout);
    elements.form.addEventListener('submit', handleFormSubmit);
    elements.btns.cancel.addEventListener('click', resetForm);
    elements.inputs.images.addEventListener('change', updateFileStatus);

    // Global access for onclick handlers in HTML
    window.switchTab = switchTab;
    window.editItem = editItem;
    window.deleteItem = deleteItem;

    // --- Core Functions ---

    function switchTab(tabName) {
        // Toggle Buttons
        Object.values(elements.tabs).forEach(btn => btn.classList.remove('active'));
        if(elements.tabs[tabName]) elements.tabs[tabName].classList.add('active');

        // Toggle Panels
        Object.values(elements.panels).forEach(p => p.classList.remove('active'));
        if(elements.panels[tabName]) elements.panels[tabName].classList.add('active');

        if(tabName === 'library') loadData(); // Refresh data when opening library
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
});