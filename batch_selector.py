import os
import pandas as pd
from app import calculate_rigorous_score, clean_text_nltk, extract_resume_data, parse_resume_sections, pdf_reader
from Courses import JOB_DESCRIPTIONS

BATCH_FOLDER = 'batch_resumes'
OUTPUT_FILE = 'candidate_rankings.csv'

def process_batch():
    results = []
    if not os.path.exists(BATCH_FOLDER):
        os.makedirs(BATCH_FOLDER)
        print(f"Created '{BATCH_FOLDER}'. Add PDFs there and run again.")
        return

    files = [f for f in os.listdir(BATCH_FOLDER) if f.endswith('.pdf')]
    print(f"Processing {len(files)} resumes...")

    for filename in files:
        filepath = os.path.join(BATCH_FOLDER, filename)
        try:
            full_text, _ = pdf_reader(filepath)
            if not full_text or len(full_text.strip()) < 20: continue

            sections = parse_resume_sections(full_text)
            cleaned_text = clean_text_nltk(full_text)
            data = extract_resume_data(full_text, cleaned_text)
            
            # Use Default JD for batch processing
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
                'Status': 'Selected' if scoring['total_score'] > 60 else 'Rejected'
            })
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    if results:
        df = pd.DataFrame(results)
        df = df.sort_values(by='Total_Score', ascending=False)
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"\nDone! Rankings saved to {OUTPUT_FILE}")
        print(df.head())
    else:
        print("No valid resumes found.")

if __name__ == '__main__':
    process_batch()