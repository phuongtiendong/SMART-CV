// API Base URL
const API_BASE = '/api';

// State
let currentJobId = null;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    initJobModal();
    loadJobs();
    loadRanking();
    
    // Setup form handlers
    document.getElementById('upload-form').addEventListener('submit', handleUploadCV);
    document.getElementById('job-form').addEventListener('submit', handleSaveJob);
    document.getElementById('ranking-job-select').addEventListener('change', () => {
        loadRanking(document.getElementById('ranking-job-select').value);
    });
});

// Tab Management
function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            const tabName = button.dataset.tab;
            
            // Update buttons
            tabButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            // Update content
            tabContents.forEach(content => content.classList.remove('active'));
            document.getElementById(`${tabName}-tab`).classList.add('active');
            
            // Load data when switching tabs
            if (tabName === 'ranking') {
                loadRanking();
            } else if (tabName === 'jobs') {
                loadJobs();
            }
        });
    });
}

// Job Management
function loadJobs() {
    showLoading('jobs-list');
    
    fetch(`${API_BASE}/jobs`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                renderJobs(data.data);
                updateJobSelects(data.data);
            } else {
                showError('Failed to load jobs: ' + data.error);
            }
        })
        .catch(err => {
            showError('Error loading jobs: ' + err.message);
        })
        .finally(() => {
            hideLoading('jobs-list');
        });
}

function renderJobs(jobs) {
    const container = document.getElementById('jobs-list');
    
    if (jobs.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📋</div>
                <p>No jobs created yet. Click "Create New Job" to get started.</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = jobs.map(job => `
        <div class="job-card">
            <div class="job-card-header">
                <div>
                    <div class="job-card-title">${escapeHtml(job.title)}</div>
                    <div class="job-card-meta">Created: ${formatDate(job.created_at)}</div>
                </div>
                <div class="job-card-actions">
                    <button class="btn btn-primary btn-small" onclick="editJob(${job.id})">Edit</button>
                    <button class="btn btn-danger btn-small" onclick="deleteJob(${job.id})">Delete</button>
                </div>
            </div>
            <div class="job-card-description">${escapeHtml(job.description.substring(0, 200))}${job.description.length > 200 ? '...' : ''}</div>
        </div>
    `).join('');
}

function updateJobSelects(jobs) {
    const selects = ['job-select', 'ranking-job-select'];
    
    selects.forEach(selectId => {
        const select = document.getElementById(selectId);
        const currentValue = select.value;
        
        // Clear options except first one
        select.innerHTML = selectId === 'job-select' 
            ? '<option value="">-- Select a job --</option>'
            : '<option value="">All Jobs</option>';
        
        // Add job options
        jobs.forEach(job => {
            const option = document.createElement('option');
            option.value = job.id;
            option.textContent = job.title;
            select.appendChild(option);
        });
        
        // Restore previous selection if still valid
        if (currentValue) {
            select.value = currentValue;
        }
    });
}

function editJob(jobId) {
    fetch(`${API_BASE}/jobs/${jobId}`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                const job = data.data;
                document.getElementById('job-id').value = job.id;
                document.getElementById('job-title').value = job.title;
                document.getElementById('job-description').value = job.description;
                document.getElementById('modal-title').textContent = 'Edit Job';
                openJobModal();
            } else {
                showError('Failed to load job: ' + data.error);
            }
        })
        .catch(err => {
            showError('Error loading job: ' + err.message);
        });
}

function deleteJob(jobId) {
    if (!confirm('Are you sure you want to delete this job? All associated CV analyses will also be deleted.')) {
        return;
    }
    
    fetch(`${API_BASE}/jobs/${jobId}`, {
        method: 'DELETE'
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showSuccess('Job deleted successfully');
                loadJobs();
                loadRanking();
            } else {
                showError('Failed to delete job: ' + data.error);
            }
        })
        .catch(err => {
            showError('Error deleting job: ' + err.message);
        });
}

