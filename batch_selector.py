import os
import pandas as pd
from utils import calculate_rigorous_score, clean_text_nltk, extract_resume_data, parse_resume_sections, pdf_reader
from Courses import JOB_DESCRIPTIONS
from celery import Celery

celery = Celery('batch_selector', broker='redis://localhost:6379/0')
BATCH_FOLDER = 'batch_resumes'
OUTPUT_FILE = 'candidate_rankings.csv'

@celery.task(bind=True)
def process_batch_task(self):
    BATCH_FOLDER = 'batch_resumes'
    OUTPUT_FOLDER = 'outputs'
    OUTPUT_FILE = 'batch_report.xlsx'
    
    if not os.path.exists(OUTPUT_FOLDER): os.makedirs(OUTPUT_FOLDER)
    results = []
    files = [f for f in os.listdir(BATCH_FOLDER) if f.endswith('.pdf')]
    
    self.update_state(state='PROGRESS', meta={'current': 0, 'total': len(files), 'status': 'Starting...'})

    try:
        for i, filename in enumerate(files):
            filepath = os.path.join(BATCH_FOLDER, filename)
            try:
                full_text, _ = pdf_reader(filepath)
                if not full_text or len(full_text.strip()) < 20: continue

                sections = parse_resume_sections(full_text)
                cleaned_text = clean_text_nltk(full_text)
                data = extract_resume_data(full_text, cleaned_text)
                
                # Uses the ENHANCED scoring function automatically
                scoring = calculate_rigorous_score(
                    resume_text=full_text,
                    resume_edu_section=sections.get('Education', ''),
                    resume_exp_section=sections.get('Experience', ''),
                    user_skills=data.get('skills', []),
                    job_description_text=JOB_DESCRIPTIONS.get('default', '')
                )

                results.append({
                    'Filename': filename,
                    'Name': data.get('name'),
                    'Email': data.get('email'),
                    'Total_Score': scoring['total_score'],
                    'Skills_Match': scoring['breakdown']['skills'],
                    'Education_Match': scoring['breakdown']['education'],
                    'Experience_Match': scoring['breakdown']['experience'],
                    'Semantic_Fit': scoring['breakdown'].get('semantic_fit', 0), # New metric
                    'Status': 'Selected' if scoring['total_score'] > 60 else 'Rejected'
                })
                
                self.update_state(state='PROGRESS', meta={'current': i+1, 'total': len(files), 'status': f'Processing {filename}...'})

            except Exception as e:
                print(f"Error processing {filename}: {e}")

        if results:
            df = pd.DataFrame(results)
            df = df.sort_values(by='Total_Score', ascending=False)
            output_path = os.path.join(OUTPUT_FOLDER, OUTPUT_FILE)
            df.to_excel(output_path, index=False, engine='openpyxl')
            return {'current': 100, 'total': len(files), 'status': 'Completed', 'result': len(results)}
        else:
            return {'current': 100, 'total': len(files), 'status': 'No valid resumes found.'}

    except Exception as e:
        return {'current': 0, 'total': 0, 'status': f'Error: {str(e)}'}