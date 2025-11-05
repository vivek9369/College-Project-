import re
from collections import Counter

class JobMatcher:
    def __init__(self):
        # Common technical skills and tools
        self.technical_skills = {
            'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin'],
            'frontend': ['html', 'css', 'javascript', 'react', 'angular', 'vue', 'jquery', 'bootstrap', 'sass', 'typescript'],
            'backend': ['node.js', 'django', 'flask', 'express', 'spring', 'asp.net', 'laravel', 'rails'],
            'database': ['mysql', 'postgresql', 'mongodb', 'sqlite', 'oracle', 'sql server', 'redis'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'github'],
            'frameworks': ['react', 'angular', 'vue', 'django', 'flask', 'express', 'spring', 'laravel'],
            'tools': ['git', 'docker', 'kubernetes', 'jenkins', 'jira', 'confluence', 'postman']
        }
        
        # Experience keywords
        self.experience_keywords = ['years', 'experience', 'senior', 'junior', 'lead', 'manager']
        
        # Education keywords
        self.education_keywords = ['bachelor', 'master', 'phd', 'degree', 'university', 'college']
    
    def calculate_match(self, resume_skills, job_description):
        """Calculate match percentage between resume and job description"""
        if not job_description.strip():
            return 100, [], []  # No job description = 100% match
        
        # Extract keywords from job description
        job_keywords = self.extract_job_keywords(job_description.lower())
        
        # Extract skills from resume
        resume_skill_list = self.extract_resume_skills(resume_skills.lower())
        
        # Calculate matches
        matched_skills = []
        missing_skills = []
        
        for keyword in job_keywords:
            if self.skill_matches(keyword, resume_skill_list):
                matched_skills.append(keyword)
            else:
                missing_skills.append(keyword)
        
        # Calculate score
        if not job_keywords:
            score = 100
        else:
            score = (len(matched_skills) / len(job_keywords)) * 100
        
        return round(score, 1), matched_skills, missing_skills
    
    def extract_job_keywords(self, job_text):
        """Extract relevant keywords from job description"""
        keywords = set()
        
        # Extract technical skills
        for category, skills in self.technical_skills.items():
            for skill in skills:
                if skill in job_text:
                    keywords.add(skill)
        
        # Extract experience requirements
        experience_pattern = r'(\d+)\+?\s*years?\s*experience'
        experience_matches = re.findall(experience_pattern, job_text)
        if experience_matches:
            keywords.add(f"{experience_matches[0]}+ years experience")
        
        # Extract education requirements
        for edu_keyword in self.education_keywords:
            if edu_keyword in job_text:
                keywords.add(edu_keyword)
        
        # Extract other common requirements
        common_requirements = [
            'agile', 'scrum', 'kanban', 'ci/cd', 'devops', 'microservices',
            'api', 'rest', 'graphql', 'testing', 'unit test', 'integration test',
            'machine learning', 'ai', 'data science', 'analytics', 'sql', 'nosql'
        ]
        
        for req in common_requirements:
            if req in job_text:
                keywords.add(req)
        
        return list(keywords)
    
    def extract_resume_skills(self, skills_text):
        """Extract skills from resume skills text"""
        skills = set()
        
        # Split by common delimiters
        skill_parts = re.split(r'[,;|]|\band\b', skills_text)
        
        for part in skill_parts:
            part = part.strip()
            if part and len(part) > 2:  # Filter out very short strings
                skills.add(part)
        
        return list(skills)
    
    def skill_matches(self, job_skill, resume_skills):
        """Check if a job skill matches any resume skill"""
        job_skill = job_skill.lower().strip()
        
        for resume_skill in resume_skills:
            resume_skill = resume_skill.lower().strip()
            
            # Exact match
            if job_skill == resume_skill:
                return True
            
            # Partial match (e.g., "python" matches "python developer")
            if job_skill in resume_skill or resume_skill in job_skill:
                return True
            
            # Abbreviation match (e.g., "js" matches "javascript")
            if self.is_abbreviation(job_skill, resume_skill):
                return True
        
        return False
    
    def is_abbreviation(self, short, long):
        """Check if short is an abbreviation of long"""
        if len(short) < 3:
            return False
        
        # Check if short appears as first letters of words in long
        short_words = short.split()
        long_words = long.split()
        
        if len(short_words) == 1 and len(long_words) > 1:
            # Single abbreviation like "js" for "javascript"
            return long.startswith(short)
        
        return False