// Job Modal
function initJobModal() {
    const modal = document.getElementById('job-modal');
    const createBtn = document.getElementById('create-job-btn');
    const closeBtn = document.querySelector('.close');
    const cancelBtn = document.getElementById('cancel-job-btn');
    
    createBtn.addEventListener('click', () => {
        document.getElementById('job-id').value = '';
        document.getElementById('job-title').value = '';
        document.getElementById('job-description').value = '';
        document.getElementById('modal-title').textContent = 'Create New Job';
        clearErrors();
        openJobModal();
    });
    
    closeBtn.addEventListener('click', closeJobModal);
    cancelBtn.addEventListener('click', closeJobModal);
    
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeJobModal();
        }
    });
}

function openJobModal() {
    document.getElementById('job-modal').classList.add('active');
}

function closeJobModal() {
    document.getElementById('job-modal').classList.remove('active');
    document.getElementById('job-form').reset();
    clearErrors();
}

function handleSaveJob(e) {
    e.preventDefault();
    
    const jobId = document.getElementById('job-id').value;
    const title = document.getElementById('job-title').value.trim();
    const description = document.getElementById('job-description').value.trim();
    
    // Validation
    clearErrors();
    let hasError = false;
    
    if (!title) {
        showFieldError('job-title-error', 'Title is required');
        hasError = true;
    }
    
    if (!description) {
        showFieldError('job-description-error', 'Description is required');
        hasError = true;
    }
    
    if (hasError) return;
    
    // Show loading
    const spinner = document.getElementById('job-spinner');
    const btnText = document.querySelector('#save-job-btn .btn-text');
    spinner.style.display = 'inline-block';
    btnText.textContent = 'Saving...';
    document.getElementById('save-job-btn').disabled = true;
    
    const url = jobId ? `${API_BASE}/jobs/${jobId}` : `${API_BASE}/jobs`;
    const method = jobId ? 'PUT' : 'POST';
    
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ title, description })
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showSuccess(jobId ? 'Job updated successfully' : 'Job created successfully');
                closeJobModal();
                loadJobs();
            } else {
                showError('Failed to save job: ' + data.error);
            }
        })
        .catch(err => {
            showError('Error saving job: ' + err.message);
        })
        .finally(() => {
            spinner.style.display = 'none';
            btnText.textContent = 'Save';
            document.getElementById('save-job-btn').disabled = false;
        });
}

// CV Upload
function handleUploadCV(e) {
    e.preventDefault();
    
    const jobId = document.getElementById('job-select').value;
    const fileInput = document.getElementById('cv-file');
    const file = fileInput.files[0];
    
    // Validation
    clearErrors();
    let hasError = false;
    
    if (!jobId) {
        showFieldError('job-select-error', 'Please select a job position');
        hasError = true;
    }
    
    if (!file) {
        showFieldError('cv-file-error', 'Please select a PDF file');
        hasError = true;
    } else if (file.type !== 'application/pdf') {
        showFieldError('cv-file-error', 'Please select a valid PDF file');
        hasError = true;
    }
    
    if (hasError) return;
    
    // Show loading
    const spinner = document.getElementById('upload-spinner');
    const btnText = document.querySelector('#upload-btn .btn-text');
    spinner.style.display = 'inline-block';
    btnText.textContent = 'Analyzing...';
    document.getElementById('upload-btn').disabled = true;
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('job_id', jobId);
    
    fetch(`${API_BASE}/cvs/process`, {
        method: 'POST',
        body: formData
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showSuccess('CV analyzed successfully');
                renderCVResult(data.data);
                loadRanking();
            } else {
                showError('Failed to analyze CV: ' + data.error);
            }
        })
        .catch(err => {
            showError('Error analyzing CV: ' + err.message);
        })
        .finally(() => {
            spinner.style.display = 'none';
            btnText.textContent = 'Analyze CV';
            document.getElementById('upload-btn').disabled = false;
        });
}

