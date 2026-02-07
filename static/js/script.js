/* =========================================
   USER LOGIC (Resume Upload & Results)
   ========================================= */

function toggleJobDescription() {
    const container = document.getElementById('job-description-container');
    if (container.classList.contains('d-none')) {
        container.classList.remove('d-none');
    } else {
        container.classList.add('d-none');
    }
}

async function uploadResume() {
    const fileInput = document.getElementById('resumeFile');
    const jobDescInput = document.getElementById('jobDescription');
    
    if (fileInput.files.length === 0) {
        alert("Please select a PDF file first.");
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    if (jobDescInput && jobDescInput.value.trim() !== "") {
        formData.append('job_description', jobDescInput.value);
    }

    document.getElementById('loader').classList.remove('d-none');
    document.getElementById('result-container').classList.add('d-none');

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        if (response.ok) {
            displayResults(data);
        } else {
            alert(data.error || "Error analyzing resume");
        }
    } catch (error) {
        console.error('Error:', error);
        alert("Server Error");
    } finally {
        document.getElementById('loader').classList.add('d-none');
    }
}

function displayResults(data) {
    const container = document.getElementById('result-container');
    const template = document.getElementById('result-template');
    const clone = template.content.cloneNode(true);

    // 1. Basic Info
    clone.querySelector('.data-name').textContent = data.name;
    clone.querySelector('.data-email').textContent = data.email;
    clone.querySelector('.data-level').textContent = data.level;
    clone.querySelector('.data-field').textContent = data.field;

    // 2. Skills
    const skillsDiv = clone.querySelector('.data-skills');
    if (data.skills && Array.isArray(data.skills)) {
        data.skills.forEach(s => {
            const span = document.createElement('span');
            span.className = 'badge bg-light text-dark border';
            span.textContent = s;
            skillsDiv.appendChild(span);
        });
    }

    // 3. Score Breakdown (Updated to include Semantic Fit)
    if (data.breakdown) {
        clone.querySelector('.data-total-score').textContent = data.score;
        clone.querySelector('.data-total-progress').style.width = data.score + '%';
        
        // Skills (Max 40)
        const skillScore = data.breakdown.skills || 0;
        const skillBar = clone.querySelector('.data-skills-bar');
        if(skillBar) skillBar.style.width = (skillScore / 40 * 100) + '%';
        const skillTxt = clone.querySelector('.data-skills-score');
        if(skillTxt) skillTxt.textContent = skillScore;

        // Education (Max 30)
        const eduScore = data.breakdown.education || 0;
        const eduBar = clone.querySelector('.data-edu-bar');
        if(eduBar) eduBar.style.width = (eduScore / 30 * 100) + '%';
        const eduTxt = clone.querySelector('.data-edu-score');
        if(eduTxt) eduTxt.textContent = eduScore;

        // Experience (Max 20 - Updated logic)
        const expScore = data.breakdown.experience || 0;
        const expBar = clone.querySelector('.data-exp-bar');
        if(expBar) expBar.style.width = (expScore / 20 * 100) + '%'; // Updated denominator from 30 to 20
        const expTxt = clone.querySelector('.data-exp-score');
        if(expTxt) expTxt.textContent = expScore;

        // NEW: Semantic Fit (Max 10)
        const semanticScore = data.breakdown.semantic_fit || 0;
        const semanticBar = clone.querySelector('.data-semantic-bar');
        if(semanticBar) {
            semanticBar.style.width = (semanticScore / 10 * 100) + '%';
            semanticBar.parentElement.style.display = 'block'; // Ensure it's visible
        }
        const semanticTxt = clone.querySelector('.data-semantic-score');
        if(semanticTxt) semanticTxt.textContent = semanticScore;

    } else {
        // Fallback for old data structure
        clone.querySelector('.data-score-display').textContent = data.score + '/100';
        const progressBar = clone.querySelector('.data-progress');
        if(progressBar) {
            progressBar.style.width = data.score + '%';
            progressBar.setAttribute('aria-valuenow', data.score);
        }
        
        const breakdownDiv = clone.querySelector('.text-start.small'); 
        if(breakdownDiv) breakdownDiv.style.display = 'none';
    }

    // 4. Recommendations
    const recSkillsDiv = clone.querySelector('.data-rec-skills');
    if (data.rec_skills && Array.isArray(data.rec_skills)) {
        data.rec_skills.forEach(s => {
            const span = document.createElement('span');
            span.className = 'badge bg-primary text-light';
            span.textContent = s;
            recSkillsDiv.appendChild(span);
        });
    }

    if (data.rec_courses) {
        const coursesHtml = data.rec_courses.map(c => `<li><a href="${c[1]}" target="_blank" class="text-decoration-none text-dark">▶ ${c[0]}</a></li>`).join('');
        const coursesDiv = clone.querySelector('.data-rec-courses');
        if(coursesDiv) coursesDiv.innerHTML = coursesHtml;
    }

    // 5. Tips
    renderResumeTips(clone, data.score);

    container.innerHTML = '';
    container.appendChild(clone);
    container.classList.remove('d-none');
}

