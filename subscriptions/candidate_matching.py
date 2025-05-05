"""
Candidate Matching System

This module implements the candidate matching functionality using the core infrastructure
components (document parsing, text processing, content validation, and data resources).
It provides comprehensive candidate-job matching with detailed scoring, relevance analysis,
and recommendations.
"""

import logging
import re
from collections import defaultdict, Counter
import math
from difflib import SequenceMatcher

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

class CandidateMatchingSystem:
    """
    Class for matching candidates with job listings using the core infrastructure.
    
    This class provides comprehensive matching functionality between candidate profiles/resumes
    and job listings, calculating match scores with detailed breakdown and recommendations.
    """
    
    def __init__(self):
        """Initialize the CandidateMatchingSystem with necessary components."""
        self.document_parser = DocumentParser()
        self.text_processor = TextProcessor()
        self.content_validator = ContentValidator(self.text_processor)
        
        # Load skills data
        self.all_skills = get_all_skills()
        self.technical_skills = get_technical_skills_by_category()
        self.soft_skills = get_soft_skills()
        self.job_titles = get_job_titles()
        self.education_data = get_education_data()
        
        # Define weights for different matching factors
        self.weights = {
            'skills_match': 0.35,
            'experience_match': 0.30,
            'education_match': 0.15,
            'job_title_match': 0.15,
            'location_match': 0.05
        }
        
        # Different tiers of match quality
        self.match_tiers = {
            'excellent': (90, 100),
            'very_good': (80, 89),
            'good': (70, 79),
            'moderate': (50, 69),
            'weak': (30, 49),
            'poor': (0, 29)
        }
    
    def match_candidate_with_job(self, resume_text=None, resume_file=None, file_name=None, job_listing=None):
        """
        Match a candidate's resume with a job listing.
        
        Args:
            resume_text (str, optional): Resume text content
            resume_file (file, optional): Resume file object
            file_name (str, optional): Resume file name (required if resume_file is provided)
            job_listing (dict): Job listing data
            
        Returns:
            dict: Match results
        """
        try:
            # Extract resume text if needed
            if resume_text is None:
                if resume_file and file_name:
                    resume_text = self.document_parser.extract_text_from_file_object(resume_file, file_name)
                else:
                    return {
                        'error': 'No resume provided for matching',
                        'is_valid': False
                    }
            
            if not job_listing:
                return {
                    'error': 'No job listing provided for matching',
                    'is_valid': False
                }
            
            # Validate resume
            resume_validation = self.content_validator.validate_document(resume_text)
            if resume_validation['document_type'] != 'resume' or resume_validation['confidence'] < self.content_validator.MEDIUM_CONFIDENCE:
                return {
                    'error': 'The provided document does not appear to be a valid resume',
                    'is_valid': False,
                    'confidence': resume_validation['confidence']
                }
            
            # Process the resume
            processed_resume = self.text_processor.process_document(resume_text, 'resume')
            
            # Extract key information from the job listing
            job_requirements = self._extract_job_requirements(job_listing)
            
            # Calculate match scores
            match_results = self._calculate_match_scores(processed_resume, job_requirements)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(processed_resume, job_requirements, match_results)
            
            # Prepare the final results
            match_results.update({
                'is_valid': True,
                'recommendations': recommendations,
                'job_id': job_listing.get('id', None),
                'job_title': job_listing.get('title', 'Unknown Position')
            })
            
            return match_results
            
        except Exception as e:
            logger.error(f"Error in candidate matching: {str(e)}")
            return {
                'error': f"Error matching candidate with job: {str(e)}",
                'is_valid': False
            }
    
    def match_job_with_candidates(self, job_listing, candidate_profiles):
        """
        Match a job listing with multiple candidate profiles.
        
        Args:
            job_listing (dict): Job listing data
            candidate_profiles (list): List of candidate profile dicts
            
        Returns:
            dict: Match results for each candidate
        """
        try:
            # Validate inputs
            if not job_listing:
                return {
                    'error': 'No job listing provided for matching',
                    'is_valid': False
                }
                
            if not candidate_profiles or not isinstance(candidate_profiles, list):
                return {
                    'error': 'No candidate profiles provided for matching',
                    'is_valid': False
                }
            
            # Extract job requirements
            job_requirements = self._extract_job_requirements(job_listing)
            
            # Match each candidate
            matches = []
            for profile in candidate_profiles:
                # Get resume text (either directly or through processing)
                resume_text = profile.get('resume_text', None)
                if resume_text is None and 'resume_file_path' in profile:
                    try:
                        resume_text = self.document_parser.extract_text(profile['resume_file_path'])
                    except Exception as e:
                        logger.error(f"Error extracting text from resume file: {str(e)}")
                        continue
                
                if not resume_text:
                    continue
                
                # Process the resume
                processed_resume = self.text_processor.process_document(resume_text, 'resume')
                
                # Calculate match scores
                match_results = self._calculate_match_scores(processed_resume, job_requirements)
                
                # Add candidate info to results
                match_results.update({
                    'candidate_id': profile.get('id', None),
                    'candidate_name': profile.get('name', 'Unknown Candidate'),
                    'job_id': job_listing.get('id', None),
                    'job_title': job_listing.get('title', 'Unknown Position')
                })
                
                matches.append(match_results)
            
            # Sort matches by overall score
            matches.sort(key=lambda x: x['overall_match'], reverse=True)
            
            return {
                'is_valid': True,
                'job_id': job_listing.get('id', None),
                'job_title': job_listing.get('title', 'Unknown Position'),
                'total_candidates': len(matches),
                'matches': matches
            }
            
        except Exception as e:
            logger.error(f"Error in job-candidate matching: {str(e)}")
            return {
                'error': f"Error matching job with candidates: {str(e)}",
                'is_valid': False
            }
    
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
        job_requirements = job_listing.get('requirements', '')
        
        # Combine if needed
        full_text = job_description
        if job_requirements and job_requirements not in job_description:
            full_text = f"{job_description}\n\n{job_requirements}"
        
        # Process the job description
        processed_job = self.text_processor.process_document(full_text, 'job_description')
        
        # Extract skills from both the processed job and directly from the job listing
        required_skills = set(processed_job.get('extracted_skills', []))
        
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
                    skill = skill.strip().lower()
                    if skill:
                        required_skills.add(skill)
        
        # Extract education requirements
        education_req = self._extract_education_requirements(full_text)
        
        # Extract experience requirements
        experience_req = self._extract_experience_requirements(full_text)
        
        # Get job title and location
        job_title = job_listing.get('title', '')
        job_location = job_listing.get('location', '')
        
        return {
            'job_title': job_title,
            'job_location': job_location,
            'required_skills': list(required_skills),
            'education_requirements': education_req,
            'experience_requirements': experience_req,
            'job_category': processed_job.get('extracted_category', ''),
            'job_industry': processed_job.get('extracted_industry', '')
        }
    
    def _extract_education_requirements(self, text):
        """
        Extract education requirements from job text.
        
        Args:
            text (str): Job description/requirements text
            
        Returns:
            dict: Education requirements
        """
        education_req = {
            'min_degree_level': None,
            'preferred_fields': [],
            'required': False
        }
        
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
    
    def _extract_experience_requirements(self, text):
        """
        Extract experience requirements from job text.
        
        Args:
            text (str): Job description/requirements text
            
        Returns:
            dict: Experience requirements
        """
        experience_req = {
            'min_years': 0,
            'preferred_years': 0,
            'areas': []
        }
        
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
                # Try to determine context (within 10 words before or after)
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
    
    def _calculate_match_scores(self, processed_resume, job_requirements):
        """
        Calculate match scores between a processed resume and job requirements.
        
        Args:
            processed_resume (dict): Processed resume data
            job_requirements (dict): Job requirements data
            
        Returns:
            dict: Match scores
        """
        # Calculate skills match
        skills_match = self._calculate_skills_match(
            processed_resume.get('extracted_skills', []),
            job_requirements['required_skills']
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
        
        # Calculate job title match
        job_title_match = self._calculate_job_title_match(
            processed_resume.get('extracted_job_titles', []),
            job_requirements['job_title'],
            job_requirements['job_category']
        )
        
        # Calculate location match (if location data is available)
        candidate_location = processed_resume.get('extracted_location', '')
        location_match = self._calculate_location_match(
            candidate_location,
            job_requirements['job_location']
        )
        
        # Calculate overall match score (weighted)
        overall_match = (
            skills_match['score'] * self.weights['skills_match'] +
            experience_match['score'] * self.weights['experience_match'] +
            education_match['score'] * self.weights['education_match'] +
            job_title_match['score'] * self.weights['job_title_match'] +
            location_match['score'] * self.weights['location_match']
        )
        
        # Round to integer
        overall_match = round(overall_match)
        
        # Determine match tier
        match_tier = 'poor'  # Default
        for tier, (min_score, max_score) in self.match_tiers.items():
            if min_score <= overall_match <= max_score:
                match_tier = tier
                break
        
        return {
            'overall_match': overall_match,
            'match_tier': match_tier,
            'skills_match': skills_match,
            'experience_match': experience_match,
            'education_match': education_match,
            'job_title_match': job_title_match,
            'location_match': location_match
        }
    
    def _calculate_skills_match(self, candidate_skills, required_skills):
        """
        Calculate skills match score and details.
        
        Args:
            candidate_skills (list): Candidate's skills
            required_skills (list): Required skills for the job
            
        Returns:
            dict: Skills match results
        """
        if not required_skills:
            return {
                'score': 100,
                'matching_skills': [],
                'missing_skills': [],
                'percentage': 100,
                'evaluation': "No specific skills were required for this job"
            }
            
        # Normalize skills for comparison
        candidate_skills_normalized = [s.lower() for s in candidate_skills]
        required_skills_normalized = [s.lower() for s in required_skills]
        
        # Initialize matches
        exact_matches = []
        close_matches = []
        missing_skills = []
        
        # Find exact and fuzzy matches
        for req_skill in required_skills_normalized:
            if req_skill in candidate_skills_normalized:
                # Exact match
                skill_index = candidate_skills_normalized.index(req_skill)
                exact_matches.append(candidate_skills[skill_index])
            else:
                # Check for fuzzy matches (synonyms or partial matches)
                fuzzy_matched = False
                
                # Check for fuzzy match
                for i, cand_skill in enumerate(candidate_skills_normalized):
                    # Check similarity score
                    similarity = SequenceMatcher(None, req_skill, cand_skill).ratio()
                    
                    # Check if one skill contains the other
                    contains = (req_skill in cand_skill) or (cand_skill in req_skill)
                    
                    if similarity >= 0.85 or contains:
                        close_matches.append((req_skill, candidate_skills[i], similarity))
                        fuzzy_matched = True
                        break
                
                if not fuzzy_matched:
                    missing_skills.append(req_skill)
        
        # Calculate match percentages
        total_required = len(required_skills_normalized)
        exact_match_count = len(exact_matches)
        close_match_count = len(close_matches)
        
        # Score calculation: exact matches are worth 1.0, fuzzy matches 0.5
        match_score = exact_match_count + (close_match_count * 0.5)
        
        # Calculate percentage
        if total_required > 0:
            match_percentage = (match_score / total_required) * 100
        else:
            match_percentage = 100
        
        # Cap at 100%
        match_percentage = min(100, match_percentage)
        
        # Generate evaluation text
        if match_percentage >= 90:
            evaluation = "Excellent skills match with almost all required skills"
        elif match_percentage >= 75:
            evaluation = "Strong skills match with most required skills"
        elif match_percentage >= 50:
            evaluation = "Moderate skills match with some missing critical skills"
        else:
            evaluation = "Limited skills match with several missing required skills"
        
        return {
            'score': round(match_percentage),
            'exact_matches': exact_matches,
            'close_matches': [{'required': r, 'candidate': c, 'similarity': s} for r, c, s in close_matches],
            'missing_skills': missing_skills,
            'percentage': round(match_percentage, 1),
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
    
    def _calculate_job_title_match(self, candidate_titles, job_title, job_category):
        """
        Calculate job title match score and details.
        
        Args:
            candidate_titles (list): Candidate's previous job titles
            job_title (str): Current job title
            job_category (str): Job category
            
        Returns:
            dict: Job title match results
        """
        if not job_title:
            return {
                'score': 100,
                'matching_titles': [],
                'evaluation': "No specific job title to match against"
            }
        
        if not candidate_titles:
            return {
                'score': 50,
                'matching_titles': [],
                'evaluation': "No previous job titles found in resume"
            }
        
        # Normalize job title for comparison
        job_title_normalized = job_title.lower()
        
        # Extract key terms from job title
        job_title_terms = set(re.findall(r'\b[a-zA-Z]+\b', job_title_normalized))
        
        # Initialize matches
        exact_matches = []
        partial_matches = []
        
        # Calculate the best match score
        best_match_score = 0
        best_match_title = ""
        
        for title in candidate_titles:
            title_normalized = title.lower()
            
            # Check for exact match
            if title_normalized == job_title_normalized:
                exact_matches.append(title)
                best_match_score = 100
                best_match_title = title
                break
            
            # Check for partial match
            title_terms = set(re.findall(r'\b[a-zA-Z]+\b', title_normalized))
            
            # Calculate term overlap
            common_terms = job_title_terms.intersection(title_terms)
            
            if common_terms:
                # Calculate Jaccard similarity
                similarity = len(common_terms) / len(job_title_terms.union(title_terms))
                match_score = similarity * 100
                
                partial_matches.append((title, match_score))
                
                if match_score > best_match_score:
                    best_match_score = match_score
                    best_match_title = title
        
        # Sort partial matches by score
        partial_matches.sort(key=lambda x: x[1], reverse=True)
        
        # Generate evaluation text
        if best_match_score >= 90:
            evaluation = f"Excellent match with previous job title: {best_match_title}"
        elif best_match_score >= 70:
            evaluation = f"Strong match with previous job title: {best_match_title}"
        elif best_match_score >= 50:
            evaluation = f"Moderate match with previous job title: {best_match_title}"
        elif best_match_score > 0:
            evaluation = f"Limited match with previous job title: {best_match_title}"
        else:
            evaluation = "No matching job titles found"
        
        return {
            'score': round(best_match_score),
            'exact_matches': exact_matches,
            'partial_matches': [{'title': t, 'score': round(s)} for t, s in partial_matches[:3]],
            'evaluation': evaluation
        }
    
    def _calculate_location_match(self, candidate_location, job_location):
        """
        Calculate location match score.
        
        Args:
            candidate_location (str): Candidate's location
            job_location (str): Job location
            
        Returns:
            dict: Location match results
        """
        if not job_location:
            return {
                'score': 100,
                'evaluation': "No specific location required for this job"
            }
        
        if not candidate_location:
            return {
                'score': 50,
                'evaluation': "No location information found in resume"
            }
        
        # Normalize locations for comparison
        candidate_location = candidate_location.lower()
        job_location = job_location.lower()
        
        # Extract key location components (city, state, country)
        candidate_components = set(re.findall(r'\b[a-zA-Z]+\b', candidate_location))
        job_components = set(re.findall(r'\b[a-zA-Z]+\b', job_location))
        
        # Calculate component overlap
        common_components = candidate_components.intersection(job_components)
        
        if common_components:
            # Calculate similarity
            similarity = len(common_components) / len(job_components)
            match_score = similarity * 100
        else:
            match_score = 0
        
        # Generate evaluation text
        if match_score >= 90:
            evaluation = f"Excellent location match: {candidate_location} matches job location: {job_location}"
        elif match_score >= 70:
            evaluation = f"Good location match: {candidate_location} is similar to job location: {job_location}"
        elif match_score >= 40:
            evaluation = f"Partial location match: {candidate_location} partially matches job location: {job_location}"
        else:
            evaluation = f"No location match: {candidate_location} does not match job location: {job_location}"
        
        return {
            'score': round(match_score),
            'candidate_location': candidate_location,
            'job_location': job_location,
            'evaluation': evaluation
        }
    
    def _generate_recommendations(self, processed_resume, job_requirements, match_results):
        """
        Generate recommendations for improving the match.
        
        Args:
            processed_resume (dict): Processed resume data
            job_requirements (dict): Job requirements
            match_results (dict): Match score results
            
        Returns:
            dict: Recommendations
        """
        recommendations = {
            'skills_recommendations': [],
            'experience_recommendations': [],
            'education_recommendations': [],
            'resume_recommendations': []
        }
        
        # Generate skills recommendations
        missing_skills = match_results['skills_match'].get('missing_skills', [])
        if missing_skills:
            skills_rec = "Consider adding the following missing skills to your resume or working to acquire them:"
            for skill in missing_skills[:5]:  # Top 5 missing skills
                skills_rec += f"\n- {skill}"
            recommendations['skills_recommendations'].append(skills_rec)
        
        # Generate experience recommendations
        exp_match = match_results['experience_match']
        years_req = exp_match.get('years_required', 0)
        years_exp = exp_match.get('years_experience', 0)
        
        if years_exp < years_req:
            recommendations['experience_recommendations'].append(
                f"You have {years_exp} years of experience but this position requires {years_req} years. " +
                "Consider roles with lower experience requirements or highlight projects/achievements that demonstrate advanced expertise."
            )
        
        missing_areas = exp_match.get('relevant_areas_missing', [])
        if missing_areas:
            areas_rec = "Your experience doesn't show sufficient expertise in these areas:"
            for area in missing_areas[:3]:  # Top 3 missing areas
                areas_rec += f"\n- {area}"
            areas_rec += "\nConsider highlighting any relevant projects or training in these areas."
            recommendations['experience_recommendations'].append(areas_rec)
        
        # Generate education recommendations
        edu_match = match_results['education_match']
        has_req_edu = edu_match.get('has_required_education', True)
        req_degree = edu_match.get('required_degree', None)
        
        if not has_req_edu and req_degree:
            recommendations['education_recommendations'].append(
                f"This position requires a {req_degree} degree. Consider pursuing additional education or focusing on positions with different requirements."
            )
        
        field_mismatches = edu_match.get('field_mismatches', [])
        if field_mismatches:
            fields_rec = "Your education doesn't match these preferred fields of study:"
            for field in field_mismatches[:3]:  # Top 3 missing fields
                fields_rec += f"\n- {field}"
            fields_rec += "\nConsider highlighting relevant coursework or additional training in these areas."
            recommendations['education_recommendations'].append(fields_rec)
        
        # Generate general resume recommendations
        if match_results['overall_match'] < 70:
            recommendations['resume_recommendations'].append(
                "Your resume could benefit from tailoring to better match this position. Highlight relevant skills, experience, and achievements that align with the job requirements."
            )
        
        if len(processed_resume.get('extracted_skills', [])) < 5:
            recommendations['resume_recommendations'].append(
                "Your resume has fewer skills listed than typical for this position. Consider expanding your skills section with relevant technical and soft skills."
            )
        
        if len(processed_resume.get('extracted_experience', [])) < 2:
            recommendations['resume_recommendations'].append(
                "Your work history section could be expanded to better demonstrate your relevant experience. Include achievements and responsibilities that align with this role."
            )
        
        return recommendations