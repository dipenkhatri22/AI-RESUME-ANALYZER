import os
import re
import nltk
import spacy
import fitz  # PyMuPDF
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from Courses import KEYWORDS, SKILLS_DICT, JOB_DESCRIPTIONS

# --- NEW: SEMANTIC SEARCH IMPORTS ---
try:
    from sentence_transformers import SentenceTransformer, util
    # 'all-MiniLM-L6-v2' is small (80MB), fast, and runs entirely on CPU.
    # It will download from HuggingFace on the FIRST run, then cache locally for offline use.
    print("Loading Semantic Model (Sentence-Transformers)...")
    semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
    print("Semantic Model Loaded successfully.")
except Exception as e:
    print(f"Warning: Could not load SentenceTransformer. Semantic scoring disabled. Error: {e}")
    semantic_model = None

# --- LOAD NLP MODELS ---
print("Loading spaCy model in utils...")
nlp = spacy.load("en_core_web_sm")
print("spaCy loaded in utils!")

def mask_pii(name, email):
    """
    Privacy Feature: Masks Personally Identifiable Information.
    Example: John Doe -> J*** D***, john@doe.com -> j***@doe.com
    """
    if not name or name == 'Candidate': return name
    if not email: return email
    
    # Mask Name
    name_parts = name.split()
    masked_name = " ".join([f"{p[0]}{'*' * (len(p)-1)}" if len(p) > 1 else p for p in name_parts])
    
    # Mask Email
    email_parts = email.split('@')
    if len(email_parts) == 2:
        user, domain = email_parts
        masked_user = user[0] + '*' * (len(user) - 1) if len(user) > 1 else user
        masked_email = f"{masked_user}@{domain}"
    else:
        masked_email = email
        
    return masked_name, masked_email

def pdf_reader(file_input):
    """
    Reads PDF from a filepath (string) or a FileStorage object.
    Handles explicit closing to prevent file locking errors (WinError 32).
    """
    text_content = ""
    doc = None
    try:
        if isinstance(file_input, str):
            doc = fitz.open(file_input)
        else:
            doc = fitz.open(stream=file_input.read(), filetype="pdf")
        
        page_count = doc.page_count
        for page in doc:
            text_content += page.get_text("text") + "\n"
            
    except Exception as e:
        print(f"Error reading PDF with PyMuPDF: {e}")
        return "", 0
    finally:
        if doc:
            doc.close()
            
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
        'Summary': ['summary', 'profile', 'about', 'objective', 'professional summary', 'professional profile', 'career objective'],
        'Experience': ['experience', 'employment', 'work history', 'professional experience', 'work experience'],
        'Education': ['education', 'academic', 'qualifications', 'academic background', 'education background'],
        'Projects': ['projects', 'portfolio', 'personal projects', 'project experience'],
        'Skills': ['skills', 'technical skills', 'technologies', 'tech stack', 'core competencies']
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
    job_title_keywords = ['developer', 'engineer', 'manager', 'specialist', 'consultant', 'analyst', 'designer', 'director', 'assistant', 'lead', 'senior', 'intern', 'recruiter', 'architect', 'scientist', 'administrator', 'tester', 'qa', 'front-end', 'frontend', 'backend', 'full stack', 'stack', 'web', 'mobile', 'data', 'cloud', 'devops', 'cyber', 'security', 'product', 'project', 'program', 'technical']
    name_exclusions = ['about', 'me', 'my', 'i', 'am', 'summary', 'profile', 'objective', 'experience', 'work', 'history', 'employment', 'education', 'academic', 'skills', 'projects', 'portfolio', 'contact', 'info', 'basic', 'phone', 'mobile', 'email', 'address', 'social', 'media']
    cities_raw = ['San Francisco', 'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose', 'Austin', 'London', 'Paris', 'Berlin', 'Tokyo', 'Toronto']
    cities = r'\b(' + '|'.join(cities_raw) + r')\b'
    first_lines = raw_text.split('\n')[:15]
    
    for line in first_lines:
        line = line.strip()
        if not line: continue
        words = line.split()
        potential_name_parts = []
        for word in words:
            word_lower = word.lower()
            if 'http' in word_lower or 'www' in word_lower or 'linkedin' in word_lower or 'github' in word_lower: continue
            if '.com' in word_lower or '.net' in word_lower or '.org' in word_lower: continue
            if '@' in word: continue
            if re.search(cities, word, flags=re.IGNORECASE): continue
            if any(kw in word_lower for kw in job_title_keywords): continue
            if word_lower in name_exclusions: continue
            if re.match(r'^[\d\-\(\)]+$', word): continue
            if re.match(r'^[A-Z][a-zA-Z\-]+$', word):
                potential_name_parts.append(word)
                if len(potential_name_parts) >= 2:
                    name = " ".join(potential_name_parts)
                    break
        if name != 'Candidate': break

    if name == 'Candidate':
        doc = nlp(raw_text)
        for ent in doc.ents:
            ent_text = ent.text
            if ent.label_ == "GPE" or ent.label_ == "LOC": continue
            if 'http' in ent_text.lower() or 'www' in ent_text.lower(): continue
            if ent_text.lower() in name_exclusions: continue
            is_job_title = any(kw in ent_text.lower() for kw in job_title_keywords)
            if ent.label_ == "PERSON" and len(ent.text.split()) >= 2 and not is_job_title:
                name = ent_text
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

