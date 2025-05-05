"""
Cover Letter Analysis System

This module implements cover letter analysis functionality using the core infrastructure
components (document parsing, text processing, content validation, and data resources).
It provides detailed analysis of cover letter content, quality assessment, and
recommendations for improvement.
"""

import logging
import re
from collections import defaultdict
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

from .document_parser import DocumentParser
from .text_processor import TextProcessor
from .content_validator import ContentValidator
from .data_resources import get_all_skills, get_all_job_titles

logger = logging.getLogger(__name__)

class CoverLetterAnalyzer:
    """
    Class for analyzing and generating cover letters using the core infrastructure.
    
    This class uses document parsing, text processing, and content validation
    to provide comprehensive cover letter analysis with detailed feedback and
    actionable recommendations. It also provides dynamic cover letter generation
    with templates for different job types, industries, and experience levels.
    """
    
    def __init__(self):
        """Initialize the CoverLetterAnalyzer with necessary components."""
        self.document_parser = DocumentParser()
        self.text_processor = TextProcessor()
        self.content_validator = ContentValidator(self.text_processor)
        
        # Load additional data for better analysis
        self.all_skills = get_all_skills()
        self.all_job_titles = get_all_job_titles()
        
        # Load cover letter templates for different job types and industries
        self.templates = self._load_templates()
        
        # Patterns for section analysis
        self.section_patterns = {
            'greeting': r'(?:dear|to whom it may concern|hello|greetings|hi)[^\.!?]*',
            'intro': r'(?:i am writing|i would like to|i am interested|i am excited|please accept|i am pleased)[^\.!?]*\.?',
            'body': r'(?:my experience|my background|throughout my career|during my time|i have been|in my role|in my previous|in my current|in my past|in my most recent)[^\.!?]*\.?',
            'closing': r'(?:thank you|sincerely|regards|best regards|yours truly|looking forward)[^\.!?]*\.?'
        }
        
        # Common phrases that indicate personalization
        self.personalization_indicators = [
            r'your company',
            r'your organization',
            r'your team',
            r'your mission',
            r'your values',
            r'your projects?',
            r'your products?',
            r'your services?',
            r'your clients?',
            r'your customers?',
            r'your website',
            r'your reputation',
            r'your commitment',
            r'your dedication',
            r'your focus',
            r'your approach',
            r'your work (?:in|on)'
        ]
        
        # Common filler phrases that indicate generic content
        self.generic_phrases = [
            r'hard[ -]working',
            r'team player',
            r'detail oriented',
            r'excellent communication skills',
            r'good communicat(?:ion|or)',
            r'people person',
            r'self[ -]motivated',
            r'fast learner',
            r'think outside the box',
            r'hit the ground running',
            r'valuable asset',
            r'perfect fit',
            r'esteemed organization',
            r'prestigious company'
        ]
    
    def analyze_cover_letter_file(self, file_path):
        """
        Analyze a cover letter from a file path.
        
        Args:
            file_path (str): Path to the cover letter file
            
        Returns:
            dict: Analysis results
        """
        try:
            # Extract text from the file
            text = self.document_parser.extract_text(file_path)
            if not text:
                return {
                    'error': 'Could not extract text from the file. The file may be empty, corrupted, or password-protected.',
                    'is_valid': False
                }
            
            # Analyze the extracted text
            return self.analyze_cover_letter_text(text)
            
        except Exception as e:
            logger.error(f"Error analyzing cover letter file {file_path}: {str(e)}")
            return {
                'error': f"Error analyzing cover letter: {str(e)}",
                'is_valid': False
            }
    
    def analyze_cover_letter_file_object(self, file_object, file_name):
        """
        Analyze a cover letter from a file object (e.g., uploaded file).
        
        Args:
            file_object: File-like object containing the cover letter
            file_name (str): Original filename with extension
            
        Returns:
            dict: Analysis results
        """
        try:
            # Extract text from the file object
            text = self.document_parser.extract_text_from_file_object(file_object, file_name)
            if not text:
                return {
                    'error': 'Could not extract text from the file. The file may be empty, corrupted, or password-protected.',
                    'is_valid': False
                }
            
            # Analyze the extracted text
            return self.analyze_cover_letter_text(text)
            
        except Exception as e:
            logger.error(f"Error analyzing cover letter file {file_name}: {str(e)}")
            return {
                'error': f"Error analyzing cover letter: {str(e)}",
                'is_valid': False
            }
    
    def analyze_cover_letter_text(self, text, job_description=None, company_name=None):
        """
        Analyze cover letter text content.
        
        Args:
            text (str): Text content of the cover letter
            job_description (str, optional): Job description for relevance analysis
            company_name (str, optional): Company name for personalization analysis
            
        Returns:
            dict: Analysis results
        """
        # First validate that this is a cover letter
        validation = self._validate_cover_letter(text)
        
        if not validation.get('is_valid_cover_letter', False):
            return {
                'is_valid': False,
                'error': validation.get('error', 'The document does not appear to be a valid cover letter.'),
                'document_type': validation.get('document_type', 'unknown'),
                'confidence': validation.get('confidence', 0)
            }
        
        # Process the document to extract sections and entities
        processed_doc = self.text_processor.process_document(text, 'cover_letter')
        
        # Analyze structure and content
        structure_analysis = self._analyze_structure(text, processed_doc)
        content_analysis = self._analyze_content(text, processed_doc)
        
        # Analyze personalization 
        personalization_score, personalization_details = self._analyze_personalization(text, company_name)
        
        # Analyze job relevance if job description is provided
        relevance_score = 0
        relevance_details = {}
        if job_description:
            relevance_score, relevance_details = self._analyze_job_relevance(text, job_description)
        
        # Calculate overall score
        structure_weight = 0.3
        content_weight = 0.4
        personalization_weight = 0.3
        
        overall_score = int((
            structure_analysis['structure_score'] * structure_weight +
            content_analysis['content_score'] * content_weight +
            personalization_score * personalization_weight
        ))
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            structure_analysis, 
            content_analysis, 
            personalization_details,
            relevance_details
        )
        
        # Prepare the analysis results
        analysis = {
            'is_valid': True,
            'document_type': 'cover_letter',
            'confidence': validation.get('confidence', 0.8),
            'structure_analysis': structure_analysis,
            'content_analysis': content_analysis,
            'personalization': {
                'score': personalization_score,
                'details': personalization_details
            },
            'overall_score': overall_score,
            'suggestions': recommendations,
            'word_count': len(text.split())
        }
        
        # Add job relevance if job description was provided
        if job_description:
            analysis['job_relevance'] = {
                'score': relevance_score,
                'details': relevance_details
            }
        
        return analysis
    
    def _validate_cover_letter(self, text):
        """
        Validate if the text is a cover letter.
        
        Args:
            text (str): Text content to validate
            
        Returns:
            dict: Validation results
        """
        # Use the content validator to check document type
        validation = self.content_validator.validate_document(text)
        
        # If it's already identified as a cover letter with medium confidence, accept it
        if validation['document_type'] == 'cover_letter' and validation['confidence'] >= self.content_validator.MEDIUM_CONFIDENCE:
            return {
                'is_valid_cover_letter': True,
                'confidence': validation['confidence'],
                'document_type': 'cover_letter'
            }
        
        # Secondary validation specific to cover letters
        is_cover_letter = False
        confidence = 0.0
        
        # Check for specific cover letter elements
        has_greeting = bool(re.search(self.section_patterns['greeting'], text.lower()))
        has_intro = bool(re.search(self.section_patterns['intro'], text.lower()))
        has_closing = bool(re.search(self.section_patterns['closing'], text.lower()))
        
        # Check for high usage of first-person pronouns
        first_person_count = len(re.findall(r'\b(?:I|me|my|mine|myself)\b', text))
        word_count = len(text.split())
        first_person_ratio = first_person_count / word_count if word_count > 0 else 0
        
        # Calculate confidence score
        score = 0.0
        if has_greeting: 
            score += 0.2
        if has_intro: 
            score += 0.2
        if has_closing: 
            score += 0.2
        if first_person_ratio > 0.03:  # More than 3% first-person pronouns
            score += 0.2
        
        # Additional indicators
        if "cover letter" in text.lower():
            score += 0.1
        if "position" in text.lower() and "apply" in text.lower():
            score += 0.1
            
        # Set results
        if score >= 0.5:
            is_cover_letter = True
            confidence = score
            
        return {
            'is_valid_cover_letter': is_cover_letter,
            'confidence': confidence,
            'document_type': 'cover_letter' if is_cover_letter else validation['document_type'],
            'error': None if is_cover_letter else "The document does not contain typical cover letter elements."
        }
    
    def _analyze_structure(self, text, processed_doc):
        """
        Analyze the structure of the cover letter.
        
        Args:
            text (str): Cover letter text
            processed_doc (dict): Processed document data
            
        Returns:
            dict: Structure analysis results
        """
        structure_results = {
            'has_greeting': False,
            'has_introduction': False,
            'has_body': False,
            'has_closing': False,
            'sections_present': [],
            'sections_missing': [],
            'structure_score': 0
        }
        
        # Check for each key section
        text_lower = text.lower()
        
        # Greeting section
        greeting_match = re.search(self.section_patterns['greeting'], text_lower)
        if greeting_match:
            structure_results['has_greeting'] = True
            structure_results['sections_present'].append('greeting')
            structure_results['greeting_text'] = greeting_match.group(0).strip()
        else:
            structure_results['sections_missing'].append('greeting')
        
        # Introduction section
        intro_match = re.search(self.section_patterns['intro'], text_lower)
        if intro_match:
            structure_results['has_introduction'] = True
            structure_results['sections_present'].append('introduction')
            structure_results['introduction_text'] = intro_match.group(0).strip()
        else:
            structure_results['sections_missing'].append('introduction')
        
        # Body section
        body_match = re.search(self.section_patterns['body'], text_lower)
        if body_match:
            structure_results['has_body'] = True
            structure_results['sections_present'].append('body')
        else:
            structure_results['sections_missing'].append('body')
        
        # Closing section
        closing_match = re.search(self.section_patterns['closing'], text_lower)
        if closing_match:
            structure_results['has_closing'] = True
            structure_results['sections_present'].append('closing')
            structure_results['closing_text'] = closing_match.group(0).strip()
        else:
            structure_results['sections_missing'].append('closing')
        
        # Additional check for signature
        signature_patterns = [
            r'Sincerely,\s*\n\s*([A-Z][a-z]+ [A-Z][a-z]+)',
            r'Regards,\s*\n\s*([A-Z][a-z]+ [A-Z][a-z]+)',
            r'Best,\s*\n\s*([A-Z][a-z]+ [A-Z][a-z]+)',
            r'Yours truly,\s*\n\s*([A-Z][a-z]+ [A-Z][a-z]+)',
            r'Respectfully,\s*\n\s*([A-Z][a-z]+ [A-Z][a-z]+)'
        ]
        
        has_signature = False
        for pattern in signature_patterns:
            if re.search(pattern, text):
                has_signature = True
                structure_results['sections_present'].append('signature')
                break
        
        if not has_signature:
            structure_results['sections_missing'].append('signature')
        
        # Calculate structure score
        structure_score = 0
        
        # Score based on sections present
        section_count = len(structure_results['sections_present'])
        if section_count >= 5:  # All sections present
            structure_score = 100
        elif section_count == 4:
            structure_score = 85
        elif section_count == 3:
            structure_score = 70
        elif section_count == 2:
            structure_score = 50
        elif section_count == 1:
            structure_score = 30
        else:
            structure_score = 10
        
        # Reduce score if key sections are missing
        if not structure_results['has_greeting']:
            structure_score -= 15
        if not structure_results['has_introduction']:
            structure_score -= 20
        if not structure_results['has_body']:
            structure_score -= 30
        if not structure_results['has_closing']:
            structure_score -= 15
        
        # Ensure score is within bounds
        structure_results['structure_score'] = max(0, min(100, structure_score))
        
        # Add structure evaluation
        if structure_results['structure_score'] >= 90:
            structure_results['evaluation'] = "Excellent structure with all necessary sections"
        elif structure_results['structure_score'] >= 75:
            structure_results['evaluation'] = "Good structure with most key sections present"
        elif structure_results['structure_score'] >= 50:
            structure_results['evaluation'] = "Adequate structure but some important sections are missing"
        else:
            structure_results['evaluation'] = "Poor structure, missing multiple critical sections"
        
        return structure_results
    
    def _analyze_content(self, text, processed_doc):
        """
        Analyze the content quality of the cover letter.
        
        Args:
            text (str): Cover letter text
            processed_doc (dict): Processed document data
            
        Returns:
            dict: Content analysis results
        """
        content_results = {
            'length_analysis': {},
            'language_quality': {},
            'achievements': [],
            'skills_mentioned': [],
            'generic_phrases': [],
            'content_score': 0
        }
        
        # Analyze length
        word_count = len(text.split())
        content_results['length_analysis']['word_count'] = word_count
        
        if word_count < 150:
            content_results['length_analysis']['evaluation'] = "Too short"
            content_results['length_analysis']['score'] = 30
        elif word_count < 250:
            content_results['length_analysis']['evaluation'] = "Slightly short"
            content_results['length_analysis']['score'] = 70
        elif word_count < 500:
            content_results['length_analysis']['evaluation'] = "Good length"
            content_results['length_analysis']['score'] = 100
        elif word_count < 600:
            content_results['length_analysis']['evaluation'] = "Slightly long"
            content_results['length_analysis']['score'] = 80
        else:
            content_results['length_analysis']['evaluation'] = "Too long"
            content_results['length_analysis']['score'] = 40
        
        # Analyze paragraph structure
        paragraphs = [p for p in text.split('\n\n') if p.strip()]
        content_results['length_analysis']['paragraph_count'] = len(paragraphs)
        
        if len(paragraphs) < 3:
            content_results['length_analysis']['paragraph_evaluation'] = "Too few paragraphs"
        elif len(paragraphs) > 7:
            content_results['length_analysis']['paragraph_evaluation'] = "Too many paragraphs"
        else:
            content_results['length_analysis']['paragraph_evaluation'] = "Good paragraph structure"
        
        # Analyze language quality
        content_results['language_quality']['sentence_count'] = len(self.text_processor.tokenize_sentences(text))
        
        # Check for achievement statements
        achievement_indicators = [
            r'(?:accomplished|achieved|completed|created|delivered|developed|established|founded|implemented|improved|increased|launched|led|managed|organized|produced|reduced|spearheaded|streamlined|succeeded|won)'
        ]
        
        achievements = []
        for indicator in achievement_indicators:
            matches = re.finditer(indicator, text, re.IGNORECASE)
            for match in matches:
                # Get the context around the achievement
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 100)
                achievement_context = text[start:end]
                
                # Clean up the context
                achievement_context = re.sub(r'\s+', ' ', achievement_context).strip()
                
                # Add if not duplicate
                if achievement_context not in achievements:
                    achievements.append(achievement_context)
        
        content_results['achievements'] = achievements[:5]  # Limit to top 5
        content_results['achievement_count'] = len(content_results['achievements'])
        
        # Check for skills mentioned
        mentioned_skills = []
        for skill in self.all_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
                mentioned_skills.append(skill)
        
        content_results['skills_mentioned'] = mentioned_skills[:10]  # Limit to top 10
        content_results['skill_count'] = len(content_results['skills_mentioned'])
        
        # Check for generic phrases
        generic_phrases_found = []
        for phrase in self.generic_phrases:
            if re.search(phrase, text.lower()):
                match = re.search(phrase, text.lower())
                generic_phrases_found.append(text[match.start():match.end()])
        
        content_results['generic_phrases'] = generic_phrases_found
        content_results['generic_phrase_count'] = len(content_results['generic_phrases'])
        
        # Calculate content score
        content_score = 0
        
        # Score based on length
        content_score += content_results['length_analysis']['score'] * 0.2
        
        # Score based on achievements
        if content_results['achievement_count'] >= 3:
            content_score += 25
        elif content_results['achievement_count'] >= 1:
            content_score += 15
        
        # Score based on skills mentioned
        if content_results['skill_count'] >= 5:
            content_score += 20
        elif content_results['skill_count'] >= 3:
            content_score += 15
        elif content_results['skill_count'] >= 1:
            content_score += 5
        
        # Penalize for generic phrases
        generic_penalty = min(30, content_results['generic_phrase_count'] * 10)
        content_score = max(0, content_score - generic_penalty)
        
        # Additional content quality checks
        sentences = self.text_processor.tokenize_sentences(text)
        
        # Check for sentence variety (length)
        if sentences:
            sentence_lengths = [len(s.split()) for s in sentences]
            avg_length = sum(sentence_lengths) / len(sentence_lengths)
            length_variance = sum((length - avg_length) ** 2 for length in sentence_lengths) / len(sentence_lengths)
            
            # Good writing has some sentence length variance
            if length_variance >= 15:
                content_score += 15
                content_results['language_quality']['sentence_variety'] = "Good sentence length variety"
            elif length_variance >= 5:
                content_score += 5
                content_results['language_quality']['sentence_variety'] = "Some sentence length variety"
            else:
                content_results['language_quality']['sentence_variety'] = "Poor sentence length variety"
        
        # Ensure score is within bounds
        content_results['content_score'] = max(0, min(100, content_score))
        
        # Add content evaluation
        if content_results['content_score'] >= 90:
            content_results['evaluation'] = "Excellent content with specific achievements and relevant skills"
        elif content_results['content_score'] >= 75:
            content_results['evaluation'] = "Good content with some specific details"
        elif content_results['content_score'] >= 50:
            content_results['evaluation'] = "Adequate content but lacks specificity"
        else:
            content_results['evaluation'] = "Poor content with generic phrases and little substance"
        
        return content_results
    
    def _analyze_personalization(self, text, company_name=None):
        """
        Analyze the level of personalization in the cover letter.
        
        Args:
            text (str): Cover letter text
            company_name (str, optional): Company name for more specific analysis
            
        Returns:
            tuple: (personalization score, personalization details)
        """
        personalization_details = {
            'company_mentions': 0,
            'specific_company_knowledge': [],
            'personalization_indicators': [],
            'evaluation': ''
        }
        
        # Check for company name mentions
        if company_name:
            company_pattern = re.escape(company_name)
            company_mentions = len(re.findall(company_pattern, text, re.IGNORECASE))
            personalization_details['company_mentions'] = company_mentions
        else:
            # Look for generic company mentions
            company_patterns = [
                r'your company', r'your organization', r'your firm',
                r'your business', r'your team', r'your department'
            ]
            
            company_mentions = 0
            for pattern in company_patterns:
                company_mentions += len(re.findall(pattern, text, re.IGNORECASE))
            
            personalization_details['company_mentions'] = company_mentions
        
        # Check for personalization indicators
        found_indicators = []
        for indicator in self.personalization_indicators:
            matches = re.findall(indicator, text, re.IGNORECASE)
            if matches:
                found_indicators.append(indicator.replace(r'\b', '').replace(r'(?:', '').replace(r')?', '').replace(r'[s]?', 's'))
        
        personalization_details['personalization_indicators'] = found_indicators
        
        # Calculate personalization score
        personalization_score = 0
        
        # Score based on company mentions
        if personalization_details['company_mentions'] >= 3:
            personalization_score += 30
        elif personalization_details['company_mentions'] >= 1:
            personalization_score += 15
        
        # Score based on personalization indicators
        if len(found_indicators) >= 5:
            personalization_score += 50
        elif len(found_indicators) >= 3:
            personalization_score += 30
        elif len(found_indicators) >= 1:
            personalization_score += 10
        
        # Look for specific company knowledge
        specific_knowledge_patterns = [
            r'your (?:recent|latest) (?:product|project|initiative|announcement)',
            r'your (?:mission|vision) statement',
            r'your (?:blog|article|interview|talk) (?:about|on)',
            r'your commitment to',
            r'your reputation for',
            r'your work (?:in|on) (?:the|your)'
        ]
        
        specific_knowledge = []
        for pattern in specific_knowledge_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            specific_knowledge.extend(matches)
        
        personalization_details['specific_company_knowledge'] = specific_knowledge
        
        # Score based on specific knowledge
        if len(specific_knowledge) >= 2:
            personalization_score += 20
        elif len(specific_knowledge) >= 1:
            personalization_score += 10
        
        # Ensure score is within bounds
        personalization_score = max(0, min(100, personalization_score))
        
        # Add personalization evaluation
        if personalization_score >= 80:
            personalization_details['evaluation'] = "Excellent personalization with specific company knowledge"
        elif personalization_score >= 60:
            personalization_details['evaluation'] = "Good personalization with company mentions"
        elif personalization_score >= 40:
            personalization_details['evaluation'] = "Some personalization but could be more specific"
        else:
            personalization_details['evaluation'] = "Little to no personalization, appears to be a generic cover letter"
        
        return personalization_score, personalization_details
    
    def _analyze_job_relevance(self, text, job_description):
        """
        Analyze how well the cover letter aligns with the job description.
        
        Args:
            text (str): Cover letter text
            job_description (str): Job description text
            
        Returns:
            tuple: (relevance score, relevance details)
        """
        relevance_details = {
            'job_keywords_matched': [],
            'job_keywords_missed': [],
            'skill_alignment': 0.0,
            'evaluation': ''
        }
        
        # Process job description to extract important keywords
        job_tokens = self.text_processor.tokenize_words(job_description.lower())
        job_tokens = self.text_processor.remove_stopwords(job_tokens)
        
        # Count keyword frequency in job description
        keyword_counts = defaultdict(int)
        for token in job_tokens:
            if len(token) > 3:  # Ignore very short words
                keyword_counts[token] += 1
        
        # Get top job keywords
        job_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
        job_keywords = [k for k, v in job_keywords[:20]]  # Top 20 keywords
        
        # Check for keyword matches in cover letter
        letter_text = text.lower()
        matched_keywords = []
        missed_keywords = []
        
        for keyword in job_keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', letter_text):
                matched_keywords.append(keyword)
            else:
                missed_keywords.append(keyword)
        
        relevance_details['job_keywords_matched'] = matched_keywords
        relevance_details['job_keywords_missed'] = missed_keywords
        
        # Calculate skill alignment
        if job_keywords:
            relevance_details['skill_alignment'] = len(matched_keywords) / len(job_keywords)
        
        # Calculate relevance score
        relevance_score = 0
        
        # Score based on keyword matches
        if job_keywords:
            match_percent = len(matched_keywords) / len(job_keywords)
            relevance_score = int(match_percent * 100)
        
        # Ensure score is within bounds
        relevance_score = max(0, min(100, relevance_score))
        
        # Add relevance evaluation
        if relevance_score >= 80:
            relevance_details['evaluation'] = "Excellent alignment with job requirements"
        elif relevance_score >= 60:
            relevance_details['evaluation'] = "Good alignment, matches many job keywords"
        elif relevance_score >= 40:
            relevance_details['evaluation'] = "Fair alignment, matches some job keywords"
        else:
            relevance_details['evaluation'] = "Poor alignment, few job keywords matched"
        
        return relevance_score, relevance_details
    
    def _load_templates(self) -> Dict[str, Dict[str, Dict[str, str]]]:
        """
        Load cover letter templates for different industries, job types, and experience levels.
        
        Returns:
            Dict with templates organized by industry, job type, and experience level
        """
        # Templates organized by industry > job type > experience level
        templates = {
            # Technology industry templates
            "technology": {
                "software_engineer": {
                    "entry": """
I am writing to express my interest in the {job_title} position at {company_name}. As a recent graduate with a background in {skills_string}, I am eager to begin my career at a forward-thinking company like yours.

During my studies and internships, I developed strong technical skills in {skills_to_highlight} and a passion for solving complex problems. {company_name}'s commitment to {company_value} particularly resonates with me, and I believe my fresh perspective and enthusiasm would be valuable to your team.

My academic projects have prepared me well for this role:
• {academic_project_1}
• Successfully collaborated with peers on team programming assignments
• {academic_project_2}
• Constantly learned new technologies and programming languages

I'm excited about the opportunity to grow professionally at {company_name} and contribute to your innovative projects. I would welcome the chance to discuss how my education and technical aptitude align with your needs.
""",
                    "mid": """
I am writing to express my interest in the {job_title} position at {company_name}. With {years_experience} years of experience in software development and expertise in {skills_string}, I am confident in my ability to make an immediate contribution to your engineering team.

Throughout my career at {previous_company}, I have successfully:
• Developed and maintained {specific_achievement_1}
• Collaborated with cross-functional teams to deliver {specific_achievement_2}
• Applied my expertise in {skills_to_highlight} to solve complex technical challenges
• Consistently met project deadlines while maintaining code quality

I am particularly drawn to {company_name}'s work on {company_project} and your commitment to {company_value}. Your approach to {industry_trend} aligns perfectly with my professional interests and strengths.

I would welcome the opportunity to discuss how my experience and technical skills would benefit {company_name}. I am confident that my problem-solving abilities and technical expertise would make me a valuable addition to your team.
""",
                    "senior": """
I am writing to express my interest in the Senior {job_title} position at {company_name}. With over {years_experience} years of experience leading software development projects and deep expertise in {skills_string}, I am well-positioned to help drive your technical initiatives forward.

In my current role as {current_role} at {previous_company}, I have:
• Led the development of {specific_achievement_1}, resulting in {quantifiable_result_1}
• Architected and implemented {specific_achievement_2}, which {quantifiable_result_2}
• Mentored junior developers and established best practices for {skills_to_highlight}
• Successfully managed complex projects from conception to deployment

I've been following {company_name}'s innovations in {company_specialty}, and I'm impressed by your approach to {industry_challenge}. My experience with {relevant_experience} would allow me to contribute significantly to these efforts.

I'm excited about the opportunity to bring my technical leadership and strategic thinking to {company_name}. I would welcome the chance to discuss how my background and accomplishments align with your goals for this senior position.
"""
                },
                "data_scientist": {
                    "entry": """
I am writing to express my interest in the {job_title} position at {company_name}. As a recent graduate with a strong foundation in statistics, machine learning, and programming in {skills_string}, I am eager to apply my analytical skills at an innovative company like yours.

During my academic career, I:
• Completed research projects using {skills_to_highlight} to analyze complex datasets
• Developed predictive models for {academic_project}
• Gained hands-on experience with data visualization and statistical analysis
• Collaborated on team projects focusing on real-world applications of data science

I'm particularly drawn to {company_name}'s data-driven approach to {company_specialty} and believe my educational background and enthusiasm for extracting insights from data would make me a valuable team member.

I would welcome the opportunity to discuss how my analytical skills and fresh perspective could contribute to {company_name}'s data initiatives.
""",
                    "mid": """
I am writing to express my interest in the {job_title} position at {company_name}. With {years_experience} years of experience applying data science techniques to business problems and expertise in {skills_string}, I am confident in my ability to deliver valuable insights for your organization.

In my current role at {previous_company}, I have:
• Designed and implemented {specific_achievement_1}, resulting in {quantifiable_result_1}
• Built and deployed machine learning models that {specific_achievement_2}
• Leveraged my expertise in {skills_to_highlight} to uncover actionable business insights
• Effectively communicated complex findings to stakeholders at all levels

{company_name}'s innovative work in {company_specialty} particularly interests me, and I believe my experience with similar challenges in {relevant_experience} would allow me to contribute immediately to your data science initiatives.

I would welcome the opportunity to discuss how my analytical skills and business acumen could help drive data-informed decisions at {company_name}.
""",
                    "senior": """
I am writing to express my interest in the Senior {job_title} position at {company_name}. With over {years_experience} years of experience leading data science teams and projects, and deep expertise in {skills_string}, I am well-positioned to help drive your data initiatives to new heights.

As {current_role} at {previous_company}, I have:
• Led a team that developed {specific_achievement_1}, driving {quantifiable_result_1}
• Architected end-to-end machine learning systems that {specific_achievement_2}
• Established data science best practices and mentored junior data scientists
• Translated complex business problems into technical solutions with measurable impact

I've been following {company_name}'s pioneering work in {company_specialty} and am impressed by your commitment to {company_value}. My experience with {relevant_experience} would enable me to make significant contributions to these initiatives.

I would welcome the opportunity to discuss how my leadership in data science and strategic approach to analytics could further {company_name}'s goals in this senior position.
"""
                }
            },
            
            # Healthcare industry templates
            "healthcare": {
                "registered_nurse": {
                    "entry": """
I am writing to express my interest in the {job_title} position at {company_name}. As a recently licensed nurse with training in {skills_string}, I am eager to begin my nursing career at a respected healthcare facility like yours.

During my clinical rotations, I developed strong skills in patient care, medical documentation, and healthcare technologies. I am particularly drawn to {company_name}'s commitment to {company_value} and patient-centered care.

My clinical experience has prepared me well for this role:
• Completed clinical rotations in {clinical_area_1} and {clinical_area_2}
• Developed proficiency in {skills_to_highlight} and patient assessment
• Demonstrated strong communication skills with patients and healthcare teams
• Committed to continuing education and evidence-based practice

I am excited about the opportunity to grow professionally at {company_name} and contribute to your mission of providing exceptional patient care. I would welcome the chance to discuss how my education and clinical experience align with your needs.
""",
                    "mid": """
I am writing to express my interest in the {job_title} position at {company_name}. With {years_experience} years of nursing experience and specialization in {skills_string}, I am confident in my ability to provide excellent patient care and contribute to your healthcare team.

In my current role at {previous_company}, I have:
• Provided direct patient care in {clinical_area}, maintaining high patient satisfaction
• Implemented {specific_achievement_1} that improved {quantifiable_result_1}
• Applied my expertise in {skills_to_highlight} to ensure positive patient outcomes
• Collaborated effectively with interdisciplinary healthcare teams

I am particularly drawn to {company_name}'s reputation for {company_value} and your innovative approaches to {healthcare_specialty}. Your commitment to quality care aligns perfectly with my professional values and nursing philosophy.

I would welcome the opportunity to discuss how my clinical experience and patient-centered approach would benefit {company_name} and the patients you serve.
""",
                    "senior": """
I am writing to express my interest in the Senior {job_title} position at {company_name}. With over {years_experience} years of nursing experience, leadership roles, and expertise in {skills_string}, I am well-positioned to help advance your clinical excellence initiatives.

As {current_role} at {previous_company}, I have:
• Led nursing teams that achieved {specific_achievement_1}, resulting in {quantifiable_result_1}
• Implemented evidence-based practices that {specific_achievement_2}
• Mentored new nurses and developed continuing education programs
• Collaborated with physicians and administrators to improve patient care processes

I've been following {company_name}'s advancements in {healthcare_specialty}, and I'm impressed by your commitment to {company_value}. My experience with {relevant_experience} would allow me to contribute significantly to these efforts.

I would welcome the opportunity to discuss how my clinical leadership and dedication to nursing excellence could further {company_name}'s mission of providing exceptional healthcare.
"""
                },
                "physician": {
                    "mid": """
I am writing to express my interest in the {job_title} position at {company_name}. With {years_experience} years of clinical experience specializing in {skills_string}, I am confident in my ability to provide exceptional patient care and contribute to your medical team.

In my current position at {previous_company}, I have:
• Provided comprehensive care to patients with diverse medical needs
• Implemented {specific_achievement_1} that improved {quantifiable_result_1}
• Utilized my expertise in {skills_to_highlight} to ensure accurate diagnoses and effective treatments
• Collaborated successfully with interdisciplinary healthcare teams

I am particularly drawn to {company_name}'s commitment to {company_value} and your innovative approaches to {healthcare_specialty}. Your focus on evidence-based medicine aligns perfectly with my practice philosophy.

I would welcome the opportunity to discuss how my clinical expertise and patient-centered approach would benefit {company_name} and the patients you serve.
""",
                    "senior": """
I am writing to express my interest in the {job_title} position at {company_name}. With over {years_experience} years of clinical practice, leadership roles, and specialization in {skills_string}, I am well-positioned to help advance your medical excellence initiatives.

As {current_role} at {previous_company}, I have:
• Led clinical teams that achieved {specific_achievement_1}, resulting in {quantifiable_result_1}
• Implemented innovative treatment protocols that {specific_achievement_2}
• Mentored medical residents and contributed to medical education programs
• Collaborated with hospital administration to improve patient care processes

I've been following {company_name}'s advancements in {healthcare_specialty}, and I'm impressed by your commitment to {company_value}. My experience with {relevant_experience} would allow me to contribute significantly to these efforts.

I would welcome the opportunity to discuss how my clinical expertise and leadership could further {company_name}'s mission of providing exceptional healthcare.
"""
                }
            },
            
            # Education industry templates
            "education": {
                "teacher": {
                    "entry": """
I am writing to express my interest in the {job_title} position at {company_name}. As a recently certified teacher with training in {skills_string}, I am eager to begin my teaching career at a respected educational institution like yours.

During my student teaching experience, I developed strong skills in curriculum development, classroom management, and educational technologies. I am particularly drawn to {company_name}'s commitment to {company_value} and student-centered learning.

My educational experience has prepared me well for this role:
• Completed student teaching in {subject_area} for grades {grade_levels}
• Developed and implemented lesson plans focused on {skills_to_highlight}
• Created inclusive classroom environments for diverse student populations
• Utilized educational technology to enhance student engagement and learning

I am excited about the opportunity to grow professionally at {company_name} and contribute to your mission of providing excellent education. I would welcome the chance to discuss how my education and teaching experience align with your needs.
""",
                    "mid": """
I am writing to express my interest in the {job_title} position at {company_name}. With {years_experience} years of teaching experience in {subject_area} and expertise in {skills_string}, I am confident in my ability to engage students and contribute to your educational team.

In my current role at {previous_company}, I have:
• Developed and implemented curriculum that improved student achievement in {subject_area}
• Created {specific_achievement_1} that enhanced {quantifiable_result_1}
• Applied my expertise in {skills_to_highlight} to support diverse learning needs
• Collaborated effectively with colleagues, administrators, and parents

I am particularly drawn to {company_name}'s reputation for {company_value} and your innovative approaches to {educational_specialty}. Your commitment to student success aligns perfectly with my teaching philosophy.

I would welcome the opportunity to discuss how my classroom experience and student-centered approach would benefit {company_name} and the students you serve.
""",
                    "senior": """
I am writing to express my interest in the {job_title} position at {company_name}. With over {years_experience} years of teaching experience, leadership roles, and expertise in {skills_string}, I am well-positioned to help advance your educational excellence initiatives.

As {current_role} at {previous_company}, I have:
• Led departmental teams that achieved {specific_achievement_1}, resulting in {quantifiable_result_1}
• Developed innovative teaching methodologies that {specific_achievement_2}
• Mentored new teachers and created professional development programs
• Collaborated with administrators to improve curriculum and educational outcomes

I've been following {company_name}'s advancements in {educational_specialty}, and I'm impressed by your commitment to {company_value}. My experience with {relevant_experience} would allow me to contribute significantly to these efforts.

I would welcome the opportunity to discuss how my educational leadership and dedication to teaching excellence could further {company_name}'s mission of providing exceptional education.
"""
                },
                "administrator": {
                    "mid": """
I am writing to express my interest in the {job_title} position at {company_name}. With {years_experience} years of experience in educational administration and expertise in {skills_string}, I am confident in my ability to provide effective leadership and contribute to your institution's success.

In my current role at {previous_company}, I have:
• Overseen {specific_achievement_1} that improved {quantifiable_result_1}
• Implemented policies and programs that {specific_achievement_2}
• Applied my expertise in {skills_to_highlight} to enhance educational outcomes
• Collaborated effectively with teachers, staff, students, and parents

I am particularly drawn to {company_name}'s reputation for {company_value} and your innovative approaches to {educational_specialty}. Your commitment to educational excellence aligns perfectly with my administrative philosophy.

I would welcome the opportunity to discuss how my administrative experience and educational leadership would benefit {company_name} and the community you serve.
""",
                    "senior": """
I am writing to express my interest in the {job_title} position at {company_name}. With over {years_experience} years of experience in educational leadership and administration, including expertise in {skills_string}, I am well-positioned to help advance your institutional excellence initiatives.

As {current_role} at {previous_company}, I have:
• Led educational initiatives that achieved {specific_achievement_1}, resulting in {quantifiable_result_1}
• Implemented strategic plans that {specific_achievement_2}
• Mentored educational leaders and developed professional growth programs
• Collaborated with stakeholders to improve educational systems and outcomes

I've been following {company_name}'s advancements in {educational_specialty}, and I'm impressed by your commitment to {company_value}. My experience with {relevant_experience} would allow me to contribute significantly to these efforts.

I would welcome the opportunity to discuss how my administrative expertise and educational vision could further {company_name}'s mission of providing exceptional education.
"""
                }
            },
            
            # Finance industry templates
            "finance": {
                "financial_analyst": {
                    "entry": """
I am writing to express my interest in the {job_title} position at {company_name}. As a recent finance graduate with strong analytical skills and knowledge of {skills_string}, I am eager to begin my career at a respected financial institution like yours.

During my academic career, I developed solid skills in financial analysis, modeling, and research. I am particularly drawn to {company_name}'s reputation for {company_value} and your innovative approaches to financial services.

My educational background has prepared me well for this role:
• Completed coursework in {finance_course_1} and {finance_course_2}
• Developed proficiency in {skills_to_highlight} and financial modeling
• Conducted research projects analyzing market trends and investment opportunities
• Demonstrated strong attention to detail and analytical thinking

I am excited about the opportunity to grow professionally at {company_name} and contribute to your financial success. I would welcome the chance to discuss how my education and analytical skills align with your needs.
""",
                    "mid": """
I am writing to express my interest in the {job_title} position at {company_name}. With {years_experience} years of experience in financial analysis and expertise in {skills_string}, I am confident in my ability to provide valuable insights and contribute to your financial team.

In my current role at {previous_company}, I have:
• Conducted in-depth financial analyses that improved {quantifiable_result_1}
• Developed {specific_achievement_1} that enhanced {quantifiable_result_2}
• Applied my expertise in {skills_to_highlight} to identify financial opportunities
• Collaborated effectively with cross-functional teams on financial planning

I am particularly drawn to {company_name}'s reputation in the {financial_specialty} sector and your innovative approaches to {industry_trend}. Your commitment to financial excellence aligns perfectly with my professional goals.

I would welcome the opportunity to discuss how my analytical skills and financial expertise would benefit {company_name} and support your strategic objectives.
""",
                    "senior": """
I am writing to express my interest in the Senior {job_title} position at {company_name}. With over {years_experience} years of experience in financial analysis and leadership, including expertise in {skills_string}, I am well-positioned to help advance your financial strategies.

As {current_role} at {previous_company}, I have:
• Led financial initiatives that achieved {specific_achievement_1}, resulting in {quantifiable_result_1}
• Implemented analytical frameworks that {specific_achievement_2}
• Mentored financial analysts and developed team capabilities
• Collaborated with executive leadership to drive strategic financial decisions

I've been following {company_name}'s performance in {financial_specialty}, and I'm impressed by your approach to {industry_trend}. My experience with {relevant_experience} would allow me to contribute significantly to these efforts.

I would welcome the opportunity to discuss how my financial leadership and analytical expertise could further {company_name}'s financial objectives and strategic vision.
"""
                }
            },
            
            # Generic templates for other industries
            "default": {
                "default": {
                    "entry": """
I am writing to express my interest in the {job_title} position at {company_name}. As a recent graduate with a background in {skills_string}, I am eager to begin my career at a respected organization like yours.

During my studies, I developed strong skills in {skills_to_highlight} and a passion for {industry_interest}. I am particularly drawn to {company_name}'s commitment to {company_value} and your innovative work in your field.

My educational background has prepared me well for this role:
• Completed relevant coursework in {course_1} and {course_2}
• Gained practical experience through internships and projects
• Developed strong {skill_type} skills applicable to this position
• Demonstrated dedication to professional growth and learning

I am excited about the opportunity to grow professionally at {company_name} and contribute to your success. I would welcome the chance to discuss how my education and enthusiasm align with your needs.
""",
                    "mid": """
I am writing to express my interest in the {job_title} position at {company_name}. With {years_experience} years of professional experience and expertise in {skills_string}, I am confident in my ability to make a valuable contribution to your team.

In my current role at {previous_company}, I have:
• Successfully {specific_achievement_1} resulting in {quantifiable_result_1}
• Developed and implemented {specific_achievement_2}
• Applied my expertise in {skills_to_highlight} to solve complex problems
• Collaborated effectively with teams to achieve organizational goals

I am particularly drawn to {company_name}'s reputation for {company_value} and your innovative approaches to {industry_trend}. Your organizational focus aligns perfectly with my professional goals and strengths.

I would welcome the opportunity to discuss how my experience and skills would benefit {company_name} and support your continued success.
""",
                    "senior": """
I am writing to express my interest in the Senior {job_title} position at {company_name}. With over {years_experience} years of professional experience and leadership, including expertise in {skills_string}, I am well-positioned to help advance your organizational objectives.

As {current_role} at {previous_company}, I have:
• Led initiatives that achieved {specific_achievement_1}, resulting in {quantifiable_result_1}
• Implemented strategies that {specific_achievement_2}
• Mentored team members and developed departmental capabilities
• Collaborated with leadership to drive organizational success

I've been following {company_name}'s developments in {industry_specialty}, and I'm impressed by your commitment to {company_value}. My experience with {relevant_experience} would allow me to contribute significantly to these efforts.

I would welcome the opportunity to discuss how my leadership and expertise could further {company_name}'s mission and strategic goals.
"""
                },
                "internship": {
                    "entry": """
I am writing to express my interest in the {job_title} internship at {company_name}. As a student studying {education_field} with a passion for {skills_string}, I am eager to gain practical experience at an organization like yours.

Throughout my academic career, I have:
• Completed coursework in {course_1} and {course_2}
• Developed skills in {skills_to_highlight} through class projects
• Participated in {extracurricular_activity} to enhance my practical knowledge
• Demonstrated a strong work ethic and ability to learn quickly

I am particularly drawn to {company_name}'s work in {company_specialty} and your commitment to {company_value}. I believe that an internship with your organization would provide valuable experience while allowing me to contribute fresh perspectives.

I would welcome the opportunity to discuss how my educational background, enthusiasm, and growth mindset could benefit your team during this internship.
"""
                }
            }
        }
        
        return templates

    def generate_cover_letter(self, job_title: str, company_name: str, user_name: str,
                              skills: List[str] = None, years_experience: int = 0,
                              industry: str = "default", education_field: str = None,
                              previous_company: str = None, company_value: str = None,
                              job_description: str = None, template_type: str = None) -> Dict[str, Any]:
        """
        Generate a personalized cover letter based on job details and user profile.
        
        Args:
            job_title: The title of the job being applied for
            company_name: The name of the company
            user_name: The applicant's name
            skills: List of user's skills
            years_experience: Years of relevant experience
            industry: The industry sector (technology, healthcare, education, etc.)
            education_field: User's field of study or specialization
            previous_company: User's most recent company
            company_value: A value or mission of the target company
            job_description: The job description text
            template_type: Specific template to use (overrides automatic selection)
            
        Returns:
            Dictionary containing cover letter content and metadata
        """
        try:
            # Normalize industry and determine experience level
            industry = self._normalize_industry(industry) if industry else "default"
            experience_level = self._categorize_experience(years_experience)
            
            # Determine job category
            job_category = self._normalize_job_title(job_title) if job_title else "default"
            
            # Override with template_type if provided
            if template_type:
                if template_type in ["internship", "entry", "mid", "senior"]:
                    experience_level = template_type
                elif template_type in ["technology", "healthcare", "education", "finance"]:
                    industry = template_type
            
            # Get appropriate template
            template = self._get_template(industry, job_category, experience_level)
            
            # Process skills
            skills_string = ", ".join(skills[:5]) if skills else "relevant skills"
            skills_to_highlight = skills[:3] if skills else ["relevant skills"]
            
            # Set current date
            current_date = datetime.now().strftime("%B %d, %Y")
            
            # Extract company values or mission from job description if not provided
            if not company_value and job_description:
                company_value = self._extract_company_value(job_description, company_name)
            
            # Use placeholder if still empty
            if not company_value:
                company_value = "innovation and excellence"
                
            # Additional customization variables
            template_vars = {
                "job_title": job_title,
                "company_name": company_name,
                "user_name": user_name,
                "skills_string": skills_string,
                "skills_to_highlight": ", ".join(skills_to_highlight) if skills_to_highlight else "relevant skills",
                "years_experience": years_experience,
                "current_date": current_date,
                "previous_company": previous_company or "my previous company",
                "current_role": f"a {job_title}" if job_title else "a professional",
                "company_value": company_value,
                "company_specialty": self._extract_company_specialty(job_description, company_name) if job_description else "your field",
                "industry_trend": self._extract_industry_trend(industry) or "industry developments",
                "education_field": education_field or "my field",
                "relevant_experience": self._extract_relevant_experience(job_description, skills) if job_description and skills else "relevant areas"
            }
            
            # Handle industry-specific variables
            if industry == "technology":
                template_vars.update({
                    "academic_project_1": "Developed a full-stack web application with user authentication and database integration",
                    "academic_project_2": "Created machine learning models to solve real-world problems",
                    "specific_achievement_1": "scalable microservices architecture",
                    "specific_achievement_2": "products with improved user experiences",
                    "quantifiable_result_1": "a 30% increase in system performance",
                    "quantifiable_result_2": "reduced development time by 25%",
                    "company_project": "cutting-edge software solutions",
                    "industry_challenge": "technological innovation"
                })
            elif industry == "healthcare":
                template_vars.update({
                    "clinical_area_1": "medical-surgical",
                    "clinical_area_2": "intensive care",
                    "specific_achievement_1": "patient care protocols",
                    "specific_achievement_2": "improved patient outcomes",
                    "quantifiable_result_1": "increased patient satisfaction scores",
                    "quantifiable_result_2": "reduced readmission rates",
                    "healthcare_specialty": "patient-centered care",
                    "clinical_area": "patient care"
                })
            elif industry == "education":
                template_vars.update({
                    "subject_area": "core subjects",
                    "grade_levels": "K-12",
                    "specific_achievement_1": "curriculum innovations",
                    "specific_achievement_2": "improved student engagement",
                    "quantifiable_result_1": "increased student achievement",
                    "quantifiable_result_2": "higher graduation rates",
                    "educational_specialty": "student learning"
                })
            elif industry == "finance":
                template_vars.update({
                    "finance_course_1": "Financial Analysis",
                    "finance_course_2": "Investment Management",
                    "specific_achievement_1": "financial models",
                    "specific_achievement_2": "investment strategies",
                    "quantifiable_result_1": "portfolio performance",
                    "quantifiable_result_2": "risk assessment accuracy",
                    "financial_specialty": "financial services",
                    "industry_trend": "data-driven financial analysis"
                })
            else:
                template_vars.update({
                    "course_1": "relevant subjects",
                    "course_2": "professional development",
                    "specific_achievement_1": "implemented key initiatives",
                    "specific_achievement_2": "developed innovative solutions",
                    "quantifiable_result_1": "measurable improvements",
                    "quantifiable_result_2": "successful outcomes",
                    "industry_specialty": "your industry",
                    "extracurricular_activity": "relevant extracurricular activities"
                })
            
            # Format the cover letter using the template and variables
            formatted_content = self._format_template(template, template_vars)
            
            # Split into sections for better structure
            sections = self._split_cover_letter_into_sections(formatted_content)
            
            # Return the cover letter and metadata
            return {
                "full_text": formatted_content,
                "sections": sections,
                "word_count": len(formatted_content.split()),
                "template_used": f"{industry}_{job_category}_{experience_level}",
                "metadata": {
                    "job_title": job_title,
                    "company_name": company_name,
                    "industry": industry,
                    "experience_level": experience_level
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating cover letter: {str(e)}")
            # Provide a basic fallback cover letter
            return {
                "error": f"Could not generate detailed cover letter: {str(e)}",
                "full_text": self._get_fallback_cover_letter(user_name, job_title, company_name),
                "sections": {
                    "header": f"{datetime.now().strftime('%B %d, %Y')}",
                    "greeting": "Dear Hiring Manager,",
                    "body": f"I am writing to express my interest in the {job_title} position at {company_name}...",
                    "closing": f"Thank you for your consideration.\n\nSincerely,\n{user_name}"
                }
            }
    
    def _get_template(self, industry, job_category, experience_level):
        """Get the appropriate template based on industry, job category, and experience level."""
        # Try to get specific template
        if industry in self.templates and job_category in self.templates[industry] and experience_level in self.templates[industry][job_category]:
            return self.templates[industry][job_category][experience_level]
        
        # Try industry default for this experience level
        if industry in self.templates and "default" in self.templates[industry] and experience_level in self.templates[industry]["default"]:
            return self.templates[industry]["default"][experience_level]
        
        # Try general default for this experience level
        if experience_level in self.templates["default"]["default"]:
            return self.templates["default"]["default"][experience_level]
        
        # Ultimate fallback
        return self.templates["default"]["default"]["mid"]
    
    def _format_template(self, template, variables):
        """Format a template with the provided variables."""
        # Start with clean formatting
        template = template.strip()
        
        # Replace variables in the template
        for key, value in variables.items():
            template = template.replace(f"{{{key}}}", str(value))
        
        # Format the final content
        return self._clean_template_formatting(template)
    
    def _clean_template_formatting(self, text):
        """Clean up template formatting for better readability."""
        # Remove excessive blank lines
        cleaned = re.sub(r'\n{3,}', '\n\n', text)
        
        # Add proper line breaks before and after sections
        cleaned = re.sub(r'([.!?])\s*(\n+)', r'\1\n\n', cleaned)
        
        return cleaned
    
    def _split_cover_letter_into_sections(self, text):
        """Split a cover letter into logical sections."""
        lines = text.split('\n')
        sections = {}
        
        # First line is typically the date
        if lines and not lines[0].startswith(('Dear', 'To whom')):
            sections['header'] = lines[0]
            lines = lines[1:]
        
        # Find greeting line
        greeting_index = -1
        for i, line in enumerate(lines):
            if re.match(r'^\s*(?:Dear|To whom|Hello|Greetings)', line, re.IGNORECASE):
                greeting_index = i
                break
        
        if greeting_index >= 0:
            sections['greeting'] = lines[greeting_index]
            
            # Everything before greeting is header
            if greeting_index > 0:
                sections['header'] = '\n'.join(lines[:greeting_index])
            
            # Find closing line
            closing_index = -1
            for i in range(len(lines) - 1, greeting_index, -1):
                if re.match(r'^\s*(?:Thank you|Sincerely|Regards|Best|Yours|Respectfully)', lines[i], re.IGNORECASE):
                    closing_index = i
                    break
            
            if closing_index > greeting_index:
                # Body is everything between greeting and closing
                sections['body'] = '\n'.join(lines[greeting_index + 1:closing_index])
                
                # Closing is everything from closing line to the end
                sections['closing'] = '\n'.join(lines[closing_index:])
            else:
                # No clear closing found, assume everything after greeting is body
                sections['body'] = '\n'.join(lines[greeting_index + 1:])
        else:
            # No clear sections found, just split into thirds
            third = len(lines) // 3
            sections['header'] = '\n'.join(lines[:third])
            sections['body'] = '\n'.join(lines[third:third*2])
            sections['closing'] = '\n'.join(lines[third*2:])
        
        return sections
    
    def _normalize_industry(self, industry):
        """Normalize industry name for template selection."""
        if not industry:
            return "default"
            
        industry_lower = industry.lower()
        
        # Map common variations to standard names
        industry_mapping = {
            # Technology
            "tech": "technology",
            "it": "technology",
            "software": "technology",
            "development": "technology",
            "programming": "technology",
            
            # Healthcare
            "health": "healthcare",
            "medical": "healthcare",
            "hospital": "healthcare",
            "nursing": "healthcare",
            "clinical": "healthcare",
            
            # Education
            "school": "education",
            "teaching": "education",
            "academic": "education",
            "university": "education",
            "college": "education",
            
            # Finance
            "banking": "finance",
            "investment": "finance",
            "accounting": "finance",
            "financial": "finance",
            "insurance": "finance"
        }
        
        # Check for matches in mapping
        for key, value in industry_mapping.items():
            if key in industry_lower:
                return value
        
        # Check for direct matches
        standard_industries = ["technology", "healthcare", "education", "finance"]
        if industry_lower in standard_industries:
            return industry_lower
            
        return "default"
    
    def _normalize_job_title(self, job_title):
        """Normalize job title for template selection."""
        if not job_title:
            return "default"
            
        job_lower = job_title.lower()
        
        # Map common variations to standard categories
        job_mapping = {
            # Technology roles
            "developer": "software_engineer",
            "engineer": "software_engineer",
            "programmer": "software_engineer",
            "software": "software_engineer",
            "web developer": "software_engineer",
            
            "data scientist": "data_scientist",
            "data analyst": "data_scientist",
            "machine learning": "data_scientist",
            "ai engineer": "data_scientist",
            
            # Healthcare roles
            "nurse": "registered_nurse",
            "registered nurse": "registered_nurse",
            "nursing": "registered_nurse",
            
            "doctor": "physician",
            "physician": "physician",
            "md": "physician",
            "medical doctor": "physician",
            
            # Education roles
            "teacher": "teacher",
            "instructor": "teacher",
            "educator": "teacher",
            "professor": "teacher",
            
            "principal": "administrator",
            "superintendent": "administrator",
            "dean": "administrator",
            "director of": "administrator",
            
            # Finance roles
            "analyst": "financial_analyst",
            "financial analyst": "financial_analyst",
            "financial advisor": "financial_analyst",
            "finance manager": "financial_analyst"
        }
        
        # Check for matches in mapping
        for key, value in job_mapping.items():
            if key in job_lower:
                return value
                
        return "default"
    
    def _categorize_experience(self, years_experience):
        """Categorize experience level based on years of experience."""
        if years_experience is None:
            return "mid"
            
        if years_experience == 0:
            return "entry"
        elif years_experience < 2:
            return "entry"
        elif years_experience < 5:
            return "mid"
        elif years_experience < 10:
            return "senior"
        else:
            return "senior"
    
    def _extract_company_value(self, job_description, company_name):
        """Extract company values or mission from job description."""
        if not job_description:
            return "innovation and excellence"
            
        # Patterns to find company values
        value_patterns = [
            r'(?:our|{}) (?:mission|vision) (?:is|:) [^.]*'.format(re.escape(company_name)),
            r'(?:our|{}) (?:values|culture|commitment) [^.]*'.format(re.escape(company_name)),
            r'(?:we|{}) (?:believe|value|strive|aim) [^.]*'.format(re.escape(company_name))
        ]
        
        for pattern in value_patterns:
            matches = re.findall(pattern, job_description, re.IGNORECASE)
            if matches:
                # Clean up the match
                value = matches[0]
                value = re.sub(r'^.*?(?:is|:)\s*', '', value).strip()
                value = re.sub(r'^\s*(?:to|in)\s+', '', value).strip()
                return value
                
        # Fallback: look for keywords
        value_keywords = [
            "innovation", "excellence", "quality", "integrity", 
            "diversity", "inclusion", "creativity", "leadership",
            "collaboration", "customer service", "sustainability"
        ]
        
        for keyword in value_keywords:
            if keyword in job_description.lower():
                return keyword
                
        return "innovation and excellence"
    
    def _extract_company_specialty(self, job_description, company_name):
        """Extract company specialty or focus area from job description."""
        if not job_description:
            return "your field"
            
        # Patterns to find company specialty
        specialty_patterns = [
            r'(?:leader|leading|specializes|focused) (?:in|on) [^.]*',
            r'(?:our|{}) (?:focus|specialty|expertise) (?:is|in|:) [^.]*'.format(re.escape(company_name))
        ]
        
        for pattern in specialty_patterns:
            matches = re.findall(pattern, job_description, re.IGNORECASE)
            if matches:
                # Clean up the match
                specialty = matches[0]
                specialty = re.sub(r'^.*?(?:in|on|:)\s*', '', specialty).strip()
                return specialty[:50]  # Limit length
                
        return "your field"
    
    def _extract_industry_trend(self, industry):
        """Get a relevant industry trend based on the industry."""
        trends = {
            "technology": "digital transformation and AI integration",
            "healthcare": "patient-centered care and telemedicine",
            "education": "personalized learning and educational technology",
            "finance": "fintech innovation and data-driven decision making"
        }
        
        return trends.get(industry, "industry innovation")
    
    def _extract_relevant_experience(self, job_description, skills):
        """Extract relevant experience areas from job skills and description."""
        if not job_description or not skills:
            return "relevant areas"
            
        # Find which skills are mentioned in the job description
        matched_skills = []
        for skill in skills:
            if skill.lower() in job_description.lower():
                matched_skills.append(skill)
                
        if matched_skills:
            return ", ".join(matched_skills[:3])
            
        return "relevant areas"
    
    def _get_fallback_cover_letter(self, user_name, job_title, company_name):
        """Generate a basic fallback cover letter when detailed generation fails."""
        current_date = datetime.now().strftime("%B %d, %Y")
        
        cover_letter = f"""
{current_date}

Dear Hiring Manager,

I am writing to express my interest in the {job_title} position at {company_name}. With my background in relevant skills, I am confident in my ability to make a valuable contribution to your team.

Throughout my career, I have developed strong technical skills and a passion for delivering high-quality solutions. I am particularly drawn to {company_name}'s commitment to excellence and believe my experience aligns well with your needs.

In my previous roles, I have:
• Successfully delivered projects on time and within budget
• Collaborated effectively with cross-functional teams
• Applied my expertise to solve complex problems
• Continuously learned and adapted to new technologies and methodologies

I am excited about the opportunity to bring my skills to {company_name} and contribute to your continued success. I welcome the chance to discuss how my background, technical skills, and enthusiasm would make me a strong addition to your team.

Thank you for considering my application. I look forward to the possibility of working with you.

Sincerely,
{user_name}
"""
        return cover_letter.strip()
        
    def generate_african_region_cover_letter(self, job_title, company_name, user_name,
                                            skills=None, years_experience=0, country="Nigeria",
                                            education_field=None, previous_company=None,
                                            template_type=None):
        """
        Generate a cover letter tailored to African regional expectations.
        
        Args:
            job_title: The title of the job being applied for
            company_name: The name of the company
            user_name: The applicant's name
            skills: List of user's skills
            years_experience: Years of relevant experience
            country: Specific African country to tailor for (e.g., Nigeria, Ghana, Kenya)
            education_field: User's field of study
            previous_company: User's most recent company
            template_type: Specific template to use (overrides automatic selection)
            
        Returns:
            Dictionary containing cover letter content and metadata
        """
        try:
            # Determine experience level
            experience_level = self._categorize_experience(years_experience)
            
            # Process skills
            skills_string = ", ".join(skills[:5]) if skills else "relevant skills"
            skills_to_highlight = skills[:3] if skills else ["relevant skills"]
            
            # Set current date
            current_date = datetime.now().strftime("%B %d, %Y")
            
            # Country-specific customizations
            country_details = self._get_african_country_details(country)
            
            # Select base template - for African regions we use slightly more formal templates
            template_base = self._get_african_template(experience_level, template_type)
            
            # Format template with variables
            template_vars = {
                "job_title": job_title,
                "company_name": company_name,
                "user_name": user_name,
                "skills_string": skills_string,
                "skills_to_highlight": skills_to_highlight[0] if skills_to_highlight else "relevant skills",
                "years_experience": years_experience,
                "current_date": current_date,
                "previous_company": previous_company or "my previous employer",
                "education_field": education_field or "my field of study",
                "country": country,
                "local_greeting": country_details.get("greeting", "Dear"),
                "local_reference": country_details.get("reference", ""),
                "currency": country_details.get("currency", ""),
                "city": country_details.get("major_city", "")
            }
            
            # Format the letter
            formatted_content = template_base.format(**template_vars)
            
            # Split into sections
            sections = self._split_cover_letter_into_sections(formatted_content)
            
            # Return the customized cover letter
            return {
                "full_text": formatted_content,
                "sections": sections,
                "word_count": len(formatted_content.split()),
                "template_used": f"african_{country.lower()}_{experience_level}",
                "region_specific": True,
                "metadata": {
                    "job_title": job_title,
                    "company_name": company_name,
                    "country": country,
                    "experience_level": experience_level
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating African region cover letter: {str(e)}")
            # Fall back to standard cover letter
            return self.generate_cover_letter(job_title, company_name, user_name, skills, 
                                             years_experience, "default", education_field)
    
    def _get_african_country_details(self, country):
        """Get country-specific details for African nations."""
        country_details = {
            "Nigeria": {
                "greeting": "Dear",
                "reference": "I am writing with reference to",
                "currency": "Naira",
                "major_city": "Lagos",
                "formal_title": "Sir/Madam"
            },
            "Ghana": {
                "greeting": "Dear",
                "reference": "I wish to apply for",
                "currency": "Ghana Cedi",
                "major_city": "Accra",
                "formal_title": "Sir/Madam"
            },
            "Kenya": {
                "greeting": "Dear",
                "reference": "I am writing in application for",
                "currency": "Kenyan Shilling",
                "major_city": "Nairobi",
                "formal_title": "Sir/Madam"
            },
            "South Africa": {
                "greeting": "Dear",
                "reference": "I wish to apply for",
                "currency": "Rand",
                "major_city": "Johannesburg",
                "formal_title": "Sir/Madam"
            }
        }
        
        # Return details for specified country or default if not found
        return country_details.get(country, {
            "greeting": "Dear",
            "reference": "I am writing to apply for",
            "currency": "local currency",
            "major_city": "your city",
            "formal_title": "Sir/Madam"
        })
    
    def _get_african_template(self, experience_level, template_type=None):
        """Get template for African region based on experience level."""
        # Override with template_type if provided
        if template_type in ["entry", "mid", "senior"]:
            experience_level = template_type
            
        templates = {
            "entry": """
{current_date}

{local_greeting} Hiring Manager,

{local_reference} the {job_title} position at {company_name}. As a recent graduate with knowledge in {skills_string}, I am eager to contribute my skills to your esteemed organization.

During my education and training, I have developed proficiency in {skills_to_highlight} and other relevant areas. I am particularly interested in working with {company_name} due to your reputation for excellence in {city} and beyond.

My educational background and training have prepared me well for this position:
• Completed relevant coursework in {education_field}
• Developed practical skills through projects and practical training
• Demonstrated strong work ethic and determination to succeed
• Committed to continuous learning and professional development

I am excited about the opportunity to begin my professional journey with {company_name} and contribute to your continued success. I would appreciate the opportunity to discuss how my qualifications align with your requirements.

Thank you for considering my application. I look forward to your positive response.

Yours faithfully,
{user_name}
""",
            "mid": """
{current_date}

{local_greeting} Hiring Manager,

{local_reference} the {job_title} position at {company_name}. With {years_experience} years of relevant experience and expertise in {skills_string}, I am confident that I would be a valuable addition to your organization.

In my current role at {previous_company}, I have successfully:
• Implemented solutions that improved operational efficiency
• Collaborated effectively with colleagues at all levels
• Applied my expertise in {skills_to_highlight} to address complex challenges
• Consistently met and exceeded performance expectations

I am particularly impressed by {company_name}'s standing in {city} and your contributions to the sector. Your organization's reputation for quality and innovation aligns perfectly with my professional values.

I would welcome the opportunity to bring my experience and skills to {company_name} and contribute to your continued success. I am confident that my background and capabilities would enable me to excel in this role.

Thank you for considering my application. I look forward to the possibility of discussing my qualifications further.

Yours faithfully,
{user_name}
""",
            "senior": """
{current_date}

{local_greeting} Hiring Manager,

{local_reference} the Senior {job_title} position at {company_name}. With over {years_experience} years of progressive experience and specialized expertise in {skills_string}, I am well-positioned to make significant contributions to your organization.

In my current capacity at {previous_company}, I have:
• Led teams that delivered exceptional results and operational improvements
• Developed strategic initiatives that enhanced organizational performance
• Utilized my expertise in {skills_to_highlight} to implement innovative solutions
• Mentored junior colleagues and fostered a culture of excellence

{company_name}'s reputation as a leader in {city} and your commitment to excellence are well-known. I am particularly interested in contributing to your continued growth and success in the competitive marketplace.

I would welcome the opportunity to discuss how my leadership experience and technical expertise align with your organization's objectives. I am confident that my professional background would be an asset to your team.

Thank you for considering my application. I look forward to a favorable response and the possibility of working with {company_name}.

Yours faithfully,
{user_name}
"""
        }
        
        return templates.get(experience_level, templates["mid"])
    
    def _generate_recommendations(self, structure_analysis, content_analysis, personalization_details, relevance_details=None):
        recommendations = []
        
        # Structure recommendations
        if structure_analysis['structure_score'] < 70:
            for section in structure_analysis['sections_missing']:
                if section == 'greeting':
                    recommendations.append("Add a proper greeting at the beginning of your cover letter (e.g., 'Dear Hiring Manager,')")
                elif section == 'introduction':
                    recommendations.append("Add an introduction that clearly states the position you're applying for and your interest in the role")
                elif section == 'body':
                    recommendations.append("Expand the body of your cover letter to highlight your relevant experience and skills")
                elif section == 'closing':
                    recommendations.append("Add a professional closing statement thanking the reader for their consideration")
                elif section == 'signature':
                    recommendations.append("Include your name at the end of the cover letter")
        
        # Content recommendations
        if content_analysis['length_analysis']['word_count'] < 200:
            recommendations.append("Expand your cover letter to at least 250-350 words to adequately highlight your qualifications")
        elif content_analysis['length_analysis']['word_count'] > 550:
            recommendations.append("Consider making your cover letter more concise (about 350-500 words) to respect the reader's time")
        
        if content_analysis['achievement_count'] < 2:
            recommendations.append("Include specific achievements with measurable results from your past experience")
        
        if content_analysis['skill_count'] < 3:
            recommendations.append("Mention more specific skills that are relevant to the position")
        
        if content_analysis['generic_phrase_count'] >= 2:
            recommendations.append("Replace generic phrases like '" + "', '".join(content_analysis['generic_phrases'][:2]) + "' with specific examples from your experience")
        
        # Personalization recommendations
        if personalization_details['company_mentions'] < 2:
            recommendations.append("Mention the company name more frequently to show your specific interest in them")
        
        if len(personalization_details['personalization_indicators']) < 3:
            recommendations.append("Personalize your cover letter by referencing specific company initiatives, values, or projects")
        
        # Job relevance recommendations
        if relevance_details and 'job_keywords_missed' in relevance_details:
            missed_keywords = relevance_details['job_keywords_missed']
            if len(missed_keywords) >= 5:
                top_missed = missed_keywords[:5]
                recommendations.append(f"Include more job-relevant keywords such as {', '.join(top_missed)}")
        
        # Limit to top 5 most important recommendations
        if len(recommendations) > 5:
            recommendations = recommendations[:5]
        
        # If no issues found, add positive feedback
        if not recommendations:
            if structure_analysis['structure_score'] >= 80 and content_analysis['content_score'] >= 80:
                recommendations.append("Your cover letter is well-structured and contains strong content. Consider tailoring it even further for each specific position.")
            else:
                recommendations.append("Continue to focus on specific achievements and skills relevant to the position.")
        
        return recommendations