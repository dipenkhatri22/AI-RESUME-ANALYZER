import os
import re
import io
import time
import datetime
import pandas as pd
import pymysql
import pdfplumber
import spacy
import nltk
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
from transformers import pipeline
from fpdf import FPDF
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# External Data
from Courses import KEYWORDS, SKILLS_DICT, COURSES, JOB_DESCRIPTIONS

# --- CONFIGURATION ---
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'super_secret_key'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- LOAD NLP MODELS ---
print("Loading spaCy model...")
nlp = spacy.load("en_core_web_sm")
print("Loading Hugging Face model...")
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
print("Models loaded!")

# --- DATABASE CONNECTION ---
try:
    connection = pymysql.connect(host='localhost', user='root', password='')
    cursor = connection.cursor()
except Exception as e:
    print(f"DB Connection Error: {e}")
    connection = None
    cursor = None

if connection:
    cursor.execute("CREATE DATABASE IF NOT EXISTS cv")
    cursor.execute("USE cv")
    table_sql = """
    CREATE TABLE IF NOT EXISTS user_data (
        ID INT NOT NULL AUTO_INCREMENT,
        Name varchar(500) NOT NULL,
        Email_ID VARCHAR(500) NOT NULL,
        resume_score VARCHAR(8) NOT NULL,
        Timestamp VARCHAR(50) NOT NULL,
        Page_no VARCHAR(5) NOT NULL,
        Predicted_Field BLOB NOT NULL,
        User_level BLOB NOT NULL,
        Actual_skills BLOB NOT NULL,
        Recommended_skills BLOB NOT NULL,
        Recommended_courses BLOB NOT NULL,
        PRIMARY KEY (ID)
    );
    """
    cursor.execute(table_sql)

# --- HELPER FUNCTIONS ---

def pdf_reader(file):
    text_content = ""
    page_count = 0
    with pdfplumber.open(file) as pdf:
        page_count = len(pdf.pages)
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text: text_content += page_text + "\n"
    if len(text_content.strip()) < 10:
        print("Warning: Very little text extracted.")
    return text_content, page_count

def clean_text_nltk(text):
    try:
        stop_words = set(nltk.corpus.stopwords.words('english'))
    except:
        nltk.download('stopwords')
        stop_words = set(nltk.corpus.stopwords.words('english'))
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^a-z0-9\s]', '', text)
    return text

def parse_resume_sections(text):
    lines = text.split('\n')
    sections_keywords = {
        'Summary': ['summary', 'profile', 'about', 'objective'],
        'Experience': ['experience', 'employment', 'work history'],
        'Education': ['education', 'academic', 'qualifications'],
        'Projects': ['projects', 'portfolio'],
        'Skills': ['skills', 'technical skills', 'technologies']
    }
    parsed_data = {k: '' for k in sections_keywords}
    current_section = 'Summary'
    current_text = []
    for line in lines:
        stripped = line.strip()
        if not stripped: continue
        found_header = False
        for section, keywords in sections_keywords.items():
            if any(kw in stripped.lower() for kw in keywords):
                if current_text: parsed_data[current_section] = "\n".join(current_text).strip()
                current_section = section
                current_text = []
                found_header = True
                break
        if not found_header: current_text.append(line)
    if current_text: parsed_data[current_section] = "\n".join(current_text).strip()
    return parsed_data

def extract_resume_data(raw_text, cleaned_text):
    name = 'Candidate'
    doc = nlp(raw_text)
    for ent in doc.ents:
        if ent.label_ == "PERSON" and len(ent.text.split()) >= 2:
            name = ent.text
            break
    
    email = 'unknown@email.com'
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', raw_text)
    if email_match: email = email_match.group(0)
    
    mobile = 'N/A'
    mobile_match = re.search(r'[\+\(]?[1-9][\s\d\.\-\(\)]{8,}[0-9]', raw_text)
    if mobile_match: mobile = mobile_match.group(0)

    found_skills = set()
    for field, keywords in KEYWORDS.items():
        for keyword in keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', cleaned_text):
                found_skills.add(keyword)
    
    return {'name': name, 'email': email, 'mobile_number': mobile, 'skills': list(found_skills)}

