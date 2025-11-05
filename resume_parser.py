import PyPDF2
from docx import Document
import re
import spacy

class ResumeParser:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            self.nlp = None
    
    def parse_resume(self, file_path):
        """Parse resume and extract only essential information"""
        file_extension = file_path.split('.')[-1].lower()
        
        if file_extension == 'pdf':
            text = self.extract_text_from_pdf(file_path)
        elif file_extension == 'docx':
            text = self.extract_text_from_docx(file_path)
        elif file_extension == 'txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            raise ValueError("Unsupported file format")
        
        # Extract only essential data
        data = {
            'name': self.extract_name(text),
            'email': self.extract_email(text),
            'phone': self.extract_phone(text),
            'skills': self.extract_skills(text)  # Needed for ATS scoring
        }
        
        return data
    
    def extract_text_from_pdf(self, file_path):
        """Extract text from PDF"""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
    
    def extract_text_from_docx(self, file_path):
        """Extract text from DOCX"""
        doc = Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    
    def extract_name(self, text):
        """Extract name using NLP or basic patterns"""
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    return ent.text.strip()
        
        # Basic pattern matching
        lines = text.split('\n')
        for line in lines[:10]:
            line = line.strip()
            if len(line.split()) <= 4 and line.replace(' ', '').isalpha():
                return line
        return "Not found"
    
    def extract_email(self, text):
        """Extract email addresses"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else "Not found"
    
    def extract_phone(self, text):
        """Extract phone numbers"""
        phone_pattern = r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        return phones[0] if phones else "Not found"
    
    def extract_skills(self, text):
        """Extract skills for ATS scoring"""
        skills = [
            'Python', 'JavaScript', 'Java', 'C++', 'C#', 'PHP', 'Ruby', 'Go',
            'React', 'Angular', 'Vue', 'Node.js', 'Django', 'Flask', 'Express',
            'MySQL', 'PostgreSQL', 'MongoDB', 'AWS', 'Azure', 'Docker', 'Kubernetes',
            'Git', 'HTML', 'CSS', 'Bootstrap', 'jQuery', 'TypeScript'
        ]
        
        found_skills = []
        text_lower = text.lower()
        for skill in skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return ', '.join(found_skills) if found_skills else "Not found"