function renderResumeTips(clone, score) {
    const sections = {
        'Objective / Summary': { score: 20 },
        'Declaration': { score: 20 },
        'Hobbies / Interests': { score: 20 },
        'Achievements': { score: 20 },
        'Projects': { score: 20 }
    };
    const presentList = clone.querySelector('#present-list'); // Use querySelector for safety
    const missingList = clone.querySelector('#missing-list');
    
    if(!presentList || !missingList) return;

    presentList.innerHTML = '';
    missingList.innerHTML = '';

    let calculatedSections = 0;

    for (const [name, info] of Object.entries(sections)) {
        calculatedSections += info.score;
        if (calculatedSections <= score) {
            presentList.innerHTML += `<li class="text-success">✅ <strong>${name}</strong></li>`;
        } else {
            missingList.innerHTML += `<li class="text-danger">❌ <strong>${name}</strong></li>`;
        }
    }
}

/* =========================================
   ADMIN LOGIC (Dashboard, Privacy, Analytics)
   ========================================= */

async function loginAdmin() {
    const u = document.getElementById('adminUser');
    const p = document.getElementById('adminPass');
    const res = await fetch('/api/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username: u.value, password: p.value})
    });
    if (res.ok) {
        window.location.href = '/dashboard';
    } else {
        const err = document.getElementById('login-error');
        if(err) err.classList.remove('d-none');
    }
}

