import json
from .ai_services import AIService

class JobPostingService:
    """Service for improving job postings."""
    
    @classmethod
    def analyze_job_posting(cls, job_listing):
        """
        Analyze a job posting and provide improvement suggestions.
        
        Args:
            job_listing: The job listing to analyze
            
        Returns:
            Dictionary containing analysis and improvement suggestions
        """
        # In a real implementation, we would send this to an AI service
        # For now, we'll use our simulated AI response
        
        prompt = f"Analyze job posting: {job_listing.title} - {job_listing.description}"
        
        # Get simulated AI response
        response = AIService.get_ai_response(prompt)
        
        try:
            # Parse the JSON response
            suggestions = json.loads(response)
            return suggestions
        except json.JSONDecodeError:
            # Return basic suggestions if there's an error
            return {
                "title_suggestions": [
                    "Make your job title more specific and searchable"
                ],
                "description_improvements": [
                    "Add more details about the role and responsibilities"
                ],
                "requirements_optimization": [
                    "Separate must-have from nice-to-have requirements"
                ]
            }
    
    @classmethod
    def generate_job_description(cls, company, job_title, responsibilities, requirements):
        """
        Generate a complete job description based on input parameters.
        
        Args:
            company: The company information
            job_title: The title of the job
            responsibilities: Key responsibilities for the role
            requirements: Key requirements for the role
            
        Returns:
            Dictionary containing the generated job description
        """
        # In a real implementation, we would send this to an AI service
        # For now, we'll use our simulated AI response
        
        prompt = f"Generate job description for: {job_title} at {company.name}"
        
        # Get simulated AI response
        response = AIService.get_ai_response(prompt)
        
        try:
            # Parse the JSON response
            job_posting_data = json.loads(response)
            
            # Get the template and customize it
            template = job_posting_data.get('sample_job_description_template', '')
            
            # Replace placeholders with actual content
            job_description = template.replace('[Job Title]', job_title)
            job_description = job_description.replace('[Company Name]', company.name)
            
            # Add company description
            company_description = company.description[:200] + '...' if len(company.description) > 200 else company.description
            job_description = job_description.replace('[2-3 sentences about your company, mission, and what makes it special]', company_description)
            
            # Add responsibilities
            resp_list = responsibilities.split('\n')
            resp_bullets = ''
            for i, resp in enumerate(resp_list[:5]):
                if resp.strip():
                    resp_bullets += f"• {resp.strip()}\n"
            
            job_description = job_description.replace('• [Specific responsibility with impact]\n• [Specific responsibility with impact]\n• [Specific responsibility with impact]\n• [Specific responsibility with impact]\n• [Specific responsibility with impact]', resp_bullets)
            
            # Add requirements
            req_list = requirements.split('\n')
            req_bullets = ''
            for i, req in enumerate(req_list[:6]):
                if req.strip():
                    req_bullets += f"• {req.strip()}\n"
            
            job_description = job_description.replace('• [Must-have skill/qualification]\n• [Must-have skill/qualification]\n• [Must-have skill/qualification]\n• [Must-have skill/qualification]\n• [Nice-to-have skill/qualification]\n• [Nice-to-have skill/qualification]', req_bullets)
            
            return {
                "job_description": job_description,
                "improvement_suggestions": job_posting_data.get('description_improvements', []),
                "seo_tips": [
                    "Include relevant keywords in the job title and description",
                    "Use industry-standard job titles",
                    "Mention key technologies and skills prominently",
                    "Include location information for better local search visibility"
                ]
            }
        except (json.JSONDecodeError, AttributeError):
            # Return a basic job description if there's an error
            return {
                "job_description": f"# {job_title} at {company.name}\n\n## About Us\n{company.description[:200]}...\n\n## Responsibilities\n{responsibilities}\n\n## Requirements\n{requirements}",
                "improvement_suggestions": [
                    "Add more details about the role",
                    "Include information about the team",
                    "Mention benefits and perks"
                ]
            }
    
    @classmethod
    def optimize_job_requirements(cls, requirements_text):
        """
        Optimize job requirements to be more inclusive and effective.
        
        Args:
            requirements_text: The current requirements text
            
        Returns:
            Dictionary containing optimized requirements and suggestions
        """
        # In a real implementation, we would send this to an AI service
        # For now, we'll return a simulated optimization
        
        # Basic analysis
        lines = [line.strip() for line in requirements_text.split('\n') if line.strip()]
        
        # Check for potential issues
        has_years_experience = any('years' in line.lower() and 'experience' in line.lower() for line in lines)
        has_degree_requirement = any('degree' in line.lower() or 'bachelor' in line.lower() or 'master' in line.lower() for line in lines)
        has_too_many_requirements = len(lines) > 10
        
        # Generate suggestions
        suggestions = []
        
        if has_years_experience:
            suggestions.append("Consider focusing on skills and capabilities rather than years of experience")
        
        if has_degree_requirement:
            suggestions.append("Consider adding 'or equivalent experience' to degree requirements to be more inclusive")
        
        if has_too_many_requirements:
            suggestions.append("Consider reducing the number of requirements to focus on the most essential ones")
        
        suggestions.extend([
            "Separate 'must-have' from 'nice-to-have' requirements",
            "Use inclusive language that doesn't discourage diverse candidates",
            "Focus on what the candidate will do rather than what they need to have"
        ])
        
        # Categorize requirements
        technical_skills = []
        soft_skills = []
        education = []
        experience = []
        
        for line in lines:
            line_lower = line.lower()
            if any(tech in line_lower for tech in ['programming', 'software', 'code', 'develop', 'technical', 'python', 'java', 'javascript', 'html', 'css', 'sql']):
                technical_skills.append(line)
            elif any(soft in line_lower for soft in ['communication', 'teamwork', 'leadership', 'problem-solving', 'collaborate', 'interpersonal']):
                soft_skills.append(line)
            elif any(edu in line_lower for edu in ['degree', 'bachelor', 'master', 'phd', 'education', 'university', 'college']):
                education.append(line)
            elif any(exp in line_lower for exp in ['experience', 'worked', 'background', 'history', 'previous']):
                experience.append(line)
            else:
                # If we can't categorize, assume it's a technical skill
                technical_skills.append(line)
        
        return {
            "original_requirements": requirements_text,
            "categorized_requirements": {
                "technical_skills": technical_skills,
                "soft_skills": soft_skills,
                "education": education,
                "experience": experience
            },
            "optimization_suggestions": suggestions,
            "inclusive_alternatives": {
                "years of experience": "demonstrated ability to",
                "degree required": "degree or equivalent experience",
                "expert in": "strong knowledge of",
                "ninja/rockstar/guru": "skilled professional"
            }
        }
