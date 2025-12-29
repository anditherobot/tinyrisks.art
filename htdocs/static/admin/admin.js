// Admin Panel JavaScript
// Handles snippet management, World Building prompts, and asset uploads

document.addEventListener('DOMContentLoaded', () => {
  // Initialize all admin features
  initSnippetManager();
  initWorldBuildingFeatures();
});

// ============================================================================
// Snippet Management (existing functionality)
// ============================================================================

function initSnippetManager() {
  const snippetForm = document.getElementById('snippetForm');
  const refreshBtn = document.getElementById('refreshBtn');
  const buildBtn = document.getElementById('buildBtn');

  if (snippetForm) {
    snippetForm.addEventListener('submit', handleSnippetSubmit);
  }

  if (refreshBtn) {
    refreshBtn.addEventListener('click', loadSnippets);
  }

  if (buildBtn) {
    buildBtn.addEventListener('click', buildSite);
  }

  // Load snippets on page load
  loadSnippets();
}

async function handleSnippetSubmit(e) {
  e.preventDefault();

  const formData = new FormData(e.target);
  const data = {
    title: formData.get('title'),
    content: formData.get('content'),
    tags: formData.get('tags')?.split(',').map(t => t.trim()).filter(Boolean) || []
  };

  try {
    const response = await fetch('/api/snippets', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    if (response.ok) {
      showNotification('Post created successfully!', 'success');
      e.target.reset();
      loadSnippets();
    } else {
      throw new Error('Failed to create post');
    }
  } catch (error) {
    showNotification('Error creating post: ' + error.message, 'error');
  }
}

async function loadSnippets() {
  const container = document.getElementById('snippetsList');
  if (!container) return;

  try {
    const response = await fetch('/api/snippets');
    const snippets = await response.json();

    if (snippets.length === 0) {
      container.innerHTML = '<p class="loading">No posts yet. Create your first one!</p>';
      return;
    }

    container.innerHTML = snippets.map(snippet => `
      <div class="snippet-item">
        <div class="snippet-header">
          <div>
            <h3 class="snippet-title">${escapeHtml(snippet.title)}</h3>
            <div class="snippet-meta">${new Date(snippet.created_at).toLocaleDateString()}</div>
          </div>
          <button class="btn-delete" onclick="deleteSnippet('${snippet.id}')">Delete</button>
        </div>
        <div class="snippet-content">${escapeHtml(snippet.content)}</div>
        ${snippet.tags?.length ? `
          <div class="snippet-tags">
            ${snippet.tags.map(tag => `<span class="tag">${escapeHtml(tag)}</span>`).join('')}
          </div>
        ` : ''}
      </div>
    `).join('');
  } catch (error) {
    container.innerHTML = '<p class="loading" style="color:var(--error)">Error loading posts</p>';
  }
}

async function deleteSnippet(id) {
  if (!confirm('Delete this post?')) return;

  try {
    const response = await fetch(`/api/snippets/${id}`, { method: 'DELETE' });
    if (response.ok) {
      showNotification('Post deleted', 'success');
      loadSnippets();
    } else {
      throw new Error('Failed to delete');
    }
  } catch (error) {
    showNotification('Error deleting post', 'error');
  }
}

async function buildSite() {
  showNotification('Building site...', 'success');
  try {
    const response = await fetch('/api/build', { method: 'POST' });
    if (response.ok) {
      showNotification('Site built successfully!', 'success');
    } else {
      throw new Error('Build failed');
    }
  } catch (error) {
    showNotification('Build error: ' + error.message, 'error');
  }
}

// ============================================================================
// World Building Features
// ============================================================================

function initWorldBuildingFeatures() {
  // Copy-to-clipboard functionality for prompts
  const copyButtons = document.querySelectorAll('.btn-copy-prompt');
  copyButtons.forEach(btn => {
    btn.addEventListener('click', handleCopyPrompt);
  });

  // Upload form enhancements
  const uploadForms = document.querySelectorAll('.wb-upload-form');
  uploadForms.forEach(form => {
    enhanceUploadForm(form);
  });

  // File input visual feedback
  const fileInputs = document.querySelectorAll('.wb-file-input');
  fileInputs.forEach(input => {
    input.addEventListener('change', handleFileInputChange);
  });
}

async function handleCopyPrompt(e) {
  const button = e.currentTarget;
  const promptText = button.getAttribute('data-prompt');

  try {
    await navigator.clipboard.writeText(promptText);

    // Visual feedback
    const originalText = button.textContent;
    button.textContent = 'Copied!';
    button.style.background = 'var(--success)';
    button.style.color = 'white';
    button.style.borderColor = 'var(--success)';

    setTimeout(() => {
      button.textContent = originalText;
      button.style.background = '';
      button.style.color = '';
      button.style.borderColor = '';
    }, 2000);

    showNotification('Prompt copied to clipboard!', 'success');
  } catch (error) {
    showNotification('Failed to copy prompt', 'error');
    console.error('Copy failed:', error);
  }
}

function enhanceUploadForm(form) {
  const fileInput = form.querySelector('input[type="file"]');
  const submitButton = form.querySelector('button[type="submit"]');

  if (!fileInput || !submitButton) return;

  // Add drag-and-drop functionality
  const dropZone = createDropZone(fileInput);
  fileInput.parentElement.appendChild(dropZone);
  fileInput.style.display = 'none';

  dropZone.addEventListener('click', () => fileInput.click());

  dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = 'var(--accent)';
    dropZone.style.background = 'rgba(214,167,108,.1)';
  });

  dropZone.addEventListener('dragleave', () => {
    dropZone.style.borderColor = '';
    dropZone.style.background = '';
  });

  dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.style.borderColor = '';
    dropZone.style.background = '';

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      fileInput.files = files;
      updateDropZoneText(dropZone, files[0]);
    }
  });

  // Add progress tracking to form submission
  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(form);
    const file = fileInput.files[0];

    if (!file) {
      showNotification('Please select a file', 'error');
      return;
    }

    // Show progress
    submitButton.disabled = true;
    submitButton.textContent = 'Uploading...';

    try {
      const response = await fetch(form.action, {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        showNotification('Upload successful!', 'success');
        // Reload page to show updated asset
        setTimeout(() => window.location.reload(), 1500);
      } else {
        const error = await response.text();
        throw new Error(error || 'Upload failed');
      }
    } catch (error) {
      showNotification('Upload error: ' + error.message, 'error');
      submitButton.disabled = false;
      submitButton.textContent = submitButton.textContent.replace('Uploading...', 'Upload');
    }
  });
}