def calculate_rigorous_score(resume_text, resume_edu_section, resume_exp_section, user_skills, job_description_text):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    
    # 1. SKILLS SCORE (40 Points)
    jd_lower = job_description_text.lower()
    unique_user_skills = set([s.lower() for s in user_skills])
    matched_skills = 0
    for skill in unique_user_skills:
        if skill in jd_lower:
            matched_skills += 1
    skills_score = (matched_skills / len(unique_user_skills)) * 40 if len(unique_user_skills) > 0 else 0

    # 2. EDUCATION SCORE (30 Points)
    edu_score = 0
    if any(deg in resume_edu_section.lower() for deg in ['bachelor', 'master', 'phd', 'b.tech', 'm.tech', 'bsc', 'msc']):
        edu_score += 15
    if resume_edu_section and job_description_text:
        vectorizer = TfidfVectorizer(stop_words='english')
        try:
            tfidf_edu = vectorizer.fit_transform([resume_edu_section, job_description_text])
            sim_edu = cosine_similarity(tfidf_edu[0:1], tfidf_edu[1:2])[0][0]
            edu_score += (sim_edu * 15)
        except: pass
    edu_score = min(edu_score, 30)

    # 3. EXPERIENCE SCORE (30 Points)
    exp_score = 0
    years_match = re.search(r'(\d+)\+?\s*years?', resume_exp_section.lower())
    if years_match:
        years = int(years_match.group(1))
        exp_score += min(years * 2, 10)
    
    if resume_exp_section and job_description_text:
        vectorizer = TfidfVectorizer(stop_words='english')
        try:
            tfidf_exp = vectorizer.fit_transform([resume_exp_section, job_description_text])
            sim_exp = cosine_similarity(tfidf_exp[0:1], tfidf_exp[1:2])[0][0]
            exp_score += (sim_exp * 20)
        except: pass
    exp_score = min(exp_score, 30)

    total_score = round(skills_score + edu_score + exp_score, 2)
    return {
        'total_score': total_score,
        'breakdown': {
            'skills': round(skills_score, 2),
            'education': round(edu_score, 2),
            'experience': round(exp_score, 2)
        }
    }
def sanitize_for_pdf(text):
    """
    Cleans text to prevent FPDF crashes on special characters.
    Replaces problematic unicode characters with safe ASCII equivalents.
    """
    if not text:
        return ""
    
    # Convert to string just in case
    text = str(text)
    
    # Replace common problematic characters found in resumes
    # 1. The specific black diamond bullet from your sample
    text = text.replace('', '-')
    
    # 2. Standard bullets
    text = text.replace('•', '*')
    text = text.replace('●', '*')
    
    # 3. Smart quotes (MS Word style)
    text = text.replace('“', '"')
    text = text.replace('”', '"')
    text = text.replace('‘', "'")
    text = text.replace('’', "'")
    
    # 4. Dashes
    text = text.replace('–', '-') # En-dash to hyphen
    text = text.replace('—', '-') # Em-dash to hyphen
    
    # 5. Remove any other non-ASCII characters that might break the PDF
    # This keeps letters, numbers, and standard punctuation
    import re
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    
    return text