def predict_field_fast(text):
    text_lower = text.lower()
    scores = {field: 0 for field in KEYWORDS}
    strong_indicators = {
        'Data Science & AI': ['scikit-learn', 'pandas', 'tensorflow', 'pytorch', 'keras', 'nlp', 'natural language processing', 'computer vision', 'generative ai', 'llm', 'hugging face', 'prompt engineering'],
        'DevOps & Cloud': ['kubernetes', 'k8s', 'jenkins', 'terraform', 'ansible', 'ci/cd', 'docker', 'aws', 'azure', 'gcp'],
        'Cybersecurity': ['penetration testing', 'pentesting', 'ethical hacking', 'kali linux', 'owasp', 'firewall', 'encryption', 'iso 27001'],
        'Mobile Development': ['android studio', 'kotlin', 'swift', 'swiftui', 'jetpack compose', 'flutter', 'react native'],
        'Product Management': ['product roadmap', 'user stories', 'stakeholder management', 'agile', 'scrum', 'kanban']
    }
    for field, words in strong_indicators.items():
        if field in scores:
            for word in words:
                if word in text_lower: scores[field] += 15 
    backend_keywords = ['django', 'flask', 'fastapi', 'node.js', 'express', 'java', 'spring boot', 'python', 'c#', '.net', 'go', 'php', 'mysql', 'postgresql', 'mongodb', 'sql']
    frontend_keywords = ['react', 'angular', 'vue', 'next.js', 'html', 'css', 'javascript', 'typescript', 'tailwind', 'bootstrap', 'redux']
    backend_count = sum(1 for kw in backend_keywords if kw in text_lower)
    frontend_count = sum(1 for kw in frontend_keywords if kw in text_lower)
    if backend_count >= 2 and frontend_count >= 2: scores['Web Development'] += 20
    for field, keywords in KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower: scores[field] += 1
    predicted_field = max(scores, key=scores.get) if any(scores.values()) else 'General'
    return predicted_field

# --- ENHANCED SCORING LOGIC ---
def calculate_rigorous_score(resume_text, resume_edu_section, resume_exp_section, user_skills, job_description_text):
    jd_lower = job_description_text.lower()
    
    # 1. SKILLS SCORE (40 Points)
    unique_user_skills = set([s.lower() for s in user_skills])
    matched_skills = 0
    for skill in unique_user_skills:
        if skill in jd_lower: matched_skills += 1
    skills_score = (matched_skills / len(unique_user_skills)) * 40 if len(unique_user_skills) > 0 else 0

    # 2. EDUCATION SCORE (30 Points)
    edu_score = 0
    if any(deg in resume_edu_section.lower() for deg in ['bachelor', 'master', 'phd', 'b.tech', 'm.tech', 'bsc', 'msc', 'associate']): edu_score += 20 
    if resume_edu_section and job_description_text:
        vectorizer = TfidfVectorizer(stop_words='english')
        try:
            tfidf_edu = vectorizer.fit_transform([resume_edu_section, job_description_text])
            sim_edu = cosine_similarity(tfidf_edu[0:1], tfidf_edu[1:2])[0][0]
            edu_score += (sim_edu * 10) 
        except: pass
    edu_score = min(edu_score, 30)

    # 3. EXPERIENCE SCORE (20 Points - Reduced slightly to make room for Semantic)
    exp_score = 0
    years_match = re.search(r'(\d+)\+?\s*years?', resume_exp_section.lower())
    resume_years = int(years_match.group(1)) if years_match else 0
    jd_years_match = re.search(r'(\d+)\+?\s*years?', jd_lower)
    required_years = int(jd_years_match.group(1)) if jd_years_match else 0
    
    if required_years > 0:
        if resume_years >= required_years: exp_score = 20
        else: exp_score = (resume_years / required_years) * 20
    else:
        exp_score = 5 if resume_years > 0 else 0
    exp_score = round(exp_score, 2)

    # 4. SEMANTIC FIT SCORE (10 Points) - NEW FEATURE
    semantic_fit = 0
    if semantic_model and resume_exp_section and job_description_text:
        try:
            # Encode text to vectors (embeddings)
            emb_resume = semantic_model.encode(resume_exp_section, convert_to_tensor=True)
            emb_jd = semantic_model.encode(job_description_text, convert_to_tensor=True)
            # Calculate cosine similarity
            score = util.cos_sim(emb_resume, emb_jd)
            # Scale 0.0-1.0 similarity to 0-10 points
            semantic_fit = float(score[0][0]) * 10
        except Exception as e:
            print(f"Semantic scoring error: {e}")
            
    total_score = round(skills_score + edu_score + exp_score + semantic_fit, 2)
    
    return {
        'total_score': total_score,
        'breakdown': {
            'skills': round(skills_score, 2),
            'education': round(edu_score, 2),
            'experience': round(exp_score, 2),
            'semantic_fit': round(semantic_fit, 2) # New metric returned to frontend
        }
    }