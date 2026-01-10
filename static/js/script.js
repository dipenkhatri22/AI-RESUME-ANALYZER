/* --- USER LOGIC --- */

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

    // 3. Score Breakdown
    if (data.breakdown) {
        clone.querySelector('.data-total-score').textContent = data.score;
        clone.querySelector('.data-total-progress').style.width = data.score + '%';
        
        const skillScore = data.breakdown.skills || 0;
        clone.querySelector('.data-skills-score').textContent = skillScore;
        clone.querySelector('.data-skills-bar').style.width = (skillScore / 40 * 100) + '%';

        const eduScore = data.breakdown.education || 0;
        clone.querySelector('.data-edu-score').textContent = eduScore;
        clone.querySelector('.data-edu-bar').style.width = (eduScore / 30 * 100) + '%';

        const expScore = data.breakdown.experience || 0;
        clone.querySelector('.data-exp-score').textContent = expScore;
        clone.querySelector('.data-exp-bar').style.width = (expScore / 30 * 100) + '%';
    } else {
        // Fallback for old data
        clone.querySelector('.data-score-display').textContent = data.score + '/100';
        const progressBar = clone.querySelector('.data-progress');
        progressBar.style.width = data.score + '%';
        progressBar.setAttribute('aria-valuenow', data.score);
        
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

    const coursesHtml = data.rec_courses.map(c => `<li><a href="${c[1]}" target="_blank" class="text-decoration-none text-dark">▶ ${c[0]}</a></li>`).join('');
    clone.querySelector('.data-rec-courses').innerHTML = coursesHtml;

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
    const presentList = clone.getElementById('present-list');
    const missingList = clone.getElementById('missing-list');
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

/* --- ADMIN LOGIC --- */

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
        document.getElementById('login-error').classList.remove('d-none');
    }
}

function logout() {
    window.location.href = '/admin';
}

async function loadDashboardData() {
    const res = await fetch('/api/data');
    const data = await res.json();

    const tbody = document.getElementById('user-table-body');
    tbody.innerHTML = data.map(row => `
        <tr>
            <td>${row[1]}</td>
            <td>${row[2]}</td>
            <td><span class="badge bg-${row[3] > 50 ? 'success' : 'danger'}">${row[3]}</span></td>
            <td>${row[6]}</td>
            <td>${row[7]}</td>
            <td class="small text-muted">${row[4]}</td>
        </tr>
    `).join('');

    const fields = {};
    const levels = {};
    data.forEach(row => {
        fields[row[6]] = (fields[row[6]] || 0) + 1;
        levels[row[7]] = (levels[row[7]] || 0) + 1;
    });

    renderChart('fieldChart', Object.keys(fields), Object.values(fields));
    renderChart('levelChart', Object.keys(levels), Object.values(levels));
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

/* --- GENERATOR LOGIC --- */

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
        document.getElementById('genAnalysisResult').style.display = 'block';
        document.getElementById('gen_res_score').textContent = result.score;
        document.getElementById('gen_res_field').textContent = result.field;
        const skillsContainer = document.getElementById('gen_res_skills');
        skillsContainer.innerHTML = ''; 
        if (result.rec_skills) {
            result.rec_skills.forEach(skill => {
                const span = document.createElement('span');
                span.className = 'badge bg-light text-dark border';
                span.textContent = skill;
                skillsContainer.appendChild(span);
            });
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

document.addEventListener("DOMContentLoaded", function() {
    const fieldChart = document.getElementById('fieldChart');
    if (fieldChart) loadDashboardData();
});

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

    // Prepare FormData
    const formData = new FormData();
    formData.append('job_description', jdInput.value);
    
    // Append all selected files with the key 'resumes'
    for (const file of fileInput.files) {
        formData.append('resumes', file);
    }

    // UI Updates
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
        
        // Highlight Top Candidate
        let rowClass = '';
        let badgeClass = 'bg-secondary';
        
        if (rank === 1) {
            rowClass = 'table-success'; // Green background for winner
            badgeClass = 'bg-success';
        } else if (candidate.score > 50) {
            badgeClass = 'bg-primary';
        } else {
            badgeClass = 'bg-danger';
        }

        // Skills Tags
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