def create_resume_pdf(data):
    """
    Generates a Professional Resume PDF matching Robert Smith format.
    Ultra-Sanitized to prevent crashes.
    """
    pdf = FPDF()
    pdf.add_page()
    
    # --- HELPER FOR SANITIZATION ---
    def sanitize(text):
        if not text: return ""
        
        import re
        
        # 1. Force to string
        text = str(text)
        
        # 2. Remove Non-Breaking Spaces (Common crasher)
        text = text.replace('\xa0', ' ')
        text = text.replace('\u200b', '') # Zero-width space
        text = text.replace('\u200c', '') # Zero-width non-joiner
        
        # 3. Replace special bullets with safe dash
        text = text.replace('', '-')
        text = text.replace('•', '-')
        text = text.replace('●', '-')
        
        # 4. Replace Smart Quotes
        text = text.replace('“', '"')
        text = text.replace('”', '"')
        text = text.replace('‘', "'")
        text = text.replace('’', "'")
        
        # 5. Replace Em-Dashes/En-Dashes
        text = text.replace('–', '-')
        text = text.replace('—', '-')
        
        # 6. Remove any other non-ASCII characters that might break PDF
        # This keeps standard letters, numbers, and punctuation
        text = re.sub(r'[^\x00-\x7F]+', '', text)
        
        return text

    # --- DATA RETRIEVAL ---
    def get_data(key):
        return sanitize(data.get(key.lower()) or data.get(key, ''))

    name = get_data('name')
    email = get_data('email')
    mobile = get_data('mobile')
    
    summary = get_data('summary')
    experience = get_data('experience')
    education = get_data('education')
    projects = get_data('projects')
    skills = get_data('skills')

    # --- HEADER SECTION ---
    # Name
    pdf.set_font("Arial", 'B', 22)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 15, name if name else "YOUR NAME", 0, 1, 'C')
    
    # Contact Info
    pdf.set_font("Arial", '', 10)
    pdf.set_text_color(60, 60, 60)
    
    contact_line = ""
    if email: contact_line += email
    if mobile:
        contact_line += " | " if contact_line else ""
        contact_line += mobile
        
    pdf.cell(0, 6, contact_line, 0, 1, 'C')
    
    # Separator Line
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(10)

    # --- SECTION HELPER ---
    def add_section_header(title):
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 8, title.upper(), 0, 1, 'L')
        pdf.set_draw_color(200, 200, 200)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.set_draw_color(0, 0, 0)
        pdf.ln(5)

    # --- SUMMARY ---
    if summary and summary != "[No Summary details found]":
        add_section_header("Objective")
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 6, summary)

    # --- SKILLS ---
    if skills and skills != "[No Skills details found]":
        add_section_header("Skills")
        pdf.set_font("Arial", '', 11)
        for skill_line in skills.split('\n'):
            pdf.multi_cell(0, 6, skill_line)

    # --- EXPERIENCE ---
    if experience and experience != "[No Experience details found]":
        add_section_header("Work Experience")
        
        lines = experience.split('\n')
        first_line_of_block = True
        
        for line in lines:
            clean_line = line.strip()
            if not clean_line: 
                first_line_of_block = True
                pdf.ln(2)
                continue

            # Detect bullets
            is_bullet = clean_line.startswith(('-', '•', '*', ''))
            
            if is_bullet:
                pdf.set_x(20)
                pdf.set_font("Arial", '', 11)
                clean_bullet = clean_line.lstrip('-*•').strip()
                pdf.cell(0, 6, u"\u2022 " + clean_bullet, 0, 1)
                pdf.set_x(10) 
            else:
                if first_line_of_block:
                    pdf.set_font("Arial", 'B', 11)
                    pdf.multi_cell(0, 6, clean_line)
                    first_line_of_block = False
                else:
                    import re
                    if re.search(r'\d{4}', clean_line):
                        pdf.set_font("Arial", 'I', 10)
                    else:
                        pdf.set_font("Arial", '', 10)
                    pdf.multi_cell(0, 5, clean_line)

    # --- PROJECTS ---
    if projects and projects != "[No Projects details found]":
        add_section_header("Projects")
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 6, projects)

    # --- EDUCATION ---
    if education and education != "[No Education details found]":
        add_section_header("Education")
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 6, education)
        
    return pdf



# --- ROUTES ---

@app.route('/')
def index(): return render_template('home.html')

@app.route('/user')
def user_view(): return render_template('user.html')

@app.route('/admin')
def admin_login_view(): return render_template('admin_login.html')

@app.route('/dashboard')
def admin_dashboard_view(): return render_template('admin_dashboard.html')

@app.route('/generator')
def generator_view(): return render_template('generator.html')

@app.route('/shortlist')
def shortlist_view():
    return render_template('shortlist.html')

