"""
Job Qualification Checker

This module provides lightweight qualification checking for job seekers browsing job listings.
It leverages the candidate matching system to provide quick match percentage calculations
that can be displayed in job listings to help job seekers find appropriate opportunities.
"""

import logging
from .candidate_matching import CandidateMatchingSystem

logger = logging.getLogger(__name__)

class JobQualificationChecker:
    """
    Provides efficient qualification checking for job listings.
    
    This class is optimized for quickly checking qualification percentages when
    browsing job listings, showing job seekers their potential match with each job.
    """
    
    def __init__(self):
        """Initialize the checker with a candidate matching system."""
        self.matcher = CandidateMatchingSystem()
        
    def check_qualification(self, resume_text, job_listing):
        """
        Calculate a qualification match percentage between a resume and job listing.
        
        Args:
            resume_text (str): The candidate's resume text
            job_listing (dict): Job listing data including requirements
            
        Returns:
            dict: Match information including percentage, tier, and key missing requirements
        """
        try:
            # Get full match results from the matcher
            match_results = self.matcher.match_candidate_with_job(
                resume_text=resume_text,
                job_listing=job_listing
            )
            
            # Check if match is valid
            if not match_results.get('is_valid', False):
                return {
                    'is_valid': False,
                    'match_percentage': 0,
                    'match_tier': 'unknown',
                    'error': match_results.get('error', 'Invalid match calculation')
                }
            
            # Extract key information for display
            match_percentage = match_results['overall_match']
            match_tier = match_results['match_tier']
            
            # Get key missing requirements
            missing_requirements = self._extract_key_missing_requirements(match_results)
            
            # Get strengths
            strengths = self._extract_key_strengths(match_results)
            
            # Create color class for visual indicator
            color_class = self._get_color_class(match_percentage)
            
            return {
                'is_valid': True,
                'match_percentage': match_percentage,
                'match_tier': match_tier,
                'missing_requirements': missing_requirements,
                'strengths': strengths,
                'color_class': color_class,
                'full_results': match_results
            }
            
        except Exception as e:
            logger.error(f"Error checking qualification: {str(e)}")
            return {
                'is_valid': False,
                'match_percentage': 0,
                'match_tier': 'error',
                'error': f"Error checking qualification: {str(e)}"
            }
    
    def check_qualification_batch(self, resume_text, job_listings):
        """
        Calculate qualification match percentages for multiple job listings.
        
        Args:
            resume_text (str): The candidate's resume text
            job_listings (list): List of job listing data
            
        Returns:
            dict: Match percentages by job ID
        """
        try:
            matches = {}
            
            for job in job_listings:
                job_id = job.get('id', None)
                if job_id is None:
                    continue
                    
                match_info = self.check_qualification(resume_text, job)
                matches[job_id] = match_info
            
            return matches
            
        except Exception as e:
            logger.error(f"Error checking qualifications in batch: {str(e)}")
            return {}
    
    def _extract_key_missing_requirements(self, match_results):
        """Extract the most important missing requirements."""
        missing_requirements = []
        
        # Extract missing skills (up to 3)
        skills_match = match_results.get('skills_match', {})
        missing_skills = skills_match.get('missing_skills', [])
        if missing_skills:
            missing_requirements.append({
                'type': 'skills',
                'items': missing_skills[:3]
            })
        
        # Extract experience gaps
        exp_match = match_results.get('experience_match', {})
        years_req = exp_match.get('years_required', 0)
        years_exp = exp_match.get('years_experience', 0)
        missing_areas = exp_match.get('relevant_areas_missing', [])
        
        if years_exp < years_req:
            missing_requirements.append({
                'type': 'experience_years',
                'required': years_req,
                'current': years_exp
            })
        
        if missing_areas:
            missing_requirements.append({
                'type': 'experience_areas',
                'items': missing_areas[:2]
            })
        
        # Extract education gaps
        edu_match = match_results.get('education_match', {})
        has_req_edu = edu_match.get('has_required_education', True)
        req_degree = edu_match.get('required_degree', None)
        
        if not has_req_edu and req_degree:
            missing_requirements.append({
                'type': 'education',
                'required': req_degree
            })
        
        return missing_requirements[:3]  # Limit to top 3 issues
    
    def _extract_key_strengths(self, match_results):
        """Extract the key strengths for this job match."""
        strengths = []
        
        # Extract matching skills (up to 3)
        skills_match = match_results.get('skills_match', {})
        matching_skills = skills_match.get('exact_matches', [])
        if matching_skills:
            strengths.append({
                'type': 'skills',
                'items': matching_skills[:3]
            })
        
        # Extract experience strengths
        exp_match = match_results.get('experience_match', {})
        years_req = exp_match.get('years_required', 0)
        years_exp = exp_match.get('years_experience', 0)
        relevant_areas = exp_match.get('relevant_areas_matched', [])
        
        if years_exp >= years_req and years_req > 0:
            strengths.append({
                'type': 'experience_years',
                'required': years_req,
                'current': years_exp
            })
        
        if relevant_areas:
            strengths.append({
                'type': 'experience_areas',
                'items': relevant_areas[:2]
            })
        
        # Extract education strengths
        edu_match = match_results.get('education_match', {})
        has_req_edu = edu_match.get('has_required_education', True)
        highest_degree = edu_match.get('candidate_highest_degree', {})
        
        if has_req_edu and highest_degree:
            degree_type = highest_degree.get('type', '')
            if degree_type:
                strengths.append({
                    'type': 'education',
                    'degree': degree_type
                })
        
        return strengths[:3]  # Limit to top 3 strengths
    
    def _get_color_class(self, match_percentage):
        """Get a color class for the match percentage for visual display."""
        if match_percentage >= 90:
            return 'excellent-match'
        elif match_percentage >= 80:
            return 'very-good-match'
        elif match_percentage >= 70:
            return 'good-match'
        elif match_percentage >= 50:
            return 'moderate-match'
        elif match_percentage >= 30:
            return 'low-match'
        else:
            return 'poor-match'
    
    def get_resume_improvement_suggestions(self, match_results, job_listing):
        """
        Generate specific suggestions for improving a resume for a job application.
        
        Args:
            match_results (dict): Full match results from check_qualification
            job_listing (dict): Job listing data
            
        Returns:
            list: Specific suggestions for improving the resume
        """
        suggestions = []
        
        # Check if we have valid results
        if not match_results.get('is_valid', False):
            return ["Update your resume with relevant skills and experience."]
        
        # Get full results
        full_results = match_results.get('full_results', {})
        
        # Add skills recommendations
        missing_skills = full_results.get('skills_match', {}).get('missing_skills', [])
        if missing_skills:
            skills_suggestion = f"Add these key skills to your resume: {', '.join(missing_skills[:5])}"
            suggestions.append(skills_suggestion)
        
        # Add experience recommendations
        exp_match = full_results.get('experience_match', {})
        years_req = exp_match.get('years_required', 0)
        years_exp = exp_match.get('years_experience', 0)
        
        if years_exp < years_req:
            suggestions.append(
                f"Highlight any additional experience to meet the {years_req} years requirement. "
                "Include relevant projects or freelance work."
            )
        
        missing_areas = exp_match.get('relevant_areas_missing', [])
        if missing_areas:
            suggestions.append(
                f"Emphasize experience in: {', '.join(missing_areas[:3])}. "
                "Include relevant projects or training."
            )
        
        # Add education recommendations
        edu_match = full_results.get('education_match', {})
        has_req_edu = edu_match.get('has_required_education', True)
        req_degree = edu_match.get('required_degree', None)
        
        if not has_req_edu and req_degree:
            suggestions.append(
                f"This position requires a {req_degree} degree. Highlight relevant coursework, "
                "certifications, or equivalent experience."
            )
        
        # Add general recommendations if match is low
        if match_results.get('match_percentage', 0) < 70:
            suggestions.append(
                "Tailor your resume specifically for this position by highlighting relevant "
                "skills and experiences that match the job requirements."
            )
        
        return suggestions if suggestions else ["Your resume appears to be a good match for this position."]