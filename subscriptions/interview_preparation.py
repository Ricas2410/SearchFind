"""
Interview Preparation System

This module implements the interview preparation functionality using the core infrastructure
components. It generates relevant interview questions based on job descriptions and user
profiles, and provides guidance for answering various types of interview questions.
"""

import logging
import re
import json
import random
from collections import defaultdict, Counter

from .text_processor import TextProcessor
from .data_resources import get_all_skills, get_soft_skills, get_technical_skills_by_category

logger = logging.getLogger(__name__)

class InterviewPreparation:
    """
    Class for generating interview questions and answer guidance.
    
    This class uses the text processing infrastructure to analyze job descriptions
    and user profiles to generate relevant interview questions and provide
    detailed guidance for answering different types of questions.
    """
    
    def __init__(self):
        """Initialize the InterviewPreparation with necessary components."""
        self.text_processor = TextProcessor()
        
        # Load skills data
        self.all_skills = get_all_skills()
        self.soft_skills = get_soft_skills()
        self.technical_skills = get_technical_skills_by_category()
        
        # Initialize question templates
        self._initialize_question_templates()
        
        # Initialize answer frameworks
        self._initialize_answer_frameworks()
    
    def _initialize_question_templates(self):
        """Initialize question templates for different categories."""
        # Technical question templates
        self.technical_question_templates = [
            "Describe your experience with {skill}.",
            "How have you used {skill} in your previous projects?",
            "Can you explain how {skill} works and when you would use it?",
            "What are the advantages and disadvantages of {skill}?",
            "How would you implement {skill} to solve {problem_type}?",
            "What's your approach to debugging issues with {skill}?",
            "Compare {skill} with {alternative_skill}. When would you choose one over the other?",
            "Describe a challenging problem you solved using {skill}.",
            "How do you stay updated with the latest developments in {skill}?",
            "What best practices do you follow when working with {skill}?"
        ]
        
        # Behavioral question templates
        self.behavioral_question_templates = [
            "Tell me about a time when you had to {situation}.",
            "Describe a situation where you {action}. What was the outcome?",
            "How do you handle {challenge}?",
            "Give an example of when you {positive_action}.",
            "Describe a time when you faced {obstacle}. How did you overcome it?",
            "Tell me about a project you're particularly proud of.",
            "How do you prioritize tasks when working on multiple projects?",
            "Describe a situation where you had to work under pressure or with tight deadlines.",
            "Tell me about a time when you had to learn a new skill quickly.",
            "How do you handle feedback or criticism?"
        ]
        
        # Company/role-specific question templates
        self.company_question_templates = [
            "Why are you interested in working for {company}?",
            "What do you know about our company and our mission?",
            "How do your skills align with the {role} position?",
            "Where do you see yourself in 5 years if you join our company?",
            "What interests you most about this position?",
            "How would your experience contribute to our team?",
            "What challenges do you think {industry} is currently facing?",
            "What do you think sets {company} apart from our competitors?",
            "How do your values align with our company culture?",
            "What questions do you have about the role or our company?"
        ]
        
        # Situation placeholders for behavioral questions
        self.behavioral_situations = {
            "situation": [
                "faced a challenging deadline",
                "had to resolve a conflict within your team",
                "had to adapt to a major change",
                "failed or made a mistake",
                "had to persuade someone to see your point of view",
                "had to make a difficult decision",
                "went above and beyond for a project",
                "had to deal with a difficult colleague or client",
                "had to prioritize competing tasks",
                "took initiative on a project"
            ],
            "action": [
                "led a team through a difficult situation",
                "implemented a significant improvement",
                "solved a complex problem",
                "received critical feedback",
                "had to compromise",
                "disagreed with your manager",
                "had to motivate a demoralized team",
                "had to learn a new skill quickly",
                "had to explain a technical concept to non-technical stakeholders",
                "had to work with limited resources"
            ],
            "challenge": [
                "tight deadlines",
                "conflicting priorities",
                "difficult team members",
                "unclear requirements",
                "limited resources",
                "resistance to change",
                "technical obstacles",
                "communication barriers",
                "failures or setbacks",
                "ambiguity"
            ],
            "positive_action": [
                "demonstrated leadership",
                "showed creativity in problem-solving",
                "influenced others without formal authority",
                "learned from a failure",
                "successfully managed conflicting priorities",
                "improved a process or system",
                "collaborated across teams",
                "adapted to unexpected changes",
                "received and implemented feedback",
                "mentored or helped a colleague"
            ],
            "obstacle": [
                "resistance to your ideas",
                "technical limitations",
                "resource constraints",
                "disagreements within the team",
                "unexpected changes to requirements",
                "tight deadlines",
                "lack of stakeholder support",
                "knowledge gaps",
                "communication challenges",
                "competing priorities"
            ]
        }
        
        # Problem types for technical questions
        self.problem_types = [
            "performance optimization",
            "scalability issues",
            "data processing",
            "system integration",
            "security vulnerabilities",
            "user experience challenges",
            "debugging complex issues",
            "legacy system modernization",
            "real-time data handling",
            "cross-platform compatibility"
        ]
    
    def _initialize_answer_frameworks(self):
        """Initialize frameworks for different answer types."""
        # STAR method for behavioral questions
        self.star_framework = {
            "title": "STAR Method",
            "description": "Structure your answer to behavioral questions with this framework",
            "steps": [
                {
                    "name": "Situation",
                    "description": "Describe the context and background of the situation you faced",
                    "tips": [
                        "Be specific about when and where the situation occurred",
                        "Provide enough context for the interviewer to understand the scenario",
                        "Keep it concise - aim for 2-3 sentences"
                    ],
                    "example": "While working at [Company] last year, our team was assigned a critical client project with a tight four-week deadline. Two weeks in, a key team member had to take unexpected leave."
                },
                {
                    "name": "Task",
                    "description": "Explain your responsibility or role in the situation",
                    "tips": [
                        "Clarify what was expected of you",
                        "Highlight any challenges or constraints",
                        "Make your specific responsibilities clear"
                    ],
                    "example": "As the senior developer, I needed to ensure the project stayed on track and was delivered on time without sacrificing quality, while also redistributing the workload fairly among the remaining team members."
                },
                {
                    "name": "Action",
                    "description": "Describe the specific actions you took to address the situation",
                    "tips": [
                        "Focus on YOUR actions (use 'I' instead of 'we')",
                        "Be detailed about the steps you took",
                        "Highlight relevant skills or qualities you demonstrated",
                        "Explain your reasoning for the actions you chose"
                    ],
                    "example": "I immediately conducted a gap analysis to identify the critical tasks that needed reassignment. I then organized a team meeting to redistribute responsibilities based on each person's strengths. I implemented daily 15-minute check-ins to monitor progress and identify potential blockers early. Additionally, I took on the most complex technical tasks myself and created detailed documentation to streamline the work."
                },
                {
                    "name": "Result",
                    "description": "Share the outcomes of your actions, quantifying if possible",
                    "tips": [
                        "Use specific metrics or numbers when possible",
                        "Mention both immediate results and longer-term impacts",
                        "Include what you learned from the experience",
                        "Connect the result back to the original situation"
                    ],
                    "example": "We successfully delivered the project one day ahead of the deadline, and the client was extremely satisfied with the quality of our work, leading to a contract renewal worth $500,000. The documentation I created became a template for future projects, reducing onboarding time by 30%. This experience taught me valuable lessons about resource allocation and contingency planning that I've applied to all subsequent projects."
                }
            ]
        }
        
        # Technical question framework
        self.technical_framework = {
            "title": "Technical Question Framework",
            "description": "Approach for answering technical questions effectively",
            "steps": [
                {
                    "name": "Understand",
                    "description": "Make sure you fully understand what is being asked",
                    "tips": [
                        "Restate the question in your own words if needed",
                        "Ask clarifying questions if any part is unclear",
                        "Consider the interviewer's intent behind the question"
                    ]
                },
                {
                    "name": "Context",
                    "description": "Provide context about your experience with the topic",
                    "tips": [
                        "Briefly mention your level of experience with the technology",
                        "Reference relevant projects or situations",
                        "Position your knowledge appropriately (expert, familiar, etc.)"
                    ]
                },
                {
                    "name": "Core Concepts",
                    "description": "Explain the fundamental concepts or principles",
                    "tips": [
                        "Start with a clear definition or explanation",
                        "Cover the most important elements first",
                        "Demonstrate depth of understanding beyond surface-level knowledge"
                    ]
                },
                {
                    "name": "Application",
                    "description": "Describe how you've applied this knowledge practically",
                    "tips": [
                        "Give a specific example from your experience",
                        "Explain your decision-making process",
                        "Highlight challenges and how you overcame them"
                    ]
                },
                {
                    "name": "Trade-offs",
                    "description": "Discuss advantages, limitations, and alternatives",
                    "tips": [
                        "Show balanced thinking by covering pros and cons",
                        "Compare with alternative approaches when relevant",
                        "Demonstrate awareness of best practices and when to apply them"
                    ]
                },
                {
                    "name": "Conclusion",
                    "description": "Summarize your answer concisely",
                    "tips": [
                        "Circle back to the original question",
                        "Reinforce your main points",
                        "End with confidence, showing you're open to follow-up questions"
                    ]
                }
            ]
        }
        
        # Company/role questions framework
        self.company_framework = {
            "title": "Company/Role Question Framework",
            "description": "Structure for answering questions about your interest in the company or role",
            "steps": [
                {
                    "name": "Research",
                    "description": "Demonstrate that you've researched the company",
                    "tips": [
                        "Reference the company's mission, values, products, or recent news",
                        "Show you understand their industry position and challenges",
                        "Mention specific aspects that genuinely interest you"
                    ]
                },
                {
                    "name": "Alignment",
                    "description": "Connect your background and goals to the company and role",
                    "tips": [
                        "Highlight specific skills or experiences that match their needs",
                        "Explain how your career goals align with what the company offers",
                        "Show how your values match their company culture"
                    ]
                },
                {
                    "name": "Value",
                    "description": "Articulate the value you would bring to the company",
                    "tips": [
                        "Focus on how you can help solve their specific challenges",
                        "Mention unique perspectives or skills you offer",
                        "Be specific about contributions you hope to make"
                    ]
                },
                {
                    "name": "Enthusiasm",
                    "description": "Express genuine interest and enthusiasm",
                    "tips": [
                        "Be authentic about why you're excited about this opportunity",
                        "Show passion for the industry, technology, or company mission",
                        "Demonstrate a forward-looking perspective about the role"
                    ]
                }
            ]
        }
        
        # Difficult questions framework
        self.difficult_framework = {
            "title": "Difficult Question Framework",
            "description": "Approach for handling challenging or unexpected questions",
            "steps": [
                {
                    "name": "Pause",
                    "description": "Take a moment to collect your thoughts",
                    "tips": [
                        "It's okay to briefly pause before answering difficult questions",
                        "Use phrases like 'That's a good question' to give yourself time",
                        "Don't rush into an answer you haven't thought through"
                    ]
                },
                {
                    "name": "Reframe",
                    "description": "Consider the purpose behind the question",
                    "tips": [
                        "Identify what the interviewer is really trying to learn",
                        "Look for opportunities to highlight your strengths",
                        "If a question seems negative, find a constructive angle"
                    ]
                },
                {
                    "name": "Structure",
                    "description": "Organize your thoughts before speaking",
                    "tips": [
                        "For complex questions, briefly outline your approach",
                        "Start with the most important point",
                        "Use a logical progression in your answer"
                    ]
                },
                {
                    "name": "Honest Reflection",
                    "description": "Be truthful while remaining positive",
                    "tips": [
                        "Address weaknesses honestly but constructively",
                        "Include what you've learned or how you're improving",
                        "Don't avoid the question or be overly negative"
                    ]
                },
                {
                    "name": "Concise Closure",
                    "description": "End your answer clearly and positively",
                    "tips": [
                        "Summarize your main point succinctly",
                        "End on a forward-looking or positive note",
                        "Don't ramble or leave your answer open-ended"
                    ]
                }
            ]
        }
    
    def generate_interview_questions(self, job_description, user_profile=None):
        """
        Generate relevant interview questions based on job description and user profile.
        
        Args:
            job_description (str): Job description text
            user_profile (dict, optional): User profile with skills, experience, etc.
            
        Returns:
            dict: Generated interview questions by category
        """
        try:
            # Process job description to extract relevant information
            processed_job = self.text_processor.process_document(job_description, "job_description")
            
            # Extract skills and key terms from job description
            job_skills = processed_job.get('extracted_skills', [])
            job_terms = processed_job.get('extracted_keywords', [])
            
            # Extract company name and role
            company_name = processed_job.get('extracted_company', 'the company')
            role_name = processed_job.get('extracted_job_title', 'this role')
            industry = processed_job.get('extracted_industry', 'this industry')
            
            # Generate technical questions
            technical_questions = self._generate_technical_questions(job_skills, job_terms)
            
            # Generate behavioral questions
            behavioral_questions = self._generate_behavioral_questions(job_description)
            
            # Generate company/role questions
            company_questions = self._generate_company_questions(company_name, role_name, industry)
            
            # If user profile is provided, customize questions based on their background
            if user_profile:
                technical_questions = self._personalize_technical_questions(technical_questions, user_profile)
                behavioral_questions = self._personalize_behavioral_questions(behavioral_questions, user_profile)
            
            return {
                'technical_questions': technical_questions,
                'behavioral_questions': behavioral_questions,
                'company_questions': company_questions,
                'job_skills': job_skills[:10],  # Include top 10 skills for reference
                'question_count': {
                    'technical': len(technical_questions),
                    'behavioral': len(behavioral_questions),
                    'company': len(company_questions),
                    'total': len(technical_questions) + len(behavioral_questions) + len(company_questions)
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating interview questions: {str(e)}")
            return self._generate_fallback_questions()
    
    def _generate_technical_questions(self, job_skills, job_terms, count=8):
        """
        Generate technical questions based on job skills.
        
        Args:
            job_skills (list): Skills extracted from job description
            job_terms (list): Key terms from job description
            count (int): Number of questions to generate
            
        Returns:
            list: Generated technical questions
        """
        # Use extracted skills, or fallback to common technical skills
        skills_to_use = job_skills if job_skills else list(random.sample(self.all_skills, min(10, len(self.all_skills))))
        
        # Ensure we have enough skills (with duplicates allowed for important skills)
        while len(skills_to_use) < count:
            skills_to_use.append(random.choice(skills_to_use + list(self.all_skills)))
        
        # Generate technical questions using templates
        questions = []
        used_templates = set()
        
        for i in range(min(count, len(skills_to_use))):
            skill = skills_to_use[i]
            
            # Try to find a template we haven't used yet
            available_templates = [t for t in self.technical_question_templates if t not in used_templates]
            if not available_templates:
                available_templates = self.technical_question_templates
            
            template = random.choice(available_templates)
            used_templates.add(template)
            
            # Format the template with the skill and other placeholders
            question = template.format(
                skill=skill,
                problem_type=random.choice(self.problem_types),
                alternative_skill=random.choice([s for s in skills_to_use if s != skill] or ["a similar technology"])
            )
            
            questions.append(question)
        
        # Include at least one language-specific question if programming language is mentioned
        programming_languages = ["Python", "JavaScript", "Java", "C#", "C++", "Ruby", "PHP", "Swift", "TypeScript", "Go"]
        found_languages = [lang for lang in programming_languages if lang in job_skills]
        
        if found_languages and len(questions) > 1:
            language = random.choice(found_languages)
            language_question = f"Describe a project where you used {language}. What specific features of the language did you leverage?"
            # Replace a random question with the language-specific one
            questions[random.randint(0, len(questions)-1)] = language_question
        
        return questions
    
    def _generate_behavioral_questions(self, job_description, count=7):
        """
        Generate behavioral questions based on job description.
        
        Args:
            job_description (str): Job description text
            count (int): Number of questions to generate
            
        Returns:
            list: Generated behavioral questions
        """
        # Look for key themes in the job description
        teamwork_focus = "team" in job_description.lower() or "collaborate" in job_description.lower()
        leadership_focus = "lead" in job_description.lower() or "manage" in job_description.lower()
        problem_solving_focus = "problem" in job_description.lower() or "solve" in job_description.lower()
        communication_focus = "communicate" in job_description.lower() or "presentation" in job_description.lower()
        
        # Generate behavioral questions using templates
        questions = []
        used_placeholders = set()
        
        # Generate initial questions based on job focus areas
        if teamwork_focus:
            questions.append("Tell me about a time when you had to work effectively as part of a team.")
        
        if leadership_focus:
            questions.append("Describe a situation where you had to lead a team through a challenging project.")
        
        if problem_solving_focus:
            questions.append("Describe a complex problem you faced and how you went about solving it.")
        
        if communication_focus:
            questions.append("Tell me about a time when you had to explain a complex technical concept to a non-technical audience.")
        
        # Fill remaining questions
        while len(questions) < count:
            template = random.choice(self.behavioral_question_templates)
            
            # Determine which placeholder to use
            placeholders = {}
            for key in self.behavioral_situations:
                if f"{{{key}}}" in template:
                    # Try to find a value we haven't used yet
                    available_values = [v for v in self.behavioral_situations[key] 
                                       if (key, v) not in used_placeholders]
                    
                    if not available_values:
                        available_values = self.behavioral_situations[key]
                    
                    value = random.choice(available_values)
                    used_placeholders.add((key, value))
                    placeholders[key] = value
            
            # Format the template with placeholders
            question = template
            for key, value in placeholders.items():
                question = question.replace(f"{{{key}}}", value)
            
            # Add if it's not a duplicate
            if question not in questions:
                questions.append(question)
        
        return questions[:count]
    
    def _generate_company_questions(self, company_name, role_name, industry, count=5):
        """
        Generate company/role-specific questions.
        
        Args:
            company_name (str): Company name
            role_name (str): Role name
            industry (str): Industry name
            count (int): Number of questions to generate
            
        Returns:
            list: Generated company questions
        """
        # Generate company questions using templates
        questions = []
        
        # Always include these key questions
        key_questions = [
            f"Why are you interested in working for {company_name}?",
            f"How do your skills align with the {role_name} position?",
            "Where do you see yourself in 5 years?"
        ]
        
        questions.extend(key_questions)
        
        # Generate additional questions
        used_templates = set(key_questions)
        
        while len(questions) < count:
            template = random.choice(self.company_question_templates)
            
            # Skip templates we've already used
            if template in used_templates:
                continue
            
            used_templates.add(template)
            
            # Format the template
            question = template.format(
                company=company_name,
                role=role_name,
                industry=industry
            )
            
            # Only add if it's not already in the list (after formatting)
            if question not in questions:
                questions.append(question)
        
        return questions[:count]
    
    def _personalize_technical_questions(self, questions, user_profile):
        """
        Personalize technical questions based on user profile.
        
        Args:
            questions (list): Initial technical questions
            user_profile (dict): User profile information
            
        Returns:
            list: Personalized technical questions
        """
        # Extract user skills
        user_skills = user_profile.get('skills', [])
        user_experience = user_profile.get('experience', [])
        
        if not user_skills and not user_experience:
            return questions
        
        # Ensure at least one question focuses on their strongest skill
        if user_skills and len(questions) > 2:
            # Assume first skill is strongest
            top_skill = user_skills[0]
            skill_question = f"You mentioned {top_skill} as one of your key skills. Can you describe a challenging problem you solved using this technology?"
            
            # Replace a random question
            questions[random.randint(0, len(questions)-1)] = skill_question
        
        # Add a question about relevant experience if available
        if user_experience and len(questions) > 3:
            recent_role = user_experience[0].get('title', 'your previous role')
            company = user_experience[0].get('company', 'your previous company')
            
            experience_question = f"In your role as {recent_role} at {company}, what were the most challenging technical problems you faced and how did you overcome them?"
            
            # Replace another random question
            remaining_indices = list(range(len(questions)))
            if len(questions) > 2:  # Don't replace the skill question we just added
                idx = random.choice(remaining_indices)
                questions[idx] = experience_question
        
        return questions
    
    def _personalize_behavioral_questions(self, questions, user_profile):
        """
        Personalize behavioral questions based on user profile.
        
        Args:
            questions (list): Initial behavioral questions
            user_profile (dict): User profile information
            
        Returns:
            list: Personalized behavioral questions
        """
        user_experience = user_profile.get('experience', [])
        
        if not user_experience or len(questions) < 3:
            return questions
        
        # Get the most recent role
        recent_role = user_experience[0]
        role_title = recent_role.get('title', 'your previous role')
        company = recent_role.get('company', 'your previous company')
        
        # Create a personalized question
        personalized_question = f"During your time as {role_title} at {company}, tell me about a situation where you demonstrated leadership or initiative."
        
        # Replace a random question
        idx = random.randint(0, len(questions)-1)
        questions[idx] = personalized_question
        
        return questions
    
    def _generate_fallback_questions(self):
        """
        Generate fallback questions if main generation fails.
        
        Returns:
            dict: Basic interview questions
        """
        return {
            'technical_questions': [
                "Tell me about your experience with programming languages and frameworks.",
                "How do you approach debugging a complex issue?",
                "Describe your experience with databases and data modeling.",
                "How do you ensure the quality of your code?",
                "Describe your experience with version control systems."
            ],
            'behavioral_questions': [
                "Tell me about a challenging project you worked on recently.",
                "Describe a situation where you had to work under pressure.",
                "How do you handle conflicts within a team?",
                "Describe a situation where you had to learn a new technology quickly.",
                "Tell me about a time when you made a mistake and how you handled it."
            ],
            'company_questions': [
                "Why are you interested in this position?",
                "What do you know about our company?",
                "Where do you see yourself in 5 years?",
                "What are your strengths and weaknesses?",
                "Do you have any questions for us?"
            ],
            'job_skills': [],
            'question_count': {
                'technical': 5,
                'behavioral': 5,
                'company': 5,
                'total': 15
            }
        }
    
    def generate_answer_guidance(self, question_type, question_text=None):
        """
        Generate guidance for answering a specific type of interview question.
        
        Args:
            question_type (str): Type of question ('technical', 'behavioral', 'company', or 'difficult')
            question_text (str, optional): Specific question text for tailored guidance
            
        Returns:
            dict: Answer guidance including framework and tips
        """
        try:
            # Determine the framework to use
            if question_type.lower() == 'technical':
                framework = self.technical_framework
                example = self._generate_technical_answer_example(question_text) if question_text else None
            elif question_type.lower() == 'behavioral':
                framework = self.star_framework
                example = self._generate_behavioral_answer_example(question_text) if question_text else None
            elif question_type.lower() == 'company':
                framework = self.company_framework
                example = self._generate_company_answer_example(question_text) if question_text else None
            elif question_type.lower() == 'difficult':
                framework = self.difficult_framework
                example = self._generate_difficult_answer_example(question_text) if question_text else None
            else:
                # Default to STAR method if question type is unknown
                framework = self.star_framework
                example = None
            
            # Generate specific tips for the question if provided
            specific_tips = []
            if question_text:
                specific_tips = self._generate_specific_tips(question_type, question_text)
            
            # Prepare guidance
            guidance = {
                'framework': framework,
                'question_type': question_type,
                'specific_tips': specific_tips
            }
            
            # Add example answer if available
            if example:
                guidance['example_answer'] = example
            
            # Add do's and don'ts
            guidance['dos_and_donts'] = self._generate_dos_and_donts(question_type)
            
            return guidance
            
        except Exception as e:
            logger.error(f"Error generating answer guidance: {str(e)}")
            return {
                'framework': self.star_framework,
                'question_type': question_type,
                'specific_tips': [
                    "Prepare concrete examples from your experience",
                    "Keep your answer concise and focused",
                    "Practice your response out loud before the interview"
                ],
                'dos_and_donts': {
                    'dos': [
                        "Be specific and use real examples",
                        "Quantify your achievements where possible",
                        "Show enthusiasm and positive attitude"
                    ],
                    'donts': [
                        "Don't speak negatively about previous employers",
                        "Avoid generic or vague answers",
                        "Don't memorize answers word-for-word"
                    ]
                }
            }
    
    def _generate_specific_tips(self, question_type, question_text):
        """
        Generate specific tips for answering a given question.
        
        Args:
            question_type (str): Type of question
            question_text (str): Question text
            
        Returns:
            list: Specific tips for answering the question
        """
        # Common tips for all questions
        common_tips = [
            "Take a moment to gather your thoughts before answering",
            "Use specific examples from your experience"
        ]
        
        # Initial tips based on question type
        if question_type.lower() == 'technical':
            tips = [
                "Show your problem-solving approach, not just the final answer",
                "Explain your thinking step by step",
                "Mention trade-offs or alternatives if relevant"
            ]
        elif question_type.lower() == 'behavioral':
            tips = [
                "Use the STAR method (Situation, Task, Action, Result)",
                "Focus on YOUR specific actions and contributions",
                "Quantify results whenever possible"
            ]
        elif question_type.lower() == 'company':
            tips = [
                "Show you've researched the company and understand their mission",
                "Connect your skills and experience to the specific role",
                "Express genuine interest in the company and position"
            ]
        elif question_type.lower() == 'difficult':
            tips = [
                "Stay calm and composed, even with challenging questions",
                "Be honest but frame your answer positively",
                "It's okay to briefly pause to organize your thoughts"
            ]
        else:
            return common_tips
        
        # Analyze the question for specific keywords
        question_lower = question_text.lower()
        
        # Additional tips based on question content
        if "challenge" in question_lower or "difficult" in question_lower:
            tips.append("Focus on how you overcame the challenge, not just the challenge itself")
        
        if "mistake" in question_lower or "fail" in question_lower:
            tips.append("Show what you learned from the experience and how you've grown")
        
        if "team" in question_lower or "collaborate" in question_lower:
            tips.append("Highlight your specific role while acknowledging team contribution")
        
        if "conflict" in question_lower or "disagree" in question_lower:
            tips.append("Emphasize professional resolution and positive outcomes")
        
        if "weakness" in question_lower:
            tips.append("Mention a genuine weakness, but focus on how you're working to improve it")
        
        if "project" in question_lower:
            tips.append("Choose a relevant project that showcases skills important for this role")
        
        # Combine tips, avoiding duplicates
        all_tips = common_tips + tips
        return list(dict.fromkeys(all_tips))  # Remove duplicates while preserving order
    
    def _generate_dos_and_donts(self, question_type):
        """
        Generate general do's and don'ts for answering questions.
        
        Args:
            question_type (str): Type of question
            
        Returns:
            dict: Do's and don'ts for the question type
        """
        if question_type.lower() == 'technical':
            return {
                'dos': [
                    "Demonstrate your problem-solving approach",
                    "Show depth of knowledge in your strongest areas",
                    "Acknowledge limitations of your approach",
                    "Refer to specific experiences with technologies",
                    "Ask clarifying questions if needed"
                ],
                'donts': [
                    "Don't bluff if you don't know something",
                    "Avoid oversimplifying complex concepts",
                    "Don't get lost in unnecessary details",
                    "Avoid jargon without explanation",
                    "Don't criticize technologies or approaches"
                ]
            }
        elif question_type.lower() == 'behavioral':
            return {
                'dos': [
                    "Use specific, real examples from your experience",
                    "Focus on your individual contribution",
                    "Quantify results and achievements",
                    "Show what you learned from the experience",
                    "Keep your answer structured and concise"
                ],
                'donts': [
                    "Don't use hypothetical scenarios instead of real experiences",
                    "Avoid vague or generic responses",
                    "Don't speak negatively about former colleagues or employers",
                    "Avoid taking credit for team accomplishments",
                    "Don't ramble or lose focus in your answer"
                ]
            }
        elif question_type.lower() == 'company':
            return {
                'dos': [
                    "Show you've researched the company thoroughly",
                    "Connect your skills to the specific role",
                    "Express authentic enthusiasm for the opportunity",
                    "Ask thoughtful questions about the role or company",
                    "Demonstrate alignment with company values"
                ],
                'donts': [
                    "Don't give generic answers that could apply to any company",
                    "Avoid focusing only on what the company can do for you",
                    "Don't mention salary or benefits as your primary motivation",
                    "Avoid mentioning only surface-level company facts",
                    "Don't express uncertainty about whether the role is right for you"
                ]
            }
        else:  # General or difficult questions
            return {
                'dos': [
                    "Be honest and authentic in your answers",
                    "Stay positive and solution-focused",
                    "Take a moment to gather your thoughts if needed",
                    "Provide specific examples to support your points",
                    "Maintain good eye contact and positive body language"
                ],
                'donts': [
                    "Don't badmouth previous employers or colleagues",
                    "Avoid being defensive or argumentative",
                    "Don't provide overly personal information",
                    "Avoid memorized or scripted-sounding answers",
                    "Don't rush through difficult questions"
                ]
            }
    
    def _generate_technical_answer_example(self, question_text):
        """
        Generate an example answer for a technical question.
        
        Args:
            question_text (str): Technical question
            
        Returns:
            str: Example answer or None if not applicable
        """
        # Basic examples for common technical questions
        if "experience with" in question_text.lower():
            technology = re.search(r"experience with ([^?,.]+)", question_text.lower())
            if technology:
                tech = technology.group(1).strip()
                return f"""
                I've been working with {tech} for about 3 years across multiple projects. Most notably, I used {tech} to build a data processing pipeline at my previous company that reduced report generation time by 40%.

                The key aspects of {tech} that I find most valuable are its [specific features/capabilities]. When implementing solutions with {tech}, I focus on [best practices] to ensure maintainability and performance.

                For example, in one particularly challenging project, we needed to [specific problem]. I approached this by [specific solution using the technology], which resulted in [specific positive outcome].

                I stay current with the latest developments in {tech} through [mention resources, communities, or practices], which has helped me continue to improve my implementation strategies over time.
                """
                
        if "debug" in question_text.lower():
            return """
            When debugging complex issues, I follow a systematic approach:

            First, I reproduce the issue to understand exactly what's happening. I isolate when and where the problem occurs by using logging, monitoring tools, or debuggers depending on the environment.

            Next, I gather information by checking logs, error messages, and recent code changes. I look for patterns in the data and form hypotheses about what might be causing the issue.

            Then I test each hypothesis methodically, starting with the most likely causes. I make small, focused changes and validate their impact.

            For particularly challenging bugs, I sometimes use rubber duck debugging or collaborate with colleagues to get fresh perspectives.

            For example, in my previous role, we faced an intermittent performance issue in our payment processing system. After methodical investigation, I discovered a database query that wasn't properly indexed, causing occasional timeouts during peak loads. By adding the appropriate index, we improved response times by 70% and eliminated the timeout errors.

            I also document the root cause and solution thoroughly to build our team's knowledge base and prevent similar issues in the future.
            """
                
        if "architecture" in question_text.lower() or "system design" in question_text.lower():
            return """
            When designing system architecture, I follow a methodical approach that balances immediate requirements with long-term flexibility.

            I start by clearly understanding the functional and non-functional requirements, including performance expectations, scalability needs, security considerations, and budget constraints.

            For example, on a recent e-commerce project, we needed to handle high traffic spikes during sales events while maintaining consistent performance. I designed a microservices architecture that separated critical components like product catalog, user authentication, and order processing.

            For the database layer, I chose a hybrid approach: using PostgreSQL for transactional data that required ACID compliance, and Redis for caching frequently accessed data to reduce database load.

            We implemented horizontal scaling for stateless services and used message queues (RabbitMQ) to handle asynchronous processing for non-critical operations like email notifications and analytics.

            For deployment, we containerized the services using Docker and orchestrated them with Kubernetes to allow for automated scaling based on traffic patterns.

            The architecture proved successful, allowing the system to handle a 500% increase in traffic during promotional events with less than 5% increase in response time, while also providing the flexibility to evolve individual components as business needs changed.

            The key trade-offs we considered were development complexity versus operational flexibility, and immediate performance versus long-term maintainability. The microservices approach required more initial setup but gave us significant advantages in independent scaling and technology flexibility.
            """
        
        # Default example if no specific match
        return None
    
    def _generate_behavioral_answer_example(self, question_text):
        """
        Generate an example answer for a behavioral question.
        
        Args:
            question_text (str): Behavioral question
            
        Returns:
            str: Example answer or None if not applicable
        """
        if "challenge" in question_text.lower() or "difficult project" in question_text.lower():
            return """
            Situation: At my previous company, we were tasked with migrating our legacy payment processing system to a new platform while ensuring zero downtime. This was particularly challenging because the system processed over 10,000 transactions daily, and any interruption would significantly impact our business and customers.

            Task: As the technical lead, I was responsible for creating and executing the migration plan, coordinating with multiple teams, and ensuring data integrity throughout the process.

            Action: First, I conducted a thorough analysis of the existing system to identify all integration points and potential risks. I then designed a phased migration approach rather than a single cutover. I created a detailed project plan with specific milestones and contingency plans.

            I implemented a parallel processing mechanism where transactions would be processed by both systems simultaneously for a validation period. I wrote comprehensive test suites to verify data consistency between the old and new systems. I also established automated monitoring to quickly identify any discrepancies.

            To minimize risk, I scheduled the critical transition phases during low-traffic periods and assembled a cross-functional "war room" team that could quickly address any issues that arose.

            Result: We successfully completed the migration with zero downtime and no data loss. The new system improved processing speed by 35% and reduced error rates by 25%. My phased approach became a template for other critical migrations within the company. Additionally, the monitoring tools I developed continued to provide value for system health tracking long after the migration was complete.
            """
            
        if "conflict" in question_text.lower() or "disagreement" in question_text.lower():
            return """
            Situation: While working on a web application redesign project, there was a significant disagreement between the UX design team and the development team regarding the implementation of a new feature. The design team proposed an interactive element that would require complex custom JavaScript, while the development team believed it would create performance issues and delay our tight launch timeline.

            Task: As the project lead straddling both teams, I needed to resolve this conflict constructively while keeping the project on track and maintaining team cohesion.

            Action: Rather than picking a side, I facilitated a structured discussion between both teams. First, I asked each team to clearly articulate their concerns and priorities. The design team emphasized user experience and engagement metrics, while the development team focused on performance benchmarks and maintenance concerns.

            I suggested we create a simple prototype to test both approaches. We used this to collect actual performance data and conducted brief user testing sessions. I ensured the discussion remained focused on objective criteria rather than personal preferences.

            I then worked with both teams to develop a compromise solution that incorporated the core interactive elements the design team wanted, but implemented them using established libraries rather than custom code, addressing the development team's maintenance concerns.

            Result: The compromise solution satisfied both teams' primary concerns. The feature launched on time with 90% of the originally designed functionality but required 40% less development time than the original estimate. Performance testing showed the compromise solution actually outperformed both original proposals. Most importantly, both teams felt their expertise was respected, which improved collaboration on subsequent projects. User feedback on the feature was overwhelmingly positive, with engagement metrics exceeding our targets by 15%.
            """
            
        if "mistake" in question_text.lower() or "failure" in question_text.lower():
            return """
            Situation: Early in my career as a software developer, I was working on implementing a new feature for our company's customer management system. The feature needed to be completed within two weeks for a major client demo.

            Task: I was responsible for developing the entire feature, including database changes, backend logic, and frontend implementation.

            Action: I was confident in my abilities and eager to impress, so I jumped straight into coding without thoroughly reviewing the requirements or creating a detailed plan. I also didn't consult with more experienced team members about my approach, believing I could handle it independently.

            As the deadline approached, I realized I had misinterpreted a key requirement, which meant a significant portion of my work wouldn't meet the client's needs. Rather than immediately alerting my manager, I tried to fix everything myself by working late nights.

            Two days before the demo, I finally admitted to my team lead that I had made a critical error and wouldn't be able to complete the feature as required.

            Result: The team had to scramble to implement a partial solution for the demo. While we managed to show core functionality, it wasn't the polished feature we had promised.

            This experience taught me several valuable lessons. First, I learned the importance of thorough planning and requirement analysis before starting implementation. Second, I recognized that asking for help early is a strength, not a weakness. Third, I understood the importance of transparent communication, especially when problems arise.

            Following this incident, I created a personal development plan that included regular check-ins during projects and establishing clear milestones. On subsequent projects, I implemented a "requirements confirmation" step where I would review my understanding with stakeholders before starting work.

            Six months later, I successfully led the complete implementation of the feature, which was well-received by clients and is now one of our platform's most-used capabilities.
            """
        
        # Default example if no specific match
        return None
    
    def _generate_company_answer_example(self, question_text):
        """
        Generate an example answer for a company/role question.
        
        Args:
            question_text (str): Company/role question
            
        Returns:
            str: Example answer or None if not applicable
        """
        if "why are you interested" in question_text.lower() or "why do you want to work" in question_text.lower():
            return """
            I'm particularly interested in joining [Company Name] for three key reasons.

            First, I'm impressed by your commitment to innovation in [specific area]. I've followed your development of [specific product/service] and how it's transforming [industry specifics]. This aligns perfectly with my professional interest in [relevant area of expertise].

            Second, I value your company culture that emphasizes [mention specific values from their website/communications]. In my research, I was particularly impressed by [specific initiative or approach], which resonates with my own professional values of [relevant personal values].

            Finally, this specific role as [position name] presents the ideal opportunity to apply my experience in [relevant skill/experience] while growing in [new challenge or skill area]. I'm excited about contributing to projects like [mention specific company initiative if known] where I can make an immediate impact while continuing to develop professionally.

            What particularly stood out to me was your recent [mention specific company news, product launch, or achievement], which demonstrates the kind of forward-thinking approach I'm looking to be part of.
            """
            
        if "strengths and weaknesses" in question_text.lower() or "greatest weakness" in question_text.lower():
            return """
            One of my key strengths is my analytical problem-solving ability. I excel at breaking down complex challenges into manageable components. For example, at my previous company, I restructured our data processing pipeline that was causing performance bottlenecks. By methodically analyzing each component, I identified and resolved issues that improved processing speed by 40%.

            I'm also particularly strong in cross-functional collaboration. I believe that diverse perspectives lead to better solutions, and I've consistently built strong working relationships across teams. This was especially valuable when I led a project that required coordination between marketing, product, and development teams.

            Regarding areas for improvement, my biggest challenge has been delegation. As someone who values quality and precision, I've sometimes taken on too much responsibility instead of trusting team members with critical tasks. I recognized this was limiting both my effectiveness and my team's growth.

            To address this, I've been working deliberately on improving my delegation skills. I've implemented a structured approach where I identify tasks that others could handle, match them with team members' development goals, and provide clear expectations while remaining available for support. I've also been taking a leadership course that focuses on effective delegation and team empowerment.

            This conscious effort has already shown positive results. On my most recent project, I delegated 30% more tasks than usual, which allowed me to focus on strategic priorities while giving team members valuable growth opportunities. The project was completed ahead of schedule, and team members reported higher satisfaction with their roles.
            """
            
        if "5 years" in question_text.lower() or "five years" in question_text.lower():
            return """
            In five years, I envision myself having progressed to a senior or lead position where I can combine my technical expertise with leadership responsibilities. I'm particularly interested in growing into a role where I can continue to contribute technically while also mentoring junior team members and helping shape technical strategy.

            I see this position at [Company] as an excellent foundation for that path. The [specific technologies/projects] you're working with align with where I believe the industry is heading, and I'm excited about deepening my expertise in these areas.

            I'm also committed to continuous learning. Over the next few years, I plan to expand my knowledge in [relevant emerging technology or skill] through both formal education and hands-on experience. I've already begun this journey by [mention relevant recent learning activity].

            What attracts me to growing with [Company] specifically is your [mention something about company growth trajectory, innovation culture, or professional development opportunities]. I'm impressed by how [specific employee or team] has been able to develop their career here, and I hope to follow a similar trajectory while making significant contributions to the company's success.

            Ultimately, I want to be in a position where I'm recognized as both a technical expert and an effective leader who helps drive innovation while developing the next generation of talent.
            """
        
        # Default example if no specific match
        return None
    
    def _generate_difficult_answer_example(self, question_text):
        """
        Generate an example answer for a difficult question.
        
        Args:
            question_text (str): Difficult question
            
        Returns:
            str: Example answer or None if not applicable
        """
        if "fired" in question_text.lower() or "terminated" in question_text.lower():
            return """
            Yes, I was let go from my position at [Previous Company] about two years ago. It was a difficult experience but one that ultimately led to valuable growth in my career.

            The company was going through a significant restructuring, and my entire department was affected. While performance was a factor in deciding which team members would be retained, I also recognize that I could have been more proactive in adapting to the company's changing priorities.

            After this experience, I took time to reflect on how I could improve. I invested in developing additional technical skills that were in high demand, specifically [mention relevant skills]. I also worked on improving my communication with management to ensure better alignment with company objectives.

            In my next role at [Current/Recent Company], I applied these lessons directly. I established regular check-ins with my manager to ensure my priorities remained aligned with team goals, and I took a more proactive approach to addressing challenges. This resulted in consistently positive performance reviews and being selected to lead several key projects.

            While losing that position was challenging at the time, I'm grateful for the growth opportunity it provided. It helped me become a more adaptable and communicative professional, skills that I believe will be valuable in this role at your company.
            """
            
        if "overqualified" in question_text.lower():
            return """
            I understand why my experience might raise that question. While I do have extensive background in [relevant field], I'm particularly interested in this role with your company for several specific reasons.

            First, I'm at a point in my career where I'm looking for the right fit in terms of company culture and values rather than simply a title or compensation package. Your company's mission of [company mission] and approach to [relevant aspect] strongly resonates with me, and that alignment is a priority for me in my next role.

            Second, this position offers unique opportunities that my previous roles haven't. Specifically, I'm excited about [mention specific aspects of the role or company that are genuinely new or different for you].

            I see my experience as an asset that would allow me to contribute quickly while taking on new challenges. For example, my background in [relevant experience] would help me understand the [specific aspect of the role], but I'm equally excited to develop new skills in [area that would be new to you].

            I'm committed to long-term growth with a company where I can add significant value, and I see this role as an excellent foundation for that journey. I'm looking for a position where I can both contribute from day one and continue to learn and develop, which is exactly what this role offers.
            """
            
        if "gap" in question_text.lower() and ("employment" in question_text.lower() or "resume" in question_text.lower()):
            return """
            Yes, there was a one-year gap in my employment between my roles at [Previous Company] and [Current/Recent Company]. This was a planned break that I took for two main purposes.

            First, I used six months of this time to care for a family member who was facing health challenges. This was a priority for me, and I'm grateful I was able to be present during that important time.

            During the latter part of this period, I took the opportunity to update my technical skills to better align with where I saw the industry heading. I completed [specific certification or course] and worked on several personal projects to apply these new skills practically.

            One project I'm particularly proud of was [briefly describe a relevant personal project], which allowed me to develop hands-on experience with [relevant technologies]. This project actually helped me secure my position at [Current/Recent Company] as I was able to demonstrate both my technical abilities and self-directed learning.

            This break proved valuable both personally and professionally. I returned to the workforce with renewed energy, updated skills, and clearer focus on where I wanted to take my career. The experience reinforced my ability to adapt and learn independently, which I believe are valuable qualities I'd bring to this role.
            """
        
        # Default example if no specific match
        return None