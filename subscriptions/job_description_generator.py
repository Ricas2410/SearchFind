"""
Job Description Generator System

This module implements the job description generation functionality using the core infrastructure
components (document parsing, text processing, content validation, and data resources).
It provides comprehensive job description generation with templates, customization options,
and optimization for effectiveness and inclusivity.
"""

import logging
import random
from collections import defaultdict
import re

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

class JobDescriptionGenerator:
    """
    Class for generating effective job descriptions using the core infrastructure.
    
    This class provides comprehensive job description generation functionality with
    templates, customization, and optimization for effectiveness and inclusivity.
    """
    
    def __init__(self):
        """Initialize the JobDescriptionGenerator with necessary components."""
        self.document_parser = DocumentParser()
        self.text_processor = TextProcessor()
        self.content_validator = ContentValidator(self.text_processor)
        
        # Load skills data
        self.all_skills = get_all_skills()
        self.technical_skills = get_technical_skills_by_category()
        self.soft_skills = get_soft_skills()
        self.job_titles = get_job_titles()
        self.education_data = get_education_data()
        
        # Job description templates by category
        self.templates = self._initialize_templates()
        
        # Inclusive language alternatives
        self.inclusive_alternatives = self._initialize_inclusive_alternatives()
        
        # Sections to include in a comprehensive job description
        self.sections = [
            'company_overview',
            'job_title',
            'job_summary',
            'responsibilities',
            'requirements',
            'preferred_qualifications',
            'benefits',
            'company_culture',
            'application_process',
            'equal_opportunity_statement'
        ]
    
    def generate_job_description(self, job_details):
        """
        Generate a professional job description based on provided details.
        
        Args:
            job_details (dict): Dictionary containing job details:
                - job_title (str): Title of the position
                - company_name (str): Name of the company
                - industry (str): Industry of the company
                - job_level (str): Level of the position (entry, mid, senior)
                - required_skills (list): List of required skills
                - preferred_skills (list): List of preferred skills
                - responsibilities (list, optional): List of job responsibilities
                - min_experience (int, optional): Minimum years of experience
                - education (str, optional): Required education level
                - location (str, optional): Job location
                - remote (bool, optional): Whether the job is remote
                - benefits (list, optional): List of benefits
                - company_description (str, optional): Brief company description
                - salary_range (dict, optional): Min and max salary
            
        Returns:
            dict: Generated job description and metadata
        """
        try:
            # Validate input
            if not job_details.get('job_title') or not job_details.get('company_name'):
                return {
                    'error': 'Job title and company name are required',
                    'is_valid': False
                }
            
            # Set defaults for optional fields
            job_details = self._set_defaults(job_details)
            
            # Determine job category and level
            job_category = job_details.get('job_category', self._infer_job_category(job_details))
            job_level = job_details.get('job_level', 'mid')
            
            # Select appropriate template
            template = self._select_template(job_category, job_level)
            
            # Generate each section
            sections = {}
            for section in self.sections:
                sections[section] = self._generate_section(section, job_details, template)
            
            # Assemble complete job description
            full_description = self._assemble_job_description(sections, job_details)
            
            # Optimize language for inclusivity
            optimized_description = self._optimize_language(full_description)
            
            # Prepare and return result
            return {
                'job_title': job_details['job_title'],
                'company_name': job_details['company_name'],
                'job_description': optimized_description,
                'sections': sections,
                'word_count': len(optimized_description.split()),
                'is_valid': True,
                'metadata': {
                    'job_category': job_category,
                    'job_level': job_level,
                    'skills_count': len(job_details['required_skills']) + len(job_details['preferred_skills']),
                    'has_salary_range': 'salary_range' in job_details and job_details['salary_range'] is not None,
                    'has_equal_opportunity': True  # We always include this
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating job description: {str(e)}")
            return {
                'error': f"Error generating job description: {str(e)}",
                'is_valid': False
            }
    
    def _set_defaults(self, job_details):
        """Set default values for optional job details."""
        defaults = {
            'industry': 'Technology',
            'job_level': 'mid',
            'required_skills': [],
            'preferred_skills': [],
            'responsibilities': [],
            'min_experience': 2,
            'education': 'Bachelor\'s degree',
            'location': 'Flexible',
            'remote': False,
            'benefits': ["Competitive salary", "Health insurance", "Retirement plan", "Paid time off"],
            'company_description': f"{job_details.get('company_name', 'Our company')} is a leading organization in the industry.",
            'salary_range': None
        }
        
        # Apply defaults for missing fields
        for key, value in defaults.items():
            if key not in job_details or job_details[key] is None:
                job_details[key] = value
        
        return job_details
    
    def _infer_job_category(self, job_details):
        """Infer the job category based on job title and skills."""
        job_title = job_details.get('job_title', '').lower()
        
        # Simple keyword matching for common categories
        if any(term in job_title for term in ['develop', 'program', 'code', 'software', 'engineer']):
            return 'software_development'
        elif any(term in job_title for term in ['data', 'analyst', 'scientist', 'analytics']):
            return 'data_science'
        elif any(term in job_title for term in ['design', 'ux', 'ui', 'user']):
            return 'design'
        elif any(term in job_title for term in ['market', 'content', 'brand', 'social media']):
            return 'marketing'
        elif any(term in job_title for term in ['sales', 'account', 'business development']):
            return 'sales'
        elif any(term in job_title for term in ['hr', 'human resources', 'talent', 'recruit']):
            return 'human_resources'
        elif any(term in job_title for term in ['product', 'project', 'manager', 'management']):
            return 'product_management'
        elif any(term in job_title for term in ['finance', 'account', 'financial']):
            return 'finance'
        elif any(term in job_title for term in ['support', 'customer', 'service']):
            return 'customer_service'
        elif any(term in job_title for term in ['operations', 'logistics']):
            return 'operations'
        else:
            return 'general'
    
    def _select_template(self, job_category, job_level):
        """Select an appropriate template based on job category and level."""
        # Try to get a specific template for the category and level
        if job_category in self.templates and job_level in self.templates[job_category]:
            return self.templates[job_category][job_level]
        
        # Fall back to general template for the level
        if 'general' in self.templates and job_level in self.templates['general']:
            return self.templates['general'][job_level]
        
        # Ultimate fallback to general mid-level template
        return self.templates['general']['mid']
    
    def _generate_section(self, section, job_details, template):
        """Generate content for a specific job description section."""
        # Select appropriate method based on section
        if section == 'company_overview':
            return self._generate_company_overview(job_details)
        elif section == 'job_title':
            return job_details['job_title']
        elif section == 'job_summary':
            return self._generate_job_summary(job_details, template)
        elif section == 'responsibilities':
            return self._generate_responsibilities(job_details, template)
        elif section == 'requirements':
            return self._generate_requirements(job_details, template)
        elif section == 'preferred_qualifications':
            return self._generate_preferred_qualifications(job_details, template)
        elif section == 'benefits':
            return self._generate_benefits(job_details, template)
        elif section == 'company_culture':
            return self._generate_company_culture(job_details)
        elif section == 'application_process':
            return self._generate_application_process(job_details)
        elif section == 'equal_opportunity_statement':
            return self._generate_equal_opportunity_statement(job_details)
        else:
            return ""
    
    def _generate_company_overview(self, job_details):
        """Generate the company overview section."""
        company_name = job_details.get('company_name', 'Our company')
        company_description = job_details.get('company_description', '')
        industry = job_details.get('industry', '')
        
        if company_description:
            return company_description
        
        # Generate a basic company description if none provided
        return f"{company_name} is a leading organization in the {industry} industry, committed to innovation and excellence. We pride ourselves on our dedicated team and our focus on delivering high-quality solutions to our clients."
    
    def _generate_job_summary(self, job_details, template):
        """Generate the job summary section."""
        job_title = job_details.get('job_title', '')
        company_name = job_details.get('company_name', '')
        industry = job_details.get('industry', '')
        job_level = job_details.get('job_level', 'mid')
        
        level_terms = {
            'entry': 'entry-level',
            'mid': 'experienced',
            'senior': 'senior-level',
            'leadership': 'leadership'
        }
        
        level_term = level_terms.get(job_level, 'experienced')
        
        # If template has a job summary, use it
        if 'job_summary' in template:
            summary = template['job_summary']
            summary = summary.replace('{{job_title}}', job_title)
            summary = summary.replace('{{company_name}}', company_name)
            summary = summary.replace('{{industry}}', industry)
            summary = summary.replace('{{level}}', level_term)
            return summary
        
        # Otherwise generate a basic summary
        return f"{company_name} is seeking a {level_term} {job_title} to join our team. The ideal candidate will have a passion for {industry} and a commitment to excellence in their work."
    
    def _generate_responsibilities(self, job_details, template):
        """Generate the responsibilities section."""
        job_title = job_details.get('job_title', '')
        responsibilities = job_details.get('responsibilities', [])
        
        # If responsibilities are provided, use them
        if responsibilities:
            if isinstance(responsibilities, list) and len(responsibilities) > 0:
                return responsibilities
            elif isinstance(responsibilities, str) and responsibilities.strip():
                # If a string, try to split into bullet points
                return responsibilities.strip().split('\n')
        
        # If template has responsibilities, use them
        if 'responsibilities' in template and template['responsibilities']:
            return template['responsibilities']
        
        # Otherwise generate generic responsibilities based on job title
        job_title_lower = job_title.lower()
        
        # Software development responsibilities
        if any(term in job_title_lower for term in ['develop', 'program', 'engineer', 'code']):
            return [
                "Design and develop high-quality software solutions",
                "Collaborate with cross-functional teams to define, design, and ship new features",
                "Write clean, maintainable code with comprehensive test coverage",
                "Troubleshoot, debug and upgrade existing systems",
                "Implement security and data protection measures"
            ]
        
        # Data science responsibilities
        elif any(term in job_title_lower for term in ['data', 'analyst', 'scientist']):
            return [
                "Analyze large datasets to extract actionable insights",
                "Build predictive models and machine learning algorithms",
                "Create data visualizations and reports for stakeholders",
                "Identify trends and opportunities for business growth",
                "Collaborate with teams to implement data-driven solutions"
            ]
        
        # Default responsibilities
        return [
            f"Contribute to the overall success of the {job_title} function",
            "Collaborate with team members to achieve objectives",
            "Implement best practices and maintain high standards of work",
            "Identify opportunities for improvement and innovation",
            "Report on progress and results to relevant stakeholders"
        ]
    
    def _generate_requirements(self, job_details, template):
        """Generate the requirements section."""
        job_title = job_details.get('job_title', '')
        required_skills = job_details.get('required_skills', [])
        min_experience = job_details.get('min_experience', 2)
        education = job_details.get('education', "Bachelor's degree")
        
        requirements = []
        
        # Add experience requirement
        if min_experience > 0:
            experience_text = f"{min_experience}+ years of experience in "
            if any(term in job_title.lower() for term in ['develop', 'program', 'engineer']):
                experience_text += "software development"
            elif 'data' in job_title.lower():
                experience_text += "data analysis or related field"
            elif 'design' in job_title.lower():
                experience_text += "design or related field"
            elif 'market' in job_title.lower():
                experience_text += "marketing or related field"
            else:
                experience_text += "a related field"
            
            requirements.append(experience_text)
        
        # Add education requirement
        if education:
            requirements.append(f"{education} in a relevant field")
        
        # Add required skills
        if required_skills and isinstance(required_skills, list):
            for skill in required_skills:
                if skill:
                    requirements.append(f"Proficiency with {skill}")
        
        # If template has requirements, append them
        if 'requirements' in template and template['requirements']:
            for req in template['requirements']:
                if req and req not in requirements:
                    requirements.append(req)
        
        # If we still don't have enough requirements, add generic ones
        if len(requirements) < 3:
            generic_requirements = [
                "Strong communication and teamwork skills",
                "Ability to work independently and manage priorities",
                "Problem-solving mindset and attention to detail"
            ]
            
            for req in generic_requirements:
                if req not in requirements:
                    requirements.append(req)
        
        return requirements
    
    def _generate_preferred_qualifications(self, job_details, template):
        """Generate the preferred qualifications section."""
        preferred_skills = job_details.get('preferred_skills', [])
        
        qualifications = []
        
        # Add preferred skills
        if preferred_skills and isinstance(preferred_skills, list):
            for skill in preferred_skills:
                if skill:
                    qualifications.append(f"Experience with {skill}")
        
        # If template has preferred qualifications, add them
        if 'preferred_qualifications' in template and template['preferred_qualifications']:
            for qual in template['preferred_qualifications']:
                if qual and qual not in qualifications:
                    qualifications.append(qual)
        
        # If we still need more, add generic ones
        if len(qualifications) < 2:
            generic_qualifications = [
                "Experience in a similar role or industry",
                "Advanced degree or specialized certification",
                "Experience with remote work or distributed teams"
            ]
            
            for qual in generic_qualifications:
                if qual not in qualifications:
                    qualifications.append(qual)
        
        return qualifications
    
    def _generate_benefits(self, job_details, template):
        """Generate the benefits section."""
        benefits = job_details.get('benefits', [])
        
        if benefits and isinstance(benefits, list) and len(benefits) > 0:
            return benefits
        
        # If template has benefits, use them
        if 'benefits' in template and template['benefits']:
            return template['benefits']
        
        # Otherwise use generic benefits
        return [
            "Competitive salary and performance bonuses",
            "Comprehensive health, dental, and vision insurance",
            "Retirement plan with employer matching",
            "Paid time off and holidays",
            "Professional development opportunities",
            "Supportive and inclusive work environment"
        ]
    
    def _generate_company_culture(self, job_details):
        """Generate the company culture section."""
        company_name = job_details.get('company_name', 'Our company')
        
        return f"At {company_name}, we value collaboration, innovation, and continuous learning. We're committed to creating a diverse, inclusive environment where all employees can thrive and grow professionally. Our team members are passionate about what they do and are dedicated to making a positive impact."
    
    def _generate_application_process(self, job_details):
        """Generate the application process section."""
        company_name = job_details.get('company_name', 'Our company')
        
        return f"To apply, please submit your resume and a brief cover letter explaining why you're interested in joining {company_name}. We review all applications carefully and will contact qualified candidates for an interview."
    
    def _generate_equal_opportunity_statement(self, job_details):
        """Generate the equal opportunity statement."""
        company_name = job_details.get('company_name', 'Our company')
        
        return f"{company_name} is an equal opportunity employer. We celebrate diversity and are committed to creating an inclusive environment for all employees. We do not discriminate on the basis of race, religion, color, national origin, gender, sexual orientation, age, marital status, veteran status, or disability status."
    
    def _assemble_job_description(self, sections, job_details):
        """Assemble the complete job description from sections."""
        job_title = job_details.get('job_title', '')
        company_name = job_details.get('company_name', '')
        location = job_details.get('location', '')
        remote = job_details.get('remote', False)
        salary_range = job_details.get('salary_range', None)
        
        # Build the job description
        description = f"# {job_title} at {company_name}\n\n"
        
        # Location
        location_text = location
        if remote:
            location_text += " (Remote)"
        description += f"**Location:** {location_text}\n\n"
        
        # Salary if provided
        if salary_range and isinstance(salary_range, dict) and 'min' in salary_range and 'max' in salary_range:
            description += f"**Salary Range:** ${salary_range['min']:,} - ${salary_range['max']:,}\n\n"
        
        # Company overview
        company_overview = sections.get('company_overview', '')
        if company_overview:
            description += f"## About {company_name}\n{company_overview}\n\n"
        
        # Job summary
        job_summary = sections.get('job_summary', '')
        if job_summary:
            description += "## Position Overview\n" + job_summary + "\n\n"
        
        # Responsibilities
        responsibilities = sections.get('responsibilities', [])
        if responsibilities:
            description += "## Key Responsibilities\n"
            for resp in responsibilities:
                description += f"- {resp}\n"
            description += "\n"
        
        # Requirements
        requirements = sections.get('requirements', [])
        if requirements:
            description += "## Requirements\n"
            for req in requirements:
                description += f"- {req}\n"
            description += "\n"
        
        # Preferred qualifications
        preferred = sections.get('preferred_qualifications', [])
        if preferred:
            description += "## Preferred Qualifications\n"
            for qual in preferred:
                description += f"- {qual}\n"
            description += "\n"
        
        # Benefits
        benefits = sections.get('benefits', [])
        if benefits:
            description += "## Benefits & Perks\n"
            for benefit in benefits:
                description += f"- {benefit}\n"
            description += "\n"
        
        # Company culture
        culture = sections.get('company_culture', '')
        if culture:
            description += f"## Our Culture\n{culture}\n\n"
        
        # Application process
        process = sections.get('application_process', '')
        if process:
            description += f"## How to Apply\n{process}\n\n"
        
        # Equal opportunity statement
        eoe = sections.get('equal_opportunity_statement', '')
        if eoe:
            description += f"---\n\n{eoe}\n"
        
        return description
    
    def _optimize_language(self, job_description):
        """Optimize job description language for inclusivity and effectiveness."""
        optimized = job_description
        
        # Replace non-inclusive terms with inclusive alternatives
        for term, alternatives in self.inclusive_alternatives.items():
            pattern = r'\b' + re.escape(term) + r'\b'
            replacement = random.choice(alternatives)
            optimized = re.sub(pattern, replacement, optimized, flags=re.IGNORECASE)
        
        return optimized
    
    def analyze_and_improve_description(self, job_description_text):
        """
        Analyze a job description and provide improvement suggestions.
        
        Args:
            job_description_text (str): The job description text
            
        Returns:
            dict: Analysis results and improvement suggestions
        """
        try:
            # Validate input
            if not job_description_text:
                return {
                    'error': 'Job description text is required',
                    'is_valid': False
                }
            
            # Process the text
            processed_text = self.text_processor.process_document(job_description_text, 'job_description')
            
            # Extract job title and company if available
            job_title = processed_text.get('extracted_job_title', '')
            company_name = processed_text.get('extracted_company', '')
            
            # Extract skills, responsibilities, requirements
            skills = processed_text.get('extracted_skills', [])
            
            # Sections analysis
            sections_present = self._identify_sections(job_description_text)
            sections_missing = [section for section in self.sections if section not in sections_present]
            
            # Analyze inclusivity
            inclusivity_issues = self._check_inclusivity(job_description_text)
            
            # Generate improvement suggestions
            suggestions = self._generate_improvement_suggestions(
                job_description_text, 
                sections_present, 
                sections_missing,
                skills,
                inclusivity_issues
            )
            
            # Prepare and return result
            return {
                'is_valid': True,
                'job_title': job_title,
                'company_name': company_name,
                'sections_analysis': {
                    'sections_present': sections_present,
                    'sections_missing': sections_missing,
                    'completeness_score': (len(sections_present) / len(self.sections)) * 100
                },
                'skills_identified': skills,
                'inclusivity_analysis': {
                    'inclusivity_issues': inclusivity_issues,
                    'inclusivity_score': 100 - (len(inclusivity_issues) * 5)
                },
                'word_count': len(job_description_text.split()),
                'improvement_suggestions': suggestions,
                'improved_description': self._create_improved_description(
                    job_description_text,
                    job_title,
                    company_name,
                    sections_missing,
                    inclusivity_issues
                )
            }
            
        except Exception as e:
            logger.error(f"Error analyzing job description: {str(e)}")
            return {
                'error': f"Error analyzing job description: {str(e)}",
                'is_valid': False
            }
    
    def _identify_sections(self, job_description_text):
        """Identify which sections are present in the job description."""
        sections_present = []
        
        # Look for company information
        if re.search(r'about (?:us|the company|our company)', job_description_text, re.IGNORECASE) or \
           re.search(r'company overview', job_description_text, re.IGNORECASE):
            sections_present.append('company_overview')
        
        # Look for job title
        if re.search(r'^#\s+.*?\s+at\s+.*?$', job_description_text, re.MULTILINE) or \
           re.search(r'^.*?\s+Position', job_description_text, re.MULTILINE):
            sections_present.append('job_title')
        
        # Look for job summary
        if re.search(r'position overview|summary|about the role', job_description_text, re.IGNORECASE):
            sections_present.append('job_summary')
        
        # Look for responsibilities
        if re.search(r'responsibilities|duties|what you.ll do|key tasks', job_description_text, re.IGNORECASE):
            sections_present.append('responsibilities')
        
        # Look for requirements
        if re.search(r'requirements|qualifications|what you need|must have', job_description_text, re.IGNORECASE):
            sections_present.append('requirements')
        
        # Look for preferred qualifications
        if re.search(r'preferred|nice to have|desirable|plus|bonus', job_description_text, re.IGNORECASE):
            sections_present.append('preferred_qualifications')
        
        # Look for benefits
        if re.search(r'benefits|perks|what we offer|compensation', job_description_text, re.IGNORECASE):
            sections_present.append('benefits')
        
        # Look for company culture
        if re.search(r'culture|values|our team|working at', job_description_text, re.IGNORECASE):
            sections_present.append('company_culture')
        
        # Look for application process
        if re.search(r'how to apply|application|apply|next steps', job_description_text, re.IGNORECASE):
            sections_present.append('application_process')
        
        # Look for equal opportunity statement
        if re.search(r'equal opportunity|eeo|diversity|inclusion', job_description_text, re.IGNORECASE):
            sections_present.append('equal_opportunity_statement')
        
        return sections_present
    
    def _check_inclusivity(self, job_description_text):
        """Check for inclusive language issues in the job description."""
        issues = []
        
        # Check for gender-coded language
        masculine_terms = [
            'aggressive', 'ambitious', 'assertive', 'competitive', 'confident', 'decisive',
            'determined', 'dominant', 'fearless', 'independent', 'strong', 'outspoken',
            'ninja', 'rockstar', 'guru', 'superhero', 'he', 'his', 'him'
        ]
        
        for term in masculine_terms:
            pattern = r'\b' + re.escape(term) + r'\b'
            if re.search(pattern, job_description_text, re.IGNORECASE):
                issues.append(f'Gender-coded term: "{term}"')
        
        # Check for ableist language
        ableist_terms = [
            'blind to', 'crippled', 'crippling', 'deaf to', 'dumb', 'insane', 'crazy',
            'psycho', 'lunatic', 'lame', 'handicapped', 'special needs'
        ]
        
        for term in ableist_terms:
            pattern = r'\b' + re.escape(term) + r'\b'
            if re.search(pattern, job_description_text, re.IGNORECASE):
                issues.append(f'Ableist term: "{term}"')
        
        # Check for age-related language
        age_terms = [
            'young', 'energetic', 'fresh', 'recent graduate', 'digital native',
            'youthful', 'vibrant', 'junior', 'mature'
        ]
        
        for term in age_terms:
            pattern = r'\b' + re.escape(term) + r'\b'
            if re.search(pattern, job_description_text, re.IGNORECASE):
                issues.append(f'Age-related term: "{term}"')
        
        # Check for unnecessary superlatives which can discourage applicants
        superlative_terms = [
            'best of the best', 'world-class', 'exceptional', 'superior', 'unparalleled',
            'outstanding', 'expert', 'extensive experience', 'perfection', 'flawless'
        ]
        
        for term in superlative_terms:
            pattern = r'\b' + re.escape(term) + r'\b'
            if re.search(pattern, job_description_text, re.IGNORECASE):
                issues.append(f'Potentially intimidating superlative: "{term}"')
        
        return issues
    
    def _generate_improvement_suggestions(self, job_description_text, sections_present, sections_missing, skills, inclusivity_issues):
        """Generate suggestions for improving the job description."""
        suggestions = []
        
        # Section improvement suggestions
        if len(sections_missing) > 0:
            missing_sections = ', '.join([s.replace('_', ' ').title() for s in sections_missing[:3]])
            if len(sections_missing) > 3:
                missing_sections += f", and {len(sections_missing) - 3} more"
            suggestions.append(f"Add missing sections: {missing_sections}")
        
        # Skills suggestions
        if len(skills) < 5:
            suggestions.append("Add more specific skills to attract qualified candidates")
        
        # Length suggestions
        word_count = len(job_description_text.split())
        if word_count < 300:
            suggestions.append("Expand the job description to provide more details (aim for 300-800 words)")
        elif word_count > 1000:
            suggestions.append("Consider shortening the job description for better readability (aim for 300-800 words)")
        
        # Inclusivity suggestions
        if inclusivity_issues:
            for issue in inclusivity_issues[:3]:
                suggestions.append(f"Replace {issue}")
            
            if len(inclusivity_issues) > 3:
                suggestions.append(f"Address {len(inclusivity_issues) - 3} additional inclusivity issues")
        
        # Add equal opportunity statement if missing
        if 'equal_opportunity_statement' not in sections_present:
            suggestions.append("Add an Equal Opportunity Employer statement to promote diversity and inclusion")
        
        # Check for salary information
        if not re.search(r'salary|compensation|pay|wage', job_description_text, re.IGNORECASE):
            suggestions.append("Consider adding salary information to attract more candidates")
        
        # Check for bullet points in responsibilities and requirements
        if 'responsibilities' in sections_present and not re.search(r'[-•*]', job_description_text):
            suggestions.append("Format responsibilities as bullet points for improved readability")
        
        # Check for application instructions clarity
        if 'application_process' in sections_present:
            application_section = re.search(r'(?:how to apply|application).*?(?:\n\n|\Z)', job_description_text, re.IGNORECASE | re.DOTALL)
            if application_section and len(application_section.group(0).split()) < 20:
                suggestions.append("Provide more detailed application instructions")
        
        return suggestions
    
    def _create_improved_description(self, original_text, job_title, company_name, sections_missing, inclusivity_issues):
        """Create an improved version of the job description."""
        improved = original_text
        
        # Fix inclusivity issues
        for issue in inclusivity_issues:
            term = re.search(r'"([^"]+)"', issue)
            if term:
                term = term.group(1)
                if "Gender-coded" in issue and term in self.inclusive_alternatives:
                    pattern = r'\b' + re.escape(term) + r'\b'
                    replacement = random.choice(self.inclusive_alternatives[term])
                    improved = re.sub(pattern, replacement, improved, flags=re.IGNORECASE)
        
        # Add missing sections if significant ones are missing
        if 'equal_opportunity_statement' in sections_missing:
            eoe = self._generate_equal_opportunity_statement({'company_name': company_name if company_name else 'Our company'})
            improved += f"\n\n---\n\n{eoe}"
        
        return improved
    
    def _initialize_templates(self):
        """Initialize job description templates by category and level."""
        templates = defaultdict(dict)
        
        # Software Development Templates
        templates['software_development']['entry'] = {
            'job_summary': "{{company_name}} is looking for an entry-level {{job_title}} to join our development team. The ideal candidate will have a strong foundation in software development principles and a willingness to learn. This position offers excellent opportunities for professional growth and hands-on experience with modern technologies.",
            'responsibilities': [
                "Write clean, maintainable code according to specifications",
                "Test and debug applications to ensure functionality and performance",
                "Collaborate with senior developers to understand requirements and implementation details",
                "Participate in code reviews to improve code quality and learn best practices",
                "Assist in troubleshooting and fixing bugs in existing systems",
                "Document code and development processes"
            ],
            'requirements': [
                "Bachelor's degree in Computer Science, Software Engineering, or related field",
                "Basic understanding of software development principles",
                "Familiarity with at least one programming language",
                "Willingness to learn new technologies and methodologies",
                "Good problem-solving skills and attention to detail"
            ],
            'preferred_qualifications': [
                "Experience with web development technologies (HTML, CSS, JavaScript)",
                "Familiarity with version control systems (Git)",
                "Knowledge of software development lifecycle",
                "Previous internship or project experience"
            ],
            'benefits': [
                "Competitive salary for entry-level positions",
                "Health, dental, and vision insurance",
                "Paid time off and holidays",
                "Mentorship program for professional development",
                "Training and certification opportunities",
                "Casual and collaborative work environment"
            ]
        }
        
        templates['software_development']['mid'] = {
            'job_summary': "{{company_name}} is seeking an experienced {{job_title}} to design, develop, and maintain high-quality software solutions. The ideal candidate will have a solid background in software development, experience with our technology stack, and a passion for creating efficient, scalable applications.",
            'responsibilities': [
                "Design and develop high-quality software solutions",
                "Write clean, maintainable, and efficient code",
                "Troubleshoot, debug, and upgrade existing systems",
                "Collaborate with cross-functional teams to define, design, and ship new features",
                "Implement security and data protection measures",
                "Write technical documentation and specifications",
                "Participate in code reviews and provide constructive feedback"
            ],
            'requirements': [
                "Bachelor's degree in Computer Science, Software Engineering, or related field",
                "3+ years of professional software development experience",
                "Strong proficiency in one or more programming languages",
                "Experience with web application development",
                "Solid understanding of software design principles and patterns",
                "Experience with databases and API design",
                "Familiarity with version control systems (Git)"
            ],
            'preferred_qualifications': [
                "Experience with cloud platforms (AWS, Azure, GCP)",
                "Knowledge of DevOps practices and CI/CD pipelines",
                "Experience with microservices architecture",
                "Understanding of containerization technologies (Docker, Kubernetes)",
                "Experience with agile development methodologies"
            ],
            'benefits': [
                "Competitive salary and performance bonuses",
                "Comprehensive health, dental, and vision insurance",
                "Retirement plan with employer matching",
                "Flexible work arrangements",
                "Professional development budget",
                "Regular team events and activities",
                "Casual and collaborative work environment"
            ]
        }
        
        templates['software_development']['senior'] = {
            'job_summary': "{{company_name}} is looking for a Senior {{job_title}} to lead development efforts and drive technical excellence. The ideal candidate will have extensive experience in software development, strong technical leadership skills, and the ability to mentor junior team members while contributing to architectural decisions and coding standards.",
            'responsibilities': [
                "Design and implement complex software systems",
                "Make significant contributions to architectural decisions and technical direction",
                "Lead development efforts and provide technical guidance to team members",
                "Mentor junior developers and conduct knowledge-sharing sessions",
                "Collaborate with product managers to define requirements and specifications",
                "Review code, debug complex issues, and ensure code quality",
                "Evaluate and recommend new technologies and methodologies",
                "Lead technical discussions and contribute to strategic planning"
            ],
            'requirements': [
                "Bachelor's degree in Computer Science, Software Engineering, or related field (Master's preferred)",
                "7+ years of professional software development experience",
                "Expert knowledge in one or more programming languages",
                "Experience designing and implementing large-scale applications",
                "Strong understanding of software architecture patterns and best practices",
                "Experience with performance optimization and scalability",
                "Proven ability to lead technical initiatives and mentor junior developers",
                "Strong problem-solving and analytical skills"
            ],
            'preferred_qualifications': [
                "Experience with distributed systems and microservices architecture",
                "Knowledge of cloud computing and serverless architectures",
                "Experience with DevOps practices and infrastructure automation",
                "Understanding of security best practices and implementation",
                "Experience with agile development and SCRUM methodologies",
                "Open source contributions or technical publications"
            ],
            'benefits': [
                "Highly competitive salary and performance bonuses",
                "Comprehensive benefits package including health, dental, and vision",
                "Retirement plan with generous employer matching",
                "Flexible work arrangements including partial remote options",
                "Substantial professional development budget",
                "Conference attendance opportunities",
                "Stock options or equity grants",
                "Leadership development programs"
            ]
        }
        
        # Data Science Templates
        templates['data_science']['mid'] = {
            'job_summary': "{{company_name}} is seeking a talented {{job_title}} to join our data team. The ideal candidate will have experience working with large datasets, building predictive models, and extracting actionable insights to drive business decisions. This role offers the opportunity to work on challenging problems and make a significant impact.",
            'responsibilities': [
                "Analyze complex datasets to identify patterns and extract insights",
                "Build and deploy machine learning models to solve business problems",
                "Collaborate with cross-functional teams to understand data needs and requirements",
                "Create data visualizations and reports to communicate findings",
                "Develop and maintain data pipelines for efficient data processing",
                "Monitor model performance and implement improvements",
                "Stay current with latest developments in data science and machine learning"
            ],
            'requirements': [
                "Bachelor's or Master's degree in Statistics, Mathematics, Computer Science, or related field",
                "3+ years of experience in data science or related role",
                "Proficiency in Python or R for data analysis and modeling",
                "Experience with SQL and database systems",
                "Strong understanding of statistical methods and machine learning algorithms",
                "Experience with data visualization tools and techniques",
                "Ability to communicate complex findings to non-technical stakeholders"
            ],
            'preferred_qualifications': [
                "Experience with big data technologies (Hadoop, Spark)",
                "Knowledge of deep learning frameworks (TensorFlow, PyTorch)",
                "Experience with cloud platforms (AWS, Azure, GCP)",
                "Background in the {{industry}} industry",
                "Advanced degree (PhD) in a quantitative field"
            ],
            'benefits': [
                "Competitive salary and performance bonuses",
                "Comprehensive health, dental, and vision insurance",
                "Retirement plan with employer matching",
                "Flexible work arrangements",
                "Professional development budget for courses and conferences",
                "Regular team events and activities",
                "Collaborative and innovation-focused work environment"
            ]
        }
        
        # Marketing Templates
        templates['marketing']['mid'] = {
            'job_summary': "{{company_name}} is looking for a creative and results-driven {{job_title}} to join our marketing team. The ideal candidate will have experience developing and implementing marketing strategies that increase brand awareness, engage customers, and drive growth. This role offers the opportunity to work on diverse campaigns and make a significant impact on our marketing efforts.",
            'responsibilities': [
                "Develop and implement marketing strategies aligned with business objectives",
                "Create compelling content for various channels (social media, website, email)",
                "Manage and optimize digital marketing campaigns",
                "Monitor campaign performance and provide regular reports",
                "Collaborate with design team to create marketing materials",
                "Stay updated on market trends and competitor activities",
                "Contribute to brand development and positioning"
            ],
            'requirements': [
                "Bachelor's degree in Marketing, Communications, or related field",
                "3+ years of experience in marketing or related role",
                "Strong understanding of digital marketing channels and tactics",
                "Experience with marketing analytics and campaign measurement",
                "Excellent written and verbal communication skills",
                "Proven ability to manage multiple projects simultaneously",
                "Creative problem-solving skills"
            ],
            'preferred_qualifications': [
                "Experience with marketing automation tools",
                "Knowledge of SEO/SEM principles",
                "Graphic design skills and experience with design software",
                "Content management system experience",
                "Background in the {{industry}} industry"
            ],
            'benefits': [
                "Competitive salary and performance bonuses",
                "Comprehensive health, dental, and vision insurance",
                "Retirement plan with employer matching",
                "Flexible work arrangements",
                "Professional development opportunities",
                "Creative and collaborative work environment",
                "Regular team events and activities"
            ]
        }
        
        # Design Templates
        templates['design']['mid'] = {
            'job_summary': "{{company_name}} is seeking a talented {{job_title}} to create visually stunning and user-centered designs. The ideal candidate will have a strong portfolio demonstrating creativity, attention to detail, and the ability to translate business requirements into effective design solutions. This role offers the opportunity to work on diverse projects and shape the visual identity of our products.",
            'responsibilities': [
                "Create user-centered designs for digital products and interfaces",
                "Develop visual design systems and style guides",
                "Collaborate with product and engineering teams to implement designs",
                "Create wireframes, prototypes, and user flows",
                "Conduct user research and incorporate feedback into designs",
                "Stay current with design trends and best practices",
                "Participate in design reviews and provide constructive feedback"
            ],
            'requirements': [
                "Bachelor's degree in Design, Fine Arts, or related field",
                "3+ years of professional design experience",
                "Strong portfolio demonstrating design capabilities",
                "Proficiency with design tools (Figma, Adobe Creative Suite)",
                "Understanding of user-centered design principles",
                "Experience designing for web and mobile platforms",
                "Strong visual design skills including typography, color theory, and layout"
            ],
            'preferred_qualifications': [
                "Experience with design systems",
                "Knowledge of HTML, CSS, and front-end development",
                "Experience with user testing and research methodologies",
                "Animation or motion design experience",
                "Background in the {{industry}} industry"
            ],
            'benefits': [
                "Competitive salary and performance bonuses",
                "Comprehensive health, dental, and vision insurance",
                "Retirement plan with employer matching",
                "Flexible work arrangements",
                "Creative work environment with the latest design tools",
                "Professional development budget for courses and conferences",
                "Regular creative workshops and design challenges"
            ]
        }
        
        # General Templates
        templates['general']['entry'] = {
            'job_summary': "{{company_name}} is seeking an entry-level {{job_title}} to join our team. This is an excellent opportunity for someone starting their career in {{industry}} to gain valuable experience and develop professional skills. The ideal candidate is eager to learn, has a positive attitude, and is committed to professional growth.",
            'responsibilities': [
                "Assist team members with day-to-day activities",
                "Learn and apply industry knowledge and best practices",
                "Contribute to team projects under guidance from experienced staff",
                "Help maintain departmental documentation and records",
                "Attend training sessions and apply new skills",
                "Communicate effectively with team members and stakeholders"
            ],
            'requirements': [
                "Bachelor's degree in a relevant field",
                "Strong communication and interpersonal skills",
                "Eagerness to learn and grow professionally",
                "Basic knowledge of {{industry}} concepts",
                "Ability to work effectively in a team environment",
                "Attention to detail and organizational skills"
            ],
            'preferred_qualifications': [
                "Internship experience in {{industry}}",
                "Familiarity with industry-specific tools or software",
                "Relevant coursework or certifications",
                "Problem-solving skills and analytical thinking"
            ],
            'benefits': [
                "Competitive salary for entry-level positions",
                "Health, dental, and vision insurance",
                "Paid time off and holidays",
                "Mentorship program for professional development",
                "Training and learning opportunities",
                "Collaborative work environment"
            ]
        }
        
        templates['general']['mid'] = {
            'job_summary': "{{company_name}} is looking for an experienced {{job_title}} to join our team. The ideal candidate will have proven experience in {{industry}}, strong problem-solving skills, and the ability to contribute to our continued success. This role offers the opportunity to work on meaningful projects and further develop your professional expertise.",
            'responsibilities': [
                "Perform core duties related to the {{job_title}} role",
                "Collaborate with team members on projects and initiatives",
                "Identify and implement process improvements",
                "Prepare reports and analyses as needed",
                "Maintain professional relationships with stakeholders",
                "Stay current with industry trends and best practices"
            ],
            'requirements': [
                "Bachelor's degree in a relevant field",
                "3+ years of experience in a similar role",
                "Strong knowledge of {{industry}} principles and practices",
                "Excellent communication and interpersonal skills",
                "Ability to manage multiple priorities effectively",
                "Problem-solving skills and attention to detail"
            ],
            'preferred_qualifications': [
                "Advanced degree or certification in relevant area",
                "Experience with industry-specific tools and technologies",
                "Project management experience",
                "Background in the {{industry}} industry"
            ],
            'benefits': [
                "Competitive salary and performance bonuses",
                "Comprehensive health, dental, and vision insurance",
                "Retirement plan with employer matching",
                "Paid time off and holidays",
                "Professional development opportunities",
                "Collaborative work environment",
                "Work-life balance"
            ]
        }
        
        templates['general']['senior'] = {
            'job_summary': "{{company_name}} is seeking a Senior {{job_title}} to provide leadership and expertise to our team. The ideal candidate will have extensive experience in {{industry}}, strong leadership skills, and the ability to drive strategic initiatives. This role offers the opportunity to make a significant impact on our organization and mentor team members.",
            'responsibilities': [
                "Lead projects and initiatives within your area of expertise",
                "Provide guidance and mentorship to junior team members",
                "Develop and implement strategies aligned with business objectives",
                "Identify opportunities for improvement and innovation",
                "Collaborate with leadership on departmental planning",
                "Represent the department in cross-functional meetings",
                "Stay current with industry trends and best practices"
            ],
            'requirements': [
                "Bachelor's degree in a relevant field (Master's preferred)",
                "7+ years of experience in {{industry}} with at least 3 years in a leadership role",
                "Expert knowledge of {{industry}} principles and practices",
                "Strong leadership and mentoring skills",
                "Excellent communication and presentation abilities",
                "Strategic thinking and problem-solving capabilities",
                "Experience managing complex projects and initiatives"
            ],
            'preferred_qualifications': [
                "Advanced degree or specialized certification",
                "Experience in the specific sector of our business",
                "History of implementing successful process improvements",
                "Budget management experience",
                "Published articles or speaking engagements in the field"
            ],
            'benefits': [
                "Highly competitive salary and performance bonuses",
                "Comprehensive benefits package",
                "Retirement plan with generous employer matching",
                "Flexible work arrangements",
                "Professional development budget",
                "Leadership development opportunities",
                "Recognition programs for exceptional performance"
            ]
        }
        
        return templates
    
    def _initialize_inclusive_alternatives(self):
        """Initialize dictionary of inclusive language alternatives."""
        inclusive_alternatives = {
            # Gender-coded terms alternatives
            'aggressive': ['proactive', 'determined', 'driven', 'bold'],
            'ambitious': ['motivated', 'goal-oriented', 'growth-minded', 'aspiring'],
            'assertive': ['confident', 'self-assured', 'direct', 'forthright'],
            'competitive': ['achievement-oriented', 'results-driven', 'excellence-focused'],
            'confident': ['self-assured', 'poised', 'composed', 'assured'],
            'decisive': ['determined', 'resolute', 'clear-thinking', 'firm'],
            'determined': ['persistent', 'resolute', 'steadfast', 'dedicated'],
            'dominant': ['influential', 'impactful', 'key', 'leading'],
            'fearless': ['courageous', 'brave', 'bold', 'undaunted'],
            'independent': ['self-reliant', 'autonomous', 'self-directed', 'self-sufficient'],
            'strong': ['capable', 'effective', 'proficient', 'skilled'],
            'outspoken': ['candid', 'frank', 'direct', 'straightforward'],
            'ninja': ['expert', 'specialist', 'professional', 'skilled professional'],
            'rockstar': ['high performer', 'talented professional', 'exceptional team member'],
            'guru': ['expert', 'specialist', 'authority', 'professional'],
            'superhero': ['high performer', 'achiever', 'outstanding contributor'],
            
            # Ableist language alternatives
            'blind to': ['unaware of', 'inattentive to', 'regardless of'],
            'crippled': ['hindered', 'impeded', 'limited'],
            'crippling': ['limiting', 'restricting', 'hindering', 'challenging'],
            'deaf to': ['unresponsive to', 'inattentive to', 'dismissive of'],
            'dumb': ['unclear', 'confusing', 'uninformed', 'unnecessary'],
            'insane': ['extraordinary', 'remarkable', 'exceptional', 'unusual'],
            'crazy': ['remarkable', 'intense', 'exceptional', 'surprising'],
            'psycho': ['intense', 'excessive', 'extreme'],
            'lunatic': ['excessive', 'unreasonable', 'extreme'],
            'lame': ['disappointing', 'inadequate', 'unsatisfactory'],
            'handicapped': ['challenged', 'limited', 'restricted'],
            'special needs': ['additional needs', 'specific requirements', 'accommodations'],
            
            # Age-related alternatives
            'young': ['early-career', 'emerging', 'developing', 'fresh perspective'],
            'energetic': ['motivated', 'enthusiastic', 'dynamic', 'passionate'],
            'fresh': ['innovative', 'new perspective', 'contemporary viewpoint'],
            'recent graduate': ['early-career professional', 'entry-level candidate'],
            'digital native': ['digitally proficient', 'technology-oriented', 'digitally skilled'],
            'youthful': ['dynamic', 'adaptable', 'innovative', 'contemporary'],
            'vibrant': ['dynamic', 'enthusiastic', 'engaged', 'spirited'],
            'junior': ['early-career', 'developing', 'entry-level'],
            'mature': ['experienced', 'seasoned', 'established', 'knowledgeable'],
            
            # Superlatives alternatives
            'best of the best': ['highly skilled', 'accomplished', 'talented'],
            'world-class': ['excellent', 'high-quality', 'outstanding', 'top-tier'],
            'exceptional': ['excellent', 'high-quality', 'outstanding', 'skilled'],
            'superior': ['excellent', 'high-quality', 'advanced', 'leading'],
            'unparalleled': ['distinctive', 'unique', 'remarkable', 'notable'],
            'outstanding': ['excellent', 'skilled', 'accomplished', 'notable'],
            'expert': ['experienced', 'knowledgeable', 'skilled', 'proficient'],
            'extensive experience': ['relevant experience', 'demonstrated experience', 'solid experience'],
            'perfection': ['excellence', 'high standards', 'quality'],
            'flawless': ['high-quality', 'careful', 'precise', 'accurate']
        }
        
        return inclusive_alternatives