@app.route('/api/shortlist', methods=['POST'])
def shortlist_resumes():
    jd = request.form.get('job_description', '')
    files = request.files.getlist('resumes')
    
    results = []
    
    # Use default JD if empty
    target_jd = jd if jd else JOB_DESCRIPTIONS.get('default', '')

    print(f"Processing {len(files)} resumes...")

    for file in files:
        if file.filename == '':
            continue
            
        try:
            # Read PDF
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath) # Save temporarily to read
            
            resume_text_raw, pages = pdf_reader(filepath)
            
            if len(resume_text_raw.strip()) < 50:
                results.append({
                    'name': file.filename,
                    'email': 'N/A',
                    'score': 0,
                    'status': 'Error: No Text'
                })
                continue

            # Parse
            resume_text_clean = clean_text_nltk(resume_text_raw)
            data = extract_resume_data(resume_text_raw, resume_text_clean)
            sections = parse_resume_sections(resume_text_raw)
            
            # Calculate Score
            score_data = calculate_rigorous_score(
                resume_text=resume_text_raw,
                resume_edu_section=sections.get('Education', ''),
                resume_exp_section=sections.get('Experience', ''),
                user_skills=data.get('skills', []),
                job_description_text=target_jd
            )
            
            results.append({
                'filename': file.filename,
                'name': data.get('name', 'Unknown'),
                'email': data.get('email', 'N/A'),
                'score': score_data['total_score'],
                'breakdown': score_data['breakdown'],
                'skills': data.get('skills', [])
            })
            
        except Exception as e:
            print(f"Error processing {file.filename}: {e}")
            results.append({
                'name': file.filename,
                'email': 'Error',
                'score': 0,
                'status': 'Processing Failed'
            })

    # Sort results by Score (Descending) - Highest first
    results.sort(key=lambda x: x['score'], reverse=True)

    return jsonify(results)


@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files: return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    job_description_input = request.form.get('job_description', '')
    target_jd = job_description_input if job_description_input else JOB_DESCRIPTIONS.get('default', '')

    if file.filename == '': return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            resume_text_raw, pages = pdf_reader(filepath)
            if len(resume_text_raw.strip()) < 50: return jsonify({'error': 'Not enough text'}), 400
            resume_text_clean = clean_text_nltk(resume_text_raw)
            data = extract_resume_data(resume_text_raw, resume_text_clean)
        except Exception as e: return jsonify({'error': f'Parsing error: {str(e)}'}), 500

        name = data.get('name', 'Unknown')
        email = data.get('email', 'Unknown')
        mobile = data.get('mobile_number', 'Unknown')
        skills = data.get('skills', [])
        cand_level = 'Fresher' if pages == 1 else ('Intermediate' if pages == 2 else 'Experienced')
        sections = parse_resume_sections(resume_text_raw)

        candidate_labels = list(KEYWORDS.keys())
        try:
            result = classifier(resume_text_raw[:1500], candidate_labels)
            reco_field = result['labels'][0]
        except: reco_field = 'General'
        
        recommended_skills = SKILLS_DICT.get(reco_field, [])
        rec_courses = COURSES.get(reco_field, [])

        # NEW SCORING
        score_data = calculate_rigorous_score(
            resume_text=resume_text_raw,
            resume_edu_section=sections.get('Education', ''),
            resume_exp_section=sections.get('Experience', ''),
            user_skills=skills,
            job_description_text=target_jd
        )
        score = score_data['total_score']

        if connection:
            ts = time.time()
            timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H:%M:%S')
            insert_sql = "INSERT INTO user_data (Name, Email_ID, resume_score, Timestamp, Page_no, Predicted_Field, User_level, Actual_skills, Recommended_skills, Recommended_courses) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(insert_sql, (name, email, str(score), timestamp, str(pages), reco_field, cand_level, str(skills), str(recommended_skills), str(rec_courses)))
            connection.commit()

        return jsonify({
            'name': name, 'email': email, 'mobile': mobile, 'pages': pages, 'level': cand_level,
            'skills': skills, 'field': reco_field, 'rec_skills': recommended_skills, 'rec_courses': rec_courses,
            'score': score, 'breakdown': score_data['breakdown']
        })

@app.route('/api/login', methods=['POST'])
def admin_login():
    d = request.json
    if d.get('username') == 'Dipen' and d.get('password') == 'dipen123': return jsonify({'success': True})
    return jsonify({'success': False}), 401

@app.route('/api/data')
def admin_data():
    if not connection: return jsonify([])
    cursor.execute("SELECT * FROM user_data")
    raw_data = cursor.fetchall()
    formatted_data = []
    for row in raw_data:
        new_row = []
        for item in row:
            if isinstance(item, bytes): new_row.append(item.decode('utf-8'))
            else: new_row.append(item)
        formatted_data.append(new_row)
    return jsonify(formatted_data)

