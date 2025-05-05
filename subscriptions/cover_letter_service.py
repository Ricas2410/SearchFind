import json
from .ai_services import AIService

class CoverLetterService:
    """Service for generating and analyzing cover letters."""
    
    @classmethod
    def generate_cover_letter(cls, user_profile, job_listing):
        """
        Generate a cover letter based on user profile and job listing.
        
        Args:
            user_profile: User profile information
            job_listing: Job listing information
            
        Returns:
            Dictionary containing the generated cover letter and customization tips
        """
        # In a real implementation, we would use the user profile and job listing
        # to create a personalized cover letter using an AI service
        
        # For now, we'll use our simulated AI response
        prompt = f"Generate cover letter for job: {job_listing.title} at {job_listing.company.name}"
        
        # Get simulated AI response
        response = AIService.get_ai_response(prompt)
        
        try:
            # Parse the JSON response
            cover_letter_data = json.loads(response)
            
            # Customize the cover letter with user and job information
            cover_letter = cover_letter_data.get('cover_letter', '')
            cover_letter = cover_letter.replace('[Job Title]', job_listing.title)
            cover_letter = cover_letter.replace('[Company Name]', job_listing.company.name)
            
            if hasattr(user_profile, 'full_name'):
                cover_letter = cover_letter.replace('[Your Name]', user_profile.full_name)
            
            # Update the response with the customized cover letter
            cover_letter_data['cover_letter'] = cover_letter
            
            return cover_letter_data
        except (json.JSONDecodeError, AttributeError):
            # Return a basic cover letter if there's an error
            return {
                "cover_letter": f"Dear Hiring Manager,\n\nI am writing to express my interest in the {job_listing.title} position at {job_listing.company.name}...",
                "customization_tips": [
                    "Add your relevant experience",
                    "Mention specific achievements",
                    "Explain why you're interested in this company"
                ]
            }
    
    @classmethod
    def analyze_cover_letter(cls, cover_letter_text, job_listing=None):
        """
        Analyze a cover letter and provide feedback.
        
        Args:
            cover_letter_text: The cover letter text to analyze
            job_listing: Optional job listing for context
            
        Returns:
            Dictionary containing analysis and improvement suggestions
        """
        # In a real implementation, we would send this to an AI service
        # For now, we'll return a simulated analysis
        
        # Basic analysis based on length
        word_count = len(cover_letter_text.split())
        
        if word_count < 150:
            length_feedback = "Your cover letter is quite short. Consider adding more details about your experience and qualifications."
        elif word_count > 400:
            length_feedback = "Your cover letter is quite long. Consider making it more concise by focusing on the most relevant information."
        else:
            length_feedback = "Your cover letter has a good length, which should keep the reader engaged."
        
        # Check for key elements
        has_greeting = any(greeting in cover_letter_text.lower() for greeting in ['dear', 'hello', 'hi', 'greetings'])
        has_introduction = len(cover_letter_text.split('\n\n')) > 1
        has_skills = any(skill in cover_letter_text.lower() for skill in ['skill', 'experience', 'qualification', 'background'])
        has_closing = any(closing in cover_letter_text.lower() for closing in ['sincerely', 'regards', 'thank you', 'looking forward'])
        
        missing_elements = []
        if not has_greeting:
            missing_elements.append("a proper greeting")
        if not has_introduction:
            missing_elements.append("a clear introduction")
        if not has_skills:
            missing_elements.append("mention of your skills and qualifications")
        if not has_closing:
            missing_elements.append("a professional closing")
        
        # Generate improvement suggestions
        suggestions = []
        
        if job_listing:
            suggestions.append(f"Tailor your cover letter to specifically address the requirements for the {job_listing.title} position")
            
            if job_listing.skills_required:
                skills = job_listing.skills_required.split(',')[:3]
                skills_text = ', '.join(skills)
                suggestions.append(f"Highlight your experience with {skills_text}")
        
        suggestions.append("Use specific examples and achievements rather than general statements")
        suggestions.append("Show enthusiasm for the company and explain why you want to work there")
        suggestions.append("Proofread carefully for grammar and spelling errors")
        
        return {
            "word_count": word_count,
            "length_feedback": length_feedback,
            "missing_elements": missing_elements,
            "improvement_suggestions": suggestions,
            "overall_assessment": "Your cover letter provides a good foundation. With some targeted improvements, it can more effectively showcase your qualifications for this position."
        }
