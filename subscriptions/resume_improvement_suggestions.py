"""
Resume Improvement Suggestions

This module provides targeted suggestions for improving resumes when applying to specific jobs.
It analyzes the gap between a resume and job requirements, then generates actionable recommendations
to help job seekers improve their chances of getting interviews.

This is a Pro-only feature that provides significant value to paying subscribers.
"""

import logging
import re
from typing import Dict, List, Tuple, Any, Optional
from collections import Counter

from .document_parser import DocumentParser
from .text_processor import TextProcessor
from .data_resources import (
    TECHNICAL_SKILLS,
    SOFT_SKILLS,
    PROFESSIONAL_SKILLS,
    COMMON_JOB_TITLES,
    EDUCATION_DEGREES,
    CERTIFICATION_PATTERNS
)
from .resume_analyzer import ResumeAnalyzer
from .job_qualification_checker import JobQualificationChecker


class ResumeImprovementSuggestions:
    """Provides targeted suggestions for improving resumes for specific job applications."""

    def __init__(self):
        """Initialize the ResumeImprovementSuggestions class."""
        self.logger = logging.getLogger(__name__)
        self.parser = DocumentParser()
        self.text_processor = TextProcessor()
        self.resume_analyzer = ResumeAnalyzer()
        self.job_matcher = JobQualificationChecker()
        
        # Define suggestion categories and priorities
        self.suggestion_categories = {
            'critical': [],    # Must-fix issues (missing required skills, etc.)
            'important': [],   # High-impact improvements
            'recommended': [], # General improvements
            'formatting': [],  # Style and formatting issues
            'long_term': []    # Longer-term career development suggestions
        }

    def analyze_resume_for_job(self, 
                              resume_file_path: Optional[str] = None,
                              resume_file_object: Optional[Any] = None,
                              resume_text: Optional[str] = None,
                              job_title: str = None,
                              job_description: str = None,
                              job_requirements: Optional[List[str]] = None,
                              job_skills: Optional[List[str]] = None,
                              job_experience_level: Optional[str] = None,
                              job_location: Optional[str] = None,
                              job_id: Optional[int] = None,
                              user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Analyze a resume against a specific job and provide improvement suggestions.
        
        Args:
            resume_file_path: Path to the resume file
            resume_file_object: File object for the resume
            resume_text: Plain text content of the resume
            job_title: Title of the job
            job_description: Full description of the job
            job_requirements: List of specific job requirements
            job_skills: List of required skills for the job
            job_experience_level: Required experience level (entry, mid, senior)
            job_location: Location of the job
            job_id: Database ID of the job listing (for using stored data)
            user_id: Database ID of the user (for using stored resume)
            
        Returns:
            Dict containing suggestions organized by priority and category
        """
        try:
            self.logger.info(f"Analyzing resume for job: {job_title}")
            
            # Reset suggestion categories
            for category in self.suggestion_categories:
                self.suggestion_categories[category] = []
            
            # Get resume text if not provided
            if resume_text is None:
                if resume_file_path:
                    resume_text = self.parser.extract_text_from_file(resume_file_path)
                elif resume_file_object:
                    resume_text = self.parser.extract_text_from_file_object(resume_file_object)
                else:
                    # If we have user_id, we can get their stored resume
                    if user_id:
                        # This would be implemented to fetch from database
                        pass
                    else:
                        raise ValueError("No resume provided for analysis")
            
            # Get job information if job_id is provided but other details are not
            if job_id and (not job_description or not job_requirements):
                # This would be implemented to fetch from database
                pass
                
            # Process resume and job text
            resume_sections = self.text_processor.extract_resume_sections(resume_text)
            resume_analysis = self.resume_analyzer.analyze_resume_text(resume_text)
            
            # Process job description
            job_sections = {}
            if job_description:
                job_sections = self.text_processor.extract_job_sections(job_description)
                
                # Extract requirements if not provided
                if not job_requirements and 'requirements' in job_sections:
                    job_requirements = self._extract_requirements_from_text(job_sections['requirements'])
                    
                # Extract skills if not provided
                if not job_skills and 'requirements' in job_sections:
                    job_skills = self.text_processor.extract_skills(job_sections['requirements'])
            
            # Generate match data between resume and job
            match_data = self._get_match_data(resume_analysis, job_title, job_description, 
                                             job_requirements, job_skills, job_experience_level)
            
            # If match score is already high, provide different suggestions
            if match_data['overall_percentage'] >= 85:
                return self._generate_high_match_suggestions(match_data, resume_analysis)
            
            # Generate suggestions based on match gaps
            suggestions = self._generate_suggestions(match_data, resume_analysis, 
                                                   job_title, job_description,
                                                   job_requirements, job_skills,
                                                   job_experience_level)
            
            # Add priority tag to each suggestion
            for category, category_suggestions in self.suggestion_categories.items():
                for i, suggestion in enumerate(category_suggestions):
                    if isinstance(suggestion, dict):
                        continue
                    self.suggestion_categories[category][i] = {
                        'text': suggestion,
                        'priority': self._get_priority_for_category(category),
                        'category': category
                    }
            
            # Compile final results
            results = {
                'match_percentage': match_data['overall_percentage'],
                'skill_match': match_data['skill_match_percentage'],
                'experience_match': match_data['experience_match_percentage'],
                'education_match': match_data['education_match_percentage'],
                'missing_skills': match_data.get('missing_skills', []),
                'partial_skills': match_data.get('partial_skills', []),
                'missing_keywords': match_data.get('missing_keywords', []),
                'improvement_suggestions': {
                    'critical': self.suggestion_categories['critical'],
                    'important': self.suggestion_categories['important'],
                    'recommended': self.suggestion_categories['recommended'],
                    'formatting': self.suggestion_categories['formatting'],
                    'long_term': self.suggestion_categories['long_term']
                },
                'focused_resume': self._generate_focused_resume_outline(resume_analysis, match_data),
                'original_resume_analysis': resume_analysis
            }
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error analyzing resume for job improvement: {str(e)}")
            # Return a basic response in case of error
            return {
                'match_percentage': 0,
                'error': str(e),
                'improvement_suggestions': {
                    'critical': [{'text': 'Unable to analyze resume. Please try again or contact support.', 'priority': 'high', 'category': 'critical'}],
                    'important': [],
                    'recommended': [],
                    'formatting': [],
                    'long_term': []
                }
            }
    
    def _get_match_data(self, resume_analysis, job_title, job_description, 
                       job_requirements, job_skills, job_experience_level):
        """Generate match data between resume and job."""
        # This is a simplified version - in a real implementation we would use the JobQualificationChecker
        # Here we're creating a mock response with the essential structure
        
        # Extract skills from resume analysis
        resume_skills = set()
        if 'skills' in resume_analysis and 'parsed_skills' in resume_analysis['skills']:
            resume_skills = set(resume_analysis['skills']['parsed_skills'])
        
        # Determine missing and partial skills
        missing_skills = []
        partial_skills = []
        if job_skills:
            job_skills_set = set(job_skills)
            missing_skills = list(job_skills_set - resume_skills)
            
            # Check for partial matches (skills that are similar but not exact matches)
            for job_skill in job_skills:
                if job_skill not in resume_skills:
                    for resume_skill in resume_skills:
                        if job_skill.lower() in resume_skill.lower() or resume_skill.lower() in job_skill.lower():
                            if job_skill not in partial_skills:
                                partial_skills.append(job_skill)
        
        # Calculate match percentages
        skill_match = self._calculate_skill_match(resume_skills, job_skills) if job_skills else 70
        experience_match = self._calculate_experience_match(resume_analysis, job_experience_level) if job_experience_level else 65
        education_match = self._calculate_education_match(resume_analysis, job_requirements) if job_requirements else 75
        
        # Calculate overall match score (weighted average)
        overall_match = int(0.5 * skill_match + 0.3 * experience_match + 0.2 * education_match)
        
        return {
            'overall_percentage': overall_match,
            'skill_match_percentage': skill_match,
            'experience_match_percentage': experience_match,
            'education_match_percentage': education_match,
            'missing_skills': missing_skills,
            'partial_skills': partial_skills,
            'missing_keywords': self._extract_important_keywords(job_description, resume_analysis)
        }
    
    def _calculate_skill_match(self, resume_skills, job_skills):
        """Calculate the skill match percentage."""
        if not job_skills:
            return 50
            
        job_skills_set = set(job_skills)
        matched_skills = resume_skills.intersection(job_skills_set)
        
        # Calculate percentage with a minimum score
        if len(job_skills_set) == 0:
            return 100
            
        match_percentage = int(min(100, max(0, len(matched_skills) / len(job_skills_set) * 100)))
        return match_percentage
    
    def _calculate_experience_match(self, resume_analysis, job_experience_level):
        """Calculate the experience match percentage."""
        # Get years of experience from resume
        total_experience = 0
        if 'experience' in resume_analysis and 'entries' in resume_analysis['experience']:
            for entry in resume_analysis['experience']['entries']:
                if 'duration_years' in entry:
                    total_experience += entry['duration_years']
        
        # Map job experience level to years
        required_years = 0
        if job_experience_level:
            level_map = {
                'entry': 0,
                'junior': 1,
                'mid': 3,
                'senior': 5,
                'lead': 7,
                'manager': 5,
                'director': 10,
                'executive': 15
            }
            required_years = level_map.get(job_experience_level.lower(), 3)
        
        # Calculate match percentage
        if required_years == 0:
            return 100
        elif total_experience >= required_years:
            return 100
        else:
            return int(min(100, max(0, (total_experience / required_years) * 100)))
    
    def _calculate_education_match(self, resume_analysis, job_requirements):
        """Calculate the education match percentage."""
        # Extract education level from job requirements
        required_education = self._extract_education_from_requirements(job_requirements)
        
        # Get education from resume
        resume_education = 0  # 0=none, 1=high school, 2=associate, 3=bachelor, 4=master, 5=doctorate
        if 'education' in resume_analysis and 'entries' in resume_analysis['education']:
            for entry in resume_analysis['education']['entries']:
                degree = entry.get('degree', '').lower()
                if 'phd' in degree or 'doctor' in degree:
                    resume_education = 5
                    break
                elif 'master' in degree or 'mba' in degree or 'ms ' in degree or 'ma ' in degree:
                    resume_education = 4
                elif 'bachelor' in degree or 'bs ' in degree or 'ba ' in degree:
                    resume_education = max(resume_education, 3)
                elif 'associate' in degree or 'aa ' in degree or 'as ' in degree:
                    resume_education = max(resume_education, 2)
                elif 'high school' in degree or 'diploma' in degree:
                    resume_education = max(resume_education, 1)
        
        # Calculate match percentage
        if required_education == 0 or resume_education >= required_education:
            return 100
        else:
            return int(min(100, max(0, (resume_education / required_education) * 100)))
    
    def _extract_education_from_requirements(self, job_requirements):
        """Extract required education level from job requirements."""
        if not job_requirements:
            return 0
            
        # Join requirements into a single string for easier processing
        requirements_text = ' '.join(job_requirements).lower()
        
        # Check for different education levels
        if 'phd' in requirements_text or 'doctorate' in requirements_text or 'doctoral' in requirements_text:
            return 5
        elif 'master' in requirements_text or 'mba' in requirements_text or 'ms degree' in requirements_text:
            return 4
        elif 'bachelor' in requirements_text or 'bs degree' in requirements_text or 'ba degree' in requirements_text:
            return 3
        elif 'associate' in requirements_text or 'aa degree' in requirements_text:
            return 2
        elif 'high school' in requirements_text or 'diploma' in requirements_text:
            return 1
        return 0
    
    def _extract_requirements_from_text(self, requirements_text):
        """Extract individual requirements from requirements text."""
        # Split by bullets and newlines
        lines = re.split(r'[\n•]+', requirements_text)
        
        # Clean up each line
        requirements = []
        for line in lines:
            line = line.strip()
            if line and len(line) > 5:
                requirements.append(line)
        
        return requirements
    
    def _extract_important_keywords(self, job_description, resume_analysis):
        """Extract important keywords from job description that are missing in resume."""
        if not job_description:
            return []
            
        # Extract common terms from job description (excluding stopwords)
        job_terms = set(self.text_processor.extract_significant_terms(job_description))
        
        # Get all resume text
        resume_text = ''
        if 'original_text' in resume_analysis:
            resume_text = resume_analysis['original_text']
        
        # Extract common terms from resume
        resume_terms = set(self.text_processor.extract_significant_terms(resume_text))
        
        # Find missing terms
        missing_terms = job_terms - resume_terms
        
        # Sort by importance (frequency in job description)
        job_words = job_description.lower().split()
        term_counts = Counter([term for term in job_words if term in missing_terms])
        
        # Return top 10 most important missing terms
        return [term for term, count in term_counts.most_common(10)]
    
    def _generate_suggestions(self, match_data, resume_analysis, job_title, job_description,
                            job_requirements, job_skills, job_experience_level):
        """Generate tailored suggestions based on match gaps."""
        
        # 1. Critical suggestions - missing required skills
        self._add_missing_skills_suggestions(match_data.get('missing_skills', []), 
                                           match_data.get('partial_skills', []))
        
        # 2. Experience suggestions
        self._add_experience_suggestions(match_data['experience_match_percentage'], 
                                        resume_analysis, job_experience_level, job_title)
        
        # 3. Education suggestions
        self._add_education_suggestions(match_data['education_match_percentage'], 
                                       resume_analysis, job_requirements)
        
        # 4. Keyword optimization suggestions
        self._add_keyword_optimization_suggestions(match_data.get('missing_keywords', []))
        
        # 5. Resume structure and formatting suggestions
        self._add_formatting_suggestions(resume_analysis)
        
        # 6. Targeted content suggestions
        self._add_content_suggestions(resume_analysis, job_title, job_description)
        
        # Return all suggestions organized by category
        return self.suggestion_categories
    
    def _add_missing_skills_suggestions(self, missing_skills, partial_skills):
        """Add suggestions for addressing missing skills."""
        # Handle missing critical skills
        if missing_skills:
            # Add top skills to critical suggestions
            top_skills = missing_skills[:5]
            self.suggestion_categories['critical'].append(
                f"Add these key required skills to your resume: {', '.join(top_skills)}"
            )
            
            # Provide context for where to add them
            self.suggestion_categories['important'].append(
                f"Include these skills in your summary section and demonstrate them in your work experience bullet points"
            )
            
            # If there are more skills, add them to important suggestions
            if len(missing_skills) > 5:
                additional_skills = missing_skills[5:10]
                self.suggestion_categories['important'].append(
                    f"Consider highlighting these additional relevant skills: {', '.join(additional_skills)}"
                )
        
        # Handle partial skill matches
        if partial_skills:
            self.suggestion_categories['important'].append(
                f"Use exact skill terms from the job description. Replace or expand these skills: {', '.join(partial_skills[:5])}"
            )
    
    def _add_experience_suggestions(self, experience_match, resume_analysis, job_experience_level, job_title):
        """Add suggestions for improving experience section."""
        if experience_match < 70:
            # Insufficient experience
            self.suggestion_categories['important'].append(
                "Highlight transferable skills and related projects to compensate for limited direct experience"
            )
            
            self.suggestion_categories['recommended'].append(
                f"Quantify achievements in your experience section to demonstrate impact relevant to {job_title}"
            )
            
            self.suggestion_categories['long_term'].append(
                f"Consider gaining additional experience through certifications, volunteering, or side projects related to {job_title}"
            )
        elif experience_match < 90:
            # Good experience but needs enhancement
            self.suggestion_categories['recommended'].append(
                "Align your work experiences more closely with job requirements by highlighting relevant responsibilities"
            )
            
            self.suggestion_categories['recommended'].append(
                f"Use industry-specific terminology from the job description in your work experience bullet points"
            )
    
    def _add_education_suggestions(self, education_match, resume_analysis, job_requirements):
        """Add suggestions for improving education section."""
        if education_match < 70:
            # Education doesn't meet requirements
            self.suggestion_categories['important'].append(
                "Highlight relevant coursework, training or certifications to compensate for education requirements"
            )
            
            self.suggestion_categories['long_term'].append(
                "Consider pursuing further education or certifications to meet job requirements"
            )
        elif education_match < 90:
            # Education meets requirements but could be better presented
            self.suggestion_categories['recommended'].append(
                "Emphasize your educational achievements and relevant coursework in your education section"
            )
    
    def _add_keyword_optimization_suggestions(self, missing_keywords):
        """Add suggestions for keyword optimization."""
        if missing_keywords:
            self.suggestion_categories['important'].append(
                f"Include these keywords from the job description: {', '.join(missing_keywords[:5])}"
            )
            
            self.suggestion_categories['recommended'].append(
                "Many employers use Applicant Tracking Systems (ATS) - incorporate these keywords naturally throughout your resume"
            )
    
    def _add_formatting_suggestions(self, resume_analysis):
        """Add suggestions for resume formatting."""
        # Check resume length
        if 'pages' in resume_analysis and resume_analysis['pages'] > 2:
            self.suggestion_categories['formatting'].append(
                "Your resume is longer than 2 pages. Consider condensing it to focus on the most relevant experiences"
            )
        
        # Check for appropriate bullet points
        if 'experience' in resume_analysis and 'entries' in resume_analysis['experience']:
            has_bullets = False
            for entry in resume_analysis['experience']['entries']:
                if 'bullet_points' in entry and entry['bullet_points']:
                    has_bullets = True
                    break
            
            if not has_bullets:
                self.suggestion_categories['formatting'].append(
                    "Use bullet points to highlight achievements and responsibilities in your work experience section"
                )
    
    def _add_content_suggestions(self, resume_analysis, job_title, job_description):
        """Add suggestions for improving resume content."""
        # Check if resume has a summary/objective
        has_summary = False
        if 'sections' in resume_analysis and resume_analysis['sections']:
            if any(section.lower() in ['summary', 'objective', 'profile'] for section in resume_analysis['sections']):
                has_summary = True
        
        if not has_summary:
            self.suggestion_categories['recommended'].append(
                f"Add a concise professional summary tailored to the {job_title} position"
            )
        else:
            self.suggestion_categories['recommended'].append(
                f"Customize your summary section to target the {job_title} position specifically"
            )
        
        # Check for quantifiable achievements
        has_quantified = False
        if 'experience' in resume_analysis and 'entries' in resume_analysis['experience']:
            for entry in resume_analysis['experience']['entries']:
                if 'description' in entry:
                    if re.search(r'\d+%|increased|decreased|improved|reduced|saved|generated|\$\d+|\d+ hours', entry['description'], re.IGNORECASE):
                        has_quantified = True
                        break
        
        if not has_quantified:
            self.suggestion_categories['important'].append(
                "Add metrics and quantifiable achievements to your experience section (e.g., 'Increased sales by 20%')"
            )
    
    def _generate_high_match_suggestions(self, match_data, resume_analysis):
        """Generate suggestions for resumes that already have a high match score."""
        results = {
            'match_percentage': match_data['overall_percentage'],
            'skill_match': match_data['skill_match_percentage'],
            'experience_match': match_data['experience_match_percentage'],
            'education_match': match_data['education_match_percentage'],
            'improvement_suggestions': {
                'critical': [],
                'important': [],
                'recommended': [
                    {
                        'text': "Your resume is already well-matched to this job! Consider customizing your cover letter to highlight your most relevant experiences.",
                        'priority': 'medium',
                        'category': 'recommended'
                    },
                    {
                        'text': "Prepare for interviews by researching the company and preparing stories that demonstrate your skills.",
                        'priority': 'medium',
                        'category': 'recommended'
                    }
                ],
                'formatting': [
                    {
                        'text': "Consider small tweaks to emphasize your strongest qualifications for this specific role.",
                        'priority': 'low',
                        'category': 'formatting'
                    }
                ],
                'long_term': []
            },
            'original_resume_analysis': resume_analysis
        }
        
        return results
    
    def _generate_focused_resume_outline(self, resume_analysis, match_data):
        """Generate an outline for a focused resume tailored to the job."""
        # This would generate a structured outline with specific content to include
        # In a real implementation, this would be more sophisticated
        
        focused_outline = {
            'summary': "A tailored professional summary highlighting your most relevant qualifications",
            'skills_to_emphasize': match_data.get('missing_skills', [])[:5],
            'experience_focus': "Focus on responsibilities and achievements most relevant to this position",
            'education_presentation': "Format education section to meet job requirements",
            'additional_sections': ["Certifications", "Projects", "Professional Development"]
        }
        
        return focused_outline
    
    def _get_priority_for_category(self, category):
        """Map category to priority level."""
        priority_map = {
            'critical': 'high',
            'important': 'high',
            'recommended': 'medium',
            'formatting': 'low',
            'long_term': 'low'
        }
        return priority_map.get(category, 'medium')

    def get_improvement_suggestions_for_job_application(self, user_id, job_id):
        """
        Public method to get resume improvement suggestions for a job application.
        
        This would integrate with the database to fetch the user's resume and job details.
        
        Args:
            user_id: ID of the user applying for the job
            job_id: ID of the job being applied for
            
        Returns:
            Dict containing improvement suggestions
        """
        # In a real implementation, this would fetch data from the database
        # Here we're creating a mock implementation
        
        try:
            # This would fetch resume and job data from the database
            resume_text = "This is a placeholder for resume text that would be fetched from the database"
            job_data = {
                'title': 'Software Developer',
                'description': 'This is a placeholder for job description that would be fetched from the database',
                'requirements': ['Bachelor\'s degree in Computer Science', 'Experience with Python'],
                'skills': ['Python', 'Django', 'JavaScript'],
                'experience_level': 'mid'
            }
            
            # Call the analysis method
            results = self.analyze_resume_for_job(
                resume_text=resume_text,
                job_title=job_data['title'],
                job_description=job_data['description'],
                job_requirements=job_data['requirements'],
                job_skills=job_data['skills'],
                job_experience_level=job_data['experience_level']
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error getting improvement suggestions for job application: {str(e)}")
            return {
                'error': str(e),
                'improvement_suggestions': {
                    'critical': [{'text': 'An error occurred while analyzing your resume.', 'priority': 'high', 'category': 'critical'}]
                }
            }