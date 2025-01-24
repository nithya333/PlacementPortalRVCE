import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from typing import List, Dict, Set

class AccurateResumeParser:
    def __init__(self, model_filename: str):
        # Load the trained model
        with open(model_filename, 'rb') as f:
            model_data = pickle.load(f)
        self.tfidf = model_data['tfidf']
        self.classifier = model_data['classifier']
        self.label_encoder = model_data['label_encoder']
        self.skill_map = {
            'python': {'python', 'py', 'python3', 'python2'},
            'javascript': {'javascript', 'js', 'es6', 'nodejs'},
            'java': {'java', 'j2ee', 'spring'},
            'react': {'react', 'reactjs', 'react native'},
            'angular': {'angular', 'angularjs', 'angular2'},
            'mongodb': {'mongodb', 'mongo', 'mongoose'},
            'postgresql': {'postgresql', 'postgres', 'psql'},
            'mysql': {'mysql', 'mariadb'},
            'aws': {'aws', 'amazon web services', 'ec2', 's3'},
            'azure': {'azure', 'microsoft azure'},
            'docker': {'docker', 'containerization'},
            'kubernetes': {'kubernetes', 'k8s'},
            'machine learning': {'machine learning', 'ml', 'deep learning', 'ai'}
        }

        
    def normalize_text(self, text: str) -> str:
        """Normalize text for consistent matching."""
        text = text.lower()
        return text.strip()
    
    def extract_skills(self, text: str) -> Set[str]:
        """Extract unique skills without repetition and redundancy."""
        normalized_text = self.normalize_text(text)
        extracted_skills = set()

        # Match predefined skill variations
        for canonical_skill, variations in self.skill_map.items():
            if any(var in normalized_text for var in variations):
                extracted_skills.add(canonical_skill)

        # TF-IDF based extraction
        text_vector = self.tfidf.transform([normalized_text])
        feature_names = self.tfidf.get_feature_names_out()

        for idx, value in zip(text_vector.indices, text_vector.data):
            term = feature_names[idx]
            if value > 0.1 and len(term) > 2: 
                extracted_skills.add(term)

        extracted_skills = sorted(extracted_skills, key=len, reverse=True)
        final_skills = set()
        for skill in extracted_skills:
            if not any(skill in longer_skill for longer_skill in final_skills):
                final_skills.add(skill)

        return final_skills

    def predict_job_match(self, resume_text: str, jobs_df: pd.DataFrame):
        """Predict top job matches for a resume."""
        normalized_resume = self.normalize_text(resume_text)
        resume_vector = self.tfidf.transform([normalized_resume])
        resume_skills = self.extract_skills(normalized_resume)

        # Predict probabilities for each job role
        probs = self.classifier.predict_proba(resume_vector)[0]
        print(probs)
        top_indices = probs.argsort()[-3:][::-1]  # Top 3 matches
        print(top_indices)
        matches = []
        for idx in top_indices:
            confidence = probs[idx]
            role = self.label_encoder.inverse_transform([idx])[0]
            job_row = jobs_df[jobs_df['Job Role'] == role].iloc[0]
            
            # Extract skills for the current job role
            job_skills = self.extract_skills(self.normalize_text(job_row['Skills']))
            matching_skills = resume_skills.intersection(job_skills)
            missing_skills = job_skills - resume_skills

            match_info = {
                'role': role,
                'company': job_row['Company'],
                'confidence': confidence,
                'resume_skills': resume_skills,
                'matching_skills': matching_skills,
                'missing_skills': missing_skills
            }
            matches.append(match_info)

        return matches