@app.route('/api/download')
def download_file():
    if not connection: return "No DB connection"
    cursor.execute("SELECT * FROM user_data")
    raw_data = cursor.fetchall()
    formatted_data = []
    for row in raw_data:
        new_row = []
        for item in row:
            if isinstance(item, bytes): new_row.append(item.decode('utf-8'))
            else: new_row.append(item)
        formatted_data.append(new_row)
    columns = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(formatted_data, columns=columns)
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name='user_data.csv')

@app.route('/api/parse_for_generator', methods=['POST'])
def parse_for_generator():
    if 'file' not in request.files: return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    try:
        resume_text_raw, pages = pdf_reader(file)
        if not resume_text_raw or len(resume_text_raw.strip()) < 5:
             return jsonify({'error': 'Could not extract text', 'name': 'Unknown', 'email': '', 'mobile': '', 'summary': '', 'experience': '', 'education': '', 'projects': '', 'skills': ''}), 200
        resume_text_clean = clean_text_nltk(resume_text_raw)
        basic_data = extract_resume_data(resume_text_raw, resume_text_clean)
        sections = parse_resume_sections(resume_text_raw)
        return jsonify({
            'name': basic_data.get('name'), 'email': basic_data.get('email'), 'mobile': basic_data.get('mobile_number'),
            'summary': sections.get('Summary', ''), 'experience': sections.get('Experience', ''),
            'education': sections.get('Education', ''), 'projects': sections.get('Projects', ''),
            'skills': "\n".join(basic_data.get('skills', []))
        })
    except Exception as e: return jsonify({'error': str(e), 'name': 'Unknown', 'email': '', 'mobile': '', 'summary': '', 'experience': '', 'education': '', 'projects': '', 'skills': ''}), 200

@app.route('/api/analyze_updated_resume', methods=['POST'])
def analyze_updated_resume():
    data = request.json
    reconstructed_text = f"{data.get('summary', '')} {data.get('experience', '')} {data.get('education', '')} {data.get('projects', '')} {data.get('skills', '')}"
    cleaned_text = clean_text_nltk(reconstructed_text)
    
    candidate_labels = list(KEYWORDS.keys())
    try:
        result = classifier(reconstructed_text[:1500], candidate_labels)
        reco_field = result['labels'][0]
    except: reco_field = 'General'
    recommended_skills = SKILLS_DICT.get(reco_field, [])
    
    score_categories = {'Career Objective': ['objective', 'summary'], 'Declaration': ['declaration'], 'Hobbies': ['hobbies'], 'Achievements': ['achievements'], 'Projects': ['projects']}
    score = 0
    for category, keywords in score_categories.items():
        if any(keyword in cleaned_text for keyword in keywords): score += 20
        
    return jsonify({'score': score, 'field': reco_field, 'rec_skills': recommended_skills, 'status': 'Analyzed Successfully'})

@app.route('/api/download_updated_resume', methods=['POST'])
def download_updated_resume():
    """
    Generates a PDF file from the form data and sends it.
    """
    data = request.json
    
    try:
        # 1. Generate PDF
        pdf = create_resume_pdf(data)
        
        # 2. Convert PDF to Bytes
        # Try latin-1 first (standard for FPDF), fall back to utf-8 if it fails
        try:
            pdf_str = pdf.output(dest='S').encode('latin-1')
        except UnicodeEncodeError:
            # If latin-1 fails, try utf-8
            pdf_str = pdf.output(dest='S').encode('utf-8')
        
        # 3. Create BytesIO object
        file_stream = io.BytesIO(pdf_str)
        file_stream.seek(0)
        
        # 4. Send File
        filename = data.get('name', 'Resume').replace(" ", "_") + "_Updated.pdf"
        
        return send_file(
            file_stream, 
            mimetype='application/pdf',
            as_attachment=True, 
            download_name=filename
        )
        
    except Exception as e:
        # PRINT THE ERROR TO YOUR TERMINAL
        import traceback
        print("=" * 50)
        print("CRITICAL PDF ERROR:")
        print(traceback.format_exc())
        print("=" * 50)
        
        return jsonify({
            'error': 'Failed to generate PDF', 
            'details': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)