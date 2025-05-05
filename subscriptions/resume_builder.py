"""
Resume Builder System

This module implements resume building functionality using the core infrastructure
components to generate professional, customized resumes based on user input or
existing content, with optional tailoring for specific job listings.
"""

import logging
import re
import json
from collections import defaultdict
import random

from .text_processor import TextProcessor
from .data_resources import (
    TECHNICAL_SKILLS, 
    SOFT_SKILLS, 
    JOB_TITLES, 
    TEMPLATES, 
    get_all_skills, 
    get_all_job_titles, 
    get_template
)

logger = logging.getLogger(__name__)

class ResumeBuilder:
    """
    Class for building and enhancing resumes using the core infrastructure.
    
    This class uses text processing and data resources to generate professional
    resumes that highlight relevant skills and achievements, optionally tailored
    to specific job listings.
    """
    
    def __init__(self):
        """Initialize the ResumeBuilder with necessary components."""
        self.text_processor = TextProcessor()
        
        # Load skills and job titles for easier matching
        self.all_skills = get_all_skills()
        self.all_job_titles = get_all_job_titles()
    
    def generate_resume(self, user_data, job_listing=None, template_style='standard'):
        """
        Generate a professional resume based on user data, optionally tailored to a job listing.
        
        Args:
            user_data (dict): User profile data with name, contact info, experience, etc.
            job_listing (dict, optional): Job listing to tailor the resume to
            template_style (str, optional): Style of resume template to use ('standard', 
                                           'technical', 'executive')
            
        Returns:
            dict: Generated resume data and formatted content
        """
        try:
            # Validate and clean user data
            clean_data = self._clean_user_data(user_data)
            
            # Extract job requirements if job listing is provided
            job_requirements = {}
            if job_listing:
                job_requirements = self._extract_job_requirements(job_listing)
            
            # Generate resume sections
            generated_summary = self._generate_summary(clean_data, job_requirements)
            generated_skills = self._generate_skills_section(clean_data, job_requirements)
            generated_experience = self._generate_experience_section(clean_data, job_requirements)
            generated_education = self._generate_education_section(clean_data)
            
            # Get appropriate template
            resume_template = get_template('resume', template_style)
            
            # Apply user data to template
            formatted_resume = self._format_resume(
                resume_template, 
                clean_data, 
                generated_summary, 
                generated_skills,
                generated_experience,
                generated_education
            )
            
            return {
                'generated_summary': generated_summary,
                'generated_skills': generated_skills,
                'generated_experience': generated_experience,
                'generated_education': generated_education,
                'formatted_resume': formatted_resume,
                'template_used': template_style
            }
        
        except Exception as e:
            logger.error(f"Error generating resume: {str(e)}")
            raise
    
    def _clean_user_data(self, user_data):
        """
        Clean and validate user data for resume generation.
        
        Args:
            user_data (dict): Raw user profile data
            
        Returns:
            dict: Cleaned and validated user data
        """
        clean_data = {}
        
        # Copy basic info
        clean_data['name'] = user_data.get('name', 'Your Name')
        clean_data['email'] = user_data.get('email', '')
        clean_data['phone'] = user_data.get('phone', '')
        clean_data['address'] = user_data.get('address', '')
        clean_data['city_state_zip'] = user_data.get('city_state_zip', '')
        clean_data['linkedin'] = user_data.get('linkedin', '')
        clean_data['website'] = user_data.get('website', '')
        clean_data['github'] = user_data.get('github', '')
        
        # Clean skills
        clean_data['skills'] = []
        if 'skills' in user_data and isinstance(user_data['skills'], list):
            clean_data['skills'] = [skill.strip() for skill in user_data['skills'] if skill.strip()]
        elif 'skills' in user_data and isinstance(user_data['skills'], str):
            skills_split = [s.strip() for s in user_data['skills'].split(',') if s.strip()]
            clean_data['skills'] = skills_split
        
        # Clean experience
        clean_data['experience'] = []
        if 'experience' in user_data and isinstance(user_data['experience'], list):
            for exp in user_data['experience']:
                if isinstance(exp, dict):
                    clean_exp = {
                        'title': exp.get('title', ''),
                        'company': exp.get('company', ''),
                        'years': exp.get('years', ''),
                        'description': exp.get('description', '')
                    }
                    clean_data['experience'].append(clean_exp)
        
        # Clean education
        clean_data['education'] = []
        if 'education' in user_data and isinstance(user_data['education'], list):
            for edu in user_data['education']:
                if isinstance(edu, dict):
                    clean_edu = {
                        'degree': edu.get('degree', ''),
                        'institution': edu.get('institution', ''),
                        'year': edu.get('year', '')
                    }
                    clean_data['education'].append(clean_edu)
        
        # Add summary if present
        if 'summary' in user_data and isinstance(user_data['summary'], str):
            clean_data['summary'] = user_data['summary']
        
        return clean_data
    
    def _extract_job_requirements(self, job_listing):
        """
        Extract requirements from a job listing for resume tailoring.
        
        Args:
            job_listing (dict): Job listing data
            
        Returns:
            dict: Extracted job requirements for tailoring
        """
        requirements = {
            'skills': [],
            'experience': [],
            'education': [],
            'keywords': []
        }
        
        # Extract skills from required skills
        if 'skills_required' in job_listing:
            if isinstance(job_listing['skills_required'], list):
                requirements['skills'] = job_listing['skills_required']
            elif isinstance(job_listing['skills_required'], str):
                skills = [s.strip() for s in job_listing['skills_required'].split(',') if s.strip()]
                requirements['skills'] = skills
        
        # Extract keywords from job description
        if 'description' in job_listing and isinstance(job_listing['description'], str):
            # Process text to extract relevant terms
            processed = self.text_processor.process_document(job_listing['description'], 'job_description')
            
            # Extract entities
            entities = processed.get('entities', {})
            skill_entities = entities.get('skills', [])
            requirements['skills'].extend(skill_entities)
            
            # Extract frequent words as keywords
            words = self.text_processor.tokenize_words(job_listing['description'].lower())
            words = self.text_processor.remove_stopwords(words)
            
            # Count word frequency
            word_counts = defaultdict(int)
            for word in words:
                if len(word) > 3:  # Skip very short words
                    word_counts[word] += 1
            
            # Get top keywords
            top_keywords = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:15]
            requirements['keywords'] = [word for word, count in top_keywords]
        
        # Extract job title
        if 'title' in job_listing:
            requirements['job_title'] = job_listing['title']
        
        # Extract company
        if 'company' in job_listing and hasattr(job_listing['company'], 'name'):
            requirements['company'] = job_listing['company'].name
        
        # Remove duplicates
        requirements['skills'] = list(set(requirements['skills']))
        
        return requirements
    
    def _generate_summary(self, user_data, job_requirements):
        """
        Generate a professional summary for the resume.
        
        Args:
            user_data (dict): Cleaned user profile data
            job_requirements (dict): Job requirements for tailoring
            
        Returns:
            str: Generated professional summary
        """
        # Use existing summary if provided
        if 'summary' in user_data and user_data['summary']:
            if job_requirements:
                # Enhance existing summary for the job
                return self._enhance_summary_for_job(user_data['summary'], job_requirements)
            return user_data['summary']
        
        # Generate a new summary
        profession = self._determine_profession(user_data)
        years_experience = self._determine_experience_years(user_data)
        key_skills = self._determine_key_skills(user_data, job_requirements)
        achievements = self._extract_achievements(user_data)
        
        # Tailor to job if provided
        job_tailoring = ""
        if job_requirements and 'job_title' in job_requirements:
            job_tailoring = f" seeking a {job_requirements['job_title']} position"
            if 'company' in job_requirements:
                job_tailoring += f" at {job_requirements['company']}"
        
        # Construct summary
        summary_parts = []
        
        # Intro sentence
        if years_experience:
            summary_parts.append(f"{profession} with {years_experience} of experience in {', '.join(key_skills[:3])}{job_tailoring}.")
        else:
            summary_parts.append(f"{profession} with expertise in {', '.join(key_skills[:3])}{job_tailoring}.")
        
        # Achievements
        if achievements:
            achievement_str = f"Demonstrated success in {', '.join(achievements[:2])}"
            if len(achievements) > 2:
                achievement_str += f", and {achievements[2]}"
            summary_parts.append(achievement_str + ".")
        
        # Skills and strengths
        if len(key_skills) > 3:
            summary_parts.append(f"Skilled in {', '.join(key_skills[3:5])} with a strong focus on delivering high-quality results.")
        
        # Combine parts
        return " ".join(summary_parts)
    
    def _enhance_summary_for_job(self, existing_summary, job_requirements):
        """
        Enhance an existing summary to better target a specific job.
        
        Args:
            existing_summary (str): Existing professional summary
            job_requirements (dict): Job requirements for tailoring
            
        Returns:
            str: Enhanced summary tailored to the job
        """
        enhanced = existing_summary
        
        # Check if job title is already mentioned
        if 'job_title' in job_requirements and job_requirements['job_title'].lower() not in existing_summary.lower():
            if enhanced.endswith('.'):
                enhanced = enhanced[:-1]
            
            enhanced += f", seeking to leverage these skills as a {job_requirements['job_title']}"
            if 'company' in job_requirements:
                enhanced += f" at {job_requirements['company']}"
            enhanced += "."
        
        # Add key skills from job requirements if not mentioned
        if 'skills' in job_requirements and job_requirements['skills']:
            job_skills = job_requirements['skills'][:3]  # Top 3 skills
            
            skills_to_add = []
            for skill in job_skills:
                if skill.lower() not in existing_summary.lower():
                    skills_to_add.append(skill)
            
            if skills_to_add:
                if enhanced.endswith('.'):
                    enhanced = enhanced[:-1]
                enhanced += f", with expertise in {', '.join(skills_to_add)}."
        
        return enhanced
    
    def _determine_profession(self, user_data):
        """
        Determine the user's profession based on experience.
        
        Args:
            user_data (dict): Cleaned user profile data
            
        Returns:
            str: Determined profession
        """
        if not user_data.get('experience'):
            return "Professional"
        
        # Get the most recent job title
        latest_job = user_data['experience'][0]
        job_title = latest_job.get('title', '')
        
        # Check for seniority indicators
        seniority_terms = ['senior', 'lead', 'principal', 'head', 'chief', 'director', 'manager', 'architect']
        has_seniority = any(term in job_title.lower() for term in seniority_terms)
        
        # Determine profession type
        if 'engineer' in job_title.lower() or 'developer' in job_title.lower():
            base = "Software Engineer" if 'engineer' in job_title.lower() else "Software Developer"
            return f"Senior {base}" if has_seniority else f"Experienced {base}"
        
        elif 'designer' in job_title.lower() or 'ux' in job_title.lower() or 'ui' in job_title.lower():
            return f"Senior Designer" if has_seniority else "Designer"
        
        elif 'product' in job_title.lower() or 'project' in job_title.lower():
            return f"Senior Product Professional" if has_seniority else "Product Professional"
        
        elif 'data' in job_title.lower() or 'analyst' in job_title.lower():
            return f"Senior Data Professional" if has_seniority else "Data Professional"
        
        elif 'market' in job_title.lower():
            return f"Senior Marketing Professional" if has_seniority else "Marketing Professional"
        
        elif has_seniority:
            return "Senior Professional"
        
        return "Experienced Professional"
    
    def _determine_experience_years(self, user_data):
        """
        Determine the user's years of experience based on their work history.
        
        Args:
            user_data (dict): Cleaned user profile data
            
        Returns:
            str: Years of experience as a string or None if can't be determined
        """
        if not user_data.get('experience'):
            return None
        
        total_years = 0
        current_year = 2025  # Use current year as reference
        
        for job in user_data['experience']:
            years_str = job.get('years', '')
            
            # Try to extract years
            year_pattern = r'(19|20)\d{2}\s*-\s*(?:(19|20)\d{2}|present|current|now)'
            match = re.search(year_pattern, years_str, re.IGNORECASE)
            
            if match:
                years_text = match.group(0).lower()
                start_year = int(re.search(r'(19|20)\d{2}', years_text).group(0))
                
                if 'present' in years_text or 'current' in years_text or 'now' in years_text:
                    end_year = current_year
                else:
                    end_match = re.search(r'-(19|20)\d{2}', years_text)
                    if end_match:
                        end_year = int(end_match.group(0)[1:])
                    else:
                        end_year = start_year + 1  # Default to 1 year if can't determine end
                
                job_years = end_year - start_year
                total_years += job_years
        
        if total_years == 0:
            return None
        elif total_years == 1:
            return "1 year"
        elif total_years < 2:
            return "over 1 year"
        elif total_years < 3:
            return "2+ years"
        elif total_years < 5:
            return "3+ years"
        elif total_years < 8:
            return "5+ years"
        elif total_years < 12:
            return "over 7 years"
        else:
            return "10+ years"
    
    def _determine_key_skills(self, user_data, job_requirements):
        """
        Determine key skills to highlight based on user data and job requirements.
        
        Args:
            user_data (dict): Cleaned user profile data
            job_requirements (dict): Job requirements for tailoring
            
        Returns:
            list: Key skills to highlight
        """
        user_skills = user_data.get('skills', [])
        
        # Extract skills from experience descriptions
        extracted_skills = set()
        for job in user_data.get('experience', []):
            description = job.get('description', '')
            if description:
                for skill in self.all_skills:
                    if re.search(r'\b' + re.escape(skill) + r'\b', description, re.IGNORECASE):
                        extracted_skills.add(skill)
        
        # Combine skills
        all_user_skills = set(user_skills) | extracted_skills
        
        # If job requirements provided, prioritize matching skills
        if job_requirements and 'skills' in job_requirements:
            job_skills = set(job_requirements['skills'])
            
            # Skills that match job requirements
            matching_skills = all_user_skills.intersection(job_skills)
            
            # Other skills from user
            other_skills = all_user_skills - matching_skills
            
            # Prioritize matching skills, then add other skills
            key_skills = list(matching_skills) + list(other_skills)
        else:
            key_skills = list(all_user_skills)
        
        # Limit and return
        return key_skills[:8] if key_skills else ["problem solving", "communication", "teamwork"]
    
    def _extract_achievements(self, user_data):
        """
        Extract key achievements from user experience.
        
        Args:
            user_data (dict): Cleaned user profile data
            
        Returns:
            list: Key achievements
        """
        achievements = []
        
        # Achievement indicators
        indicators = [
            r'(?:increased|improved|enhanced|boosted|grew)\s+(?:by\s+)?(\d+[%]|\d+\s*percent)',
            r'(?:reduced|decreased|cut|minimized)\s+(?:by\s+)?(\d+[%]|\d+\s*percent)',
            r'(?:generated|produced|delivered|created)\s+(?:over\s+)?(\$\d+|\d+\s*million|\d+\s*k)',
            r'(?:managed|led|supervised|oversaw)\s+(?:a\s+)?(?:team|group|department)\s+(?:of\s+)?(\d+|\d+\+)',
            r'(?:developed|created|built|designed|implemented|launched)\s+(?:a\s+)?(?:new|custom|innovative)'
        ]
        
        for job in user_data.get('experience', []):
            description = job.get('description', '')
            if description:
                # Look for achievements using indicators
                for indicator in indicators:
                    matches = re.finditer(indicator, description, re.IGNORECASE)
                    for match in matches:
                        # Get the context around the achievement
                        start = max(0, match.start() - 20)
                        end = min(len(description), match.end() + 40)
                        achievement_context = description[start:end]
                        
                        # Clean up the context
                        achievement_context = re.sub(r'\s+', ' ', achievement_context).strip()
                        
                        # Extract the key phrase
                        achievement_words = achievement_context.split()
                        if len(achievement_words) > 8:
                            # Get a reasonable snippet
                            mid_point = len(achievement_words) // 2
                            achievement_snippet = ' '.join(achievement_words[max(0, mid_point - 4):min(len(achievement_words), mid_point + 4)])
                        else:
                            achievement_snippet = achievement_context
                        
                        # Add if not duplicate
                        if achievement_snippet not in achievements:
                            achievements.append(achievement_snippet)
        
        # Generate generic achievements if none found
        if not achievements:
            job_titles = [job.get('title', '').lower() for job in user_data.get('experience', [])]
            
            if any('develop' in title for title in job_titles):
                achievements.append("developing high-quality software solutions")
            
            if any('design' in title for title in job_titles):
                achievements.append("creating user-centered designs")
            
            if any('manage' in title or 'lead' in title for title in job_titles):
                achievements.append("leading cross-functional teams")
            
            if any('data' in title or 'analy' in title for title in job_titles):
                achievements.append("analyzing complex data and delivering insights")
            
            if not achievements:
                achievements.append("delivering high-quality results")
                achievements.append("collaborating effectively in team environments")
        
        return achievements[:4]  # Limit to top 4 achievements
    
    def _generate_skills_section(self, user_data, job_requirements):
        """
        Generate an enhanced skills section for the resume.
        
        Args:
            user_data (dict): Cleaned user profile data
            job_requirements (dict): Job requirements for tailoring
            
        Returns:
            list: Enhanced list of skills to include
        """
        # Start with user's specified skills
        skills = set(user_data.get('skills', []))
        
        # Extract skills from experience
        for job in user_data.get('experience', []):
            description = job.get('description', '')
            if description:
                for skill in self.all_skills:
                    if re.search(r'\b' + re.escape(skill) + r'\b', description, re.IGNORECASE):
                        skills.add(skill)
        
        # If job requirements provided, add relevant skills user might have
        if job_requirements and 'skills' in job_requirements:
            # For each job skill, check if user might have it based on experience
            for job_skill in job_requirements['skills']:
                # Don't add if already in skills
                if job_skill in skills:
                    continue
                
                # Check experience descriptions for related terms
                skill_terms = job_skill.lower().split()
                for job in user_data.get('experience', []):
                    description = job.get('description', '').lower()
                    # If main terms from skill appear in description, user might have this skill
                    if all(term in description for term in skill_terms if len(term) > 3):
                        skills.add(job_skill)
                        break
        
        # Convert set to list and return
        return sorted(list(skills))
    
    def _generate_experience_section(self, user_data, job_requirements):
        """
        Generate an enhanced experience section for the resume.
        
        Args:
            user_data (dict): Cleaned user profile data
            job_requirements (dict): Job requirements for tailoring
            
        Returns:
            list: Enhanced experience entries
        """
        enhanced_experience = []
        
        # Enhance each experience entry
        for job in user_data.get('experience', []):
            enhanced_job = job.copy()
            
            # Enhance description if needed
            description = job.get('description', '')
            if description and job_requirements:
                enhanced_description = self._enhance_job_description(description, job_requirements)
                enhanced_job['description'] = enhanced_description
            
            enhanced_experience.append(enhanced_job)
        
        return enhanced_experience
    
    def _enhance_job_description(self, description, job_requirements):
        """
        Enhance a job description to better highlight relevant experience.
        
        Args:
            description (str): Original job description
            job_requirements (dict): Job requirements for tailoring
            
        Returns:
            str: Enhanced job description
        """
        enhanced = description
        
        # Check if description already has bullet points
        has_bullets = re.search(r'[•\-\*]', description) is not None
        
        # If no bullet points and description is long enough, break into bullets
        if not has_bullets and len(description.split()) > 20:
            sentences = re.split(r'(?<=[.!?])\s+', description)
            if len(sentences) > 1:
                bullet_points = []
                for sentence in sentences:
                    if len(sentence) > 10:  # Skip very short sentences
                        # Ensure the sentence starts with a strong verb
                        modified = self._ensure_strong_verb_start(sentence)
                        bullet_points.append('• ' + modified)
                
                enhanced = '\n'.join(bullet_points)
        
        # Highlight key skills from job requirements
        if 'skills' in job_requirements and job_requirements['skills']:
            for skill in job_requirements['skills']:
                # Don't modify if already highlighted
                if skill in enhanced and skill + ' ' in enhanced:
                    continue
                
                # Use word boundaries for replacement to avoid partial word matches
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, enhanced, re.IGNORECASE):
                    # Replace with the same text but ensure correct capitalization
                    match = re.search(pattern, enhanced, re.IGNORECASE).group(0)
                    enhanced = re.sub(pattern, skill, enhanced, flags=re.IGNORECASE)
        
        return enhanced
    
    def _ensure_strong_verb_start(self, sentence):
        """
        Ensure a sentence starts with a strong action verb.
        
        Args:
            sentence (str): Original sentence
            
        Returns:
            str: Sentence starting with a strong verb
        """
        # List of strong action verbs for resumes
        strong_verbs = [
            "Developed", "Implemented", "Created", "Designed", "Managed", "Led",
            "Coordinated", "Improved", "Increased", "Reduced", "Generated",
            "Analyzed", "Evaluated", "Resolved", "Delivered", "Launched",
            "Streamlined", "Established", "Executed", "Produced", "Transformed"
        ]
        
        # Check if sentence already starts with a verb
        first_word = sentence.strip().split()[0] if sentence.strip().split() else ""
        
        # If not starting with a strong verb, add one
        if first_word.lower() not in [v.lower() for v in strong_verbs]:
            # Choose a verb that fits the context (simplified approach)
            if "develop" in sentence.lower() or "create" in sentence.lower() or "build" in sentence.lower():
                verb = "Developed"
            elif "design" in sentence.lower() or "architect" in sentence.lower():
                verb = "Designed"
            elif "manage" in sentence.lower() or "lead" in sentence.lower() or "direct" in sentence.lower():
                verb = "Managed"
            elif "improve" in sentence.lower() or "enhance" in sentence.lower() or "increase" in sentence.lower():
                verb = "Improved"
            elif "analyze" in sentence.lower() or "study" in sentence.lower() or "research" in sentence.lower():
                verb = "Analyzed"
            else:
                verb = random.choice(strong_verbs)
            
            # Add the verb, being careful about capitalization
            if sentence[0].isupper():
                first_char = 0
                # Handle bullet points or other markers
                if sentence.startswith('• ') or sentence.startswith('* ') or sentence.startswith('- '):
                    first_char = 2
                
                # If sentence starts with capitalized word, replace that word
                return sentence[:first_char] + verb + sentence[first_char:].lower()
            else:
                return verb + " " + sentence
        
        return sentence
    
    def _generate_education_section(self, user_data):
        """
        Generate an enhanced education section for the resume.
        
        Args:
            user_data (dict): Cleaned user profile data
            
        Returns:
            list: Enhanced education entries
        """
        # Use existing education entries if available
        if user_data.get('education'):
            return user_data['education']
        
        # If no education provided, return an empty list
        return []
    
    def _format_resume(self, template, user_data, summary, skills, experience, education):
        """
        Format resume using the selected template.
        
        Args:
            template (str): Resume template text
            user_data (dict): User profile data
            summary (str): Generated professional summary
            skills (list): Enhanced list of skills
            experience (list): Enhanced experience entries
            education (list): Enhanced education entries
            
        Returns:
            str: Formatted resume text
        """
        # Create a copy of the template
        formatted = template
        
        # Replace name placeholder
        formatted = formatted.replace('[YOUR NAME]', user_data.get('name', 'Your Name'))
        
        # Build contact line
        contact_parts = []
        if user_data.get('address'):
            contact_parts.append(user_data['address'])
        if user_data.get('city_state_zip'):
            contact_parts.append(user_data['city_state_zip'])
        if user_data.get('phone'):
            contact_parts.append(user_data['phone'])
        if user_data.get('email'):
            contact_parts.append(user_data['email'])
        
        # Add social profiles
        social_parts = []
        if user_data.get('linkedin'):
            social_parts.append(user_data['linkedin'])
        if user_data.get('website'):
            social_parts.append(user_data['website'])
        if user_data.get('github'):
            social_parts.append(user_data['github'])
        
        # Replace contact information
        if contact_parts:
            contact_line = ' | '.join(contact_parts)
            formatted = formatted.replace('[Your Address] | [City, State ZIP] | [Phone] | [Email]', contact_line)
            formatted = formatted.replace('[Email] | [Phone] | [LinkedIn]', contact_line)
            formatted = formatted.replace('[Phone] | [Email] | [LinkedIn]', contact_line)
        
        if social_parts:
            social_line = ' | '.join(social_parts)
            formatted = formatted.replace('[LinkedIn/Website]', social_line)
            formatted = formatted.replace('[Links to GitHub/Portfolio/Technical Blog]', social_line)
        
        # Replace summary
        formatted = formatted.replace('[2-3 sentences about your key skills, experience, and what makes you unique]', summary)
        formatted = formatted.replace('[Concise overview of your technical expertise, years of experience, and specialization]', summary)
        formatted = formatted.replace('[Powerful summary of career achievements, leadership style, and value proposition]', summary)
        
        # Replace skills
        if '[List your technical skills]' in formatted:
            technical_skills = [s for s in skills if any(s.lower() in tech_skill.lower() for tech_skill in self.all_skills)]
            tech_skills_str = ', '.join(technical_skills[:8])
            formatted = formatted.replace('[List your technical skills]', tech_skills_str)
        
        if '[List your soft skills]' in formatted:
            soft_skills = [s for s in skills if s not in technical_skills]
            soft_skills_str = ', '.join(soft_skills[:5])
            formatted = formatted.replace('[List your soft skills]', soft_skills_str)
        
        # More specific technical skill categories
        if '**Languages**:' in formatted:
            lang_skills = [s for s in skills if any(s.lower() in lang.lower() for lang in TECHNICAL_SKILLS['programming_languages'])]
            formatted = formatted.replace('[List programming languages]', ', '.join(lang_skills or ['Python', 'JavaScript']))
        
        if '**Frameworks & Libraries**:' in formatted:
            framework_skills = [s for s in skills if any(s.lower() in fw.lower() for fw in TECHNICAL_SKILLS['web_development'])]
            formatted = formatted.replace('[List frameworks and libraries]', ', '.join(framework_skills or ['React', 'Django']))
        
        if '**Databases**:' in formatted:
            db_skills = [s for s in skills if any(s.lower() in db.lower() for db in TECHNICAL_SKILLS['databases'])]
            formatted = formatted.replace('[List databases]', ', '.join(db_skills or ['SQL', 'MongoDB']))
        
        if '**Tools & Platforms**:' in formatted:
            tool_skills = [s for s in skills if any(s.lower() in tool.lower() for tool in TECHNICAL_SKILLS['devops'])]
            formatted = formatted.replace('[List tools, platforms, and methodologies]', ', '.join(tool_skills or ['Git', 'Docker']))
        
        if '**Cloud Services**:' in formatted:
            cloud_skills = [s for s in skills if 'aws' in s.lower() or 'azure' in s.lower() or 'cloud' in s.lower()]
            formatted = formatted.replace('[List cloud services]', ', '.join(cloud_skills or ['AWS', 'GCP']))
        
        # Replace key leadership areas
        if '[Key Leadership Area]' in formatted:
            leadership_areas = ['Strategic Planning', 'Team Leadership', 'Business Development', 
                              'Operational Excellence', 'Product Innovation', 'Change Management']
            
            # Replace each occurrence
            for i in range(formatted.count('[Key Leadership Area]')):
                if i < len(leadership_areas):
                    formatted = formatted.replace('[Key Leadership Area]', leadership_areas[i], 1)
                else:
                    formatted = formatted.replace('[Key Leadership Area]', 'Leadership', 1)
        
        # Replace experience entries
        exp_placeholder = '[Accomplishment statement with measurable results]'
        exp_placeholder_count = formatted.count(exp_placeholder)
        
        if exp_placeholder_count > 0 and experience:
            # Replace job title, company, etc.
            for i, exp in enumerate(experience[:3]):  # Limit to 3 experiences
                company_placeholder = f'[Company Name], [Location]'
                title_placeholder = f'[Job Title]'
                years_placeholder = f'[Start Date] - [End Date/Present]'
                
                if i == 0:  # First experience
                    replacement_exp = f"{exp.get('company', 'Company')}"
                    formatted = formatted.replace('[Company Name], [Location]', replacement_exp, 1)
                    
                    replacement_title = f"{exp.get('title', 'Job Title')}"
                    formatted = formatted.replace('[Job Title]', replacement_title, 1)
                    
                    replacement_years = f"{exp.get('years', 'Start - End')}"
                    formatted = formatted.replace('[Start Date] - [End Date/Present]', replacement_years, 1)
                    
                    # Replace bullet points for first experience
                    if exp.get('description'):
                        bullets = self._get_description_bullets(exp['description'])
                        for j, bullet in enumerate(bullets[:3]):  # Limit to 3 bullets per experience
                            if exp_placeholder in formatted:
                                formatted = formatted.replace(exp_placeholder, bullet, 1)
                
                elif i == 1:  # Second experience  
                    replacement_exp = f"{exp.get('company', 'Previous Company')}"
                    formatted = formatted.replace('[Previous Company Name], [Location]', replacement_exp, 1)
                    
                    replacement_title = f"{exp.get('title', 'Previous Job Title')}"
                    formatted = formatted.replace('[Previous Job Title]', replacement_title, 1)
                    
                    replacement_years = f"{exp.get('years', 'Start - End')}"
                    formatted = formatted.replace('[Start Date] - [End Date]', replacement_years, 1)
                    
                    # Replace remaining bullet points for second experience
                    if exp.get('description'):
                        bullets = self._get_description_bullets(exp['description'])
                        for j, bullet in enumerate(bullets[:3]):  # Limit to 3 bullets per experience
                            if exp_placeholder in formatted:
                                formatted = formatted.replace(exp_placeholder, bullet, 1)
            
            # Handle any remaining bullet points
            while exp_placeholder in formatted:
                formatted = formatted.replace(exp_placeholder, "Demonstrated excellence in collaborative team environments", 1)
        
        # Replace education entries
        if education:
            edu = education[0]  # Use first education entry
            
            # Replace degree
            degree_placeholder = '[Degree]'
            if degree_placeholder in formatted:
                formatted = formatted.replace(degree_placeholder, edu.get('degree', 'Degree'), 1)
            
            # Replace university
            univ_placeholder = '[University Name], [Location]'
            if univ_placeholder in formatted:
                formatted = formatted.replace(univ_placeholder, edu.get('institution', 'University'), 1)
            
            # Replace graduation year
            year_placeholder = '[Graduation Date]'
            if year_placeholder in formatted:
                formatted = formatted.replace(year_placeholder, str(edu.get('year', 'Year')), 1)
        
        # Return the formatted resume
        return formatted
    
    def _get_description_bullets(self, description):
        """
        Convert a job description into bullet points if needed.
        
        Args:
            description (str): Job description text
            
        Returns:
            list: Description as bullet points
        """
        # If already has bullet points, extract them
        if '•' in description or '-' in description or '*' in description:
            # Split by bullet points
            bullet_pattern = r'[•\-\*]\s*(.*?)(?=(?:[•\-\*]|\n\n|\Z))'
            bullets = re.findall(bullet_pattern, description, re.DOTALL)
            
            # Clean up bullet points
            cleaned_bullets = []
            for bullet in bullets:
                bullet = bullet.strip()
                if bullet:
                    # Ensure strong verb start
                    bullet = self._ensure_strong_verb_start(bullet)
                    cleaned_bullets.append(bullet)
            
            return cleaned_bullets
        
        # If not, split into sentences and convert to bullets
        sentences = re.split(r'(?<=[.!?])\s+', description)
        
        bullets = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Skip very short sentences
                # Ensure strong verb start
                sentence = self._ensure_strong_verb_start(sentence)
                bullets.append(sentence)
        
        return bullets