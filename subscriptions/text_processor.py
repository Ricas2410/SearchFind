import re
import logging
import string
from collections import defaultdict
import nltk

# Try to download NLTK data, with fallback if it fails
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
except Exception as e:
    logging.warning(f"NLTK download error: {str(e)}. Some features may be limited.")

# Import after download attempt
try:
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    logging.warning("NLTK imports failed. Using basic text processing instead.")

logger = logging.getLogger(__name__)

class TextProcessor:
    """
    Class for processing and analyzing text extracted from documents.
    
    This class handles text cleaning, normalization, section identification,
    and basic entity recognition for further analysis.
    """
    
    # Common section headers found in resumes
    RESUME_SECTIONS = {
        'experience': ['experience', 'work experience', 'employment history', 'work history', 'professional experience'],
        'education': ['education', 'academic background', 'educational background', 'academic history'],
        'skills': ['skills', 'technical skills', 'core competencies', 'key skills', 'competencies'],
        'projects': ['projects', 'project experience', 'key projects', 'professional projects'],
        'summary': ['summary', 'professional summary', 'executive summary', 'profile', 'about me'],
        'certifications': ['certifications', 'certificates', 'professional certifications', 'credentials'],
        'languages': ['languages', 'language proficiency', 'language skills'],
        'volunteer': ['volunteer', 'volunteering', 'volunteer experience', 'community service'],
        'publications': ['publications', 'research publications', 'papers', 'articles'],
        'interests': ['interests', 'hobbies', 'activities', 'personal interests']
    }
    
    # Common section headers found in cover letters
    COVER_LETTER_SECTIONS = {
        'greeting': ['dear', 'hello', 'hi', 'greetings', 'to whom it may concern'],
        'introduction': ['i am writing', 'please accept', 'i would like to', 'i am pleased'],
        'body': ['my experience', 'my skills', 'i have worked', 'i developed', 'i managed'],
        'closing': ['thank you', 'sincerely', 'best regards', 'looking forward', 'yours truly'],
        'signature': []  # Often doesn't have explicit headers
    }
    
    # Common section headers found in job descriptions
    JOB_DESCRIPTION_SECTIONS = {
        'about_company': ['about us', 'company overview', 'our company', 'who we are'],
        'job_summary': ['job summary', 'position summary', 'role overview', 'about the role'],
        'responsibilities': ['responsibilities', 'duties', 'what you\'ll do', 'key responsibilities'],
        'requirements': ['requirements', 'qualifications', 'what you need', 'must have', 'who you are'],
        'benefits': ['benefits', 'perks', 'what we offer', 'compensation', 'why join us'],
        'application_process': ['how to apply', 'application process', 'next steps']
    }
    
    def __init__(self):
        """Initialize the TextProcessor with necessary components."""
        self.lemmatizer = WordNetLemmatizer() if NLTK_AVAILABLE else None
        self.stop_words = set(stopwords.words('english')) if NLTK_AVAILABLE else set()
    
    def clean_text(self, text):
        """
        Clean and normalize the given text.
        
        Args:
            text (str): The raw text to clean
            
        Returns:
            str: Cleaned and normalized text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Replace multiple newlines with single newline
        text = re.sub(r'\n+', '\n', text)
        
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Remove other special characters
        text = re.sub(r'[^\w\s\n.,-:]', ' ', text)
        
        return text.strip()
    
    def tokenize_sentences(self, text):
        """
        Split text into sentences.
        
        Args:
            text (str): Text to split into sentences
            
        Returns:
            list: List of sentences
        """
        if NLTK_AVAILABLE:
            return sent_tokenize(text)
        else:
            # Basic sentence splitting
            return [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    
    def tokenize_words(self, text):
        """
        Split text into words.
        
        Args:
            text (str): Text to split into words
            
        Returns:
            list: List of words
        """
        if NLTK_AVAILABLE:
            return word_tokenize(text)
        else:
            # Basic word splitting
            return [w.strip() for w in re.split(r'\W+', text) if w.strip()]
    
    def remove_stopwords(self, tokens):
        """
        Remove common stopwords from a list of tokens.
        
        Args:
            tokens (list): List of word tokens
            
        Returns:
            list: Filtered list with stopwords removed
        """
        if NLTK_AVAILABLE:
            return [token for token in tokens if token.lower() not in self.stop_words]
        else:
            # Basic stopwords list
            basic_stopwords = {'a', 'an', 'the', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 
                              'to', 'of', 'in', 'for', 'with', 'on', 'at', 'by', 'from', 'about'}
            return [token for token in tokens if token.lower() not in basic_stopwords]
    
    def lemmatize_tokens(self, tokens):
        """
        Lemmatize tokens to their base form.
        
        Args:
            tokens (list): List of word tokens
            
        Returns:
            list: List of lemmatized tokens
        """
        if NLTK_AVAILABLE and self.lemmatizer:
            return [self.lemmatizer.lemmatize(token) for token in tokens]
        else:
            # Without NLTK, return the original tokens
            return tokens
    
    def identify_sections(self, text, document_type='resume'):
        """
        Identify and extract sections from the document.
        
        Args:
            text (str): Processed document text
            document_type (str): Type of document ('resume', 'cover_letter', 'job_description')
            
        Returns:
            dict: Dictionary of section names and their content
        """
        sections = {}
        
        # Choose appropriate section headers based on document type
        if document_type.lower() == 'resume':
            section_headers = self.RESUME_SECTIONS
        elif document_type.lower() == 'cover_letter':
            section_headers = self.COVER_LETTER_SECTIONS
        elif document_type.lower() == 'job_description':
            section_headers = self.JOB_DESCRIPTION_SECTIONS
        else:
            section_headers = {}
        
        # Split the text by lines
        lines = text.split('\n')
        
        # Initialize variables
        current_section = 'unknown'
        sections[current_section] = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this line is a section header
            found_section = False
            for section, header_variations in section_headers.items():
                # Check if line matches a header pattern
                line_lower = line.lower().strip(':')
                if line_lower in header_variations or any(header in line_lower for header in header_variations):
                    current_section = section
                    if current_section not in sections:
                        sections[current_section] = []
                    found_section = True
                    break
                
            if not found_section:
                # Add the line to the current section
                sections[current_section].append(line)
        
        # Convert lists to strings
        for section, content in sections.items():
            sections[section] = '\n'.join(content)
            
        return sections
    
    def extract_entities(self, text, entity_types=None):
        """
        Extract entities like skills, job titles, companies, etc. from text.
        
        Args:
            text (str): Processed document text
            entity_types (list): Types of entities to extract (default: all)
            
        Returns:
            dict: Dictionary of entity types and extracted entities
        """
        # Basic pattern matching for different entity types
        entities = defaultdict(set)
        
        # Adjust entity extraction based on requested types
        if not entity_types or 'skills' in entity_types:
            entities['skills'].update(self._extract_skills(text))
            
        if not entity_types or 'job_titles' in entity_types:
            entities['job_titles'].update(self._extract_job_titles(text))
            
        if not entity_types or 'companies' in entity_types:
            entities['companies'].update(self._extract_companies(text))
            
        if not entity_types or 'education' in entity_types:
            entities['education'].update(self._extract_education(text))
            
        # Convert sets to lists for better serialization
        return {k: list(v) for k, v in entities.items()}
    
    def _extract_skills(self, text):
        """Extract skill entities from text using pattern matching."""
        skills = set()
        
        # Look for skill lists (comma or bullet separated)
        skill_sections = re.findall(r'(?:skills|expertise|competencies|proficiencies)(?:[\s\n]*:[\s\n]*)([\s\S]+?)(?:\n\n|\Z)', text, re.IGNORECASE)
        
        for section in skill_sections:
            # Try to split by bullets or commas
            if '•' in section or '·' in section or '-' in section:
                # Split by common bullet characters
                bullet_skills = re.split(r'[•·-]\s*', section)
                for skill in bullet_skills:
                    if skill.strip():
                        skills.add(skill.strip())
            else:
                # Split by commas
                comma_skills = section.split(',')
                for skill in comma_skills:
                    if skill.strip():
                        skills.add(skill.strip())
        
        # Look for common programming languages and technologies
        tech_patterns = [
            r'\b(?:python|java|javascript|js|typescript|ts|c\+\+|ruby|php|go|rust|swift|kotlin)\b',
            r'\b(?:html|css|sass|less|sql|nosql|mongodb|mysql|postgresql|oracle|redis)\b',
            r'\b(?:react|angular|vue|svelte|node\.?js|express|django|flask|spring|rails)\b',
            r'\b(?:aws|azure|gcp|google cloud|docker|kubernetes|k8s|terraform|jenkins|git)\b',
            r'\b(?:machine learning|ml|ai|artificial intelligence|data science|nlp|computer vision)\b'
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            skills.update([match.strip() for match in matches if match.strip()])
        
        return skills
    
    def _extract_job_titles(self, text):
        """Extract job title entities from text using pattern matching."""
        job_titles = set()
        
        # Common job title patterns
        title_patterns = [
            r'(?:^|\n)(?:title|position|role)(?:[\s\n]*:[\s\n]*)([^\n]+)',
            r'(?:^|\n)([a-z ]+(?:developer|engineer|manager|director|analyst|designer|consultant|specialist))(?:$|\n|,)',
            r'(?:^|\n)(?:senior|lead|principal|junior|staff) ([a-z ]+)(?:$|\n|,)'
        ]
        
        for pattern in title_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            job_titles.update([match.strip() for match in matches if match.strip()])
        
        return job_titles
    
    def _extract_companies(self, text):
        """Extract company name entities from text using pattern matching."""
        companies = set()
        
        # Look for company patterns
        company_patterns = [
            r'(?:^|\n)(?:company|employer|organization)(?:[\s\n]*:[\s\n]*)([^\n]+)',
            r'(?:worked at|employed by|experience at) ([A-Z][A-Za-z0-9 .,&]+)',
            r'(?:^|\n)([A-Z][A-Za-z0-9 .,&]+)(?:[\s\n]*,[\s\n]*)((?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|january|february|march|april|may|june|july|august|september|october|november|december))',
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            
            for match in matches:
                if isinstance(match, tuple):
                    company = match[0].strip()
                else:
                    company = match.strip()
                
                if company:
                    # Filter out dates and other non-company text
                    if not re.match(r'^(?:19|20)\d{2}$', company) and not re.match(r'^(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|january|february|march|april|may|june|july|august|september|october|november|december)', company.lower()):
                        companies.add(company)
        
        return companies
    
    def _extract_education(self, text):
        """Extract education entities from text using pattern matching."""
        education = set()
        
        # Look for education patterns
        education_patterns = [
            r'(?:^|\n)(?:degree|education|qualification)(?:[\s\n]*:[\s\n]*)([^\n]+)',
            r'(?:bachelor|master|doctorate|phd|bs|ba|ms|ma|mba|b\.s\.|b\.a\.|m\.s\.|m\.a\.|ph\.d\.)(?:[\s\n]*in[\s\n]*)([^\n,]+)',
            r'(?:university|college|institute|school) of ([^\n,]+)',
            r'([a-z ]+(?:university|college|institute|school))(?:$|\n|,)'
        ]
        
        for pattern in education_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            education.update([match.strip() for match in matches if match.strip()])
        
        return education
    
    def process_document(self, text, document_type='resume'):
        """
        Process a document with all available text processing methods.
        
        Args:
            text (str): Raw document text
            document_type (str): Type of document ('resume', 'cover_letter', 'job_description')
            
        Returns:
            dict: Processed document data with sections and entities
        """
        # Clean the text
        cleaned_text = self.clean_text(text)
        
        # Identify sections
        sections = self.identify_sections(cleaned_text, document_type)
        
        # Extract entities
        entities = self.extract_entities(cleaned_text)
        
        # Basic stats
        sentences = self.tokenize_sentences(cleaned_text)
        words = self.tokenize_words(cleaned_text)
        word_count = len(words)
        
        return {
            'document_type': document_type,
            'word_count': word_count,
            'sentence_count': len(sentences),
            'sections': sections,
            'entities': entities,
        }