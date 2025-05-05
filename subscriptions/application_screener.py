"""
Application Screening Assistant

This module implements functionality for screening job applications using the core infrastructure
components (document parsing, text processing, content validation, and data resources).
It provides automated application review, scoring, and filtering to help employers identify
the most qualified candidates efficiently.
"""

import logging
import re
from collections import defaultdict, Counter
import math
from operator import itemgetter

from .document_parser import DocumentParser
from .text_processor import TextProcessor
from .content_validator import ContentValidator
from .data_resources import (
    get_all_skills,
    get_technical_skills_by_category,
    get_soft_skills,
    get_job_titles,
    get_education_data
)

logger = logging.getLogger(__name__)

class ApplicationScreener:
    """
    Class for screening job applications using the core infrastructure.
    
    This class provides comprehensive application screening functionality with scoring,
    filtering, and automated initial assessment to help employers identify qualified candidates.
    """
    
    def __init__(self):
        """Initialize the ApplicationScreener with necessary components."""
        self.document_parser = DocumentParser()
        self.text_processor = TextProcessor()
        self.content_validator = ContentValidator(self.text_processor)
        
        # Load skills data
        self.all_skills = get_all_skills()
        self.technical_skills = get_technical_skills_by_category()
        self.soft_skills = get_soft_skills()
        self.job_titles = get_job_titles()
        self.education_data = get_education_data()
        
        # Define weights for different screening factors
        self.weights = {
            'skills_match': 0.35,
            'experience_match': 0.25,
            'education_match': 0.20,
            'resume_quality': 0.10,
            'cover_letter_quality': 0.10
        }
        
        # Different tiers of candidate quality
        self.candidate_tiers = {
            'excellent': (90, 100),
            'strong': (80, 89),
            'good': (70, 79),
            'potential': (60, 69),
            'limited': (40, 59),
            'poor': (0, 39)
        }
    
    def screen_application(self, job_listing, application_data):
        """
        Screen a job application against job requirements.
        
        Args:
            job_listing (dict): Job listing information including:
                - title (str): Job title
                - description (str): Job description
                - requirements (str): Job requirements
                - skills_required (str/list): Required skills
                - preferred_skills (str/list): Preferred skills
                - education_required (str): Required education
                - min_experience (int): Minimum years of experience
                
            application_data (dict): Application data including:
                - resume_text (str, optional): Text of resume
                - resume_file (file, optional): Resume file object
                - resume_file_name (str, optional): Name of resume file
                - cover_letter_text (str, optional): Text of cover letter
                - cover_letter_file (file, optional): Cover letter file object
                - cover_letter_file_name (str, optional): Name of cover letter file
                - candidate_name (str, optional): Name of the candidate
                - application_note (str, optional): Additional application notes
                
        Returns:
            dict: Screening results
        """
        try:
            # Validate inputs
            if not job_listing:
                return {
                    'error': 'No job listing provided for screening',
                    'is_valid': False
                }
                
            if not application_data:
                return {
                    'error': 'No application data provided for screening',
                    'is_valid': False
                }
            
            # Extract resume text
            resume_text = self._extract_resume_text(application_data)
            if not resume_text:
                return {
                    'error': 'No resume provided or could not extract resume text',
                    'is_valid': False
                }
            
            # Validate the resume
            resume_validation = self.content_validator.validate_document(resume_text)
            if resume_validation['document_type'] != 'resume' or resume_validation['confidence'] < self.content_validator.MEDIUM_CONFIDENCE:
                return {
                    'error': 'The provided document does not appear to be a valid resume',
                    'is_valid': False,
                    'confidence': resume_validation['confidence'],
                    'detected_type': resume_validation['document_type']
                }
            
            # Extract cover letter text if available
            cover_letter_text = self._extract_cover_letter_text(application_data)
            
            # Process the resume
            processed_resume = self.text_processor.process_document(resume_text, 'resume')
            
            # Process the cover letter if available
            processed_cover_letter = None
            if cover_letter_text:
                cover_letter_validation = self.content_validator.validate_document(cover_letter_text)
                if cover_letter_validation['document_type'] == 'cover_letter' and cover_letter_validation['confidence'] >= self.content_validator.LOW_CONFIDENCE:
                    processed_cover_letter = self.text_processor.process_document(cover_letter_text, 'cover_letter')
            
            # Extract job requirements
            job_requirements = self._extract_job_requirements(job_listing)
            
            # Calculate scores
            scores = self._calculate_scores(
                processed_resume, 
                processed_cover_letter, 
                job_requirements
            )
            
            # Determine candidate tier
            tier = self._determine_candidate_tier(scores['overall_score'])
            
            # Generate screening summary
            screening_summary = self._generate_screening_summary(
                scores, 
                tier, 
                processed_resume, 
                processed_cover_letter, 
                job_requirements
            )
            
            # Prepare final result
            result = {
                'is_valid': True,
                'candidate_name': application_data.get('candidate_name', 'Unknown Candidate'),
                'overall_score': scores['overall_score'],
                'candidate_tier': tier,
                'skills_match': scores['skills_match'],
                'experience_match': scores['experience_match'],
                'education_match': scores['education_match'],
                'resume_quality': scores['resume_quality'],
                'cover_letter_quality': scores.get('cover_letter_quality', {'score': 0, 'evaluation': 'No cover letter provided'}),
                'has_cover_letter': processed_cover_letter is not None,
                'screening_summary': screening_summary,
                'job_title': job_listing.get('title', 'Unknown Position')
            }
            
            # Add red flags if found
            red_flags = self._identify_red_flags(processed_resume, processed_cover_letter, job_requirements)
            if red_flags:
                result['red_flags'] = red_flags
            
            # Add recommended actions
            result['recommended_actions'] = self._recommend_actions(scores, tier, red_flags)
            
            # Add suggested screening questions for interview
            result['suggested_questions'] = self._generate_screening_questions(
                processed_resume, 
                job_requirements, 
                scores
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error in application screening: {str(e)}")
            return {
                'error': f"Error screening application: {str(e)}",
                'is_valid': False
            }
    
    def bulk_screen_applications(self, job_listing, applications):
        """
        Screen multiple applications and provide ranked results.
        
        Args:
            job_listing (dict): Job listing information
            applications (list): List of application data dicts
                
        Returns:
            dict: Screening results for all applications, ranked by score
        """
        try:
            # Validate inputs
            if not job_listing:
                return {
                    'error': 'No job listing provided for screening',
                    'is_valid': False
                }
                
            if not applications or not isinstance(applications, list):
                return {
                    'error': 'No applications provided for screening',
                    'is_valid': False
                }
            
            # Screen each application
            screening_results = []
            for application in applications:
                result = self.screen_application(job_listing, application)
                if result.get('is_valid', False):
                    result['application_id'] = application.get('id')
                    screening_results.append(result)
            
            # Sort by overall score
            screening_results.sort(key=lambda x: x['overall_score'], reverse=True)
            
            # Group candidates by tier
            candidates_by_tier = defaultdict(list)
            for result in screening_results:
                candidates_by_tier[result['candidate_tier']].append(result)
            
            # Calculate stats
            stats = {
                'total_applications': len(applications),
                'valid_applications': len(screening_results),
                'tier_distribution': {tier: len(candidates) for tier, candidates in candidates_by_tier.items()},
                'average_score': sum(r['overall_score'] for r in screening_results) / max(1, len(screening_results))
            }
            
            return {
                'is_valid': True,
                'job_title': job_listing.get('title', 'Unknown Position'),
                'screening_results': screening_results,
                'candidates_by_tier': {tier: [
                    {'candidate_name': r['candidate_name'], 
                     'overall_score': r['overall_score'],
                     'application_id': r.get('application_id')} 
                    for r in candidates
                ] for tier, candidates in candidates_by_tier.items()},
                'stats': stats
            }
            
        except Exception as e:
            logger.error(f"Error in bulk application screening: {str(e)}")
            return {
                'error': f"Error screening applications: {str(e)}",
                'is_valid': False
            }
    
    def generate_screening_criteria(self, job_listing):
        """
        Generate screening criteria based on job listing.
        
        Args:
            job_listing (dict): Job listing information
                
        Returns:
            dict: Recommended screening criteria
        """
        try:
            job_requirements = self._extract_job_requirements(job_listing)
            
            # Identify must-have skills versus nice-to-have
            must_have_skills = job_requirements.get('required_skills', [])[:5]  # Top 5 required skills
            nice_to_have_skills = job_requirements.get('preferred_skills', [])
            
            # Define minimum education level
            education_req = job_requirements.get('education_requirements', {})
            min_education = education_req.get('min_degree_level', 'Bachelor\'s degree')
            education_fields = education_req.get('preferred_fields', [])
            
            # Define minimum experience
            min_experience = job_requirements.get('experience_requirements', {}).get('min_years', 1)
            experience_areas = job_requirements.get('experience_requirements', {}).get('areas', [])
            
            # Generate questions for screening
            general_questions = [
                "Why are you interested in this position?",
                "What makes you a good fit for our company?",
                "What are your salary expectations?",
                "When would you be available to start?",
                "Are you legally authorized to work in this country?"
            ]
            
            skill_questions = [f"Describe your experience with {skill}" for skill in must_have_skills[:3]]
            
            experience_questions = []
            for area in experience_areas[:2]:
                experience_questions.append(f"Tell me about your experience with {area}")
            
            # Create screening criteria
            screening_criteria = {
                'skills': {
                    'must_have': must_have_skills,
                    'nice_to_have': nice_to_have_skills
                },
                'education': {
                    'minimum_level': min_education,
                    'preferred_fields': education_fields
                },
                'experience': {
                    'minimum_years': min_experience,
                    'key_areas': experience_areas
                },
                'screening_questions': general_questions + skill_questions + experience_questions,
                'automatic_disqualifiers': [
                    "Insufficient required skills",
                    "Does not meet minimum experience requirement",
                    "Does not meet minimum education requirement",
                    "Ineligible to work in the country",
                    "Salary expectations far exceed budget"
                ],
                'red_flags': [
                    "Frequent job changes (less than 1 year)",
                    "Unexplained gaps in employment",
                    "Declining career progression",
                    "Poor attention to detail in application",
                    "Generic application not tailored to position"
                ]
            }
            
            return {
                'is_valid': True,
                'job_title': job_listing.get('title', 'Unknown Position'),
                'screening_criteria': screening_criteria
            }
            
        except Exception as e:
            logger.error(f"Error generating screening criteria: {str(e)}")
            return {
                'error': f"Error generating screening criteria: {str(e)}",
                'is_valid': False
            }
    
    def _extract_resume_text(self, application_data):
        """Extract resume text from application data."""
        # Check if resume text is directly provided
        if 'resume_text' in application_data and application_data['resume_text']:
            return application_data['resume_text']
        
        # Try to extract text from resume file
        if 'resume_file' in application_data and application_data['resume_file']:
            try:
                if 'resume_file_name' in application_data:
                    return self.document_parser.extract_text_from_file_object(
                        application_data['resume_file'],
                        application_data['resume_file_name']
                    )
                elif hasattr(application_data['resume_file'], 'name'):
                    return self.document_parser.extract_text_from_file_object(
                        application_data['resume_file'],
                        application_data['resume_file'].name
                    )
            except Exception as e:
                logger.error(f"Error extracting text from resume file: {str(e)}")
        
        # Try to extract from file path
        if 'resume_file_path' in application_data and application_data['resume_file_path']:
            try:
                return self.document_parser.extract_text(application_data['resume_file_path'])
            except Exception as e:
                logger.error(f"Error extracting text from resume file path: {str(e)}")
        
        return None
    
    def _extract_cover_letter_text(self, application_data):
        """Extract cover letter text from application data."""
        # Check if cover letter text is directly provided
        if 'cover_letter_text' in application_data and application_data['cover_letter_text']:
            return application_data['cover_letter_text']
        
        # Try to extract text from cover letter file
        if 'cover_letter_file' in application_data and application_data['cover_letter_file']:
            try:
                if 'cover_letter_file_name' in application_data:
                    return self.document_parser.extract_text_from_file_object(
                        application_data['cover_letter_file'],
                        application_data['cover_letter_file_name']
                    )
                elif hasattr(application_data['cover_letter_file'], 'name'):
                    return self.document_parser.extract_text_from_file_object(
                        application_data['cover_letter_file'],
                        application_data['cover_letter_file'].name
                    )
            except Exception as e:
                logger.error(f"Error extracting text from cover letter file: {str(e)}")
        
        # Try to extract from file path
        if 'cover_letter_file_path' in application_data and application_data['cover_letter_file_path']:
            try:
                return self.document_parser.extract_text(application_data['cover_letter_file_path'])
            except Exception as e:
                logger.error(f"Error extracting text from cover letter file path: {str(e)}")
        
        return None
    
    def _extract_job_requirements(self, job_listing):
        """
        Extract the key requirements from a job listing.
        
        Args:
            job_listing (dict): Job listing data
            
        Returns:
            dict: Structured job requirements
        """
        # Get base text
        job_description = job_listing.get('description', '')
        job_requirements_text = job_listing.get('requirements', '')
        
        # Combine if needed
        full_text = job_description
        if job_requirements_text and job_requirements_text not in job_description:
            full_text = f"{job_description}\n\n{job_requirements_text}"
        
        # Process the job description
        processed_job = self.text_processor.process_document(full_text, 'job_description')
        
        # Extract skills from both the processed job and directly from the job listing
        required_skills = set(processed_job.get('extracted_skills', []))
        preferred_skills = set()
        
        # Add skills directly specified in the job listing
        skills_required = job_listing.get('skills_required', '')
        if skills_required:
            if isinstance(skills_required, str):
                for skill in skills_required.split(','):
                    skill = skill.strip().lower()
                    if skill:
                        required_skills.add(skill)
            elif isinstance(skills_required, list):
                for skill in skills_required:
                    skill = skill.strip().lower() if isinstance(skill, str) else str(skill).lower()
                    if skill:
                        required_skills.add(skill)
        
        # Add preferred skills if specified
        skills_preferred = job_listing.get('preferred_skills', '')
        if skills_preferred:
            if isinstance(skills_preferred, str):
                for skill in skills_preferred.split(','):
                    skill = skill.strip().lower()
                    if skill:
                        preferred_skills.add(skill)
            elif isinstance(skills_preferred, list):
                for skill in skills_preferred:
                    skill = skill.strip().lower() if isinstance(skill, str) else str(skill).lower()
                    if skill:
                        preferred_skills.add(skill)
        
        # Extract education requirements
        education_req = self._extract_education_requirements(full_text, job_listing)
        
        # Extract experience requirements
        experience_req = self._extract_experience_requirements(full_text, job_listing)
        
        # Get job title and location
        job_title = job_listing.get('title', '')
        job_location = job_listing.get('location', '')
        
        return {
            'job_title': job_title,
            'job_location': job_location,
            'required_skills': list(required_skills),
            'preferred_skills': list(preferred_skills),
            'education_requirements': education_req,
            'experience_requirements': experience_req,
            'job_category': processed_job.get('extracted_category', ''),
            'job_industry': processed_job.get('extracted_industry', '')
        }
    
    def _extract_education_requirements(self, text, job_listing=None):
        """
        Extract education requirements from job text and listing.
        
        Args:
            text (str): Job description/requirements text
            job_listing (dict, optional): Job listing data
            
        Returns:
            dict: Education requirements
        """
        education_req = {
            'min_degree_level': None,
            'preferred_fields': [],
            'required': False
        }
        
        # Check if education is explicitly specified in job listing
        if job_listing and 'education_required' in job_listing:
            education_text = job_listing.get('education_required', '')
            if education_text:
                education_req['min_degree_level'] = education_text
                education_req['required'] = True
        
        # If not, extract from text
        if not education_req['min_degree_level']:
            # Degree level patterns
            degree_patterns = [
                (r'\b(?:phd|doctorate|doctoral)\b', 'PhD', 5),
                (r'\b(?:master\'?s?|ms|ma|mba)\b', 'Master\'s', 4),
                (r'\b(?:bachelor\'?s?|bs|ba|bsc|undergraduate degree)\b', 'Bachelor\'s', 3),
                (r'\b(?:associate\'?s?|aas|aa)\b', 'Associate\'s', 2),
                (r'\b(?:high school|diploma|ged)\b', 'High School', 1)
            ]
            
            # Find the highest degree level mentioned
            highest_level = 0
            for pattern, degree, level in degree_patterns:
                if re.search(pattern, text.lower()):
                    if level > highest_level:
                        highest_level = level
                        education_req['min_degree_level'] = degree
            
            # Check if education is required or preferred
            if re.search(r'\b(?:must have|required|minimum)\b.*(?:degree|education)\b', text.lower()):
                education_req['required'] = True
        
        # Extract fields of study
        field_patterns = [
            r'(?:degree|education)(?:[^.]*?)(in|with)([^.]*?)(?:\.|\,|\(|or |and |preferred|required|\+|;)',
            r'(?:bachelor\'?s?|master\'?s?|phd|doctorate|ms|ma|mba|bs|ba)(?:[^.]*?)(in|with)([^.]*?)(?:\.|\,|\(|or |and |preferred|required|\+|;)'
        ]
        
        fields = set()
        for pattern in field_patterns:
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                if len(match.groups()) > 1:
                    field_text = match.group(2).strip()
                    # Clean up the field text
                    field_text = re.sub(r'\b(?:or|and|the|a|an|degree|field)\b', '', field_text)
                    # Split into multiple fields if needed
                    for field in re.split(r'[,/]', field_text):
                        clean_field = field.strip()
                        if clean_field and len(clean_field) > 2:
                            fields.add(clean_field)
        
        education_req['preferred_fields'] = list(fields)
        
        return education_req
    
    def _extract_experience_requirements(self, text, job_listing=None):
        """
        Extract experience requirements from job text and listing.
        
        Args:
            text (str): Job description/requirements text
            job_listing (dict, optional): Job listing data
            
        Returns:
            dict: Experience requirements
        """
        experience_req = {
            'min_years': 0,
            'preferred_years': 0,
            'areas': []
        }
        
        # Check if experience is explicitly specified in job listing
        if job_listing and 'min_experience' in job_listing:
            min_exp = job_listing.get('min_experience')
            if min_exp is not None:
                try:
                    experience_req['min_years'] = int(min_exp)
                except (ValueError, TypeError):
                    # Try to extract number from text
                    if isinstance(min_exp, str):
                        match = re.search(r'(\d+)', min_exp)
                        if match:
                            try:
                                experience_req['min_years'] = int(match.group(1))
                            except (ValueError, IndexError):
                                pass
        
        # If min_years is still 0, try to extract from text
        if experience_req['min_years'] == 0:
            # Experience patterns
            exp_patterns = [
                r'(\d+)(?:\+|\s*\+|\s*plus|\s*or more)?\s*(?:years?|yrs?)(?:\s+of)?\s+experience',
                r'experience(?:\s+of)?\s+(\d+)(?:\+|\s*\+|\s*plus|\s*or more)?\s*(?:years?|yrs?)'
            ]
            
            years = []
            for pattern in exp_patterns:
                matches = re.finditer(pattern, text.lower())
                for match in matches:
                    try:
                        year = int(match.group(1))
                        years.append(year)
                    except (ValueError, IndexError):
                        continue
            
            if years:
                # Find minimum years (usually the smallest number in a required context)
                required_years = []
                preferred_years = []
                
                for year in years:
                    # Try to determine context (within 50 characters before or after)
                    for match in re.finditer(r'\b\d+\b', text):
                        if str(year) == match.group(0):
                            start = max(0, match.start() - 50)
                            end = min(len(text), match.end() + 50)
                            context = text[start:end].lower()
                            
                            if re.search(r'\b(?:required|must have|minimum|at least)\b', context):
                                required_years.append(year)
                            elif re.search(r'\b(?:preferred|ideally|nice to have|plus)\b', context):
                                preferred_years.append(year)
                            else:
                                # Default to required
                                required_years.append(year)
                
                if required_years:
                    experience_req['min_years'] = min(required_years)
                
                if preferred_years:
                    experience_req['preferred_years'] = min(preferred_years)
                
                # If we have years but couldn't classify them, use the minimum as required
                if not required_years and not preferred_years and years:
                    experience_req['min_years'] = min(years)
        
        # Extract experience areas
        exp_area_patterns = [
            r'experience (?:in|with) ([^.,;()]+)',
            r'knowledge of ([^.,;()]+)',
            r'proficiency (?:in|with) ([^.,;()]+)',
            r'background (?:in|with) ([^.,;()]+)'
        ]
        
        areas = set()
        for pattern in exp_area_patterns:
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                area = match.group(1).strip()
                # Clean up the area text
                area = re.sub(r'\b(?:and|or|the|a|an)\b', '', area)
                if area and len(area) > 2:
                    areas.add(area)
        
        experience_req['areas'] = list(areas)
        
        return experience_req
    
    def _calculate_scores(self, processed_resume, processed_cover_letter, job_requirements):
        """
        Calculate screening scores based on processed resume and job requirements.
        
        Args:
            processed_resume (dict): Processed resume data
            processed_cover_letter (dict): Processed cover letter data
            job_requirements (dict): Job requirements data
            
        Returns:
            dict: Scores for different screening factors
        """
        # Calculate skills match
        skills_match = self._calculate_skills_match(
            processed_resume.get('extracted_skills', []),
            job_requirements['required_skills'],
            job_requirements['preferred_skills']
        )
        
        # Calculate experience match
        experience_match = self._calculate_experience_match(
            processed_resume,
            job_requirements['experience_requirements']
        )
        
        # Calculate education match
        education_match = self._calculate_education_match(
            processed_resume,
            job_requirements['education_requirements']
        )
        
        # Calculate resume quality
        resume_quality = self._calculate_resume_quality(processed_resume)
        
        # Calculate cover letter quality if available
        cover_letter_quality = None
        if processed_cover_letter:
            cover_letter_quality = self._calculate_cover_letter_quality(
                processed_cover_letter,
                job_requirements['job_title'],
                job_requirements.get('company_name', '')
            )
        else:
            cover_letter_quality = {
                'score': 0,
                'evaluation': 'No cover letter provided'
            }
        
        # Calculate weighted overall score
        overall_score = (
            skills_match['score'] * self.weights['skills_match'] +
            experience_match['score'] * self.weights['experience_match'] +
            education_match['score'] * self.weights['education_match'] +
            resume_quality['score'] * self.weights['resume_quality'] +
            cover_letter_quality['score'] * self.weights['cover_letter_quality']
        )
        
        # Round to integer
        overall_score = round(overall_score)
        
        return {
            'overall_score': overall_score,
            'skills_match': skills_match,
            'experience_match': experience_match,
            'education_match': education_match,
            'resume_quality': resume_quality,
            'cover_letter_quality': cover_letter_quality
        }
    
    def _calculate_skills_match(self, candidate_skills, required_skills, preferred_skills):
        """
        Calculate skills match score and details.
        
        Args:
            candidate_skills (list): Candidate's skills
            required_skills (list): Required skills for the job
            preferred_skills (list): Preferred skills for the job
            
        Returns:
            dict: Skills match results
        """
        if not required_skills:
            return {
                'score': 100,
                'matching_required': [],
                'missing_required': [],
                'matching_preferred': [],
                'percentage_required': 100,
                'percentage_preferred': 0,
                'evaluation': "No specific skills were required for this job"
            }
            
        # Normalize skills for comparison
        candidate_skills_normalized = [s.lower() for s in candidate_skills]
        required_skills_normalized = [s.lower() for s in required_skills]
        preferred_skills_normalized = [s.lower() for s in preferred_skills] if preferred_skills else []
        
        # Find matching and missing required skills
        matching_required = []
        missing_required = []
        
        for req_skill in required_skills_normalized:
            if req_skill in candidate_skills_normalized:
                matching_required.append(req_skill)
            else:
                # Check for similar matches
                for cand_skill in candidate_skills_normalized:
                    if (req_skill in cand_skill or cand_skill in req_skill) and len(min(req_skill, cand_skill)) > 3:
                        matching_required.append(req_skill)
                        break
                else:
                    missing_required.append(req_skill)
        
        # Find matching preferred skills
        matching_preferred = []
        
        for pref_skill in preferred_skills_normalized:
            if pref_skill in candidate_skills_normalized:
                matching_preferred.append(pref_skill)
            else:
                # Check for similar matches
                for cand_skill in candidate_skills_normalized:
                    if (pref_skill in cand_skill or cand_skill in pref_skill) and len(min(pref_skill, cand_skill)) > 3:
                        matching_preferred.append(pref_skill)
                        break
        
        # Calculate percentages
        if required_skills_normalized:
            percentage_required = (len(matching_required) / len(required_skills_normalized)) * 100
        else:
            percentage_required = 100
        
        if preferred_skills_normalized:
            percentage_preferred = (len(matching_preferred) / len(preferred_skills_normalized)) * 100
        else:
            percentage_preferred = 0
        
        # Calculate overall skills score
        # Required skills are weighted more heavily
        if percentage_required < 50:
            # If less than half the required skills match, score is based mostly on required skills
            score = percentage_required * 0.9 + percentage_preferred * 0.1
        else:
            # If most required skills match, preferred skills have more weight
            score = percentage_required * 0.7 + percentage_preferred * 0.3
        
        # Cap at 100
        score = min(100, score)
        
        # Generate evaluation text
        if percentage_required == 100:
            if percentage_preferred >= 70:
                evaluation = "Excellent skills match with all required skills and most preferred skills"
            else:
                evaluation = "Strong skills match with all required skills"
        elif percentage_required >= 80:
            evaluation = "Good skills match with most required skills"
        elif percentage_required >= 60:
            evaluation = "Moderate skills match with some missing required skills"
        else:
            evaluation = "Limited skills match with several missing required skills"
        
        return {
            'score': round(score),
            'matching_required': matching_required,
            'missing_required': missing_required,
            'matching_preferred': matching_preferred,
            'percentage_required': round(percentage_required, 1),
            'percentage_preferred': round(percentage_preferred, 1),
            'evaluation': evaluation
        }
    
    def _calculate_experience_match(self, processed_resume, experience_requirements):
        """
        Calculate experience match score and details.
        
        Args:
            processed_resume (dict): Processed resume data
            experience_requirements (dict): Experience requirements
            
        Returns:
            dict: Experience match results
        """
        # Extract work experience entries and total years
        work_experience = processed_resume.get('extracted_experience', [])
        
        # Calculate total years of experience
        total_years = 0
        for exp in work_experience:
            years_text = exp.get('years', '')
            # Try to extract years
            years_match = re.search(r'(\d{4})\s*-\s*(?:present|current|now|(\d{4}))', years_text, re.IGNORECASE)
            if years_match:
                start_year = int(years_match.group(1))
                end_year = 2025 if 'present' in years_text.lower() else int(years_match.group(2) or 2025)
                years = end_year - start_year
                if 0 <= years <= 50:  # Sanity check
                    total_years += years
        
        # Get required and preferred years
        min_years_required = experience_requirements.get('min_years', 0)
        preferred_years = experience_requirements.get('preferred_years', 0)
        experience_areas = experience_requirements.get('areas', [])
        
        # Calculate years match
        years_score = 0
        
        if min_years_required == 0:
            # No specific years requirement
            years_score = 100
            years_evaluation = "No specific years of experience required"
        elif total_years >= preferred_years and preferred_years > min_years_required:
            # Exceeds preferred years
            years_score = 100
            years_evaluation = f"Experience ({total_years} years) exceeds preferred level ({preferred_years} years)"
        elif total_years >= min_years_required:
            # Meets minimum requirement, calculate score
            if preferred_years > min_years_required:
                # Score between minimum and preferred
                years_ratio = (total_years - min_years_required) / (preferred_years - min_years_required)
                years_score = 80 + (20 * min(1, years_ratio))
                years_evaluation = f"Experience ({total_years} years) meets required ({min_years_required} years) and is approaching preferred level ({preferred_years} years)"
            else:
                # No preferred level defined, just exceed minimum
                extra_years = total_years - min_years_required
                years_score = 80 + min(20, extra_years * 5)
                years_evaluation = f"Experience ({total_years} years) exceeds minimum requirement ({min_years_required} years)"
        else:
            # Below minimum requirement
            years_ratio = total_years / max(1, min_years_required)
            years_score = 70 * years_ratio
            years_evaluation = f"Experience ({total_years} years) is below the required minimum ({min_years_required} years)"
        
        # Check for relevance of experience to required areas
        areas_match = []
        missing_areas = []
        
        for area in experience_areas:
            area_found = False
            for exp in work_experience:
                desc = exp.get('description', '').lower()
                title = exp.get('title', '').lower()
                company = exp.get('company', '').lower()
                
                if area in desc or area in title or area in company:
                    areas_match.append(area)
                    area_found = True
                    break
            
            if not area_found:
                missing_areas.append(area)
        
        # Calculate areas match score
        if not experience_areas:
            areas_score = 100
            areas_evaluation = "No specific experience areas required"
        else:
            areas_match_ratio = len(areas_match) / len(experience_areas)
            areas_score = areas_match_ratio * 100
            
            if areas_score >= 80:
                areas_evaluation = "Experience highly relevant to job requirements"
            elif areas_score >= 60:
                areas_evaluation = "Experience mostly relevant to job requirements"
            elif areas_score >= 40:
                areas_evaluation = "Experience somewhat relevant to job requirements"
            else:
                areas_evaluation = "Limited relevant experience for this position"
        
        # Calculate total experience score (weighted)
        total_score = (years_score * 0.6) + (areas_score * 0.4)
        
        return {
            'score': round(total_score),
            'years_experience': total_years,
            'years_required': min_years_required,
            'years_preferred': preferred_years, 
            'years_score': round(years_score),
            'years_evaluation': years_evaluation,
            'relevant_areas_matched': areas_match,
            'relevant_areas_missing': missing_areas,
            'areas_score': round(areas_score),
            'areas_evaluation': areas_evaluation,
            'experience_entries': len(work_experience)
        }
    
    def _calculate_education_match(self, processed_resume, education_requirements):
        """
        Calculate education match score and details.
        
        Args:
            processed_resume (dict): Processed resume data
            education_requirements (dict): Education requirements
            
        Returns:
            dict: Education match results
        """
        # Extract education entries
        education_entries = processed_resume.get('extracted_education', [])
        
        # Get requirement details
        required_degree = education_requirements.get('min_degree_level', None)
        preferred_fields = education_requirements.get('preferred_fields', [])
        is_required = education_requirements.get('required', False)
        
        # Map degree levels to numeric values for comparison
        degree_levels = {
            'PhD': 5,
            'Master\'s': 4,
            'Bachelor\'s': 3,
            'Associate\'s': 2,
            'High School': 1,
            None: 0
        }
        
        # Find the highest degree from the candidate
        candidate_highest_degree = None
        candidate_highest_level = 0
        candidate_fields = []
        
        for edu in education_entries:
            degree = edu.get('degree', '').strip()
            institution = edu.get('institution', '').strip()
            year = edu.get('year', '').strip()
            
            # Skip empty entries
            if not degree:
                continue
            
            # Try to determine degree level
            degree_level = 0
            degree_lower = degree.lower()
            
            if re.search(r'\b(?:phd|doctorate|doctoral)\b', degree_lower):
                degree_level = 5
                degree_type = 'PhD'
            elif re.search(r'\b(?:master|ms|ma|mba)\b', degree_lower):
                degree_level = 4
                degree_type = 'Master\'s'
            elif re.search(r'\b(?:bachelor|bs|ba|bsc|b\.a|b\.s)\b', degree_lower):
                degree_level = 3
                degree_type = 'Bachelor\'s'
            elif re.search(r'\b(?:associate|aas|aa|a\.a)\b', degree_lower):
                degree_level = 2
                degree_type = 'Associate\'s'
            elif re.search(r'\b(?:high school|diploma|ged)\b', degree_lower):
                degree_level = 1
                degree_type = 'High School'
            
            # Update highest degree if this one is higher
            if degree_level > candidate_highest_level:
                candidate_highest_level = degree_level
                candidate_highest_degree = {
                    'type': degree_type if degree_level > 0 else degree,
                    'field': self._extract_degree_field(degree),
                    'institution': institution,
                    'year': year
                }
            
            # Add field of study
            field = self._extract_degree_field(degree)
            if field:
                candidate_fields.append(field)
        
        # Calculate degree level match
        if not required_degree:
            # No specific degree requirement
            degree_score = 100
            degree_evaluation = "No specific degree requirement for this position"
        else:
            required_level = degree_levels.get(required_degree, 0)
            
            if candidate_highest_level >= required_level:
                # Meets or exceeds requirement
                degree_score = 100
                
                if candidate_highest_level > required_level:
                    degree_evaluation = f"Education ({candidate_highest_degree['type']}) exceeds required level ({required_degree})"
                else:
                    degree_evaluation = f"Education ({candidate_highest_degree['type']}) meets required level ({required_degree})"
            else:
                # Below requirement - partial credit
                if candidate_highest_level > 0:
                    # Calculate score based on how close to the requirement
                    degree_score = (candidate_highest_level / required_level) * 100
                    degree_evaluation = f"Education ({candidate_highest_degree['type'] if candidate_highest_degree else 'None'}) is below required level ({required_degree})"
                else:
                    # No degree found
                    degree_score = 0 if is_required else 50
                    degree_evaluation = "No degree information found in resume"
        
        # Calculate field match
        if not preferred_fields:
            # No specific fields required
            field_score = 100
            field_evaluation = "No specific field of study required"
            field_matches = []
            field_mismatches = []
        else:
            # Check if any candidate fields match the preferred fields
            field_matches = []
            field_mismatches = preferred_fields.copy()
            
            for cf in candidate_fields:
                for pf in preferred_fields:
                    # Check for partial matches too
                    if pf in cf.lower() or cf.lower() in pf:
                        field_matches.append(cf)
                        if pf in field_mismatches:
                            field_mismatches.remove(pf)
                        break
            
            # Calculate field match score
            if field_matches:
                field_match_ratio = len(field_matches) / len(preferred_fields)
                field_score = field_match_ratio * 100
                
                if field_score >= 80:
                    field_evaluation = "Field of study highly relevant to job requirements"
                elif field_score >= 50:
                    field_evaluation = "Field of study somewhat relevant to job requirements"
                else:
                    field_evaluation = "Field of study has limited relevance to job requirements"
            else:
                field_score = 40
                field_evaluation = "Field of study does not match job requirements"
        
        # Calculate overall education score (weighted)
        # Degree level is more important if requirement is specified
        if required_degree:
            overall_score = (degree_score * 0.7) + (field_score * 0.3)
        else:
            # If no degree requirement, field match is more important
            overall_score = (degree_score * 0.3) + (field_score * 0.7)
        
        # If education is not required, ensure minimum score of 70
        if not is_required and overall_score < 70:
            overall_score = 70
        
        return {
            'score': round(overall_score),
            'has_required_education': candidate_highest_level >= degree_levels.get(required_degree, 0),
            'candidate_highest_degree': candidate_highest_degree,
            'required_degree': required_degree,
            'degree_score': round(degree_score),
            'degree_evaluation': degree_evaluation,
            'field_matches': field_matches,
            'field_mismatches': field_mismatches,
            'field_score': round(field_score),
            'field_evaluation': field_evaluation,
            'is_education_required': is_required
        }
    
    def _extract_degree_field(self, degree_text):
        """
        Extract the field of study from a degree text.
        
        Args:
            degree_text (str): Degree text
            
        Returns:
            str: Field of study or empty string
        """
        if not degree_text:
            return ""
        
        # Common degree prefixes
        prefixes = [
            'bachelor of', 'master of', 'doctor of', 'bachelor\'s in', 'master\'s in', 'doctorate in',
            'bs in', 'ba in', 'ms in', 'ma in', 'phd in', 'b.s. in', 'b.a. in', 'm.s. in', 'm.a. in',
            'bachelor', 'master', 'doctorate', 'associate'
        ]
        
        # Try to extract field based on prefixes
        for prefix in prefixes:
            if prefix in degree_text.lower():
                parts = degree_text.lower().split(prefix, 1)
                if len(parts) > 1 and parts[1].strip():
                    return parts[1].strip()
        
        # Check if there's "in" or "of" in the degree
        in_match = re.search(r'\b(?:in|of)\s+([^,;.]+)', degree_text.lower())
        if in_match:
            return in_match.group(1).strip()
        
        return ""
    
    def _calculate_resume_quality(self, processed_resume):
        """
        Calculate the quality score for a resume.
        
        Args:
            processed_resume (dict): Processed resume data
            
        Returns:
            dict: Resume quality results
        """
        scores = {}
        
        # Score the completeness of the resume
        experience_entries = processed_resume.get('extracted_experience', [])
        education_entries = processed_resume.get('extracted_education', [])
        skills = processed_resume.get('extracted_skills', [])
        
        # Points for completeness
        completeness_score = 0
        
        # Experience section
        if experience_entries:
            completeness_score += 30 * min(1, len(experience_entries) / 3)  # Up to 30 points for 3+ entries
        
        # Education section
        if education_entries:
            completeness_score += 20 * min(1, len(education_entries) / 2)  # Up to 20 points for 2+ entries
        
        # Skills section
        if skills:
            completeness_score += 20 * min(1, len(skills) / 10)  # Up to 20 points for 10+ skills
        
        # Contact information
        if processed_resume.get('extracted_contact_info', {}):
            completeness_score += 10  # 10 points for contact info
        
        # Summary or objective
        if processed_resume.get('extracted_summary', ''):
            completeness_score += 10  # 10 points for summary
        
        # Achievement-oriented language in experience
        achievement_score = 0
        achievement_keywords = ['increased', 'decreased', 'improved', 'achieved', 'won', 
                               'delivered', 'reduced', 'saved', 'created', 'developed',
                               'implemented', 'managed', 'led', 'trained', 'designed',
                               '%', 'percent', 'award', 'recognition']
        
        # Check for achievements in experience descriptions
        achievement_count = 0
        for exp in experience_entries:
            desc = exp.get('description', '').lower()
            if any(keyword in desc for keyword in achievement_keywords):
                achievement_count += 1
        
        if achievement_count > 0:
            achievement_score = min(20, achievement_count * 5)  # Up to 20 points for achievements
        
        # Format and organization assessment
        # (In a real implementation, this would be more sophisticated)
        formatting_score = 60  # Default reasonable format score
        
        # Total quality score
        quality_score = (completeness_score * 0.5) + (achievement_score * 0.3) + (formatting_score * 0.2)
        
        # Generate evaluation
        if quality_score >= 85:
            evaluation = "Excellent resume with comprehensive details and achievement-oriented descriptions"
        elif quality_score >= 70:
            evaluation = "Good resume with adequate information but could be improved"
        elif quality_score >= 50:
            evaluation = "Basic resume with some gaps or areas for improvement"
        else:
            evaluation = "Limited resume with significant room for improvement"
        
        # Generate specific suggestions
        suggestions = []
        
        if len(experience_entries) < 2:
            suggestions.append("Add more details about work experience")
        
        if achievement_count < 2:
            suggestions.append("Include specific achievements with measurable results")
        
        if len(skills) < 8:
            suggestions.append("Expand the skills section")
        
        return {
            'score': round(quality_score),
            'completeness_score': round(completeness_score),
            'achievement_score': round(achievement_score),
            'formatting_score': round(formatting_score),
            'evaluation': evaluation,
            'suggestions': suggestions
        }
    
    def _calculate_cover_letter_quality(self, processed_cover_letter, job_title, company_name):
        """
        Calculate the quality score for a cover letter.
        
        Args:
            processed_cover_letter (dict): Processed cover letter data
            job_title (str): Job title
            company_name (str): Company name
            
        Returns:
            dict: Cover letter quality results
        """
        scores = {}
        
        # Personalization score
        personalization_score = 0
        job_title_mentioned = False
        company_mentioned = False
        
        cover_letter_text = processed_cover_letter.get('cleaned_text', '').lower()
        
        # Check for job title
        if job_title and job_title.lower() in cover_letter_text:
            job_title_mentioned = True
            personalization_score += 20
        
        # Check for company name
        if company_name and company_name.lower() in cover_letter_text:
            company_mentioned = True
            personalization_score += 20
        
        # Check for generic phrases that indicate a non-personalized letter
        generic_phrases = ['to whom it may concern', 'dear hiring manager', 'your company', 'your organization']
        generic_count = sum(1 for phrase in generic_phrases if phrase in cover_letter_text)
        personalization_score = max(0, personalization_score - (generic_count * 10))
        
        # Additional personalization for specific company details
        specific_company_details = processed_cover_letter.get('company_references', [])
        if specific_company_details:
            personalization_score += min(20, len(specific_company_details) * 10)
        
        # Content relevance score
        relevance_score = 0
        
        # Relevant skills mentioned
        skills_mentioned = processed_cover_letter.get('skills_mentioned', [])
        if skills_mentioned:
            relevance_score += min(30, len(skills_mentioned) * 5)
        
        # Achievements mentioned
        achievements = processed_cover_letter.get('achievements', [])
        if achievements:
            relevance_score += min(30, len(achievements) * 10)
        
        # Structure and length analysis
        structure_score = 0
        sections = processed_cover_letter.get('sections', {})
        
        # Introduction, body, closing
        if 'introduction' in sections:
            structure_score += 15
        
        if 'body' in sections:
            structure_score += 15
        
        if 'closing' in sections:
            structure_score += 15
        
        # Appropriate length
        word_count = len(cover_letter_text.split())
        if 250 <= word_count <= 500:
            structure_score += 15
        elif word_count > 500:
            structure_score += 5
        elif word_count < 150:
            structure_score += 5
        
        # Overall quality score
        quality_score = (personalization_score * 0.4) + (relevance_score * 0.4) + (structure_score * 0.2)
        
        # Generate evaluation
        if quality_score >= 85:
            evaluation = "Excellent cover letter with strong personalization and relevant content"
        elif quality_score >= 70:
            evaluation = "Good cover letter with adequate personalization but could be improved"
        elif quality_score >= 50:
            evaluation = "Basic cover letter with limited personalization"
        else:
            evaluation = "Generic cover letter with significant room for improvement"
        
        # Generate specific suggestions
        suggestions = []
        
        if not job_title_mentioned:
            suggestions.append("Mention the specific job title")
        
        if not company_mentioned:
            suggestions.append("Include the company name")
        
        if len(skills_mentioned) < 3:
            suggestions.append("Highlight more relevant skills")
        
        if len(achievements) < 2:
            suggestions.append("Include specific achievements relevant to the position")
        
        return {
            'score': round(quality_score),
            'personalization_score': round(personalization_score),
            'relevance_score': round(relevance_score),
            'structure_score': round(structure_score),
            'evaluation': evaluation,
            'suggestions': suggestions,
            'job_title_mentioned': job_title_mentioned,
            'company_mentioned': company_mentioned
        }
    
    def _determine_candidate_tier(self, overall_score):
        """
        Determine the candidate tier based on the overall score.
        
        Args:
            overall_score (int): Overall candidate score
            
        Returns:
            str: Candidate tier
        """
        for tier, (min_score, max_score) in self.candidate_tiers.items():
            if min_score <= overall_score <= max_score:
                return tier
        return 'poor'  # Default
    
    def _generate_screening_summary(self, scores, tier, processed_resume, processed_cover_letter, job_requirements):
        """
        Generate a screening summary based on the scores and analysis.
        
        Args:
            scores (dict): Screening scores
            tier (str): Candidate tier
            processed_resume (dict): Processed resume data
            processed_cover_letter (dict): Processed cover letter data
            job_requirements (dict): Job requirements data
            
        Returns:
            str: Screening summary
        """
        # Start with overall assessment
        if tier == 'excellent':
            summary = "Excellent candidate with strong match across all requirements. "
        elif tier == 'strong':
            summary = "Strong candidate with good match to most requirements. "
        elif tier == 'good':
            summary = "Good candidate with reasonable match to requirements. "
        elif tier == 'potential':
            summary = "Potential candidate with some match to requirements but areas of concern. "
        elif tier == 'limited':
            summary = "Limited match to requirements with significant gaps. "
        else:
            summary = "Poor match to requirements with major deficiencies. "
        
        # Add detail about skills match
        skills_match = scores['skills_match']
        if skills_match['percentage_required'] >= 90:
            summary += "Matches all or nearly all required skills. "
        elif skills_match['percentage_required'] >= 70:
            summary += "Matches most required skills. "
        elif skills_match['percentage_required'] >= 50:
            summary += "Matches some required skills with notable gaps. "
        else:
            summary += "Significant skills gaps compared to requirements. "
        
        # Add detail about experience
        experience_match = scores['experience_match']
        if experience_match['years_experience'] >= experience_match['years_required']:
            if experience_match['areas_score'] >= 70:
                summary += "Has sufficient experience in relevant areas. "
            else:
                summary += "Has sufficient years of experience but in less relevant areas. "
        else:
            summary += f"Has less than the required {experience_match['years_required']} years of experience. "
        
        # Add detail about education
        education_match = scores['education_match']
        if education_match['has_required_education']:
            if education_match['field_score'] >= 70:
                summary += "Education meets requirements with relevant field of study. "
            else:
                summary += "Education level meets requirements but in less relevant field. "
        elif education_match['is_education_required']:
            summary += "Does not meet the required education level. "
        
        # Add recommendation based on tier
        if tier in ['excellent', 'strong']:
            summary += "Recommended for interview."
        elif tier == 'good':
            summary += "Consider for interview."
        elif tier == 'potential':
            summary += "May be worth further screening."
        else:
            summary += "Not recommended based on current qualifications."
        
        return summary
    
    def _identify_red_flags(self, processed_resume, processed_cover_letter, job_requirements):
        """
        Identify potential red flags in the application.
        
        Args:
            processed_resume (dict): Processed resume data
            processed_cover_letter (dict): Processed cover letter data
            job_requirements (dict): Job requirements data
            
        Returns:
            list: Red flags
        """
        red_flags = []
        
        # Check for experience gaps
        experience_entries = processed_resume.get('extracted_experience', [])
        if experience_entries:
            # Sort entries by years (start date)
            sorted_entries = sorted(experience_entries, key=lambda x: x.get('years', ''), reverse=True)
            
            # Check for short stints
            short_stints = 0
            for exp in experience_entries:
                years_text = exp.get('years', '')
                # Try to extract years
                years_match = re.search(r'(\d{4})\s*-\s*(?:present|current|now|(\d{4}))', years_text, re.IGNORECASE)
                if years_match:
                    start_year = int(years_match.group(1))
                    end_year = 2025 if 'present' in years_text.lower() else int(years_match.group(2) or 2025)
                    duration = end_year - start_year
                    if duration < 1:
                        short_stints += 1
            
            if short_stints >= 2:
                red_flags.append("Multiple short-term positions (less than 1 year)")
            
            # Check for gaps
            if len(sorted_entries) >= 2:
                for i in range(len(sorted_entries) - 1):
                    current = sorted_entries[i]
                    next_entry = sorted_entries[i + 1]
                    
                    # Extract years
                    current_years = current.get('years', '')
                    next_years = next_entry.get('years', '')
                    
                    current_match = re.search(r'(\d{4})\s*-', current_years)
                    next_match = re.search(r'-\s*(?:present|current|now|(\d{4}))', next_years)
                    
                    if current_match and next_match:
                        current_start = int(current_match.group(1))
                        next_end = 2025 if 'present' in next_years.lower() else int(next_match.group(1) or 2025)
                        
                        if current_start - next_end > 1:
                            red_flags.append(f"Gap in employment history ({next_end} to {current_start})")
        
        # Check for missing critical skills
        skills_match = job_requirements.get('required_skills', [])
        candidate_skills = processed_resume.get('extracted_skills', [])
        
        # Normalize skills for comparison
        candidate_skills_normalized = [s.lower() for s in candidate_skills]
        
        critical_skills_missing = []
        for skill in skills_match[:3]:  # Consider the first 3 skills as critical
            if skill.lower() not in candidate_skills_normalized:
                critical_skills_missing.append(skill)
        
        if critical_skills_missing:
            red_flags.append(f"Missing critical skills: {', '.join(critical_skills_missing)}")
        
        # Check for insufficient experience
        min_years_required = job_requirements.get('experience_requirements', {}).get('min_years', 0)
        total_years = sum(
            max(0, (2025 if 'present' in exp.get('years', '').lower() else 
                int(re.search(r'-\s*(\d{4})', exp.get('years', '')).group(1) if re.search(r'-\s*(\d{4})', exp.get('years', '')) else 2025)) - 
            int(re.search(r'(\d{4})\s*-', exp.get('years', '')).group(1) if re.search(r'(\d{4})\s*-', exp.get('years', '')) else 0))
            for exp in experience_entries
            if re.search(r'(\d{4})\s*-', exp.get('years', ''))
        )
        
        if min_years_required > 0 and total_years < min_years_required:
            red_flags.append(f"Insufficient experience: {total_years} years (required: {min_years_required})")
        
        # Check for education mismatch if education is required
        education_req = job_requirements.get('education_requirements', {})
        required_degree = education_req.get('min_degree_level', None)
        is_required = education_req.get('required', False)
        
        if is_required and required_degree:
            education_entries = processed_resume.get('extracted_education', [])
            
            # Map degree levels to numeric values for comparison
            degree_levels = {
                'PhD': 5,
                'Master\'s': 4,
                'Bachelor\'s': 3,
                'Associate\'s': 2,
                'High School': 1,
                None: 0
            }
            
            # Find the highest degree from the candidate
            candidate_highest_level = 0
            
            for edu in education_entries:
                degree = edu.get('degree', '').strip().lower()
                
                if 'phd' in degree or 'doctorate' in degree:
                    candidate_highest_level = max(candidate_highest_level, 5)
                elif 'master' in degree or 'ms' in degree or 'ma' in degree or 'mba' in degree:
                    candidate_highest_level = max(candidate_highest_level, 4)
                elif 'bachelor' in degree or 'bs' in degree or 'ba' in degree:
                    candidate_highest_level = max(candidate_highest_level, 3)
                elif 'associate' in degree or 'aa' in degree:
                    candidate_highest_level = max(candidate_highest_level, 2)
                elif 'high school' in degree or 'diploma' in degree or 'ged' in degree:
                    candidate_highest_level = max(candidate_highest_level, 1)
            
            required_level = degree_levels.get(required_degree, 0)
            
            if candidate_highest_level < required_level:
                red_flags.append(f"Education below required level: {required_degree}")
        
        # Check for cover letter issues
        if processed_cover_letter:
            cover_letter_text = processed_cover_letter.get('cleaned_text', '').lower()
            
            # Check for generic cover letter
            generic_phrases = [
                'to whom it may concern',
                'dear hiring manager',
                'your company',
                'your organization',
                'i am writing to apply',
                'i am writing to express my interest'
            ]
            
            generic_count = sum(1 for phrase in generic_phrases if phrase in cover_letter_text)
            
            if generic_count >= 3:
                red_flags.append("Generic cover letter with little personalization")
            
            # Check if company name is mentioned
            company_name = job_requirements.get('company_name', '')
            if company_name and company_name.lower() not in cover_letter_text:
                red_flags.append("Cover letter does not mention company name")
            
            # Check if job title is mentioned
            job_title = job_requirements.get('job_title', '')
            if job_title and job_title.lower() not in cover_letter_text:
                red_flags.append("Cover letter does not mention job title")
        
        return red_flags
    
    def _recommend_actions(self, scores, tier, red_flags):
        """
        Recommend actions based on screening results.
        
        Args:
            scores (dict): Screening scores
            tier (str): Candidate tier
            red_flags (list): Red flags
            
        Returns:
            list: Recommended actions
        """
        actions = []
        
        # Base actions on tier
        if tier in ['excellent', 'strong']:
            actions.append("Schedule interview")
            actions.append("Contact candidate to discuss qualifications")
        elif tier == 'good':
            actions.append("Consider for interview if other candidates are limited")
            actions.append("Consider a screening call to clarify qualifications")
        elif tier == 'potential':
            actions.append("Hold for further review")
            actions.append("Request additional information or samples")
            if red_flags:
                actions.append("Address red flags in screening call")
        else:
            actions.append("Reject application")
            actions.append("Send standard rejection email")
        
        # Additional actions based on specific scores
        skills_match = scores['skills_match']
        if skills_match['missing_required'] and tier in ['excellent', 'strong', 'good', 'potential']:
            actions.append(f"Verify skills in {', '.join(skills_match['missing_required'][:3])}")
        
        experience_match = scores['experience_match']
        if experience_match['years_experience'] < experience_match['years_required'] and tier in ['good', 'potential']:
            actions.append("Assess if quality of experience compensates for years")
        
        return actions
    
    def _generate_screening_questions(self, processed_resume, job_requirements, scores):
        """
        Generate screening questions based on resume and job requirements.
        
        Args:
            processed_resume (dict): Processed resume data
            job_requirements (dict): Job requirements data
            scores (dict): Screening scores
            
        Returns:
            dict: Suggested screening questions
        """
        questions = {
            'skills_questions': [],
            'experience_questions': [],
            'general_questions': []
        }
        
        # Skills questions
        skills_match = scores['skills_match']
        
        # Questions about missing skills
        for skill in skills_match['missing_required'][:2]:
            questions['skills_questions'].append(f"Do you have any experience with {skill}?")
        
        # Questions about matched skills
        for skill in skills_match['matching_required'][:2]:
            questions['skills_questions'].append(f"Can you describe your experience with {skill} in more detail?")
        
        # Experience questions
        experience_match = scores['experience_match']
        
        # Questions about missing experience areas
        for area in experience_match['relevant_areas_missing'][:2]:
            questions['experience_questions'].append(f"Do you have any experience with {area}?")
        
        # Questions about work history
        work_experience = processed_resume.get('extracted_experience', [])
        if work_experience:
            most_recent = work_experience[0]
            questions['experience_questions'].append(f"Can you tell me more about your role at {most_recent.get('company', 'your most recent company')}?")
        
        if experience_match['years_experience'] < experience_match['years_required']:
            questions['experience_questions'].append(f"The role requires {experience_match['years_required']} years of experience. Can you explain how your experience qualifies you despite having fewer years?")
        
        # General questions
        questions['general_questions'] = [
            "Why are you interested in this position?",
            "What are your salary expectations?",
            "When would you be available to start if selected?",
            "Are you comfortable with the location/remote requirements of this position?",
            "Do you have any questions about the role or company?"
        ]
        
        return questions