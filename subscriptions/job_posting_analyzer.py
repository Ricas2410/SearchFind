"""
Job Posting Analysis System

This module implements job posting analysis functionality using the core infrastructure
components (document parsing, text processing, content validation, and data resources).
It provides detailed analysis of job posting content, optimization suggestions, and
recommendations for improving job descriptions and requirements.
"""

import logging
import re
from collections import defaultdict, Counter

from .document_parser import DocumentParser
from .text_processor import TextProcessor
from .content_validator import ContentValidator
from .data_resources import (
    get_all_skills, 
    get_technical_skills_by_category, 
    get_soft_skills, 
    get_inclusive_language_patterns,
    get_exclusive_language_patterns,
    get_job_posting_templates
)

logger = logging.getLogger(__name__)

class JobPostingAnalyzer:
    """
    Class for analyzing job postings using the core infrastructure.
    
    This class uses document parsing, text processing, and content validation
    to provide comprehensive job posting analysis with detailed feedback and
    actionable recommendations for improvement.
    """
    
    def __init__(self):
        """Initialize the JobPostingAnalyzer with necessary components."""
        self.document_parser = DocumentParser()
        self.text_processor = TextProcessor()
        self.content_validator = ContentValidator(self.text_processor)
        
        # Load skills data
        self.all_skills = get_all_skills()
        self.technical_skills = get_technical_skills_by_category()
        self.soft_skills = get_soft_skills()
        
        # Load language patterns
        self.inclusive_patterns = get_inclusive_language_patterns()
        self.exclusive_patterns = get_exclusive_language_patterns()
        
        # Load job posting templates
        self.job_posting_templates = get_job_posting_templates()
        
        # Common job posting sections
        self.expected_sections = [
            'company_overview',
            'job_description',
            'responsibilities',
            'requirements',
            'qualifications',
            'benefits',
            'application_process'
        ]
        
        # Common job requirement phrases
        self.requirement_phrases = [
            r'required',
            r'must have',
            r'essential',
            r'necessary',
            r'needed',
            r'minimum'
        ]
        
        # Optional requirement phrases
        self.optional_phrases = [
            r'preferred',
            r'nice to have',
            r'bonus',
            r'desirable',
            r'plus',
            r'advantageous'
        ]
        
        # Initialize analysis metrics
        self._initialize_analysis_metrics()
    
    def _initialize_analysis_metrics(self):
        """Initialize metrics for job posting analysis."""
        # Common metrics on job posting quality
        self.quality_metrics = {
            'title_quality': {
                'description': 'How clear, specific, and searchable the job title is',
                'weight': 0.15
            },
            'description_quality': {
                'description': 'How well the job is described, including role details and context',
                'weight': 0.20
            },
            'requirements_clarity': {
                'description': 'How clearly required vs. preferred skills are distinguished',
                'weight': 0.15
            },
            'responsibilities_clarity': {
                'description': 'How clearly job responsibilities are defined',
                'weight': 0.15
            },
            'benefits_appeal': {
                'description': 'How appealing and complete the benefits description is',
                'weight': 0.10
            },
            'inclusivity_score': {
                'description': 'Use of inclusive language that appeals to diverse candidates',
                'weight': 0.15
            },
            'structure_quality': {
                'description': 'Organization and readability of the overall posting',
                'weight': 0.10
            }
        }
        
        # Specific language patterns to watch for
        self.language_patterns = {
            'gender_coded': [
                r'\b(?:he|him|his|himself|man|men|male|masculine)\b',
                r'\b(?:she|her|hers|herself|woman|women|female|feminine)\b',
                r'\b(?:ninja|rockstar|guru|superstar|superhero)\b'
            ],
            'years_of_experience': [
                r'\b(\d+)(?:\+|\s*-\s*\d+)?\s*(?:years?|yrs?)(?:\s+of)?\s+experience\b'
            ],
            'education_requirements': [
                r'\b(?:bachelor\'?s?|master\'?s?|phd|doctorate|mba|bs|ba|ms|ma|degree)\b'
            ],
            'ambiguous_terms': [
                r'\b(?:familiar with|knowledge of|understanding of)\b'
            ],
            'strong_requirements': [
                r'\b(?:expert|expertise|proficient|advanced|strong|excellent|extensive)\b'
            ],
            'culture_fit': [
                r'\b(?:culture fit|team fit|fit in|personality|attitude|work hard play hard)\b'
            ]
        }
    
    def analyze_job_posting_file(self, file_path):
        """
        Analyze a job posting from a file path.
        
        Args:
            file_path (str): Path to the job posting file
            
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
            return self.analyze_job_posting_text(text)
            
        except Exception as e:
            logger.error(f"Error analyzing job posting file {file_path}: {str(e)}")
            return {
                'error': f"Error analyzing job posting: {str(e)}",
                'is_valid': False
            }
    
    def analyze_job_posting_file_object(self, file_object, file_name):
        """
        Analyze a job posting from a file object (e.g., uploaded file).
        
        Args:
            file_object: File-like object containing the job posting
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
            return self.analyze_job_posting_text(text)
            
        except Exception as e:
            logger.error(f"Error analyzing job posting file {file_name}: {str(e)}")
            return {
                'error': f"Error analyzing job posting: {str(e)}",
                'is_valid': False
            }
    
    def analyze_job_posting_text(self, text):
        """
        Analyze job posting text content.
        
        Args:
            text (str): Text content of the job posting
            
        Returns:
            dict: Analysis results
        """
        # First validate that this is a job posting
        validation = self._validate_job_posting(text)
        
        if not validation.get('is_valid_job_posting', False):
            return {
                'is_valid': False,
                'error': validation.get('error', 'The document does not appear to be a valid job posting.'),
                'document_type': validation.get('document_type', 'unknown'),
                'confidence': validation.get('confidence', 0)
            }
        
        # Process the document to extract sections and entities
        processed_doc = self.text_processor.process_document(text, 'job_description')
        
        # Extract key information
        extracted_info = self._extract_job_posting_info(text, processed_doc)
        
        # Analyze structure and content
        structure_analysis = self._analyze_structure(text, processed_doc)
        content_analysis = self._analyze_content(text, processed_doc, extracted_info)
        
        # Analyze requirements
        requirements_analysis = self._analyze_requirements(text, processed_doc, extracted_info)
        
        # Analyze language for inclusivity
        inclusivity_analysis = self._analyze_inclusivity(text)
        
        # Calculate quality scores
        quality_scores = self._calculate_quality_scores(
            structure_analysis, 
            content_analysis, 
            requirements_analysis, 
            inclusivity_analysis
        )
        
        # Generate optimization suggestions
        optimization_suggestions = self._generate_optimization_suggestions(
            structure_analysis,
            content_analysis,
            requirements_analysis,
            inclusivity_analysis,
            quality_scores,
            extracted_info
        )
        
        # Prepare the analysis results
        analysis = {
            'is_valid': True,
            'document_type': 'job_posting',
            'confidence': validation.get('confidence', 0.8),
            'extracted_info': extracted_info,
            'structure_analysis': structure_analysis,
            'content_analysis': content_analysis,
            'requirements_analysis': requirements_analysis,
            'inclusivity_analysis': inclusivity_analysis,
            'quality_scores': quality_scores,
            'optimization_suggestions': optimization_suggestions,
            'word_count': len(text.split())
        }
        
        return analysis
    
    def _validate_job_posting(self, text):
        """
        Validate if the text is a job posting.
        
        Args:
            text (str): Text content to validate
            
        Returns:
            dict: Validation results
        """
        # Use the content validator to check document type
        validation = self.content_validator.validate_document(text)
        
        # If it's already identified as a job description with medium confidence, accept it
        if validation['document_type'] == 'job_description' and validation['confidence'] >= self.content_validator.MEDIUM_CONFIDENCE:
            return {
                'is_valid_job_posting': True,
                'confidence': validation['confidence'],
                'document_type': 'job_posting'
            }
        
        # Secondary validation specific to job postings
        is_job_posting = False
        confidence = 0.0
        
        # Common job posting keywords
        job_posting_indicators = [
            r'\bjob description\b',
            r'\bposition\b',
            r'\brole\b',
            r'\bresponsibilities\b',
            r'\brequirements\b',
            r'\bqualifications\b',
            r'\bwe are looking for\b',
            r'\bwe are seeking\b',
            r'\bapply\b',
            r'\bemployment\b',
            r'\bcareer\b',
            r'\bopportunity\b',
            r'\bbenefits\b',
            r'\bsalary\b',
            r'\bfull[ -]time\b',
            r'\bpart[ -]time\b',
            r'\bremote\b',
            r'\bhybrid\b',
            r'\bin[ -]office\b'
        ]
        
        # Check for job posting indicators
        match_count = 0
        for indicator in job_posting_indicators:
            if re.search(indicator, text.lower()):
                match_count += 1
        
        # Calculate confidence based on match count
        indicator_ratio = match_count / len(job_posting_indicators)
        
        # Common job posting sections
        section_indicators = [
            r'\bcompany overview\b',
            r'\babout (?:us|the company|our team)\b',
            r'\bjob (?:description|summary)\b',
            r'\bresponsibilities\b',
            r'\bduties\b',
            r'\brequirements\b',
            r'\bqualifications\b',
            r'\bskills\b',
            r'\bexperience\b',
            r'\bbenefits\b',
            r'\bperks\b',
            r'\bhow to apply\b',
            r'\bapplication process\b'
        ]
        
        # Check for section indicators
        section_match_count = 0
        for indicator in section_indicators:
            if re.search(indicator, text.lower()):
                section_match_count += 1
        
        # Calculate confidence based on section match count
        section_ratio = min(1.0, section_match_count / 5.0)  # At least 5 sections expected
        
        # Combined confidence score
        confidence = 0.6 * indicator_ratio + 0.4 * section_ratio
        
        # Set results
        if confidence >= 0.5:
            is_job_posting = True
            
        return {
            'is_valid_job_posting': is_job_posting,
            'confidence': confidence,
            'document_type': 'job_posting' if is_job_posting else validation['document_type'],
            'error': None if is_job_posting else "The document does not contain typical job posting elements."
        }
    
    def _extract_job_posting_info(self, text, processed_doc):
        """
        Extract key information from the job posting.
        
        Args:
            text (str): Job posting text
            processed_doc (dict): Processed document data
            
        Returns:
            dict: Extracted information
        """
        # Get extracted entities from processed document
        job_title = processed_doc.get('extracted_job_title', '')
        company_name = processed_doc.get('extracted_company', '')
        location = processed_doc.get('extracted_location', '')
        extracted_skills = processed_doc.get('extracted_skills', [])
        industry = processed_doc.get('extracted_industry', '')
        
        # Extract employment type
        employment_type_patterns = [
            (r'\bfull[ -]time\b', 'Full-time'),
            (r'\bpart[ -]time\b', 'Part-time'),
            (r'\bcontract\b', 'Contract'),
            (r'\bfreelance\b', 'Freelance'),
            (r'\btemporary\b', 'Temporary'),
            (r'\binternship\b', 'Internship'),
            (r'\bapprentice(?:ship)?\b', 'Apprenticeship')
        ]
        
        employment_type = None
        for pattern, etype in employment_type_patterns:
            if re.search(pattern, text.lower()):
                employment_type = etype
                break
        
        # Extract work arrangement
        work_arrangement_patterns = [
            (r'\bremote\b', 'Remote'),
            (r'\bin[ -]office\b', 'In-office'),
            (r'\bon[ -]site\b', 'On-site'),
            (r'\bhybrid\b', 'Hybrid'),
            (r'\bflexible\b', 'Flexible')
        ]
        
        work_arrangement = None
        for pattern, arrangement in work_arrangement_patterns:
            if re.search(pattern, text.lower()):
                work_arrangement = arrangement
                break
        
        # Extract experience requirements
        experience_matches = re.findall(r'(\d+)(?:\+|\s*-\s*\d+)?\s*(?:years?|yrs?)(?:\s+of)?\s+experience', text.lower())
        years_of_experience = None
        if experience_matches:
            years_of_experience = min([int(years) for years in experience_matches])
        
        # Extract education requirements
        education_patterns = [
            (r'\b(?:bachelor\'?s?|bs|ba)\b', "Bachelor's Degree"),
            (r'\b(?:master\'?s?|ms|ma)\b', "Master's Degree"),
            (r'\b(?:phd|doctorate)\b', "PhD/Doctorate"),
            (r'\b(?:mba)\b', "MBA"),
            (r'\bhigh school\b', "High School"),
            (r'\bassociate\'?s?\b', "Associate's Degree")
        ]
        
        education_requirement = None
        for pattern, level in education_patterns:
            if re.search(pattern, text.lower()):
                education_requirement = level
                break
        
        # Extract salary information
        salary_pattern = r'(?:salary|compensation)(?:[^.]*?)(?:[$£€](\d{1,3}(?:,\d{3})*(?:\.\d+)?)[kK]?(?:\s*-\s*[$£€](\d{1,3}(?:,\d{3})*(?:\.\d+)?)[kK]?)?)'
        salary_range = None
        
        salary_match = re.search(salary_pattern, text.lower())
        if salary_match:
            if salary_match.group(1) and salary_match.group(2):
                salary_range = {
                    'min': salary_match.group(1),
                    'max': salary_match.group(2)
                }
            elif salary_match.group(1):
                salary_range = {
                    'min': salary_match.group(1),
                    'max': None
                }
        
        # Extract benefits
        benefit_patterns = [
            r'health (?:insurance|care|benefits)',
            r'dental (?:insurance|care|benefits)',
            r'vision (?:insurance|care|benefits)',
            r'\b401[kK]\b',
            r'retirement\b',
            r'pension\b',
            r'paid (?:time off|vacation|holidays)',
            r'pto\b',
            r'flexible (?:work|hours|scheduling)',
            r'remote work',
            r'work from home',
            r'professional development',
            r'tuition (?:reimbursement|assistance)',
            r'child care',
            r'parental leave',
            r'wellness program',
            r'gym membership',
            r'stock options',
            r'equity',
            r'bonus',
            r'relocation (?:assistance|package)',
            r'commuter benefits'
        ]
        
        benefits = []
        for pattern in benefit_patterns:
            if re.search(pattern, text.lower()):
                # Extract the matched benefit phrase for more context
                match = re.search(r'([^.;:]*)(?:' + pattern + ')[^.;:]*[.;:]', text.lower())
                if match:
                    benefit_context = match.group(0).strip()
                    if benefit_context not in benefits:
                        benefits.append(benefit_context)
                else:
                    # If no context found, just add the pattern itself
                    benefit_name = pattern.replace(r'\b', '').replace(r'(?:', '').replace(r')?', '')
                    if benefit_name not in benefits:
                        benefits.append(benefit_name)
        
        # Return the extracted information
        return {
            'job_title': job_title,
            'company_name': company_name,
            'location': location,
            'employment_type': employment_type,
            'work_arrangement': work_arrangement,
            'years_of_experience': years_of_experience,
            'education_requirement': education_requirement,
            'salary_range': salary_range,
            'benefits': benefits[:10],  # Top 10 benefits
            'skills_required': extracted_skills[:15],  # Top 15 skills
            'industry': industry
        }
    
    def _analyze_structure(self, text, processed_doc):
        """
        Analyze the structure of the job posting.
        
        Args:
            text (str): Job posting text
            processed_doc (dict): Processed document data
            
        Returns:
            dict: Structure analysis results
        """
        structure_results = {
            'sections_present': [],
            'sections_missing': [],
            'section_order': [],
            'section_lengths': {},
            'structure_score': 0
        }
        
        # Check for each expected section
        section_patterns = {
            'company_overview': [
                r'\babout (?:us|our company|our team|the company)\b',
                r'\bcompany overview\b',
                r'\bwho we are\b'
            ],
            'job_description': [
                r'\bjob (?:description|summary)\b',
                r'\brole overview\b',
                r'\bposition (?:description|summary|overview)\b'
            ],
            'responsibilities': [
                r'\bresponsibilities\b',
                r'\bduties\b',
                r'\bwhat you\'ll do\b',
                r'\bday[ -]to[ -]day\b',
                r'\bkey activities\b'
            ],
            'requirements': [
                r'\brequirements\b',
                r'\bskills (?:required|needed)\b',
                r'\bqualifications\b',
                r'\bwhat you\'ll need\b',
                r'\bwho we\'re looking for\b'
            ],
            'benefits': [
                r'\bbenefits\b',
                r'\bperks\b',
                r'\bwhat we offer\b',
                r'\bcompensation\b',
                r'\bwhy work (?:for|with) us\b'
            ],
            'application_process': [
                r'\bhow to apply\b',
                r'\bapplication process\b',
                r'\bnext steps\b',
                r'\bto apply\b'
            ]
        }
        
        # Check each section
        for section, patterns in section_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text.lower()):
                    structure_results['sections_present'].append(section)
                    break
            else:
                structure_results['sections_missing'].append(section)
        
        # Remove duplicates
        structure_results['sections_present'] = list(dict.fromkeys(structure_results['sections_present']))
        structure_results['sections_missing'] = list(dict.fromkeys(structure_results['sections_missing']))
        
        # Analyze section order by finding the first occurrence of each section
        section_positions = {}
        for section, patterns in section_patterns.items():
            positions = []
            for pattern in patterns:
                match = re.search(pattern, text.lower())
                if match:
                    positions.append(match.start())
            if positions:
                section_positions[section] = min(positions)
        
        # Sort sections by position
        sorted_sections = sorted(section_positions.items(), key=lambda x: x[1])
        structure_results['section_order'] = [section for section, _ in sorted_sections]
        
        # Analyze section lengths
        for i, (section, position) in enumerate(sorted_sections):
            if i < len(sorted_sections) - 1:
                next_section, next_position = sorted_sections[i+1]
                section_text = text[position:next_position]
            else:
                section_text = text[position:]
            
            section_word_count = len(section_text.split())
            structure_results['section_lengths'][section] = section_word_count
        
        # Calculate structure score
        structure_score = 0
        
        # Score based on presence of key sections
        essential_sections = ['job_description', 'responsibilities', 'requirements']
        important_sections = ['company_overview', 'benefits']
        helpful_sections = ['application_process']
        
        present_essential = sum(1 for section in essential_sections if section in structure_results['sections_present'])
        present_important = sum(1 for section in important_sections if section in structure_results['sections_present'])
        present_helpful = sum(1 for section in helpful_sections if section in structure_results['sections_present'])
        
        essential_score = (present_essential / len(essential_sections)) * 50
        important_score = (present_important / len(important_sections)) * 30
        helpful_score = (present_helpful / len(helpful_sections)) * 20
        
        structure_score = essential_score + important_score + helpful_score
        
        # Analyze section order
        ideal_order = ['company_overview', 'job_description', 'responsibilities', 'requirements', 'benefits', 'application_process']
        order_score = 0
        
        if structure_results['section_order']:
            # Check if sections appear in the expected order
            expected_positions = {section: i for i, section in enumerate(ideal_order)}
            actual_positions = {section: i for i, section in enumerate(structure_results['section_order'])}
            
            common_sections = set(structure_results['section_order']).intersection(ideal_order)
            if common_sections:
                # Calculate how many sections are in the correct relative order
                correct_order_count = 0
                for section1 in common_sections:
                    for section2 in common_sections:
                        if section1 != section2:
                            expected_order = expected_positions[section1] < expected_positions[section2]
                            actual_order = actual_positions[section1] < actual_positions[section2]
                            if expected_order == actual_order:
                                correct_order_count += 1
                
                total_possible_comparisons = len(common_sections) * (len(common_sections) - 1)
                if total_possible_comparisons > 0:
                    order_score = (correct_order_count / total_possible_comparisons) * 10
        
        structure_score += order_score
        
        # Analyze section balance
        section_balance_score = 0
        if structure_results['section_lengths']:
            lengths = list(structure_results['section_lengths'].values())
            min_length = min(lengths)
            max_length = max(lengths)
            
            # Check if any section is too short or too long relative to others
            if min_length > 20 and max_length / min_length < 5:
                section_balance_score = 10
            elif min_length > 10 and max_length / min_length < 10:
                section_balance_score = 5
        
        structure_score += section_balance_score
        
        # Ensure score is within bounds
        structure_results['structure_score'] = max(0, min(100, structure_score))
        
        # Add structure evaluation
        if structure_results['structure_score'] >= 90:
            structure_results['evaluation'] = "Excellent structure with all key sections in logical order"
        elif structure_results['structure_score'] >= 75:
            structure_results['evaluation'] = "Good structure with most key sections present"
        elif structure_results['structure_score'] >= 50:
            structure_results['evaluation'] = "Adequate structure but missing some important sections"
        else:
            structure_results['evaluation'] = "Poor structure, missing multiple critical sections"
        
        return structure_results
    
    def _analyze_content(self, text, processed_doc, extracted_info):
        """
        Analyze the content quality of the job posting.
        
        Args:
            text (str): Job posting text
            processed_doc (dict): Processed document data
            extracted_info (dict): Extracted job posting information
            
        Returns:
            dict: Content analysis results
        """
        content_results = {
            'title_analysis': {},
            'company_description_analysis': {},
            'job_description_analysis': {},
            'responsibilities_analysis': {},
            'content_score': 0,
            'unique_selling_points': []
        }
        
        # Analyze job title
        job_title = extracted_info.get('job_title', '')
        
        if job_title:
            title_analysis = {
                'is_present': True,
                'specificity': 'Low',
                'industry_standard': 'No',
                'seniority_level': 'Not specified',
                'searchability': 'Low',
                'score': 0
            }
            
            # Check title length
            if len(job_title.split()) >= 2 and len(job_title.split()) <= 5:
                title_analysis['score'] += 20
            
            # Check for seniority level
            seniority_levels = ['junior', 'senior', 'lead', 'principal', 'staff', 'head', 'chief', 'director', 'vp', 'manager']
            for level in seniority_levels:
                if level in job_title.lower():
                    title_analysis['seniority_level'] = level.capitalize()
                    title_analysis['score'] += 20
                    break
            
            # Check for specificity (tech stack or specialization)
            tech_matches = [tech for tech in self.technical_skills if tech.lower() in job_title.lower()]
            specialization_terms = ['frontend', 'backend', 'full stack', 'devops', 'data', 'machine learning', 'ai', 'mobile', 'web']
            specialization_matches = [term for term in specialization_terms if term in job_title.lower()]
            
            if tech_matches or specialization_matches:
                title_analysis['specificity'] = 'High'
                title_analysis['score'] += 30
            elif len(job_title.split()) >= 3:
                title_analysis['specificity'] = 'Medium'
                title_analysis['score'] += 15
            
            # Common industry standard titles
            standard_titles = [
                'software engineer', 'software developer', 'web developer', 'data scientist', 
                'data analyst', 'product manager', 'project manager', 'ux designer', 
                'ui designer', 'devops engineer', 'systems administrator', 'network engineer',
                'database administrator', 'security engineer', 'qa engineer', 'test engineer'
            ]
            
            for standard in standard_titles:
                if standard in job_title.lower():
                    title_analysis['industry_standard'] = 'Yes'
                    title_analysis['score'] += 30
                    break
            
            # Set searchability based on score
            if title_analysis['score'] >= 70:
                title_analysis['searchability'] = 'High'
            elif title_analysis['score'] >= 40:
                title_analysis['searchability'] = 'Medium'
            
            # Ensure score is within bounds
            title_analysis['score'] = min(100, title_analysis['score'])
            
            content_results['title_analysis'] = title_analysis
        else:
            content_results['title_analysis'] = {
                'is_present': False,
                'score': 0,
                'evaluation': 'Job title not found in the posting'
            }
        
        # Analyze company description
        company_section_patterns = [
            r'(?:about (?:us|our company|our team|the company)|company overview|who we are)[^\n]*(?:\n|$)(.+?)(?=\n\s*\n|\n\s*[A-Z]|\Z)',
            r'(?:we are|we\'re|our company is)[^\n]*(?:\n|$)(.+?)(?=\n\s*\n|\n\s*[A-Z]|\Z)'
        ]
        
        company_description = ""
        for pattern in company_section_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                company_description = match.group(1).strip()
                break
        
        if company_description:
            company_analysis = {
                'is_present': True,
                'word_count': len(company_description.split()),
                'mentions_values': False,
                'mentions_culture': False,
                'mentions_mission': False,
                'mentions_growth': False,
                'score': 0
            }
            
            # Check length
            if company_analysis['word_count'] >= 100:
                company_analysis['score'] += 30
            elif company_analysis['word_count'] >= 50:
                company_analysis['score'] += 15
            elif company_analysis['word_count'] >= 25:
                company_analysis['score'] += 5
            
            # Check for key elements
            if re.search(r'\b(?:values|value|believe|principles)\b', company_description, re.IGNORECASE):
                company_analysis['mentions_values'] = True
                company_analysis['score'] += 15
            
            if re.search(r'\b(?:culture|environment|team|colleagues|work\s+life)\b', company_description, re.IGNORECASE):
                company_analysis['mentions_culture'] = True
                company_analysis['score'] += 15
            
            if re.search(r'\b(?:mission|vision|purpose|goal|aim|strive)\b', company_description, re.IGNORECASE):
                company_analysis['mentions_mission'] = True
                company_analysis['score'] += 20
            
            if re.search(r'\b(?:grow|growing|growth|expand|expanding|expansion|scale|scaling)\b', company_description, re.IGNORECASE):
                company_analysis['mentions_growth'] = True
                company_analysis['score'] += 20
            
            # Ensure score is within bounds
            company_analysis['score'] = min(100, company_analysis['score'])
            
            # Add evaluation
            if company_analysis['score'] >= 80:
                company_analysis['evaluation'] = "Excellent company description with mission, values, and culture"
            elif company_analysis['score'] >= 60:
                company_analysis['evaluation'] = "Good company description that covers most key elements"
            elif company_analysis['score'] >= 40:
                company_analysis['evaluation'] = "Adequate company description but missing some important elements"
            else:
                company_analysis['evaluation'] = "Basic company description that needs more detail"
            
            content_results['company_description_analysis'] = company_analysis
        else:
            content_results['company_description_analysis'] = {
                'is_present': False,
                'score': 0,
                'evaluation': 'Company description not found in the posting'
            }
        
        # Analyze job description
        job_desc_section_patterns = [
            r'(?:job (?:description|summary)|role overview|position (?:description|summary|overview))[^\n]*(?:\n|$)(.+?)(?=\n\s*\n|\n\s*[A-Z]|\Z)',
            r'(?:the role|this position|this role|the job)[^\n]*(?:\n|$)(.+?)(?=\n\s*\n|\n\s*[A-Z]|\Z)'
        ]
        
        job_description = ""
        for pattern in job_desc_section_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                job_description = match.group(1).strip()
                break
        
        if job_description:
            job_desc_analysis = {
                'is_present': True,
                'word_count': len(job_description.split()),
                'describes_role': False,
                'mentions_team': False,
                'mentions_impact': False,
                'score': 0
            }
            
            # Check length
            if job_desc_analysis['word_count'] >= 100:
                job_desc_analysis['score'] += 25
            elif job_desc_analysis['word_count'] >= 50:
                job_desc_analysis['score'] += 15
            elif job_desc_analysis['word_count'] >= 25:
                job_desc_analysis['score'] += 5
            
            # Check for key elements
            if re.search(r'\b(?:you will|you\'ll|responsible for|role involves|role includes|position involves|position includes)\b', job_description, re.IGNORECASE):
                job_desc_analysis['describes_role'] = True
                job_desc_analysis['score'] += 25
            
            if re.search(r'\b(?:team|collaborate|work with|report to|manager|director|lead)\b', job_description, re.IGNORECASE):
                job_desc_analysis['mentions_team'] = True
                job_desc_analysis['score'] += 25
            
            if re.search(r'\b(?:impact|influence|contribute|help|improve|create|build|develop|deliver)\b', job_description, re.IGNORECASE):
                job_desc_analysis['mentions_impact'] = True
                job_desc_analysis['score'] += 25
            
            # Ensure score is within bounds
            job_desc_analysis['score'] = min(100, job_desc_analysis['score'])
            
            # Add evaluation
            if job_desc_analysis['score'] >= 80:
                job_desc_analysis['evaluation'] = "Excellent job description that clearly explains the role, team, and impact"
            elif job_desc_analysis['score'] >= 60:
                job_desc_analysis['evaluation'] = "Good job description that covers most key elements"
            elif job_desc_analysis['score'] >= 40:
                job_desc_analysis['evaluation'] = "Adequate job description but missing some important context"
            else:
                job_desc_analysis['evaluation'] = "Basic job description that needs more detail"
            
            content_results['job_description_analysis'] = job_desc_analysis
        else:
            content_results['job_description_analysis'] = {
                'is_present': False,
                'score': 0,
                'evaluation': 'Job description not found in the posting'
            }
        
        # Analyze responsibilities section
        resp_section_patterns = [
            r'(?:responsibilities|duties|what you\'ll do|day[ -]to[ -]day|key activities)[^\n]*(?:\n|$)(.+?)(?=\n\s*\n|\n\s*[A-Z]|\Z)',
            r'(?:you will be responsible for|you\'ll be responsible for|your responsibilities will include)[^\n]*(?:\n|$)(.+?)(?=\n\s*\n|\n\s*[A-Z]|\Z)'
        ]
        
        responsibilities = ""
        for pattern in resp_section_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                responsibilities = match.group(1).strip()
                break
        
        if responsibilities:
            resp_analysis = {
                'is_present': True,
                'word_count': len(responsibilities.split()),
                'has_bullet_points': False,
                'responsibility_count': 0,
                'specific_responsibilities': [],
                'score': 0
            }
            
            # Check for bullet points or numbered list
            bullet_matches = re.findall(r'(?:•|\*|\-|\d+\.)\s+(.+?)(?=\n|$)', responsibilities)
            if bullet_matches:
                resp_analysis['has_bullet_points'] = True
                resp_analysis['responsibility_count'] = len(bullet_matches)
                resp_analysis['specific_responsibilities'] = bullet_matches[:5]  # First 5 only
                
                # Score based on number of responsibilities
                if resp_analysis['responsibility_count'] >= 5:
                    resp_analysis['score'] += 40
                elif resp_analysis['responsibility_count'] >= 3:
                    resp_analysis['score'] += 25
                else:
                    resp_analysis['score'] += 10
            else:
                # Try to identify responsibilities in paragraph format
                sentence_matches = re.findall(r'[^.!?]+[.!?]', responsibilities)
                if sentence_matches:
                    resp_analysis['responsibility_count'] = len(sentence_matches)
                    resp_analysis['specific_responsibilities'] = sentence_matches[:5]  # First 5 only
                    
                    # Score based on number of responsibilities (lower than bullet points)
                    if resp_analysis['responsibility_count'] >= 5:
                        resp_analysis['score'] += 25
                    elif resp_analysis['responsibility_count'] >= 3:
                        resp_analysis['score'] += 15
                    else:
                        resp_analysis['score'] += 5
            
            # Check for specificity in responsibilities
            specificity_score = 0
            for resp in resp_analysis['specific_responsibilities']:
                # Check for specific verbs
                if re.search(r'\b(?:design|develop|implement|create|manage|lead|analyze|build|maintain|test|deploy)\b', resp, re.IGNORECASE):
                    specificity_score += 5
                
                # Check for specific metrics or outcomes
                if re.search(r'\b(?:improve|increase|reduce|enhance|optimize|ensure)\b', resp, re.IGNORECASE):
                    specificity_score += 5
            
            resp_analysis['score'] += min(40, specificity_score)
            
            # Check for overall responsibility section length
            if resp_analysis['word_count'] >= 150:
                resp_analysis['score'] += 20
            elif resp_analysis['word_count'] >= 75:
                resp_analysis['score'] += 10
            
            # Ensure score is within bounds
            resp_analysis['score'] = min(100, resp_analysis['score'])
            
            # Add evaluation
            if resp_analysis['score'] >= 80:
                resp_analysis['evaluation'] = "Excellent responsibilities section with specific, actionable items"
            elif resp_analysis['score'] >= 60:
                resp_analysis['evaluation'] = "Good responsibilities section with clear duties"
            elif resp_analysis['score'] >= 40:
                resp_analysis['evaluation'] = "Adequate responsibilities section but could be more specific"
            else:
                resp_analysis['evaluation'] = "Basic responsibilities section that needs more detail"
            
            content_results['responsibilities_analysis'] = resp_analysis
        else:
            content_results['responsibilities_analysis'] = {
                'is_present': False,
                'score': 0,
                'evaluation': 'Responsibilities section not found in the posting'
            }
        
        # Identify unique selling points
        selling_points = []
        
        # Look for company benefits or perks
        if extracted_info['benefits']:
            selling_points.extend(extracted_info['benefits'][:3])
        
        # Look for growth or advancement opportunities
        growth_patterns = [
            r'(?:growth|advancement|career|promotion)\s+opportunities',
            r'opportunity\s+to\s+(?:grow|advance|develop|learn)',
            r'career\s+(?:path|development|progression)'
        ]
        
        for pattern in growth_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                context = self._get_context(text, match.start(), match.end())
                if context and context not in selling_points:
                    selling_points.append(context)
                    break
        
        # Look for company culture highlights
        culture_patterns = [
            r'(?:great|positive|inclusive|collaborative|innovative)\s+(?:culture|environment|workplace)',
            r'work-life\s+balance',
            r'flexible\s+(?:hours|schedule|working)',
            r'diverse\s+(?:and\s+)?inclusive'
        ]
        
        for pattern in culture_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                context = self._get_context(text, match.start(), match.end())
                if context and context not in selling_points:
                    selling_points.append(context)
                    break
        
        # Look for technology or tools highlights
        tech_patterns = [
            r'(?:cutting[ -]edge|latest|modern|state[ -]of[ -]the[ -]art)\s+(?:technology|tools|stack|equipment)',
            r'opportunity\s+to\s+work\s+with\s+(?:new|modern|cutting[ -]edge)\s+technology'
        ]
        
        for pattern in tech_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                context = self._get_context(text, match.start(), match.end())
                if context and context not in selling_points:
                    selling_points.append(context)
                    break
        
        content_results['unique_selling_points'] = selling_points[:5]  # Limit to top 5
        
        # Calculate overall content score
        title_weight = 0.25 if content_results['title_analysis'].get('is_present', False) else 0
        company_weight = 0.20 if content_results['company_description_analysis'].get('is_present', False) else 0
        job_desc_weight = 0.25 if content_results['job_description_analysis'].get('is_present', False) else 0
        resp_weight = 0.30 if content_results['responsibilities_analysis'].get('is_present', False) else 0
        
        # Adjust weights if some sections are missing
        total_weight = title_weight + company_weight + job_desc_weight + resp_weight
        if total_weight > 0:
            if title_weight == 0:
                job_desc_weight += 0.10
                resp_weight += 0.15
            if company_weight == 0:
                title_weight += 0.05
                job_desc_weight += 0.05
                resp_weight += 0.10
            if job_desc_weight == 0:
                title_weight += 0.10
                resp_weight += 0.15
            if resp_weight == 0:
                title_weight += 0.10
                job_desc_weight += 0.20
            
            # Normalize weights to ensure they sum to 1
            total_weight = title_weight + company_weight + job_desc_weight + resp_weight
            title_weight /= total_weight
            company_weight /= total_weight
            job_desc_weight /= total_weight
            resp_weight /= total_weight
            
            # Calculate weighted score
            content_score = 0
            if content_results['title_analysis'].get('is_present', False):
                content_score += content_results['title_analysis'].get('score', 0) * title_weight
            
            if content_results['company_description_analysis'].get('is_present', False):
                content_score += content_results['company_description_analysis'].get('score', 0) * company_weight
            
            if content_results['job_description_analysis'].get('is_present', False):
                content_score += content_results['job_description_analysis'].get('score', 0) * job_desc_weight
            
            if content_results['responsibilities_analysis'].get('is_present', False):
                content_score += content_results['responsibilities_analysis'].get('score', 0) * resp_weight
        else:
            # If all major sections are missing, score based on text length
            word_count = len(text.split())
            if word_count >= 500:
                content_score = 40
            elif word_count >= 300:
                content_score = 30
            elif word_count >= 150:
                content_score = 20
            else:
                content_score = 10
        
        # Add points for unique selling points
        selling_points_bonus = min(15, len(content_results['unique_selling_points']) * 3)
        content_score += selling_points_bonus
        
        # Ensure score is within bounds
        content_results['content_score'] = max(0, min(100, round(content_score)))
        
        # Add overall content evaluation
        if content_results['content_score'] >= 85:
            content_results['evaluation'] = "Excellent content with comprehensive information and clear selling points"
        elif content_results['content_score'] >= 70:
            content_results['evaluation'] = "Good content that covers most key areas effectively"
        elif content_results['content_score'] >= 50:
            content_results['evaluation'] = "Adequate content but missing some important information"
        else:
            content_results['evaluation'] = "Basic content that needs significant improvement"
        
        return content_results
    
    def _analyze_requirements(self, text, processed_doc, extracted_info):
        """
        Analyze the requirements section of the job posting.
        
        Args:
            text (str): Job posting text
            processed_doc (dict): Processed document data
            extracted_info (dict): Extracted job posting information
            
        Returns:
            dict: Requirements analysis results
        """
        requirements_results = {
            'requirements_present': False,
            'has_must_have': False,
            'has_nice_to_have': False,
            'must_have_count': 0,
            'nice_to_have_count': 0,
            'must_have_requirements': [],
            'nice_to_have_requirements': [],
            'excessive_requirements': False,
            'years_experience_requirements': [],
            'education_requirements': [],
            'ambiguous_requirements': [],
            'requirements_score': 0
        }
        
        # Extract requirements section
        req_section_patterns = [
            r'(?:requirements|qualifications|what you\'ll need|who we\'re looking for)[^\n]*(?:\n|$)(.+?)(?=\n\s*\n|\n\s*[A-Z]|\Z)',
            r'(?:you should have|you must have|you need to have|we require)[^\n]*(?:\n|$)(.+?)(?=\n\s*\n|\n\s*[A-Z]|\Z)'
        ]
        
        requirements_text = ""
        for pattern in req_section_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                requirements_text = match.group(1).strip()
                requirements_results['requirements_present'] = True
                break
        
        if not requirements_results['requirements_present']:
            # If no dedicated section, try to find requirements throughout the text
            all_requirements = []
            for req_phrase in self.requirement_phrases + self.optional_phrases:
                matches = re.finditer(req_phrase, text, re.IGNORECASE)
                for match in matches:
                    sentence = self._get_context(text, match.start(), match.end())
                    if sentence and sentence not in all_requirements:
                        all_requirements.append(sentence)
            
            if all_requirements:
                requirements_text = "\n".join(all_requirements)
                requirements_results['requirements_present'] = True
        
        if requirements_results['requirements_present']:
            # Check for must-have vs. nice-to-have distinction
            must_have_requirements = []
            nice_to_have_requirements = []
            ambiguous_requirements = []
            
            # First check for bullet points or numbered list items
            bullet_matches = re.findall(r'(?:•|\*|\-|\d+\.)\s+(.+?)(?=\n|$)', requirements_text)
            
            if bullet_matches:
                # Process each bullet point
                for bullet in bullet_matches:
                    # Check if it's a must-have
                    is_must_have = False
                    for phrase in self.requirement_phrases:
                        if re.search(phrase, bullet, re.IGNORECASE):
                            is_must_have = True
                            break
                    
                    # Check if it's a nice-to-have
                    is_nice_to_have = False
                    for phrase in self.optional_phrases:
                        if re.search(phrase, bullet, re.IGNORECASE):
                            is_nice_to_have = True
                            break
                    
                    # Categorize the requirement
                    if is_must_have:
                        must_have_requirements.append(bullet)
                    elif is_nice_to_have:
                        nice_to_have_requirements.append(bullet)
                    else:
                        # If no explicit categorization, check for contextual clues
                        if re.search(r'\b(?:should|ideally|typically|usually|generally)\b', bullet, re.IGNORECASE):
                            nice_to_have_requirements.append(bullet)
                        elif re.search(r'\b(?:must|required|essential|need|demonstrate|able to|ability to)\b', bullet, re.IGNORECASE):
                            must_have_requirements.append(bullet)
                        else:
                            ambiguous_requirements.append(bullet)
            else:
                # Try to identify requirements in paragraph format
                sentence_matches = re.findall(r'[^.!?]+[.!?]', requirements_text)
                
                for sentence in sentence_matches:
                    # Check if it's a must-have
                    is_must_have = False
                    for phrase in self.requirement_phrases:
                        if re.search(phrase, sentence, re.IGNORECASE):
                            is_must_have = True
                            break
                    
                    # Check if it's a nice-to-have
                    is_nice_to_have = False
                    for phrase in self.optional_phrases:
                        if re.search(phrase, sentence, re.IGNORECASE):
                            is_nice_to_have = True
                            break
                    
                    # Categorize the requirement
                    if is_must_have:
                        must_have_requirements.append(sentence)
                    elif is_nice_to_have:
                        nice_to_have_requirements.append(sentence)
                    else:
                        # If no explicit categorization, check for contextual clues
                        if re.search(r'\b(?:should|ideally|typically|usually|generally)\b', sentence, re.IGNORECASE):
                            nice_to_have_requirements.append(sentence)
                        elif re.search(r'\b(?:must|required|essential|need|demonstrate|able to|ability to)\b', sentence, re.IGNORECASE):
                            must_have_requirements.append(sentence)
                        else:
                            ambiguous_requirements.append(sentence)
            
            # If there's no explicit nice-to-have section but there are ambiguous requirements,
            # treat a subset of them as implicit nice-to-haves
            if not nice_to_have_requirements and ambiguous_requirements:
                # If must_have_requirements are explicitly marked, then ambiguous ones can be nice-to-have
                if must_have_requirements:
                    nice_to_have_requirements = ambiguous_requirements
                    ambiguous_requirements = []
                # Otherwise, try to split ambiguous ones between must-have and nice-to-have
                else:
                    # First half as must-have, second half as nice-to-have
                    split_point = len(ambiguous_requirements) // 2
                    must_have_requirements = ambiguous_requirements[:split_point]
                    nice_to_have_requirements = ambiguous_requirements[split_point:]
                    ambiguous_requirements = []
            
            # Update results
            requirements_results['has_must_have'] = len(must_have_requirements) > 0
            requirements_results['has_nice_to_have'] = len(nice_to_have_requirements) > 0
            requirements_results['must_have_count'] = len(must_have_requirements)
            requirements_results['nice_to_have_count'] = len(nice_to_have_requirements)
            requirements_results['must_have_requirements'] = must_have_requirements[:7]  # Limit to top 7
            requirements_results['nice_to_have_requirements'] = nice_to_have_requirements[:5]  # Limit to top 5
            requirements_results['ambiguous_requirements'] = ambiguous_requirements[:3]  # Limit to top 3
            
            # Check for excessive requirements
            total_requirements = len(must_have_requirements) + len(nice_to_have_requirements) + len(ambiguous_requirements)
            requirements_results['excessive_requirements'] = total_requirements > 15
            
            # Look for years of experience requirements
            for req in must_have_requirements + nice_to_have_requirements + ambiguous_requirements:
                exp_matches = re.findall(r'(\d+)(?:\+|\s*-\s*\d+)?\s*(?:years?|yrs?)(?:\s+of)?\s+experience', req, re.IGNORECASE)
                if exp_matches:
                    for match in exp_matches:
                        years = int(match)
                        requirement_type = "Must Have" if req in must_have_requirements else "Nice to Have" if req in nice_to_have_requirements else "Unspecified"
                        
                        # Extract the skill or area the experience is required for
                        after_years = req[req.find(match) + len(match):]
                        skill_match = re.search(r'experience(?:\s+(?:in|with))?\s+([^.,;]+)', after_years, re.IGNORECASE)
                        skill_area = skill_match.group(1).strip() if skill_match else "Unspecified area"
                        
                        requirements_results['years_experience_requirements'].append({
                            'years': years,
                            'area': skill_area,
                            'type': requirement_type,
                            'full_text': req
                        })
            
            # Look for education requirements
            education_patterns = [
                (r'\b(?:bachelor\'?s?|bs|ba)\b', "Bachelor's Degree"),
                (r'\b(?:master\'?s?|ms|ma)\b', "Master's Degree"),
                (r'\b(?:phd|doctorate)\b', "PhD/Doctorate"),
                (r'\b(?:mba)\b', "MBA"),
                (r'\bhigh school\b', "High School"),
                (r'\bassociate\'?s?\b', "Associate's Degree")
            ]
            
            for req in must_have_requirements + nice_to_have_requirements + ambiguous_requirements:
                for pattern, level in education_patterns:
                    if re.search(pattern, req, re.IGNORECASE):
                        requirement_type = "Must Have" if req in must_have_requirements else "Nice to Have" if req in nice_to_have_requirements else "Unspecified"
                        
                        # Check if it's required or preferred
                        if re.search(r'\b(?:must|required|need)\b', req, re.IGNORECASE):
                            requirement_status = "Required"
                        elif re.search(r'\b(?:preferred|desirable|ideal)\b', req, re.IGNORECASE):
                            requirement_status = "Preferred"
                        else:
                            requirement_status = "Unspecified"
                        
                        # Look for field of study
                        field_match = re.search(r'\b(?:in|with)\s+([^.,;]+)', req, re.IGNORECASE)
                        field = field_match.group(1).strip() if field_match else "Unspecified field"
                        
                        requirements_results['education_requirements'].append({
                            'level': level,
                            'field': field,
                            'status': requirement_status,
                            'type': requirement_type,
                            'full_text': req
                        })
                        break  # Find the highest level mentioned
            
            # Look for ambiguous or subjective requirements
            ambiguous_terms = [
                r'\b(?:familiar with|knowledge of|understanding of|background in)\b',
                r'\b(?:strong|excellent|exceptional|outstanding|superior)\b',
                r'\b(?:effective|solid|good)\b'
            ]
            
            for req in must_have_requirements + nice_to_have_requirements:
                for term in ambiguous_terms:
                    if re.search(term, req, re.IGNORECASE):
                        if not any(existing_req['text'] == req for existing_req in requirements_results['ambiguous_requirements']):
                            ambiguous_match = re.search(term, req, re.IGNORECASE)
                            ambiguous_term = req[ambiguous_match.start():ambiguous_match.end()]
                            requirements_results['ambiguous_requirements'].append({
                                'text': req,
                                'ambiguous_term': ambiguous_term,
                                'type': "Must Have" if req in must_have_requirements else "Nice to Have"
                            })
                            break
            
            # Calculate requirements score
            requirements_score = 0
            
            # Score based on must-have vs. nice-to-have distinction
            if requirements_results['has_must_have'] and requirements_results['has_nice_to_have']:
                requirements_score += 30
            elif requirements_results['has_must_have'] or requirements_results['has_nice_to_have']:
                requirements_score += 15
            
            # Score based on number of requirements
            if 5 <= requirements_results['must_have_count'] <= 10:
                requirements_score += 25  # Ideal range
            elif 3 <= requirements_results['must_have_count'] < 5 or 10 < requirements_results['must_have_count'] <= 15:
                requirements_score += 15  # Acceptable range
            elif requirements_results['must_have_count'] > 0:
                requirements_score += 5  # At least some requirements
            
            # Penalize for excessive requirements
            if requirements_results['excessive_requirements']:
                requirements_score -= 15
            
            # Score based on clarity (lack of ambiguity)
            ambiguity_ratio = len(requirements_results['ambiguous_requirements']) / total_requirements if total_requirements > 0 else 0
            if ambiguity_ratio <= 0.1:
                requirements_score += 25  # Very clear
            elif ambiguity_ratio <= 0.25:
                requirements_score += 15  # Mostly clear
            elif ambiguity_ratio <= 0.5:
                requirements_score += 5  # Somewhat clear
            
            # Score based on years of experience requirements
            if requirements_results['years_experience_requirements']:
                # Check if experience requirements are reasonable
                max_years = max(req['years'] for req in requirements_results['years_experience_requirements'])
                if max_years <= 5:
                    requirements_score += 10  # Reasonable
                elif max_years <= 8:
                    requirements_score += 5  # Somewhat high
                else:
                    requirements_score -= 5  # Potentially exclusionary
            
            # Score based on education requirements
            if requirements_results['education_requirements']:
                # Check if education is required or preferred
                required_education = [req for req in requirements_results['education_requirements'] if req['status'] == 'Required']
                if not required_education:
                    requirements_score += 10  # No strict education requirements
                elif any(req['level'] in ["High School", "Associate's Degree"] for req in required_education):
                    requirements_score += 5  # Lower barrier to entry
            else:
                requirements_score += 15  # No explicit education requirements
            
            # Ensure score is within bounds
            requirements_results['requirements_score'] = max(0, min(100, requirements_score))
            
            # Add requirements evaluation
            if requirements_results['requirements_score'] >= 85:
                requirements_results['evaluation'] = "Excellent requirements section with clear must-have vs. nice-to-have distinction and reasonable expectations"
            elif requirements_results['requirements_score'] >= 70:
                requirements_results['evaluation'] = "Good requirements section with reasonable expectations"
            elif requirements_results['requirements_score'] >= 50:
                requirements_results['evaluation'] = "Adequate requirements section but could use more clarity"
            else:
                requirements_results['evaluation'] = "Poor requirements section with unclear expectations or potential barriers"
        else:
            # No requirements section found
            requirements_results['evaluation'] = "No clear requirements section found in the job posting"
            requirements_results['requirements_score'] = 0
        
        return requirements_results
    
    def _analyze_inclusivity(self, text):
        """
        Analyze the job posting for inclusive language and diversity considerations.
        
        Args:
            text (str): Job posting text
            
        Returns:
            dict: Inclusivity analysis results
        """
        inclusivity_results = {
            'inclusive_language_score': 0,
            'exclusive_language_instances': [],
            'inclusive_language_instances': [],
            'gendered_language_instances': [],
            'mentions_diversity': False,
            'mentions_equal_opportunity': False,
            'accessibility_considerations': False
        }
        
        # Check for exclusive language patterns
        exclusive_count = 0
        for pattern in self.exclusive_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                context = self._get_context(text, match.start(), match.end())
                exclusive_count += 1
                if len(inclusivity_results['exclusive_language_instances']) < 5:  # Limit to 5 examples
                    inclusivity_results['exclusive_language_instances'].append({
                        'text': context,
                        'term': match.group(0)
                    })
        
        # Check for inclusive language patterns
        inclusive_count = 0
        for pattern in self.inclusive_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                context = self._get_context(text, match.start(), match.end())
                inclusive_count += 1
                if len(inclusivity_results['inclusive_language_instances']) < 5:  # Limit to 5 examples
                    inclusivity_results['inclusive_language_instances'].append({
                        'text': context,
                        'term': match.group(0)
                    })
        
        # Check for gendered language
        gendered_patterns = [
            r'\b(?:he|him|his|himself|man|men|male|guy|guys|gentlemen)\b',
            r'\b(?:she|her|hers|herself|woman|women|female|lady|ladies)\b',
            r'\b(?:maternal|paternal)\b',
            r'\b(?:chairman|chairwoman|fireman|policeman|salesman|stewardess)\b',
            r'\b(?:manpower|workmanship|mankind)\b'
        ]
        
        gendered_count = 0
        for pattern in gendered_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Exclude matches that are part of inclusive alternatives
                if not re.search(r'\b(?:he/she|s?he|him/her)\b', match.group(0), re.IGNORECASE):
                    context = self._get_context(text, match.start(), match.end())
                    gendered_count += 1
                    if len(inclusivity_results['gendered_language_instances']) < 5:  # Limit to 5 examples
                        inclusivity_results['gendered_language_instances'].append({
                            'text': context,
                            'term': match.group(0)
                        })
        
        # Check for diversity and inclusion statements
        diversity_patterns = [
            r'\b(?:diversity|diverse|inclusion|inclusive)\b',
            r'\b(?:equal opportunity|eeo|affirmative action)\b',
            r'\b(?:backgrounds|perspectives|viewpoints)\b',
            r'\bdiscrimination\b'
        ]
        
        for pattern in diversity_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                inclusivity_results['mentions_diversity'] = True
                break
        
        # Check for equal opportunity employer statement
        eeo_patterns = [
            r'equal opportunity employer',
            r'eeo',
            r'does not discriminate',
            r'regardless of (?:race|gender|religion|age|disability|sexual orientation|identity)'
        ]
        
        for pattern in eeo_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                inclusivity_results['mentions_equal_opportunity'] = True
                break
        
        # Check for accessibility considerations
        accessibility_patterns = [
            r'accommodation',
            r'accessible',
            r'disability',
            r'disabilities',
            r'access needs'
        ]
        
        for pattern in accessibility_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                inclusivity_results['accessibility_considerations'] = True
                break
        
        # Calculate inclusivity score
        inclusivity_score = 50  # Start at neutral
        
        # Add points for inclusive language and practices
        inclusivity_score += min(25, inclusive_count * 5)
        
        # Subtract points for exclusive or gendered language
        inclusivity_score -= min(30, (exclusive_count + gendered_count) * 5)
        
        # Add points for diversity and inclusion statements
        if inclusivity_results['mentions_diversity']:
            inclusivity_score += 15
        
        if inclusivity_results['mentions_equal_opportunity']:
            inclusivity_score += 10
        
        if inclusivity_results['accessibility_considerations']:
            inclusivity_score += 10
        
        # Ensure score is within bounds
        inclusivity_results['inclusive_language_score'] = max(0, min(100, inclusivity_score))
        
        # Add inclusivity evaluation
        if inclusivity_results['inclusive_language_score'] >= 85:
            inclusivity_results['evaluation'] = "Excellent use of inclusive language with strong diversity and inclusion statements"
        elif inclusivity_results['inclusive_language_score'] >= 70:
            inclusivity_results['evaluation'] = "Good use of inclusive language with some diversity considerations"
        elif inclusivity_results['inclusive_language_score'] >= 50:
            inclusivity_results['evaluation'] = "Adequate inclusivity but room for improvement"
        else:
            inclusivity_results['evaluation'] = "Poor inclusivity with potential barriers or exclusive language"
        
        return inclusivity_results
    
    def _calculate_quality_scores(self, structure_analysis, content_analysis, requirements_analysis, inclusivity_analysis):
        """
        Calculate overall quality scores for the job posting.
        
        Args:
            structure_analysis (dict): Structure analysis results
            content_analysis (dict): Content analysis results
            requirements_analysis (dict): Requirements analysis results
            inclusivity_analysis (dict): Inclusivity analysis results
            
        Returns:
            dict: Quality scores
        """
        quality_scores = {}
        
        # Title quality
        if 'title_analysis' in content_analysis and content_analysis['title_analysis'].get('is_present', False):
            quality_scores['title_quality'] = {
                'score': content_analysis['title_analysis'].get('score', 0),
                'weight': self.quality_metrics['title_quality']['weight'],
                'description': self.quality_metrics['title_quality']['description'],
                'evaluation': self._generate_score_evaluation(
                    content_analysis['title_analysis'].get('score', 0),
                    "title"
                )
            }
        else:
            quality_scores['title_quality'] = {
                'score': 0,
                'weight': self.quality_metrics['title_quality']['weight'],
                'description': self.quality_metrics['title_quality']['description'],
                'evaluation': "Missing job title"
            }
        
        # Description quality
        description_score = 0
        description_components = 0
        
        if 'company_description_analysis' in content_analysis and content_analysis['company_description_analysis'].get('is_present', False):
            description_score += content_analysis['company_description_analysis'].get('score', 0)
            description_components += 1
        
        if 'job_description_analysis' in content_analysis and content_analysis['job_description_analysis'].get('is_present', False):
            description_score += content_analysis['job_description_analysis'].get('score', 0)
            description_components += 1
        
        if 'responsibilities_analysis' in content_analysis and content_analysis['responsibilities_analysis'].get('is_present', False):
            description_score += content_analysis['responsibilities_analysis'].get('score', 0)
            description_components += 1
        
        if description_components > 0:
            description_score = description_score / description_components
        
        quality_scores['description_quality'] = {
            'score': description_score,
            'weight': self.quality_metrics['description_quality']['weight'],
            'description': self.quality_metrics['description_quality']['description'],
            'evaluation': self._generate_score_evaluation(
                description_score,
                "job description"
            )
        }
        
        # Requirements clarity
        if 'requirements_score' in requirements_analysis:
            quality_scores['requirements_clarity'] = {
                'score': requirements_analysis['requirements_score'],
                'weight': self.quality_metrics['requirements_clarity']['weight'],
                'description': self.quality_metrics['requirements_clarity']['description'],
                'evaluation': self._generate_score_evaluation(
                    requirements_analysis['requirements_score'],
                    "requirements"
                )
            }
        else:
            quality_scores['requirements_clarity'] = {
                'score': 0,
                'weight': self.quality_metrics['requirements_clarity']['weight'],
                'description': self.quality_metrics['requirements_clarity']['description'],
                'evaluation': "Missing requirements section"
            }
        
        # Responsibilities clarity
        if 'responsibilities_analysis' in content_analysis and content_analysis['responsibilities_analysis'].get('is_present', False):
            quality_scores['responsibilities_clarity'] = {
                'score': content_analysis['responsibilities_analysis'].get('score', 0),
                'weight': self.quality_metrics['responsibilities_clarity']['weight'],
                'description': self.quality_metrics['responsibilities_clarity']['description'],
                'evaluation': self._generate_score_evaluation(
                    content_analysis['responsibilities_analysis'].get('score', 0),
                    "responsibilities"
                )
            }
        else:
            quality_scores['responsibilities_clarity'] = {
                'score': 0,
                'weight': self.quality_metrics['responsibilities_clarity']['weight'],
                'description': self.quality_metrics['responsibilities_clarity']['description'],
                'evaluation': "Missing responsibilities section"
            }
        
        # Benefits appeal
        benefits_score = 0
        
        # Check for benefits section in structure analysis
        if 'sections_present' in structure_analysis and 'benefits' in structure_analysis['sections_present']:
            benefits_score += 40
        
        # Add points for each listed benefit
        if 'extracted_info' in locals() and 'benefits' in locals()['extracted_info']:
            benefits_count = len(locals()['extracted_info']['benefits'])
            benefits_score += min(40, benefits_count * 8)
        
        # Add points for salary information
        if 'extracted_info' in locals() and 'salary_range' in locals()['extracted_info'] and locals()['extracted_info']['salary_range']:
            benefits_score += 20
        
        quality_scores['benefits_appeal'] = {
            'score': benefits_score,
            'weight': self.quality_metrics['benefits_appeal']['weight'],
            'description': self.quality_metrics['benefits_appeal']['description'],
            'evaluation': self._generate_score_evaluation(
                benefits_score,
                "benefits"
            )
        }
        
        # Inclusivity score
        quality_scores['inclusivity_score'] = {
            'score': inclusivity_analysis['inclusive_language_score'],
            'weight': self.quality_metrics['inclusivity_score']['weight'],
            'description': self.quality_metrics['inclusivity_score']['description'],
            'evaluation': inclusivity_analysis['evaluation']
        }
        
        # Structure quality
        quality_scores['structure_quality'] = {
            'score': structure_analysis['structure_score'],
            'weight': self.quality_metrics['structure_quality']['weight'],
            'description': self.quality_metrics['structure_quality']['description'],
            'evaluation': structure_analysis['evaluation']
        }
        
        # Calculate overall quality score (weighted average)
        overall_score = sum(
            score_data['score'] * score_data['weight']
            for score_data in quality_scores.values()
        )
        
        quality_scores['overall_quality'] = {
            'score': overall_score,
            'evaluation': self._generate_score_evaluation(
                overall_score,
                "overall job posting"
            )
        }
        
        return quality_scores
    
    def _generate_optimization_suggestions(self, structure_analysis, content_analysis, requirements_analysis, inclusivity_analysis, quality_scores, extracted_info):
        """
        Generate optimization suggestions based on analysis results.
        
        Args:
            structure_analysis (dict): Structure analysis results
            content_analysis (dict): Content analysis results
            requirements_analysis (dict): Requirements analysis results
            inclusivity_analysis (dict): Inclusivity analysis results
            quality_scores (dict): Quality scores
            extracted_info (dict): Extracted job posting information
            
        Returns:
            dict: Optimization suggestions by category
        """
        suggestions = {
            'title_suggestions': [],
            'structure_suggestions': [],
            'content_suggestions': [],
            'requirements_suggestions': [],
            'inclusivity_suggestions': [],
            'general_suggestions': []
        }
        
        # Title suggestions
        if 'title_analysis' in content_analysis:
            title_analysis = content_analysis['title_analysis']
            
            if not title_analysis.get('is_present', False):
                suggestions['title_suggestions'].append("Add a clear job title to the posting")
            elif title_analysis.get('score', 0) < 70:
                if title_analysis.get('specificity', 'Low') == 'Low':
                    suggestions['title_suggestions'].append("Make the job title more specific by including key technologies or specializations (e.g., 'Frontend React Developer' instead of 'Web Developer')")
                
                if title_analysis.get('seniority_level', 'Not specified') == 'Not specified':
                    suggestions['title_suggestions'].append("Indicate the seniority level in the job title (e.g., 'Senior', 'Junior', 'Lead')")
                
                if title_analysis.get('industry_standard', 'No') == 'No':
                    suggestions['title_suggestions'].append("Use industry-standard terminology in the job title to improve searchability")
        
        # Structure suggestions
        if 'sections_missing' in structure_analysis:
            missing_sections = structure_analysis['sections_missing']
            
            for section in missing_sections:
                if section == 'company_overview':
                    suggestions['structure_suggestions'].append("Add a company overview section to introduce your organization to candidates")
                elif section == 'job_description':
                    suggestions['structure_suggestions'].append("Include a job description section that provides context about the role")
                elif section == 'responsibilities':
                    suggestions['structure_suggestions'].append("Add a clear responsibilities section outlining key duties of the role")
                elif section == 'requirements':
                    suggestions['structure_suggestions'].append("Include a requirements section detailing necessary qualifications")
                elif section == 'benefits':
                    suggestions['structure_suggestions'].append("Add a benefits section highlighting what you offer to employees")
                elif section == 'application_process':
                    suggestions['structure_suggestions'].append("Include application instructions to guide candidates on next steps")
        
        if structure_analysis.get('structure_score', 0) < 70:
            if 'section_order' in structure_analysis and structure_analysis['section_order']:
                ideal_order = ['company_overview', 'job_description', 'responsibilities', 'requirements', 'benefits', 'application_process']
                current_order = structure_analysis['section_order']
                
                # Check if the order is significantly different
                if len(set(current_order).intersection(ideal_order)) >= 3:
                    suggestions['structure_suggestions'].append("Consider reordering sections to follow a standard flow: company overview → job description → responsibilities → requirements → benefits → application process")
        
        # Content suggestions
        if 'company_description_analysis' in content_analysis:
            company_analysis = content_analysis['company_description_analysis']
            
            if not company_analysis.get('is_present', False):
                suggestions['content_suggestions'].append("Add a company description to help candidates understand your organization")
            elif company_analysis.get('score', 0) < 70:
                missing_elements = []
                
                if not company_analysis.get('mentions_mission', False):
                    missing_elements.append("mission/vision")
                if not company_analysis.get('mentions_values', False):
                    missing_elements.append("values")
                if not company_analysis.get('mentions_culture', False):
                    missing_elements.append("culture")
                
                if missing_elements:
                    suggestions['content_suggestions'].append(f"Enhance your company description by including information about your {', '.join(missing_elements)}")
        
        if 'job_description_analysis' in content_analysis:
            job_desc_analysis = content_analysis['job_description_analysis']
            
            if not job_desc_analysis.get('is_present', False):
                suggestions['content_suggestions'].append("Add a job description section explaining the role and its context")
            elif job_desc_analysis.get('score', 0) < 70:
                missing_elements = []
                
                if not job_desc_analysis.get('describes_role', False):
                    missing_elements.append("role details")
                if not job_desc_analysis.get('mentions_team', False):
                    missing_elements.append("team context")
                if not job_desc_analysis.get('mentions_impact', False):
                    missing_elements.append("impact of the role")
                
                if missing_elements:
                    suggestions['content_suggestions'].append(f"Improve your job description by adding {', '.join(missing_elements)}")
        
        if 'responsibilities_analysis' in content_analysis:
            resp_analysis = content_analysis['responsibilities_analysis']
            
            if not resp_analysis.get('is_present', False):
                suggestions['content_suggestions'].append("Add a responsibilities section detailing what the candidate will be doing")
            elif resp_analysis.get('score', 0) < 70:
                if not resp_analysis.get('has_bullet_points', False):
                    suggestions['content_suggestions'].append("Format responsibilities as bullet points for better readability")
                
                if resp_analysis.get('responsibility_count', 0) < 5:
                    suggestions['content_suggestions'].append("List more specific responsibilities to give candidates a clearer picture of the role")
        
        # Requirements suggestions
        if 'requirements_present' in requirements_analysis:
            if not requirements_analysis['requirements_present']:
                suggestions['requirements_suggestions'].append("Add a clear requirements section listing necessary qualifications")
            else:
                if not requirements_analysis['has_must_have'] and not requirements_analysis['has_nice_to_have']:
                    suggestions['requirements_suggestions'].append("Distinguish between required and preferred qualifications")
                
                if requirements_analysis['excessive_requirements']:
                    suggestions['requirements_suggestions'].append("Reduce the number of requirements to focus on the most essential qualifications")
                
                if requirements_analysis['years_experience_requirements']:
                    high_experience_reqs = [
                        req for req in requirements_analysis['years_experience_requirements'] 
                        if req['years'] > 5 and req['type'] == "Must Have"
                    ]
                    
                    if high_experience_reqs:
                        suggestions['requirements_suggestions'].append("Consider reducing years of experience requirements or moving them to 'Nice to Have' to avoid excluding qualified candidates")
                
                if requirements_analysis['ambiguous_requirements']:
                    suggestions['requirements_suggestions'].append("Replace ambiguous terms like 'familiar with' or 'strong' with more specific, measurable criteria")
        
        # Inclusivity suggestions
        if inclusivity_analysis['inclusive_language_score'] < 70:
            if inclusivity_analysis['gendered_language_instances']:
                suggestions['inclusivity_suggestions'].append("Replace gendered terms with gender-neutral alternatives")
            
            if inclusivity_analysis['exclusive_language_instances']:
                suggestions['inclusivity_suggestions'].append("Remove potentially exclusive language that might deter diverse candidates")
            
            if not inclusivity_analysis['mentions_diversity']:
                suggestions['inclusivity_suggestions'].append("Add a statement about your commitment to diversity and inclusion")
            
            if not inclusivity_analysis['mentions_equal_opportunity']:
                suggestions['inclusivity_suggestions'].append("Include an equal opportunity employer statement")
            
            if not inclusivity_analysis['accessibility_considerations']:
                suggestions['inclusivity_suggestions'].append("Add information about accommodations for candidates with disabilities")
        
        # General suggestions
        benefits_score = quality_scores.get('benefits_appeal', {}).get('score', 0)
        if benefits_score < 60:
            missing_benefits = []
            common_benefits = ["health insurance", "paid time off", "retirement plans", "professional development", "flexible working arrangements"]
            
            extracted_benefits = [b.lower() for b in extracted_info.get('benefits', [])]
            for benefit in common_benefits:
                if not any(benefit in b for b in extracted_benefits):
                    missing_benefits.append(benefit)
            
            if missing_benefits:
                suggestions['general_suggestions'].append(f"Highlight more benefits such as {', '.join(missing_benefits)}")
            
            if not extracted_info.get('salary_range'):
                suggestions['general_suggestions'].append("Consider including salary information to attract more qualified candidates")
        
        # Prioritize and limit suggestions
        for category in suggestions:
            if len(suggestions[category]) > 3:
                suggestions[category] = suggestions[category][:3]
        
        # Add improved job posting template if overall score is below threshold
        overall_score = quality_scores.get('overall_quality', {}).get('score', 0)
        if overall_score < 60:
            job_title = extracted_info.get('job_title', '[Job Title]')
            company_name = extracted_info.get('company_name', '[Company Name]')
            
            template = self._generate_job_posting_template(job_title, company_name, extracted_info)
            suggestions['improved_job_posting_template'] = template
        
        return suggestions
    
    def _generate_job_posting_template(self, job_title, company_name, extracted_info):
        """
        Generate an improved job posting template based on extracted information.
        
        Args:
            job_title (str): Job title
            company_name (str): Company name
            extracted_info (dict): Extracted job posting information
            
        Returns:
            str: Improved job posting template
        """
        # Use actual information where available
        employment_type = extracted_info.get('employment_type', 'Full-time')
        location = extracted_info.get('location', '[Location]')
        work_arrangement = extracted_info.get('work_arrangement', '[Work Arrangement]')
        
        template = f"""# {job_title} at {company_name}

## About Us
{company_name} is [2-3 sentences about your company mission, values, and what makes it special]. We're passionate about [industry/product] and committed to [company goal].

## The Role
We're looking for a {job_title} to join our team. This is a {employment_type} role based in {location} with a {work_arrangement} working arrangement.

In this position, you'll be responsible for developing and implementing solutions that help us [achieve business goal]. You'll work closely with cross-functional teams to deliver high-quality results.

## What You'll Do
• [Specific responsibility with impact]
• [Specific responsibility with impact]
• [Specific responsibility with impact]
• [Specific responsibility with impact]
• [Specific responsibility with impact]

## Required Qualifications
• [Essential skill/qualification]
• [Essential skill/qualification]
• [Essential skill/qualification]
• [Essential skill/qualification]

## Preferred Qualifications
• [Nice-to-have skill/qualification]
• [Nice-to-have skill/qualification]
• [Nice-to-have skill/qualification]

## What We Offer
"""
        
        # Add benefits if available
        if extracted_info.get('benefits'):
            for benefit in extracted_info.get('benefits')[:5]:
                template += f"• {benefit}\n"
        else:
            template += """• Competitive salary and benefits package
• Professional development opportunities
• Collaborative and inclusive work environment
• [Other benefits/perks]
• [Other benefits/perks]
"""
        
        # Add equal opportunity statement
        template += """
## How to Apply
[Instructions for applying, including any required documents and the application process]

{company_name} is an equal opportunity employer. We celebrate diversity and are committed to creating an inclusive environment for all employees.
"""
        
        return template
    
    def _get_context(self, text, start_pos, end_pos, context_chars=100):
        """
        Get surrounding context for a match in the text.
        
        Args:
            text (str): Full text
            start_pos (int): Start position of the match
            end_pos (int): End position of the match
            context_chars (int): Number of characters of context to include
            
        Returns:
            str: Context string
        """
        # Calculate context boundaries
        start = max(0, start_pos - context_chars)
        end = min(len(text), end_pos + context_chars)
        
        # Get context with the match in the middle
        context = text[start:end]
        
        # Try to make the context more readable by starting and ending at sentence boundaries
        if start > 0:
            sentence_start = context.find('. ')
            if sentence_start != -1:
                context = context[sentence_start + 2:]
        
        if end < len(text):
            sentence_end = context.rfind('. ')
            if sentence_end != -1:
                context = context[:sentence_end + 1]
        
        return context.strip()
    
    def _generate_score_evaluation(self, score, category):
        """
        Generate an evaluation message based on a score.
        
        Args:
            score (float): Score value
            category (str): Category being evaluated
            
        Returns:
            str: Evaluation message
        """
        if score >= 90:
            return f"Excellent {category}"
        elif score >= 80:
            return f"Very good {category}"
        elif score >= 70:
            return f"Good {category}"
        elif score >= 60:
            return f"Above average {category}"
        elif score >= 50:
            return f"Average {category}"
        elif score >= 40:
            return f"Below average {category}"
        elif score >= 30:
            return f"Poor {category}"
        elif score >= 20:
            return f"Very poor {category}"
        else:
            return f"Inadequate {category}"

    def optimize_requirements(self, requirements_text):
        """
        Optimize a job requirements section to be more inclusive and effective.
        
        Args:
            requirements_text (str): Requirements section text
            
        Returns:
            dict: Optimized requirements with explanations
        """
        # First analyze the requirements
        processed_doc = self.text_processor.process_document(requirements_text, 'job_description')
        
        # Extract requirements as bullet points or sentences
        raw_requirements = []
        bullet_matches = re.findall(r'(?:•|\*|\-|\d+\.)\s+(.+?)(?=\n|$)', requirements_text)
        
        if bullet_matches:
            raw_requirements = bullet_matches
        else:
            # Try to identify requirements in paragraph format
            sentence_matches = re.findall(r'[^.!?]+[.!?]', requirements_text)
            if sentence_matches:
                raw_requirements = sentence_matches
        
        # Categorize and optimize each requirement
        must_have = []
        nice_to_have = []
        
        for req in raw_requirements:
            req = req.strip()
            
            # Skip empty requirements
            if not req:
                continue
            
            # Check if it's explicitly a must-have
            is_must_have = any(re.search(phrase, req, re.IGNORECASE) for phrase in self.requirement_phrases)
            
            # Check if it's explicitly a nice-to-have
            is_nice_to_have = any(re.search(phrase, req, re.IGNORECASE) for phrase in self.optional_phrases)
            
            # Process the requirement
            optimized_req, rationale = self._optimize_single_requirement(req)
            
            # Categorize based on original classification or content
            if is_nice_to_have or re.search(r'\b(?:ideally|plus|bonus|helpful|preferred)\b', req, re.IGNORECASE):
                nice_to_have.append({
                    'original': req,
                    'optimized': optimized_req,
                    'rationale': rationale
                })
            elif is_must_have or re.search(r'\b(?:must|required|essential|needs?)\b', req, re.IGNORECASE):
                must_have.append({
                    'original': req,
                    'optimized': optimized_req,
                    'rationale': rationale
                })
            else:
                # Use content to determine categorization
                if re.search(r'\b(?:\d+\+?\s*(?:years?|yrs?))\b', req, re.IGNORECASE) or re.search(r'\b(?:degree|bachelor|master|phd)\b', req, re.IGNORECASE):
                    # Move experience and education requirements to nice-to-have unless clearly stated as required
                    nice_to_have.append({
                        'original': req,
                        'optimized': optimized_req,
                        'rationale': rationale + " (Moved to preferred qualifications to be more inclusive)"
                    })
                else:
                    must_have.append({
                        'original': req,
                        'optimized': optimized_req,
                        'rationale': rationale
                    })
        
        # Generate formatted requirements sections
        formatted_must_have = "## Required Qualifications\n\n"
        for req in must_have:
            formatted_must_have += f"- {req['optimized']}\n"
        
        formatted_nice_to_have = "\n## Preferred Qualifications\n\n"
        for req in nice_to_have:
            formatted_nice_to_have += f"- {req['optimized']}\n"
        
        formatted_requirements = formatted_must_have + formatted_nice_to_have
        
        # Generate explanations for the changes
        explanations = {
            'structure_changes': "Requirements have been organized into 'Required' and 'Preferred' sections for clarity",
            'language_changes': "Ambiguous language has been replaced with more specific, measurable criteria",
            'inclusivity_improvements': "Barriers to entry have been reduced by moving some requirements to the 'Preferred' section",
            'specific_changes': []
        }
        
        for req in must_have + nice_to_have:
            if req['original'] != req['optimized']:
                explanations['specific_changes'].append({
                    'original': req['original'],
                    'optimized': req['optimized'],
                    'rationale': req['rationale']
                })
        
        return {
            'optimized_requirements': formatted_requirements,
            'must_have_count': len(must_have),
            'nice_to_have_count': len(nice_to_have),
            'explanations': explanations
        }
    
    def _optimize_single_requirement(self, requirement):
        """
        Optimize a single job requirement to be more inclusive and specific.
        
        Args:
            requirement (str): Job requirement text
            
        Returns:
            tuple: (optimized_requirement, rationale)
        """
        original = requirement
        rationale = []
        
        # Replace experience requirements
        exp_match = re.search(r'(\d+)(?:\+|\s*-\s*\d+)?\s*(?:years?|yrs?)(?:\s+of)?\s+experience', requirement, re.IGNORECASE)
        if exp_match:
            years = int(exp_match.group(1))
            
            if years > 5:
                # High experience requirements can exclude qualified candidates
                new_req = requirement.replace(exp_match.group(0), f"experience with" if years <= 8 else f"significant experience with")
                rationale.append(f"Removed specific years requirement ({years} years) to focus on actual skills and avoid excluding qualified candidates")
                requirement = new_req
            elif years >= 3:
                after_match = requirement[exp_match.end():]
                skill_match = re.search(r'(?:in|with)\s+([^.,;]+)', after_match, re.IGNORECASE)
                
                if skill_match:
                    skill_area = skill_match.group(1).strip()
                    new_req = requirement.replace(exp_match.group(0), "proven experience")
                    rationale.append(f"Changed '{exp_match.group(0)}' to 'proven experience' to focus on demonstrated ability rather than time")
                    requirement = new_req
        
        # Replace education requirements if not clearly necessary
        edu_patterns = [
            (r'\b(?:bachelor\'?s?|bs|ba)\s+(?:degree)?\s+(?:in|with)\s+([^.,;]+)', "Bachelor's degree in"),
            (r'\b(?:master\'?s?|ms|ma)\s+(?:degree)?\s+(?:in|with)\s+([^.,;]+)', "Master's degree in"),
            (r'\b(?:phd|doctorate)\s+(?:in|with)\s+([^.,;]+)', "PhD in")
        ]
        
        for pattern, replacement_base in edu_patterns:
            edu_match = re.search(pattern, requirement, re.IGNORECASE)
            if edu_match:
                field = edu_match.group(1).strip() if len(edu_match.groups()) > 0 else ""
                
                # Check if it's presented as a hard requirement
                if re.search(r'\b(?:must|required|need)\b', requirement, re.IGNORECASE):
                    # Keep as is, but enhance clarity
                    if field:
                        new_req = re.sub(pattern, f"{replacement_base} {field} or equivalent practical experience", requirement, flags=re.IGNORECASE)
                        rationale.append(f"Added 'or equivalent practical experience' to education requirement to be more inclusive")
                        requirement = new_req
                else:
                    # Convert to preferred or equivalent experience
                    if field:
                        new_req = re.sub(pattern, f"{replacement_base} {field} or equivalent practical experience", requirement, flags=re.IGNORECASE)
                        rationale.append(f"Added 'or equivalent practical experience' to education requirement to be more inclusive")
                        requirement = new_req
        
        # Replace ambiguous qualifiers
        ambiguous_terms = [
            (r'\bfamiliar with\b', "experience using"),
            (r'\bknowledge of\b', "experience with"),
            (r'\bunderstanding of\b', "experience applying"),
            (r'\bstrong\b', "demonstrated"),
            (r'\bexcellent\b', "proven"),
            (r'\boutstanding\b', "effective")
        ]
        
        for term, replacement in ambiguous_terms:
            if re.search(term, requirement, re.IGNORECASE):
                new_req = re.sub(term, replacement, requirement, flags=re.IGNORECASE)
                rationale.append(f"Replaced ambiguous term '{term.strip()}' with more specific '{replacement}'")
                requirement = new_req
        
        # Make bullet points consistent and action-oriented
        if not requirement.strip().startswith(("Experience", "Ability", "Knowledge", "Skills", "Proficient")):
            # Try to convert to an action-oriented format
            for prefix in ["Experience with", "Ability to", "Proficiency in"]:
                if re.search(r'\b' + re.escape(prefix.lower()) + r'\b', requirement.lower()):
                    # Already has an action prefix somewhere in the text
                    break
            else:
                # No action prefix found, add one if appropriate
                if re.search(r'\b(?:using|developing|managing|creating|designing|implementing)\b', requirement, re.IGNORECASE):
                    new_req = f"Experience with {requirement[0].lower()}{requirement[1:]}"
                    rationale.append(f"Reformatted to start with action-oriented 'Experience with' for consistency")
                    requirement = new_req
                elif re.search(r'\b(?:communicate|collaborate|work|solve|analyze|lead|present)\b', requirement, re.IGNORECASE):
                    new_req = f"Ability to {requirement[0].lower()}{requirement[1:]}"
                    rationale.append(f"Reformatted to start with action-oriented 'Ability to' for consistency")
                    requirement = new_req
        
        # If no changes were made
        if original == requirement:
            return requirement, "No changes needed"
        
        return requirement, "; ".join(rationale)