function createDropZone(fileInput) {
  const dropZone = document.createElement('div');
  dropZone.className = 'wb-drop-zone';
  dropZone.style.cssText = `
    border: 2px dashed var(--line);
    padding: 2rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s;
    background: #0e1219;
    color: var(--muted);
    font-size: 0.9rem;
  `;

  const accept = fileInput.getAttribute('accept') || '';
  const fileType = accept.includes('image') ? 'image' :
                   accept.includes('video') ? 'video' :
                   accept.includes('audio') ? 'audio' : 'file';

  dropZone.innerHTML = `
    <div style="margin-bottom: 0.5rem; font-size: 2rem; color: var(--accent);">📁</div>
    <div>Click to select ${fileType} or drag and drop here</div>
    <div style="font-size: 0.75rem; margin-top: 0.5rem; color: var(--muted);">
      Accepted: ${accept || 'any file'}
    </div>
  `;

  return dropZone;
}

function updateDropZoneText(dropZone, file) {
  const icon = file.type.includes('image') ? '🖼️' :
               file.type.includes('video') ? '🎬' :
               file.type.includes('audio') ? '🎵' : '📄';

  dropZone.innerHTML = `
    <div style="margin-bottom: 0.5rem; font-size: 2rem;">${icon}</div>
    <div style="color: var(--accent);">${escapeHtml(file.name)}</div>
    <div style="font-size: 0.75rem; margin-top: 0.5rem; color: var(--muted);">
      ${formatFileSize(file.size)} • Click to change
    </div>
  `;
}

function handleFileInputChange(e) {
  const input = e.target;
  const file = input.files[0];

  if (!file) return;

  // Find the drop zone sibling if it exists
  const dropZone = input.parentElement.querySelector('.wb-drop-zone');
  if (dropZone) {
    updateDropZoneText(dropZone, file);
  }
}

// ============================================================================
// Utility Functions
// ============================================================================

function showNotification(message, type = 'success') {
  const notification = document.getElementById('notification');
  if (!notification) return;

  notification.textContent = message;
  notification.className = `notification ${type} show`;

  setTimeout(() => {
    notification.classList.remove('show');
  }, 3000);
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}