function renderCVResult(data) {
    const container = document.getElementById('upload-result');
    const info = data.candidate_info;
    const scores = data.scores;
    const reasons = data.reasons;
    
    container.innerHTML = `
        <div class="candidate-info">
            <h3>Candidate Information</h3>
            <div class="info-section">
                <strong>Name:</strong> ${escapeHtml(info.name || 'N/A')}<br>
                <strong>Email:</strong> ${escapeHtml(info.email || 'N/A')}<br>
                <strong>Phone:</strong> ${escapeHtml(info.phone || 'N/A')}<br>
                <strong>Address:</strong> ${escapeHtml(info.address || 'N/A')}
            </div>
        </div>
        
        <div class="score-section">
            ${Object.keys(scores).map(category => `
                <div class="score-card">
                    <h5>${category}</h5>
                    <div class="score-value">${scores[category]}/100</div>
                    <div class="score-reason">${escapeHtml(reasons[category] || 'No reason provided')}</div>
                </div>
            `).join('')}
        </div>
        
        <div class="total-score">
            <div class="total-score-value">${data.total_score.toFixed(1)}</div>
            <div>Total Score</div>
        </div>
    `;
    
    container.classList.add('active');
}

// Ranking
function loadRanking(jobId = '') {
    showLoading('ranking-table-container');
    
    const url = jobId 
        ? `${API_BASE}/cvs/ranking?job_id=${jobId}`
        : `${API_BASE}/cvs/ranking`;
    
    fetch(url)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                renderRanking(data.data);
            } else {
                showError('Failed to load ranking: ' + data.error);
            }
        })
        .catch(err => {
            showError('Error loading ranking: ' + err.message);
        })
        .finally(() => {
            hideLoading('ranking-table-container');
        });
}

function renderRanking(ranking) {
    const container = document.getElementById('ranking-table-container');
    
    if (ranking.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📊</div>
                <p>No CVs analyzed yet. Upload a CV to see rankings.</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = `
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Job Position</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Phone</th>
                    <th>Score</th>
                    <th>Date</th>
                </tr>
            </thead>
            <tbody>
                ${ranking.map((candidate, index) => `
                    <tr>
                        <td>${index + 1}</td>
                        <td>${escapeHtml(candidate.job_title || 'N/A')}</td>
                        <td>${escapeHtml(candidate.name || 'N/A')}</td>
                        <td>${escapeHtml(candidate.email || 'N/A')}</td>
                        <td>${escapeHtml(candidate.phone || 'N/A')}</td>
                        <td>
                            <span class="score-badge ${getScoreClass(candidate.score)}">
                                ${candidate.score ? candidate.score.toFixed(1) : '0.0'}
                            </span>
                        </td>
                        <td>${formatDate(candidate.created_at)}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function getScoreClass(score) {
    if (score >= 70) return 'score-high';
    if (score >= 40) return 'score-medium';
    return 'score-low';
}

// Utility Functions
function showSuccess(message) {
    showMessage(message, 'success');
}

function showError(message) {
    showMessage(message, 'error');
}

function showInfo(message) {
    showMessage(message, 'info');
}

function showMessage(message, type) {
    const container = document.getElementById('message-container');
    const messageEl = document.createElement('div');
    messageEl.className = `message message-${type}`;
    messageEl.textContent = message;
    
    container.appendChild(messageEl);
    
    setTimeout(() => {
        messageEl.style.animation = 'slideInRight 0.3s reverse';
        setTimeout(() => messageEl.remove(), 300);
    }, 3000);
}

function showFieldError(fieldId, message) {
    document.getElementById(fieldId).textContent = message;
}

function clearErrors() {
    document.querySelectorAll('.error-message').forEach(el => {
        el.textContent = '';
    });
}

function showLoading(containerId) {
    const container = document.getElementById(containerId);
    container.innerHTML = '<div class="empty-state"><div class="spinner" style="margin: 0 auto;"></div><p>Loading...</p></div>';
}

function hideLoading(containerId) {
    // Loading will be replaced by actual content
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}
