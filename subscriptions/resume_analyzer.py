"""
Resume Analysis System

This module implements resume analysis functionality using the core infrastructure
components (document parsing, text processing, content validation, and data resources).
It provides detailed analysis of resume content, quality assessment, and recommendations
for improvement.
"""

import logging
import os
import json
from collections import Counter
import re

from .document_parser import DocumentParser
from .text_processor import TextProcessor
from .content_validator import ContentValidator
from .data_resources import TECHNICAL_SKILLS, SOFT_SKILLS, get_all_skills, get_all_job_titles

logger = logging.getLogger(__name__)

class ResumeAnalyzer:
    """
    Class for analyzing resumes using the core infrastructure.

    This class uses document parsing, text processing, and content validation
    to provide comprehensive resume analysis with detailed feedback and
    actionable recommendations.
    """

    def __init__(self):
        """Initialize the ResumeAnalyzer with necessary components."""
        self.document_parser = DocumentParser()
        self.text_processor = TextProcessor()
        self.content_validator = ContentValidator(self.text_processor)

        # Flatten skill lists for easier matching
        self.all_skills = get_all_skills()
        self.all_job_titles = get_all_job_titles()

        # Load skill categories for grouping
        self.technical_skill_categories = {}
        for category, skills in TECHNICAL_SKILLS.items():
            for skill in skills:
                self.technical_skill_categories[skill.lower()] = category

        self.soft_skill_categories = {}
        for category, skills in SOFT_SKILLS.items():
            for skill in skills:
                self.soft_skill_categories[skill.lower()] = category

    def analyze_resume_file(self, file_path):
        """
        Analyze a resume from a file path.

        Args:
            file_path (str): Path to the resume file

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
            return self.analyze_resume_text(text)

        except Exception as e:
            logger.error(f"Error analyzing resume file {file_path}: {str(e)}")
            return {
                'error': f"Error analyzing resume: {str(e)}",
                'is_valid': False
            }

    def analyze_resume_file_object(self, file_object, file_name):
        """
        Analyze a resume from a file object (e.g., uploaded file).

        Args:
            file_object: File-like object containing the resume
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
            return self.analyze_resume_text(text)

        except Exception as e:
            logger.error(f"Error analyzing resume file {file_name}: {str(e)}")
            return {
                'error': f"Error analyzing resume: {str(e)}",
                'is_valid': False
            }

    def analyze_resume_text(self, text):
        """
        Analyze resume text content.

        Args:
            text (str): Text content of the resume

        Returns:
            dict: Analysis results
        """
        # First validate that this is a resume
        validation = self.content_validator.validate_resume(text)

        # Even if the validator doesn't think it's a resume, we'll try to analyze it anyway
        # This makes the system more lenient with different resume formats
        if not validation.get('is_valid_resume', False):
            logger.warning(f"Document validation failed, but proceeding with analysis anyway. Confidence: {validation.get('confidence', 0)}")
            logger.warning(f"Document type detected: {validation.get('document_type', 'unknown')}")

            # Only return error for completely empty documents
            if not text.strip():
                return {
                    'is_valid': False,
                    'error': 'The document appears to be empty.',
                    'document_type': 'unknown',
                    'confidence': 0
                }

        # Process the document to extract sections and entities
        processed_doc = self.text_processor.process_document(text, 'resume')

        # Extract skills from the resume
        parsed_skills = self._extract_and_categorize_skills(text, processed_doc)

        # Extract experience from the resume
        parsed_experience = self._extract_experience(text, processed_doc)

        # Extract education from the resume
        parsed_education = self._extract_education(text, processed_doc)

        # Calculate scores
        skill_score = self._calculate_skill_score(parsed_skills)
        experience_score = self._calculate_experience_score(parsed_experience)
        education_score = self._calculate_education_score(parsed_education)

        # Overall score is weighted average
        overall_score = int((skill_score * 0.4) + (experience_score * 0.4) + (education_score * 0.2))

        # Generate recommendations
        recommendations = self._generate_recommendations(
            validation,
            skill_score,
            experience_score,
            education_score,
            parsed_skills,
            parsed_experience,
            parsed_education
        )

        # Generate detailed analysis
        detailed_analysis = self._generate_detailed_analysis(
            parsed_skills,
            parsed_experience,
            parsed_education,
            skill_score,
            experience_score,
            education_score
        )

        # Prepare the analysis results
        analysis = {
            'is_valid': True,
            'parsed_skills': parsed_skills,
            'parsed_experience': parsed_experience,
            'parsed_education': parsed_education,
            'skill_score': skill_score,
            'experience_score': experience_score,
            'education_score': education_score,
            'overall_score': overall_score,
            'suggestions': recommendations,
            'section_scores': validation.get('sections', {}),
            'missing_sections': validation.get('missing_sections', []),
            'completeness': validation.get('completeness', 0),
            'detailed_analysis': detailed_analysis,
            'extracted_text': text  # Include the extracted text in the results
        }

        return analysis

    def _generate_detailed_analysis(self, parsed_skills, parsed_experience, parsed_education, skill_score, experience_score, education_score):
        """
        Generate detailed analysis of the resume.

        Args:
            parsed_skills (dict): Parsed skills
            parsed_experience (list): Parsed experience
            parsed_education (list): Parsed education
            skill_score (int): Skill score
            experience_score (int): Experience score
            education_score (int): Education score

        Returns:
            dict: Detailed analysis
        """
        detailed_analysis = {}

        # Skills analysis
        technical_skills = parsed_skills.get('technical', [])
        soft_skills = parsed_skills.get('soft', [])

        skills_analysis = {
            'technical_skills_count': len(technical_skills),
            'soft_skills_count': len(soft_skills),
            'skill_diversity': self._analyze_skill_diversity(technical_skills),
            'in_demand_skills': self._identify_in_demand_skills(technical_skills),
            'skill_improvement_areas': []
        }

        # Identify skill improvement areas
        if len(technical_skills) < 5:
            skills_analysis['skill_improvement_areas'].append("Add more technical skills to showcase your expertise")
        if len(soft_skills) < 3:
            skills_analysis['skill_improvement_areas'].append("Include more soft skills to demonstrate your workplace effectiveness")

        # Experience analysis
        experience_analysis = {
            'experience_entries_count': len(parsed_experience),
            'has_detailed_descriptions': False,
            'has_quantifiable_achievements': False,
            'experience_timeline': self._analyze_experience_timeline(parsed_experience),
            'experience_improvement_areas': []
        }

        # Check for detailed descriptions and achievements
        achievement_indicators = [
            'achieve', 'improve', 'increase', 'reduce', 'save', 'create', 'develop', 'implement',
            'lead', 'manage', 'coordinate', 'launch', 'design', 'mentor', 'win', 'award',
            'percent', '%', 'million', 'thousand', 'growth', 'revenue', 'cost', 'efficiency'
        ]

        for entry in parsed_experience:
            description = entry.get('description', '')
            if len(description.split()) >= 20:
                experience_analysis['has_detailed_descriptions'] = True

            if any(indicator in description.lower() for indicator in achievement_indicators):
                experience_analysis['has_quantifiable_achievements'] = True

        # Identify experience improvement areas
        if not experience_analysis['has_detailed_descriptions']:
            experience_analysis['experience_improvement_areas'].append("Add more detailed descriptions of your responsibilities")
        if not experience_analysis['has_quantifiable_achievements']:
            experience_analysis['experience_improvement_areas'].append("Include quantifiable achievements with metrics")

        # Education analysis
        education_analysis = {
            'education_entries_count': len(parsed_education),
            'highest_degree': self._identify_highest_degree(parsed_education),
            'education_improvement_areas': []
        }

        # Identify education improvement areas
        if len(parsed_education) == 0:
            education_analysis['education_improvement_areas'].append("Add your educational background")
        else:
            for entry in parsed_education:
                if "not specified" in entry.get('degree', '') or "not specified" in entry.get('institution', ''):
                    education_analysis['education_improvement_areas'].append("Complete your education details with degree and institution information")
                    break

        detailed_analysis = {
            'skills_analysis': skills_analysis,
            'experience_analysis': experience_analysis,
            'education_analysis': education_analysis,
            'ats_compatibility': self._analyze_ats_compatibility(parsed_skills, parsed_experience, parsed_education)
        }

        return detailed_analysis

    def _analyze_skill_diversity(self, technical_skills):
        """Analyze the diversity of technical skills."""
        tech_categories = set()
        for skill in technical_skills:
            skill_lower = skill.lower()
            if skill_lower in self.technical_skill_categories:
                tech_categories.add(self.technical_skill_categories[skill_lower])

        diversity_level = "Low"
        if len(tech_categories) >= 4:
            diversity_level = "High"
        elif len(tech_categories) >= 2:
            diversity_level = "Medium"

        return {
            'level': diversity_level,
            'categories': list(tech_categories)
        }

    def _identify_in_demand_skills(self, technical_skills):
        """Identify in-demand skills from the technical skills."""
        # List of currently in-demand skills
        in_demand = [
            "Python", "JavaScript", "React", "Node.js", "AWS", "Azure", "GCP",
            "Docker", "Kubernetes", "Machine Learning", "Data Science", "AI",
            "DevOps", "Cloud Computing", "Cybersecurity", "Blockchain",
            "SQL", "NoSQL", "Big Data", "Data Analysis", "Data Visualization"
        ]

        matches = []
        for skill in technical_skills:
            if any(in_demand_skill.lower() == skill.lower() for in_demand_skill in in_demand):
                matches.append(skill)

        return matches

    def _analyze_experience_timeline(self, parsed_experience):
        """Analyze the timeline of work experience."""
        if not parsed_experience:
            return {
                'total_years': 0,
                'has_gaps': False,
                'most_recent_experience': None
            }

        # Extract years from experience entries
        years_data = []
        for entry in parsed_experience:
            years = entry.get('years', '')
            if 'present' in years.lower() or 'current' in years.lower():
                years_data.append({
                    'entry': entry,
                    'is_current': True
                })
            else:
                years_data.append({
                    'entry': entry,
                    'is_current': False
                })

        # Sort by recency (assuming entries with 'present' are most recent)
        years_data.sort(key=lambda x: x['is_current'], reverse=True)

        most_recent = None
        if years_data:
            most_recent = years_data[0]['entry']

        # Estimate total years (simplified)
        total_years = len(parsed_experience) * 2  # Rough estimate

        return {
            'total_years': total_years,
            'has_gaps': False,  # Simplified
            'most_recent_experience': most_recent
        }

    def _identify_highest_degree(self, parsed_education):
        """Identify the highest degree from education entries."""
        if not parsed_education:
            return None

        # Degree hierarchy
        degree_levels = {
            'phd': 5,
            'doctorate': 5,
            'doctor': 5,
            'master': 4,
            'mba': 4,
            'bachelor': 3,
            'undergraduate': 3,
            'associate': 2,
            'diploma': 1,
            'certificate': 1,
            'high school': 0
        }

        highest_level = -1
        highest_degree = None

        for entry in parsed_education:
            degree = entry.get('degree', '').lower()
            for key, level in degree_levels.items():
                if key in degree and level > highest_level:
                    highest_level = level
                    highest_degree = entry

        return highest_degree

    def _analyze_ats_compatibility(self, parsed_skills, parsed_experience, parsed_education):
        """Analyze ATS (Applicant Tracking System) compatibility."""
        compatibility_score = 70  # Base score

        # Check for key elements that improve ATS compatibility
        if parsed_skills.get('technical', []) and parsed_skills.get('soft', []):
            compatibility_score += 10

        if parsed_experience and all(entry.get('title') != "Unknown Position" for entry in parsed_experience):
            compatibility_score += 10

        if parsed_education:
            compatibility_score += 10

        compatibility_level = "Medium"
        if compatibility_score >= 90:
            compatibility_level = "High"
        elif compatibility_score < 70:
            compatibility_level = "Low"

        improvement_tips = []
        if compatibility_score < 90:
            improvement_tips = [
                "Use standard section headings (e.g., 'Experience', 'Education', 'Skills')",
                "Avoid using tables, headers, footers, or complex formatting",
                "Include keywords from job descriptions you're targeting",
                "Use standard job titles and company names",
                "Avoid using acronyms without spelling them out first"
            ]

        return {
            'score': compatibility_score,
            'level': compatibility_level,
            'improvement_tips': improvement_tips
        }

    def _extract_and_categorize_skills(self, text, processed_doc):
        """
        Extract and categorize skills from resume text.

        Args:
            text (str): Resume text content
            processed_doc (dict): Processed document data

        Returns:
            dict: Categorized skills
        """
        # Get skills from entities
        entities = processed_doc.get('entities', {})
        skills_from_entities = set(entities.get('skills', []))

        # Additional skill extraction using regex patterns
        skills_section = processed_doc.get('sections', {}).get('skills', '')

        # Look for skills in the skills section and throughout the text
        all_skills_found = set()

        # Check for exact skill matches
        for skill in self.all_skills:
            # Look for whole word matches
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                all_skills_found.add(skill)

        # Combine skills from different sources
        all_skills_found.update(skills_from_entities)

        # Categorize skills
        technical_skills = []
        soft_skills = []

        for skill in all_skills_found:
            skill_lower = skill.lower()

            # Check if it's a technical skill
            if skill_lower in self.technical_skill_categories or any(s.lower() == skill_lower for s in TECHNICAL_SKILLS.get('programming_languages', [])):
                technical_skills.append(skill)
            # Check if it's a soft skill
            elif skill_lower in self.soft_skill_categories:
                soft_skills.append(skill)
            # If not categorized, determine based on common technical terms
            elif any(tech_term in skill_lower for tech_term in ['program', 'develop', 'code', 'script', 'framework', 'database', 'system', 'network', 'software', 'hardware', 'cyber', 'cloud', 'web', 'app']):
                technical_skills.append(skill)
            else:
                soft_skills.append(skill)

        return {
            'technical': sorted(technical_skills),
            'soft': sorted(soft_skills)
        }

    def _extract_experience(self, text, processed_doc):
        """
        Extract work experience from resume text.

        Args:
            text (str): Resume text content
            processed_doc (dict): Processed document data

        Returns:
            list: Extracted work experience entries
        """
        experience_entries = []
        experience_section = processed_doc.get('sections', {}).get('experience', '')

        if not experience_section:
            # Try to find experience section using regex if text_processor didn't identify it
            exp_matches = re.search(r'(?:experience|employment|work history|professional experience)(?:.*?)(?:\n\n|\Z)', text, re.IGNORECASE | re.DOTALL)
            if exp_matches:
                experience_section = exp_matches.group(0)

        if experience_section:
            # Split experience section into entries
            # Look for patterns indicating separate job entries
            job_entries = re.split(r'\n(?=[A-Z][^a-z\n]*\n|[A-Z][^a-z\n]*\s+(?:19|20)\d{2})', experience_section)

            for entry in job_entries:
                if len(entry.strip()) < 10:  # Skip very short entries
                    continue

                # Extract job title
                title_match = re.search(r'\b(?:senior|lead|principal|junior|staff)?\s*([A-Za-z][A-Za-z\s]+(?:developer|engineer|manager|director|analyst|designer|consultant|specialist|coordinator|assistant|associate|admin|supervisor|advisor|officer|representative|clerk|intern))\b', entry, re.IGNORECASE)
                title = title_match.group(1) if title_match else "Unknown Position"

                # Extract company name
                company_match = re.search(r'(?:at|with|for)\s+([A-Z][A-Za-z0-9\s&.,]+)(?:,|\s+in|\s+\(|\s+\d|\s*$)', entry)
                if not company_match:
                    company_match = re.search(r'\b([A-Z][A-Za-z0-9\s&.,]+(?:Inc|LLC|Ltd|Corporation|Corp|Company|Co))\b', entry)

                company = company_match.group(1).strip() if company_match else "Unknown Company"

                # Extract dates
                date_match = re.search(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\s*-\s*(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|Present|Current)\b', entry, re.IGNORECASE)
                if not date_match:
                    date_match = re.search(r'\b((?:19|20)\d{2})\s*-\s*((?:19|20)\d{2}|Present|Current)\b', entry, re.IGNORECASE)

                years = date_match.group(0) if date_match else "Unknown Date Range"

                # Extract description
                description_lines = []
                for line in entry.split('\n'):
                    line = line.strip()
                    if line and title not in line and company not in line and years not in line:
                        description_lines.append(line)

                description = ' '.join(description_lines)

                # Add the entry
                experience_entries.append({
                    'title': title,
                    'company': company,
                    'years': years,
                    'description': description
                })

        return experience_entries

    def _extract_education(self, text, processed_doc):
        """
        Extract education information from resume text.

        Args:
            text (str): Resume text content
            processed_doc (dict): Processed document data

        Returns:
            list: Extracted education entries
        """
        education_entries = []
        education_section = processed_doc.get('sections', {}).get('education', '')

        if not education_section:
            # Try to find education section using regex if text_processor didn't identify it
            edu_matches = re.search(r'(?:education|academic background|qualifications)(?:.*?)(?:\n\n|\Z)', text, re.IGNORECASE | re.DOTALL)
            if edu_matches:
                education_section = edu_matches.group(0)

        if education_section:
            # Look for degree patterns
            degree_patterns = [
                r'\b(Bachelor|Master|Doctor|PhD|BS|BA|MS|MA|MBA|B\.S\.|B\.A\.|M\.S\.|M\.A\.|Ph\.D\.)[^\n.]*?(?:in|of)\s+([^\n,]+)',
                r'\b(Associate\'s Degree|Bachelor\'s Degree|Master\'s Degree|Doctorate)[^\n.]*?(?:in|of)\s+([^\n,]+)',
                r'\b(High School Diploma|GED|Certificate)[^\n.]*'
            ]

            degrees = []
            for pattern in degree_patterns:
                matches = re.finditer(pattern, education_section, re.IGNORECASE)
                for match in matches:
                    degree_text = match.group(0)
                    degrees.append(degree_text)

            # Look for institution names
            institution_pattern = r'\b(?:University|College|Institute|School) of [A-Z][^\n,]+|\b[A-Z][A-Za-z\s&]+ (?:University|College|Institute|School)\b'
            institutions = re.findall(institution_pattern, education_section)

            # Look for years
            year_pattern = r'\b(19|20)\d{2}\b'
            years = re.findall(year_pattern, education_section)

            # Try to form education entries
            if degrees and institutions:
                # Match each degree with an institution and year if possible
                for i, degree in enumerate(degrees):
                    institution = institutions[i] if i < len(institutions) else institutions[-1]
                    year = years[i] if i < len(years) else (years[-1] if years else "")

                    education_entries.append({
                        'degree': degree.strip(),
                        'institution': institution.strip(),
                        'year': year
                    })
            elif institutions:
                # If we have institutions but no degrees
                for i, institution in enumerate(institutions):
                    year = years[i] if i < len(years) else (years[-1] if years else "")

                    education_entries.append({
                        'degree': "Degree not specified",
                        'institution': institution.strip(),
                        'year': year
                    })
            elif degrees:
                # If we have degrees but no institutions
                for i, degree in enumerate(degrees):
                    year = years[i] if i < len(years) else (years[-1] if years else "")

                    education_entries.append({
                        'degree': degree.strip(),
                        'institution': "Institution not specified",
                        'year': year
                    })

        return education_entries

    def _calculate_skill_score(self, parsed_skills):
        """
        Calculate a score for the skills section.

        Args:
            parsed_skills (dict): Categorized skills

        Returns:
            int: Score from 0-100
        """
        technical_skills = parsed_skills.get('technical', [])
        soft_skills = parsed_skills.get('soft', [])

        # Base score
        score = 50

        # Evaluate technical skills
        if len(technical_skills) >= 10:
            score += 25
        elif len(technical_skills) >= 5:
            score += 15
        elif len(technical_skills) >= 1:
            score += 5

        # Evaluate soft skills
        if len(soft_skills) >= 5:
            score += 15
        elif len(soft_skills) >= 3:
            score += 10
        elif len(soft_skills) >= 1:
            score += 5

        # Check skill diversity
        tech_categories = set()
        for skill in technical_skills:
            skill_lower = skill.lower()
            if skill_lower in self.technical_skill_categories:
                tech_categories.add(self.technical_skill_categories[skill_lower])

        if len(tech_categories) >= 3:
            score += 10
        elif len(tech_categories) >= 2:
            score += 5

        # Ensure score is within bounds
        return max(0, min(100, score))

    def _calculate_experience_score(self, parsed_experience):
        """
        Calculate a score for the experience section.

        Args:
            parsed_experience (list): Extracted work experience entries

        Returns:
            int: Score from 0-100
        """
        # Base score
        score = 50

        # No experience entries is a problem
        if not parsed_experience:
            return 30

        # More experience entries is better
        if len(parsed_experience) >= 3:
            score += 15
        elif len(parsed_experience) >= 2:
            score += 10
        elif len(parsed_experience) >= 1:
            score += 5

        # Check for detailed descriptions
        has_detailed_descriptions = False
        has_achievements = False

        for entry in parsed_experience:
            description = entry.get('description', '')

            # Check description length
            if len(description.split()) >= 20:
                has_detailed_descriptions = True
                score += 5
                break

        # Check for achievement indicators in descriptions
        achievement_indicators = [
            'achieve', 'improve', 'increase', 'reduce', 'save', 'create', 'develop', 'implement',
            'lead', 'manage', 'coordinate', 'launch', 'design', 'mentor', 'win', 'award',
            'percent', '%', 'million', 'thousand', 'growth', 'revenue', 'cost', 'efficiency'
        ]

        for entry in parsed_experience:
            description = entry.get('description', '').lower()

            if any(indicator in description for indicator in achievement_indicators):
                has_achievements = True
                score += 10
                break

        # Check for job progression
        titles = [entry.get('title', '') for entry in parsed_experience]
        progression_indicators = ['senior', 'lead', 'manager', 'director', 'head', 'chief', 'principal']

        if any(indicator in ' '.join(titles).lower() for indicator in progression_indicators):
            score += 10

        # Deduct points for issues
        for entry in parsed_experience:
            if entry.get('title', '') == "Unknown Position" or entry.get('company', '') == "Unknown Company":
                score -= 5

        # Ensure score is within bounds
        return max(0, min(100, score))

    def _calculate_education_score(self, parsed_education):
        """
        Calculate a score for the education section.

        Args:
            parsed_education (list): Extracted education entries

        Returns:
            int: Score from 0-100
        """
        # Base score
        score = 50

        # No education entries is a problem
        if not parsed_education:
            return 30

        # Check degree level
        highest_degree_level = 0
        has_relevant_degree = False

        degree_levels = {
            'associate': 1,
            'bachelor': 2,
            'bs': 2, 'ba': 2, 'b.s': 2, 'b.a': 2,
            'master': 3,
            'ms': 3, 'ma': 3, 'm.s': 3, 'm.a': 3, 'mba': 3,
            'doctor': 4, 'phd': 4, 'ph.d': 4
        }

        relevant_fields = [
            'computer science', 'information technology', 'software engineering',
            'data science', 'cybersecurity', 'information systems', 'computer engineering',
            'electrical engineering', 'mathematics', 'statistics', 'physics',
            'business', 'finance', 'economics', 'management', 'marketing',
            'human resources', 'communication', 'psychology'
        ]

        for entry in parsed_education:
            degree = entry.get('degree', '').lower()

            # Check degree level
            for level_name, level_value in degree_levels.items():
                if level_name in degree:
                    highest_degree_level = max(highest_degree_level, level_value)

            # Check relevance
            for field in relevant_fields:
                if field in degree:
                    has_relevant_degree = True

        # Score based on highest degree
        if highest_degree_level >= 4:
            score += 25
        elif highest_degree_level >= 3:
            score += 20
        elif highest_degree_level >= 2:
            score += 15
        elif highest_degree_level >= 1:
            score += 10

        # Additional points for relevant degree
        if has_relevant_degree:
            score += 15

        # Points for prestigious institutions
        prestigious_keywords = [
            'harvard', 'stanford', 'mit', 'princeton', 'yale', 'columbia',
            'berkeley', 'oxford', 'cambridge', 'caltech', 'chicago', 'penn'
        ]

        for entry in parsed_education:
            institution = entry.get('institution', '').lower()

            if any(keyword in institution for keyword in prestigious_keywords):
                score += 10
                break

        # Ensure score is within bounds
        return max(0, min(100, score))

    def _generate_recommendations(self, validation, skill_score, experience_score, education_score, parsed_skills, parsed_experience, parsed_education):
        """
        Generate recommendations for resume improvement.

        Args:
            validation (dict): Resume validation results
            skill_score (int): Skill section score
            experience_score (int): Experience section score
            education_score (int): Education section score
            parsed_skills (dict): Parsed skills
            parsed_experience (list): Parsed work experience
            parsed_education (list): Parsed education

        Returns:
            list: Recommendations for improvement
        """
        recommendations = []

        # Add recommendations based on missing sections
        for missing in validation.get('missing_sections', []):
            recommendations.append(f"Add a {missing} section to your resume")

        # Skills recommendations
        technical_skills = parsed_skills.get('technical', [])
        soft_skills = parsed_skills.get('soft', [])

        if skill_score < 70:
            if len(technical_skills) < 5:
                recommendations.append("Add more technical skills to your resume")

            if len(soft_skills) < 3:
                recommendations.append("Include some soft skills that are relevant to your target role")

        # Experience recommendations
        if experience_score < 70:
            if not parsed_experience:
                recommendations.append("Add work experience to your resume")
            else:
                # Check for detailed descriptions
                has_short_descriptions = False
                has_missing_achievements = True

                for entry in parsed_experience:
                    description = entry.get('description', '')

                    # Check description length
                    if description and len(description.split()) < 20:
                        has_short_descriptions = True

                    # Check for achievement indicators
                    achievement_indicators = [
                        'achieve', 'improve', 'increase', 'reduce', 'save', 'create', 'develop', 'implement',
                        'lead', 'manage', 'coordinate', 'launch', 'design', 'percent', '%'
                    ]

                    if any(indicator in description.lower() for indicator in achievement_indicators):
                        has_missing_achievements = False

                if has_short_descriptions:
                    recommendations.append("Add more details to your work experience descriptions")

                if has_missing_achievements:
                    recommendations.append("Include specific achievements with measurable results in your work experience")

        # Education recommendations
        if education_score < 70 and parsed_education:
            for entry in parsed_education:
                if "not specified" in entry.get('degree', '') or "not specified" in entry.get('institution', ''):
                    recommendations.append("Complete your education section with degree and institution details")
                    break

        # Format and structure recommendations
        if validation.get('completeness', 0) < 80:
            recommendations.append("Improve the overall structure and completeness of your resume")

        # Ensure we don't have too many recommendations
        if len(recommendations) > 5:
            recommendations = recommendations[:5]

        # Add general recommendation if we don't have any specific ones
        if not recommendations:
            # Add more specific recommendations
            recommendations = [
                "Add more specific achievements with metrics in your experience section",
                "Include relevant certifications and professional development",
                "Highlight leadership experience and team collaboration skills",
                "Use strong action verbs to describe your responsibilities and achievements",
                "Tailor your resume to the specific job you're applying for"
            ]

        return recommendations