function togglePassword(el) {
    const pass = document.getElementById('adminPass');
    const icon = el.querySelector('i');

    if (pass.type === 'password') {
        pass.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        pass.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}


function logout() {
    window.location.href = '/admin';
}

async function loadDashboardData() {
    // Check Privacy Toggle
    const privacyToggle = document.getElementById('privacyToggle');
    const isPrivacy = privacyToggle ? privacyToggle.checked : false;
    const url = isPrivacy ? '/api/data?privacy=true' : '/api/data';

    try {
        const res = await fetch(url);
        const data = await res.json();

        const tbody = document.getElementById('user-table-body');
        if(!tbody) return;

        // Updated: Added the Action column at the end
        tbody.innerHTML = data.map(row => `
            <tr>
                <td>${row[1]}</td>
                <td>${row[2]}</td>
                <td><span class="badge bg-${row[3] > 50 ? 'success' : 'danger'}">${row[3]}</span></td>
                <td>${row[6]}</td>
                <td>${row[7]}</td>
                <td class="small text-muted">${row[4]}</td>
                <td>
                    <button onclick="deleteCandidate(${row[0]})" class="btn btn-sm btn-danger">Delete</button>
                </td>
            </tr>
        `).join('');

        // Chart Logic (Field & Level)
        const fields = {};
        const levels = {};
        data.forEach(row => {
            fields[row[6]] = (fields[row[6]] || 0) + 1;
            levels[row[7]] = (levels[row[7]] || 0) + 1;
        });

        const fieldChartCanvas = document.getElementById('fieldChart');
        const levelChartCanvas = document.getElementById('levelChart');

        if(fieldChartCanvas) renderChart('fieldChart', Object.keys(fields), Object.values(fields));
        if(levelChartCanvas) renderChart('levelChart', Object.keys(levels), Object.values(levels));

        // Load Analytics
        loadAnalytics();

    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

/* --- NEW: DELETE CANDIDATE FUNCTION --- */
async function deleteCandidate(id) {
    if (!confirm("Are you sure you want to delete this candidate? This cannot be undone.")) {
        return;
    }

    try {
        const response = await fetch(`/api/candidate/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            // Reload the dashboard data to remove the row from view
            loadDashboardData(); 
        } else {
            alert("Error deleting candidate.");
        }
    } catch (error) {
        console.error('Error:', error);
        alert("Server Error");
    }
}

function renderChart(canvasId, labels, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{ data: data, backgroundColor: ['#3498db', '#e74c3c', '#2ecc71', '#f1c40f', '#9b59b6', '#34495e'] }]
        },
        options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
    });
}

// NEW: Analytics Functions
async function loadAnalytics() {
    // 1. Skills Gap Chart
    try {
        const res = await fetch('/api/analytics/skills_gap');
        const skillsData = await res.json();
        renderSkillsChart(skillsData);
    } catch (e) { console.log("Skills analytics not available"); }

    // 2. High Potential List
    try {
        const res = await fetch('/api/analytics/high_potential');
        const hpData = await res.json();
        renderHighPotential(hpData);
    } catch (e) { console.log("High Potential data not available"); }
}

function renderSkillsChart(data) {
    const ctx = document.getElementById('skillsChart');
    if (!ctx) return;

    const labels = data.map(item => item.skill);
    const counts = data.map(item => item.count);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: '# of Candidates',
                data: counts,
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: { y: { beginAtZero: true } }
        }
    });
}

function renderHighPotential(data) {
    const list = document.getElementById('highPotentialList');
    if (!list) return;
    
    list.innerHTML = '';
    if (data.length === 0) {
        list.innerHTML = '<li>No rising talent found yet.</li>';
        return;
    }

    data.forEach(candidate => {
        const li = document.createElement('li');
        li.className = 'high-potential-item';
        li.innerHTML = `
            <span><strong>${candidate.name}</strong> <small>(${candidate.field})</small></span>
            <span class="score-badge">${candidate.score}</span>
        `;
        list.appendChild(li);
    });
}

/* =========================================
   GENERATOR LOGIC (Including AI Optimization)
   ========================================= */

async function handleGeneratorUpload() {
    const fileInput = document.getElementById('fileInput');
    const loader = document.querySelector('.gen-loader');
    if (!fileInput || fileInput.files.length === 0) return;
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    loader.style.display = 'block';

    try {
        const response = await fetch('/api/parse_for_generator', { method: 'POST', body: formData });
        const data = await response.json();
        
        document.getElementById('gen_name').value = data.name || '';
        document.getElementById('gen_email').value = data.email || '';
        document.getElementById('gen_mobile').value = data.mobile || '';
        document.getElementById('gen_summary').value = data.summary || '';
        document.getElementById('gen_experience').value = data.experience || '';
        document.getElementById('gen_education').value = data.education || '';
        document.getElementById('gen_projects').value = data.projects || '';
        document.getElementById('gen_skills').value = data.skills || '';
        
        if (!data.error) analyzeGeneratorResume();
    } catch (error) { console.error("Error:", error); }
    finally { loader.style.display = 'none'; }
}

async function analyzeGeneratorResume() {
    const payload = {
        name: document.getElementById('gen_name').value,
        email: document.getElementById('gen_email').value,
        mobile: document.getElementById('gen_mobile').value,
        summary: document.getElementById('gen_summary').value,
        experience: document.getElementById('gen_experience').value,
        education: document.getElementById('gen_education').value,
        projects: document.getElementById('gen_projects').value,
        skills: document.getElementById('gen_skills').value
    };
    try {
        const response = await fetch('/api/analyze_updated_resume', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const result = await response.json();
        const resBox = document.getElementById('genAnalysisResult');
        if(resBox) resBox.style.display = 'block';
        
        const scoreEl = document.getElementById('gen_res_score');
        if(scoreEl) scoreEl.textContent = result.score;

        const fieldEl = document.getElementById('gen_res_field');
        if(fieldEl) fieldEl.textContent = result.field;

        const skillsContainer = document.getElementById('gen_res_skills');
        if(skillsContainer) {
            skillsContainer.innerHTML = ''; 
            if (result.rec_skills) {
                result.rec_skills.forEach(skill => {
                    const span = document.createElement('span');
                    span.className = 'badge bg-light text-dark border';
                    span.textContent = skill;
                    skillsContainer.appendChild(span);
                });
            }
        }
    } catch (error) { console.error("Analysis error", error); }
}

async function downloadGeneratorPDF() {
    const payload = {
        name: document.getElementById('gen_name').value,
        email: document.getElementById('gen_email').value,
        mobile: document.getElementById('gen_mobile').value,
        summary: document.getElementById('gen_summary').value,
        experience: document.getElementById('gen_experience').value,
        education: document.getElementById('gen_education').value,
        projects: document.getElementById('gen_projects').value,
        skills: document.getElementById('gen_skills').value
    };
    try {
        const response = await fetch('/api/download_updated_resume', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!response.ok) throw new Error('PDF Generation failed');
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        const safeName = payload.name.replace(/[^a-z0-9]/gi, '_').toLowerCase();
        a.download = `${safeName}_new_resume.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (error) { alert("Error generating PDF: " + error.message); }
}

// NEW: AI Optimization Function
async function optimizeField(fieldId) {
    const textarea = document.getElementById(fieldId);
    const originalText = textarea.value;
    
    // Find the button that called this function
    const btn = document.querySelector(`button[onclick="optimizeField('${fieldId}')"]`);

    if (!originalText.trim()) {
        alert("Please enter some text first!");
        return;
    }

    // UI Feedback
    const originalBtnText = btn.innerHTML;
    btn.innerHTML = "⏳ Thinking...";
    btn.disabled = true;

    try {
        const response = await fetch('/api/llm/optimize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: originalText })
        });
        const result = await response.json();
        
        if (result.optimized) {
            textarea.value = result.optimized;
            // Trigger analysis update to reflect new score
            analyzeGeneratorResume();
        } else {
            alert("Optimization failed.");
        }
    } catch (error) {
        console.error(error);
        alert("Error connecting to AI server.");
    } finally {
        btn.innerHTML = originalBtnText;
        btn.disabled = false;
    }
}

/* =========================================
   SHORTLIST LOGIC
   ========================================= */

async function processShortlist() {
    const fileInput = document.getElementById('resumeFiles');
    const jdInput = document.getElementById('jobDesc');
    const loader = document.getElementById('loader');
    const resultsSection = document.getElementById('results-section');
    const resultsBody = document.getElementById('results-body');

    if (fileInput.files.length === 0) {
        alert("Please select at least one resume PDF.");
        return;
    }

    const formData = new FormData();
    formData.append('job_description', jdInput.value);
    for (const file of fileInput.files) {
        formData.append('resumes', file);
    }

    loader.classList.remove('d-none');
    resultsSection.classList.add('d-none');
    resultsBody.innerHTML = '';

    try {
        const response = await fetch('/api/shortlist', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();

        if (response.ok) {
            renderShortlistTable(data);
            resultsSection.classList.remove('d-none');
        } else {
            alert("Error processing files.");
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Server Error");
    } finally {
        loader.classList.add('d-none');
    }
}

function renderShortlistTable(candidates) {
    const tbody = document.getElementById('results-body');
    tbody.innerHTML = '';

    if (candidates.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">No valid resumes found.</td></tr>';
        return;
    }

    candidates.forEach((candidate, index) => {
        const rank = index + 1;
        let rowClass = '';
        let badgeClass = 'bg-secondary';
        
        if (rank === 1) {
            rowClass = 'table-success';
            badgeClass = 'bg-success';
        } else if (candidate.score > 50) {
            badgeClass = 'bg-primary';
        } else {
            badgeClass = 'bg-danger';
        }

        const skillsHtml = candidate.skills 
            ? candidate.skills.slice(0, 3).map(s => `<span class="badge bg-light text-dark border me-1">${s}</span>`).join('') 
            : 'N/A';

        const tr = document.createElement('tr');
        tr.className = rowClass;
        tr.innerHTML = `
            <td class="fw-bold">#${rank} ${rank === 1 ? '🏆' : ''}</td>
            <td>
                <div class="fw-bold">${candidate.name}</div>
                <small class="text-muted">${candidate.filename}</small>
            </td>
            <td>${candidate.email}</td>
            <td>
                <div class="d-flex align-items-center">
                    <div class="progress flex-grow-1 me-2" style="height: 20px;">
                        <div class="progress-bar ${badgeClass}" style="width: ${candidate.score}%">${candidate.score}</div>
                    </div>
                </div>
            </td>
            <td><small>${skillsHtml}</small></td>
            <td>
                <button class="btn btn-sm btn-outline-primary" onclick="alert('Selected: ${candidate.name}')">Select</button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

/* =========================================
   INITIALIZATION
   ========================================= */

document.addEventListener("DOMContentLoaded", function() {
    // Check if we are on the dashboard page
    const fieldChart = document.getElementById('fieldChart');
    if (fieldChart) {
        loadDashboardData();
        
        // Add event listener for Privacy Toggle
        const privacyToggle = document.getElementById('privacyToggle');
        if(privacyToggle) {
            privacyToggle.addEventListener('change', loadDashboardData);
        }
    }
});