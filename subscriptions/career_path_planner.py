"""
Career Path Planning System

This module provides comprehensive career path planning for Pro users.
It analyzes current career positions and offers detailed guidance on potential
progression paths, required skills, certifications, and timeline estimates.

Key features:
- Multiple career path options based on current role
- Skill gap analysis and learning recommendations
- Personalized timeline estimates
- Industry-specific guidance
- Interactive career mapping
"""

import logging
import re
import json
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

from .data_resources import DataResources
from .text_processor import TextProcessor

class CareerPathPlanner:
    """
    Provides advanced career path planning and progression guidance for Pro users.
    
    This class leverages industry data, role mapping, and skill requirements to
    generate detailed career progression paths with actionable recommendations.
    """
    
    def __init__(self):
        """Initialize the CareerPathPlanner with necessary resources."""
        self.logger = logging.getLogger(__name__)
        self.data_resources = DataResources()
        self.text_processor = TextProcessor()
        
        # Load career data from resources
        self._career_paths = self._load_career_paths()
        self._skill_requirements = self._load_skill_requirements()
        self._certifications = self._load_certifications()
        self._industry_transitions = self._load_industry_transitions()
        self._salary_progression = self._load_salary_progression()
        self._learning_resources = self._load_learning_resources()
        
    def _load_career_paths(self) -> Dict[str, Dict[str, Any]]:
        """
        Load career path data for different industries and roles.
        
        In a production environment, this would load from a database or external API.
        For this implementation, we use synthetic data based on research.
        """
        # Structure: {industry: {role: {next_roles: [], typical_duration: ""}}}
        career_paths = {
            # Technology industry
            "technology": {
                "junior_developer": {
                    "next_roles": ["mid_level_developer", "quality_assurance_engineer", "devops_engineer"],
                    "typical_duration": "1-2 years",
                    "required_experience": 0,
                    "description": "Entry-level position focused on building foundational programming skills and understanding software development lifecycle.",
                },
                "mid_level_developer": {
                    "next_roles": ["senior_developer", "technical_lead", "devops_engineer", "product_manager"],
                    "typical_duration": "2-3 years",
                    "required_experience": 2,
                    "description": "Intermediate position handling more complex tasks, mentoring junior developers, and participating in architectural decisions.",
                },
                "senior_developer": {
                    "next_roles": ["technical_lead", "software_architect", "engineering_manager", "product_manager"],
                    "typical_duration": "3-5 years",
                    "required_experience": 5,
                    "description": "Advanced position leading development efforts, making significant architectural decisions, and mentoring other developers.",
                },
                "technical_lead": {
                    "next_roles": ["software_architect", "engineering_manager", "cto", "director_of_engineering"],
                    "typical_duration": "2-4 years",
                    "required_experience": 8,
                    "description": "Leadership position guiding technical direction, managing small teams, and bridging technical and business requirements.",
                },
                "software_architect": {
                    "next_roles": ["principal_architect", "engineering_manager", "cto", "technical_director"],
                    "typical_duration": "3-5 years",
                    "required_experience": 10,
                    "description": "Specialized position designing complex systems, establishing technical standards, and providing technical governance.",
                },
                "engineering_manager": {
                    "next_roles": ["director_of_engineering", "vp_of_engineering", "cto"],
                    "typical_duration": "3-6 years",
                    "required_experience": 10,
                    "description": "Management position overseeing engineering teams, coordinating project delivery, and aligning with business objectives.",
                },
                "devops_engineer": {
                    "next_roles": ["devops_manager", "site_reliability_engineer", "cloud_architect"],
                    "typical_duration": "2-3 years",
                    "required_experience": 2,
                    "description": "Specialized position focused on deployment automation, infrastructure management, and operational excellence.",
                },
                "data_scientist": {
                    "next_roles": ["senior_data_scientist", "machine_learning_engineer", "ai_researcher", "data_science_manager"],
                    "typical_duration": "2-3 years",
                    "required_experience": 1,
                    "description": "Analytical position using statistical methods and machine learning to extract insights from data.",
                },
                "senior_data_scientist": {
                    "next_roles": ["data_science_manager", "ai_research_lead", "chief_data_scientist"],
                    "typical_duration": "3-5 years",
                    "required_experience": 4,
                    "description": "Advanced analytical position leading complex data projects and developing sophisticated machine learning models.",
                },
                "product_manager": {
                    "next_roles": ["senior_product_manager", "director_of_product", "vp_of_product"],
                    "typical_duration": "2-4 years",
                    "required_experience": 3,
                    "description": "Cross-functional position defining product vision, prioritizing features, and coordinating development efforts.",
                },
                "ux_designer": {
                    "next_roles": ["senior_ux_designer", "ux_manager", "product_designer", "creative_director"],
                    "typical_duration": "2-3 years",
                    "required_experience": 1,
                    "description": "Creative position focused on user research, interface design, and improving user experience.",
                },
                "quality_assurance_engineer": {
                    "next_roles": ["qa_lead", "test_automation_engineer", "devops_engineer", "mid_level_developer"],
                    "typical_duration": "1-3 years",
                    "required_experience": 0,
                    "description": "Testing position ensuring software quality through manual and automated testing strategies.",
                },
                # Default for unknown roles in technology
                "default": {
                    "next_roles": ["senior_position", "management_track", "specialist_track"],
                    "typical_duration": "2-3 years",
                    "required_experience": 2,
                    "description": "Standard technology career progression from junior to senior to management or specialized roles.",
                }
            },
            
            # Finance industry
            "finance": {
                "financial_analyst": {
                    "next_roles": ["senior_financial_analyst", "investment_analyst", "finance_manager"],
                    "typical_duration": "2-3 years",
                    "required_experience": 0,
                    "description": "Entry-level position analyzing financial data, preparing reports, and supporting business decisions.",
                },
                "senior_financial_analyst": {
                    "next_roles": ["finance_manager", "investment_manager", "financial_controller"],
                    "typical_duration": "2-4 years",
                    "required_experience": 3,
                    "description": "Advanced analytical position leading financial analyses, forecasting, and providing strategic recommendations.",
                },
                "finance_manager": {
                    "next_roles": ["finance_director", "controller", "chief_financial_officer"],
                    "typical_duration": "3-5 years",
                    "required_experience": 5,
                    "description": "Management position overseeing financial operations, budgeting, and financial strategy.",
                },
                "investment_banker": {
                    "next_roles": ["associate", "vice_president", "director", "managing_director"],
                    "typical_duration": "2-3 years",
                    "required_experience": 0,
                    "description": "Advisory position helping clients raise capital, execute mergers and acquisitions, and provide financial guidance.",
                },
                # Default for unknown roles in finance
                "default": {
                    "next_roles": ["senior_position", "management_track", "specialist_track"],
                    "typical_duration": "2-3 years",
                    "required_experience": 2,
                    "description": "Standard finance career progression from analyst to senior analyst to management or specialized roles.",
                }
            },
            
            # Healthcare industry
            "healthcare": {
                "registered_nurse": {
                    "next_roles": ["nurse_practitioner", "nurse_manager", "clinical_specialist"],
                    "typical_duration": "2-4 years",
                    "required_experience": 1,
                    "description": "Clinical position providing direct patient care, administering treatments, and coordinating with healthcare team.",
                },
                "nurse_practitioner": {
                    "next_roles": ["clinical_director", "healthcare_administrator", "nursing_director"],
                    "typical_duration": "3-5 years",
                    "required_experience": 5,
                    "description": "Advanced clinical position diagnosing and treating patients, prescribing medications, and providing primary care.",
                },
                "physician": {
                    "next_roles": ["specialist_physician", "medical_director", "chief_medical_officer"],
                    "typical_duration": "5-7 years",
                    "required_experience": 4,
                    "description": "Medical position diagnosing and treating patients, performing procedures, and directing care plans.",
                },
                # Default for unknown roles in healthcare
                "default": {
                    "next_roles": ["senior_position", "management_track", "specialist_track"],
                    "typical_duration": "2-4 years",
                    "required_experience": 2,
                    "description": "Standard healthcare career progression from entry-level to specialist or management roles.",
                }
            },
            
            # Marketing industry
            "marketing": {
                "marketing_coordinator": {
                    "next_roles": ["marketing_specialist", "digital_marketing_specialist", "content_marketer"],
                    "typical_duration": "1-2 years",
                    "required_experience": 0,
                    "description": "Entry-level position supporting marketing campaigns, events, and content creation.",
                },
                "marketing_specialist": {
                    "next_roles": ["marketing_manager", "brand_manager", "product_marketing_manager"],
                    "typical_duration": "2-3 years",
                    "required_experience": 2,
                    "description": "Focused position implementing marketing strategies, analyzing campaign performance, and managing specific channels.",
                },
                "marketing_manager": {
                    "next_roles": ["senior_marketing_manager", "marketing_director", "vp_of_marketing"],
                    "typical_duration": "3-5 years",
                    "required_experience": 4,
                    "description": "Management position developing marketing strategies, overseeing campaigns, and coordinating marketing teams.",
                },
                "content_strategist": {
                    "next_roles": ["content_manager", "content_director", "digital_marketing_manager"],
                    "typical_duration": "2-3 years",
                    "required_experience": 2,
                    "description": "Specialized position planning content initiatives, creating editorial calendars, and measuring content performance.",
                },
                # Default for unknown roles in marketing
                "default": {
                    "next_roles": ["senior_position", "management_track", "specialist_track"],
                    "typical_duration": "2-3 years",
                    "required_experience": 2,
                    "description": "Standard marketing career progression from coordinator to specialist to management roles.",
                }
            },
            
            # Default for other industries
            "default": {
                "entry_level": {
                    "next_roles": ["mid_level", "specialist_track"],
                    "typical_duration": "1-3 years",
                    "required_experience": 0,
                    "description": "Entry-level position building foundational skills and knowledge in the field.",
                },
                "mid_level": {
                    "next_roles": ["senior_level", "management_track", "specialist_track"],
                    "typical_duration": "2-4 years",
                    "required_experience": 3,
                    "description": "Intermediate position with increased responsibilities and deeper expertise.",
                },
                "senior_level": {
                    "next_roles": ["leadership", "management_track", "expert_track"],
                    "typical_duration": "3-5 years",
                    "required_experience": 5,
                    "description": "Advanced position leading initiatives, mentoring others, and contributing to strategic decisions.",
                },
                "management_track": {
                    "next_roles": ["director_level", "executive_level"],
                    "typical_duration": "3-6 years",
                    "required_experience": 8,
                    "description": "Leadership position managing teams, operations, and aligning with organizational objectives.",
                },
                "default": {
                    "next_roles": ["senior_position", "management_position", "specialist_position"],
                    "typical_duration": "2-4 years",
                    "required_experience": 2,
                    "description": "Standard career progression from entry-level to senior to management or specialized roles.",
                }
            }
        }
        
        return career_paths
    
    def _load_skill_requirements(self) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """
        Load skill requirements for different roles and industries.
        """
        skill_requirements = {
            # Technology industry
            "technology": {
                "junior_developer": [
                    {"name": "Programming fundamentals", "importance": "essential", "difficulty": "medium"},
                    {"name": "Basic algorithms and data structures", "importance": "essential", "difficulty": "medium"},
                    {"name": "Version control (Git)", "importance": "essential", "difficulty": "low"},
                    {"name": "Basic database knowledge", "importance": "important", "difficulty": "medium"},
                    {"name": "HTML/CSS", "importance": "helpful", "difficulty": "low"},
                    {"name": "Problem-solving", "importance": "essential", "difficulty": "medium"},
                    {"name": "Communication", "importance": "important", "difficulty": "medium"}
                ],
                "mid_level_developer": [
                    {"name": "Advanced programming concepts", "importance": "essential", "difficulty": "high"},
                    {"name": "Software architecture principles", "importance": "important", "difficulty": "high"},
                    {"name": "Testing methodologies", "importance": "important", "difficulty": "medium"},
                    {"name": "Database design", "importance": "important", "difficulty": "medium"},
                    {"name": "APIs and integrations", "importance": "essential", "difficulty": "medium"},
                    {"name": "Code optimization", "importance": "important", "difficulty": "high"},
                    {"name": "Mentoring", "importance": "helpful", "difficulty": "medium"}
                ],
                "senior_developer": [
                    {"name": "System design", "importance": "essential", "difficulty": "high"},
                    {"name": "Technical leadership", "importance": "essential", "difficulty": "high"},
                    {"name": "Performance optimization", "importance": "important", "difficulty": "high"},
                    {"name": "Security best practices", "importance": "important", "difficulty": "high"},
                    {"name": "Architectural patterns", "importance": "essential", "difficulty": "high"},
                    {"name": "CI/CD technologies", "importance": "important", "difficulty": "medium"},
                    {"name": "Project management", "importance": "important", "difficulty": "medium"}
                ],
                "product_manager": [
                    {"name": "Market research", "importance": "essential", "difficulty": "medium"},
                    {"name": "User experience principles", "importance": "essential", "difficulty": "medium"},
                    {"name": "Agile methodologies", "importance": "essential", "difficulty": "medium"},
                    {"name": "Product roadmapping", "importance": "essential", "difficulty": "high"},
                    {"name": "Data analysis", "importance": "important", "difficulty": "medium"},
                    {"name": "Stakeholder management", "importance": "essential", "difficulty": "high"},
                    {"name": "Technical understanding", "importance": "important", "difficulty": "medium"}
                ],
                "data_scientist": [
                    {"name": "Statistics", "importance": "essential", "difficulty": "high"},
                    {"name": "Python or R", "importance": "essential", "difficulty": "medium"},
                    {"name": "Machine learning", "importance": "essential", "difficulty": "high"},
                    {"name": "Data visualization", "importance": "important", "difficulty": "medium"},
                    {"name": "SQL", "importance": "important", "difficulty": "medium"},
                    {"name": "Data cleaning", "importance": "essential", "difficulty": "medium"},
                    {"name": "Experimental design", "importance": "important", "difficulty": "high"}
                ],
                "default": [
                    {"name": "Technical knowledge", "importance": "essential", "difficulty": "medium"},
                    {"name": "Problem-solving", "importance": "essential", "difficulty": "medium"},
                    {"name": "Communication", "importance": "important", "difficulty": "medium"},
                    {"name": "Continuous learning", "importance": "essential", "difficulty": "medium"}
                ]
            },
            
            # Finance industry
            "finance": {
                "financial_analyst": [
                    {"name": "Financial modeling", "importance": "essential", "difficulty": "high"},
                    {"name": "Excel proficiency", "importance": "essential", "difficulty": "medium"},
                    {"name": "Accounting principles", "importance": "essential", "difficulty": "medium"},
                    {"name": "Financial statement analysis", "importance": "essential", "difficulty": "medium"},
                    {"name": "Valuation methods", "importance": "important", "difficulty": "high"},
                    {"name": "Industry analysis", "importance": "important", "difficulty": "medium"},
                    {"name": "Data visualization", "importance": "helpful", "difficulty": "medium"}
                ],
                "investment_banker": [
                    {"name": "Financial modeling", "importance": "essential", "difficulty": "high"},
                    {"name": "Valuation techniques", "importance": "essential", "difficulty": "high"},
                    {"name": "Merger & acquisition analysis", "importance": "essential", "difficulty": "high"},
                    {"name": "Capital markets knowledge", "importance": "essential", "difficulty": "high"},
                    {"name": "Presentation skills", "importance": "essential", "difficulty": "medium"},
                    {"name": "Negotiation", "importance": "important", "difficulty": "high"},
                    {"name": "Financial modeling", "importance": "essential", "difficulty": "high"}
                ],
                "default": [
                    {"name": "Financial knowledge", "importance": "essential", "difficulty": "medium"},
                    {"name": "Analytical thinking", "importance": "essential", "difficulty": "medium"},
                    {"name": "Attention to detail", "importance": "essential", "difficulty": "medium"},
                    {"name": "Communication", "importance": "important", "difficulty": "medium"}
                ]
            },
            
            # Healthcare industry
            "healthcare": {
                "registered_nurse": [
                    {"name": "Patient assessment", "importance": "essential", "difficulty": "high"},
                    {"name": "Clinical procedures", "importance": "essential", "difficulty": "high"},
                    {"name": "Medical terminology", "importance": "essential", "difficulty": "medium"},
                    {"name": "Patient education", "importance": "important", "difficulty": "medium"},
                    {"name": "Electronic health records", "importance": "important", "difficulty": "medium"},
                    {"name": "Critical thinking", "importance": "essential", "difficulty": "high"},
                    {"name": "Compassion and empathy", "importance": "essential", "difficulty": "medium"}
                ],
                "physician": [
                    {"name": "Medical diagnosis", "importance": "essential", "difficulty": "high"},
                    {"name": "Treatment planning", "importance": "essential", "difficulty": "high"},
                    {"name": "Clinical procedures", "importance": "essential", "difficulty": "high"},
                    {"name": "Medical research interpretation", "importance": "important", "difficulty": "high"},
                    {"name": "Patient communication", "importance": "essential", "difficulty": "medium"},
                    {"name": "Medical ethics", "importance": "essential", "difficulty": "medium"},
                    {"name": "Healthcare regulations", "importance": "important", "difficulty": "medium"}
                ],
                "default": [
                    {"name": "Medical knowledge", "importance": "essential", "difficulty": "high"},
                    {"name": "Patient care", "importance": "essential", "difficulty": "medium"},
                    {"name": "Healthcare regulations", "importance": "important", "difficulty": "medium"},
                    {"name": "Empathy", "importance": "essential", "difficulty": "medium"}
                ]
            },
            
            # Marketing industry
            "marketing": {
                "marketing_manager": [
                    {"name": "Marketing strategy", "importance": "essential", "difficulty": "high"},
                    {"name": "Campaign planning", "importance": "essential", "difficulty": "medium"},
                    {"name": "Analytics and measurement", "importance": "essential", "difficulty": "medium"},
                    {"name": "Digital marketing", "importance": "important", "difficulty": "medium"},
                    {"name": "Budget management", "importance": "important", "difficulty": "medium"},
                    {"name": "Brand management", "importance": "important", "difficulty": "medium"},
                    {"name": "Team leadership", "importance": "important", "difficulty": "high"}
                ],
                "content_strategist": [
                    {"name": "Content planning", "importance": "essential", "difficulty": "medium"},
                    {"name": "SEO knowledge", "importance": "essential", "difficulty": "medium"},
                    {"name": "Copywriting", "importance": "essential", "difficulty": "medium"},
                    {"name": "Content analytics", "importance": "important", "difficulty": "medium"},
                    {"name": "Audience research", "importance": "important", "difficulty": "medium"},
                    {"name": "Editorial calendar management", "importance": "important", "difficulty": "low"},
                    {"name": "Content management systems", "importance": "helpful", "difficulty": "low"}
                ],
                "default": [
                    {"name": "Marketing fundamentals", "importance": "essential", "difficulty": "medium"},
                    {"name": "Communication", "importance": "essential", "difficulty": "medium"},
                    {"name": "Creativity", "importance": "important", "difficulty": "medium"},
                    {"name": "Data analysis", "importance": "important", "difficulty": "medium"}
                ]
            },
            
            # Default for other industries
            "default": {
                "entry_level": [
                    {"name": "Fundamental knowledge", "importance": "essential", "difficulty": "medium"},
                    {"name": "Basic technical skills", "importance": "essential", "difficulty": "medium"},
                    {"name": "Communication", "importance": "important", "difficulty": "medium"},
                    {"name": "Time management", "importance": "important", "difficulty": "medium"}
                ],
                "mid_level": [
                    {"name": "Advanced technical skills", "importance": "essential", "difficulty": "medium"},
                    {"name": "Problem-solving", "importance": "essential", "difficulty": "medium"},
                    {"name": "Project management", "importance": "important", "difficulty": "medium"},
                    {"name": "Team collaboration", "importance": "important", "difficulty": "medium"}
                ],
                "senior_level": [
                    {"name": "Expert technical skills", "importance": "essential", "difficulty": "high"},
                    {"name": "Strategic thinking", "importance": "essential", "difficulty": "high"},
                    {"name": "Mentoring", "importance": "important", "difficulty": "medium"},
                    {"name": "Decision making", "importance": "essential", "difficulty": "high"}
                ],
                "management_track": [
                    {"name": "Leadership", "importance": "essential", "difficulty": "high"},
                    {"name": "Team management", "importance": "essential", "difficulty": "high"},
                    {"name": "Budget planning", "importance": "important", "difficulty": "medium"},
                    {"name": "Strategic planning", "importance": "essential", "difficulty": "high"}
                ],
                "default": [
                    {"name": "Industry knowledge", "importance": "essential", "difficulty": "medium"},
                    {"name": "Technical skills", "importance": "important", "difficulty": "medium"},
                    {"name": "Communication", "importance": "important", "difficulty": "medium"},
                    {"name": "Problem solving", "importance": "important", "difficulty": "medium"}
                ]
            }
        }
        
        return skill_requirements
    
    def _load_certifications(self) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """
        Load certification recommendations for different roles and industries.
        """
        certifications = {
            # Technology industry
            "technology": {
                "junior_developer": [
                    {"name": "AWS Certified Cloud Practitioner", "value": "medium", "difficulty": "low", "time_investment": "1-2 months"},
                    {"name": "Microsoft Certified: Azure Fundamentals", "value": "medium", "difficulty": "low", "time_investment": "1-2 months"},
                    {"name": "CompTIA IT Fundamentals", "value": "low", "difficulty": "low", "time_investment": "1 month"}
                ],
                "mid_level_developer": [
                    {"name": "AWS Certified Developer", "value": "high", "difficulty": "medium", "time_investment": "2-3 months"},
                    {"name": "Microsoft Certified: Azure Developer Associate", "value": "high", "difficulty": "medium", "time_investment": "2-3 months"},
                    {"name": "Professional Scrum Developer", "value": "medium", "difficulty": "medium", "time_investment": "1-2 months"}
                ],
                "senior_developer": [
                    {"name": "AWS Certified Solutions Architect", "value": "high", "difficulty": "high", "time_investment": "3-6 months"},
                    {"name": "Google Professional Cloud Architect", "value": "high", "difficulty": "high", "time_investment": "3-6 months"},
                    {"name": "Certified Kubernetes Administrator", "value": "high", "difficulty": "high", "time_investment": "2-4 months"}
                ],
                "technical_lead": [
                    {"name": "AWS Certified DevOps Engineer", "value": "high", "difficulty": "high", "time_investment": "3-6 months"},
                    {"name": "Certified Scrum Master", "value": "medium", "difficulty": "medium", "time_investment": "1-2 months"},
                    {"name": "Project Management Professional (PMP)", "value": "high", "difficulty": "high", "time_investment": "6-12 months"}
                ],
                "data_scientist": [
                    {"name": "Google Professional Data Engineer", "value": "high", "difficulty": "high", "time_investment": "3-6 months"},
                    {"name": "Microsoft Certified: Azure Data Scientist Associate", "value": "high", "difficulty": "medium", "time_investment": "2-4 months"},
                    {"name": "TensorFlow Developer Certificate", "value": "medium", "difficulty": "medium", "time_investment": "2-3 months"}
                ],
                "product_manager": [
                    {"name": "Certified Scrum Product Owner", "value": "high", "difficulty": "medium", "time_investment": "1-2 months"},
                    {"name": "Product Management Certificate (various institutions)", "value": "medium", "difficulty": "medium", "time_investment": "3-6 months"},
                    {"name": "Pragmatic Marketing Certification", "value": "high", "difficulty": "medium", "time_investment": "1-3 months"}
                ],
                "default": [
                    {"name": "Industry-specific certification", "value": "medium", "difficulty": "medium", "time_investment": "2-3 months"},
                    {"name": "Project management certification", "value": "medium", "difficulty": "medium", "time_investment": "3-6 months"},
                    {"name": "Leadership training", "value": "medium", "difficulty": "medium", "time_investment": "1-3 months"}
                ]
            },
            
            # Finance industry
            "finance": {
                "financial_analyst": [
                    {"name": "Chartered Financial Analyst (CFA)", "value": "high", "difficulty": "high", "time_investment": "18-36 months"},
                    {"name": "Financial Modeling & Valuation Analyst (FMVA)", "value": "medium", "difficulty": "medium", "time_investment": "3-6 months"},
                    {"name": "Certified Financial Planner (CFP)", "value": "medium", "difficulty": "high", "time_investment": "12-18 months"}
                ],
                "investment_banker": [
                    {"name": "Chartered Financial Analyst (CFA)", "value": "high", "difficulty": "high", "time_investment": "18-36 months"},
                    {"name": "Series 79 - Investment Banking Representative", "value": "high", "difficulty": "high", "time_investment": "2-4 months"},
                    {"name": "MBA from top business school", "value": "very high", "difficulty": "very high", "time_investment": "12-24 months"}
                ],
                "default": [
                    {"name": "Finance certification", "value": "high", "difficulty": "high", "time_investment": "6-12 months"},
                    {"name": "Accounting certification", "value": "medium", "difficulty": "high", "time_investment": "6-12 months"},
                    {"name": "Business administration course", "value": "medium", "difficulty": "medium", "time_investment": "3-6 months"}
                ]
            },
            
            # Healthcare industry
            "healthcare": {
                "registered_nurse": [
                    {"name": "Basic Life Support (BLS)", "value": "essential", "difficulty": "low", "time_investment": "1 day"},
                    {"name": "Advanced Cardiac Life Support (ACLS)", "value": "high", "difficulty": "medium", "time_investment": "2-3 days"},
                    {"name": "Specialty nursing certifications", "value": "high", "difficulty": "medium", "time_investment": "3-6 months"}
                ],
                "physician": [
                    {"name": "Board Certification in specialty", "value": "essential", "difficulty": "very high", "time_investment": "1-2 years"},
                    {"name": "Advanced life support certifications", "value": "essential", "difficulty": "medium", "time_investment": "1 week"},
                    {"name": "Continuing Medical Education credits", "value": "required", "difficulty": "medium", "time_investment": "ongoing"}
                ],
                "default": [
                    {"name": "Healthcare certification", "value": "high", "difficulty": "high", "time_investment": "6-12 months"},
                    {"name": "Patient care certification", "value": "medium", "difficulty": "medium", "time_investment": "1-3 months"},
                    {"name": "Healthcare administration course", "value": "medium", "difficulty": "medium", "time_investment": "3-6 months"}
                ]
            },
            
            # Marketing industry
            "marketing": {
                "marketing_manager": [
                    {"name": "Digital Marketing Certification", "value": "high", "difficulty": "medium", "time_investment": "1-3 months"},
                    {"name": "Google Analytics Certification", "value": "medium", "difficulty": "medium", "time_investment": "2-4 weeks"},
                    {"name": "HubSpot Marketing Certification", "value": "medium", "difficulty": "low", "time_investment": "1-2 weeks"}
                ],
                "content_strategist": [
                    {"name": "Content Marketing Certification", "value": "medium", "difficulty": "medium", "time_investment": "1-2 months"},
                    {"name": "SEO Certification", "value": "high", "difficulty": "medium", "time_investment": "1-2 months"},
                    {"name": "Social Media Marketing Certification", "value": "medium", "difficulty": "low", "time_investment": "2-4 weeks"}
                ],
                "default": [
                    {"name": "Marketing certification", "value": "medium", "difficulty": "medium", "time_investment": "1-3 months"},
                    {"name": "Digital marketing course", "value": "medium", "difficulty": "medium", "time_investment": "1-3 months"},
                    {"name": "Analytics certification", "value": "medium", "difficulty": "medium", "time_investment": "1-2 months"}
                ]
            },
            
            # Default for other industries
            "default": {
                "entry_level": [
                    {"name": "Industry-specific foundational certification", "value": "medium", "difficulty": "low", "time_investment": "1-3 months"},
                    {"name": "Basic technical skills course", "value": "medium", "difficulty": "low", "time_investment": "1-2 months"},
                    {"name": "Professional communication course", "value": "low", "difficulty": "low", "time_investment": "2-4 weeks"}
                ],
                "mid_level": [
                    {"name": "Advanced industry certification", "value": "high", "difficulty": "medium", "time_investment": "3-6 months"},
                    {"name": "Project management fundamentals", "value": "medium", "difficulty": "medium", "time_investment": "1-3 months"},
                    {"name": "Technical specialization course", "value": "medium", "difficulty": "medium", "time_investment": "2-4 months"}
                ],
                "senior_level": [
                    {"name": "Expert-level industry certification", "value": "high", "difficulty": "high", "time_investment": "6-12 months"},
                    {"name": "Leadership training", "value": "high", "difficulty": "medium", "time_investment": "3-6 months"},
                    {"name": "Strategic planning course", "value": "medium", "difficulty": "medium", "time_investment": "2-4 months"}
                ],
                "default": [
                    {"name": "Industry certification", "value": "medium", "difficulty": "medium", "time_investment": "3-6 months"},
                    {"name": "Management training", "value": "medium", "difficulty": "medium", "time_investment": "1-3 months"},
                    {"name": "Communication skills course", "value": "low", "difficulty": "low", "time_investment": "1-2 months"}
                ]
            }
        }
        
        return certifications
    
    def _load_industry_transitions(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """
        Load data about transitioning between industries.
        """
        industry_transitions = {
            "technology": {
                "finance": {
                    "difficulty": "medium",
                    "transferable_skills": ["data analysis", "programming", "project management"],
                    "additional_skills_needed": ["financial knowledge", "regulatory understanding", "industry-specific software"],
                    "transition_roles": ["fintech developer", "financial systems analyst", "quantitative analyst"],
                    "time_investment": "6-12 months"
                },
                "healthcare": {
                    "difficulty": "medium-high",
                    "transferable_skills": ["programming", "data management", "systems thinking"],
                    "additional_skills_needed": ["healthcare regulations", "medical terminology", "HIPAA compliance"],
                    "transition_roles": ["healthcare IT specialist", "medical software developer", "health informatics"],
                    "time_investment": "6-18 months"
                },
                "marketing": {
                    "difficulty": "low-medium",
                    "transferable_skills": ["data analysis", "technical understanding", "problem-solving"],
                    "additional_skills_needed": ["creative thinking", "market research", "brand strategy"],
                    "transition_roles": ["digital marketing specialist", "marketing analytics", "martech specialist"],
                    "time_investment": "3-9 months"
                }
            },
            "finance": {
                "technology": {
                    "difficulty": "medium",
                    "transferable_skills": ["analytical thinking", "data analysis", "attention to detail"],
                    "additional_skills_needed": ["programming", "software development lifecycle", "technical tools"],
                    "transition_roles": ["fintech specialist", "financial software analyst", "data analyst"],
                    "time_investment": "6-12 months"
                },
                "healthcare": {
                    "difficulty": "medium-high",
                    "transferable_skills": ["data analysis", "regulatory compliance", "reporting"],
                    "additional_skills_needed": ["healthcare regulations", "medical terminology", "patient care understanding"],
                    "transition_roles": ["healthcare financial analyst", "medical billing specialist", "healthcare administrator"],
                    "time_investment": "9-18 months"
                },
                "marketing": {
                    "difficulty": "medium",
                    "transferable_skills": ["data analysis", "strategic thinking", "business acumen"],
                    "additional_skills_needed": ["creativity", "communication skills", "brand understanding"],
                    "transition_roles": ["financial marketing specialist", "marketing analyst", "product marketing"],
                    "time_investment": "6-12 months"
                }
            },
            "healthcare": {
                "technology": {
                    "difficulty": "high",
                    "transferable_skills": ["attention to detail", "problem-solving", "specialized knowledge"],
                    "additional_skills_needed": ["programming", "technology platforms", "software development"],
                    "transition_roles": ["health informatics", "healthcare software specialist", "medical systems analyst"],
                    "time_investment": "12-24 months"
                },
                "finance": {
                    "difficulty": "medium-high",
                    "transferable_skills": ["attention to detail", "regulatory compliance", "analytical thinking"],
                    "additional_skills_needed": ["financial principles", "accounting", "investment knowledge"],
                    "transition_roles": ["healthcare financial analyst", "medical billing specialist", "health insurance analyst"],
                    "time_investment": "9-18 months"
                },
                "marketing": {
                    "difficulty": "medium",
                    "transferable_skills": ["communication", "patient interactions", "specialized knowledge"],
                    "additional_skills_needed": ["marketing principles", "digital marketing", "content creation"],
                    "transition_roles": ["healthcare marketing specialist", "patient communication coordinator", "healthcare content writer"],
                    "time_investment": "6-12 months"
                }
            },
            "marketing": {
                "technology": {
                    "difficulty": "medium-high",
                    "transferable_skills": ["digital tools", "project management", "user perspective"],
                    "additional_skills_needed": ["programming", "technical knowledge", "systems thinking"],
                    "transition_roles": ["product marketing manager", "UX specialist", "digital product specialist"],
                    "time_investment": "9-18 months"
                },
                "finance": {
                    "difficulty": "high",
                    "transferable_skills": ["data analysis", "strategic thinking", "presentation skills"],
                    "additional_skills_needed": ["financial principles", "regulatory knowledge", "analysis methodologies"],
                    "transition_roles": ["financial communications", "investment relations", "financial product marketing"],
                    "time_investment": "12-24 months"
                },
                "healthcare": {
                    "difficulty": "medium",
                    "transferable_skills": ["communication", "content creation", "audience understanding"],
                    "additional_skills_needed": ["medical terminology", "healthcare regulations", "patient privacy"],
                    "transition_roles": ["healthcare communications", "patient education specialist", "healthcare content strategist"],
                    "time_investment": "6-12 months"
                }
            },
            "default": {
                "technology": {
                    "difficulty": "medium-high",
                    "transferable_skills": ["problem-solving", "analytical thinking", "attention to detail"],
                    "additional_skills_needed": ["programming", "technical skills", "system understanding"],
                    "transition_roles": ["entry-level technical role", "quality assurance", "support specialist"],
                    "time_investment": "9-18 months"
                },
                "finance": {
                    "difficulty": "high",
                    "transferable_skills": ["analytical thinking", "attention to detail", "communication"],
                    "additional_skills_needed": ["financial principles", "regulatory knowledge", "industry software"],
                    "transition_roles": ["entry-level analyst", "financial administrator", "support role"],
                    "time_investment": "12-24 months"
                },
                "healthcare": {
                    "difficulty": "high",
                    "transferable_skills": ["communication", "organization", "empathy"],
                    "additional_skills_needed": ["medical terminology", "healthcare regulations", "patient care principles"],
                    "transition_roles": ["administrative role", "patient coordinator", "support staff"],
                    "time_investment": "12-24 months"
                },
                "marketing": {
                    "difficulty": "medium",
                    "transferable_skills": ["communication", "creativity", "organization"],
                    "additional_skills_needed": ["marketing principles", "digital tools", "analytics"],
                    "transition_roles": ["marketing assistant", "content creator", "social media specialist"],
                    "time_investment": "6-12 months"
                }
            }
        }
        
        return industry_transitions
    
    def _load_salary_progression(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """
        Load data about salary progression in different career paths.
        """
        salary_progression = {
            # Technology industry
            "technology": {
                "developer_path": {
                    "junior_developer": {"range": (60000, 90000), "median": 75000, "growth_rate": 15},
                    "mid_level_developer": {"range": (85000, 130000), "median": 105000, "growth_rate": 10},
                    "senior_developer": {"range": (115000, 180000), "median": 140000, "growth_rate": 8},
                    "technical_lead": {"range": (140000, 210000), "median": 170000, "growth_rate": 7},
                    "software_architect": {"range": (160000, 230000), "median": 190000, "growth_rate": 5}
                },
                "data_path": {
                    "data_analyst": {"range": (65000, 95000), "median": 80000, "growth_rate": 14},
                    "data_scientist": {"range": (90000, 140000), "median": 115000, "growth_rate": 12},
                    "senior_data_scientist": {"range": (125000, 190000), "median": 155000, "growth_rate": 8},
                    "data_science_manager": {"range": (150000, 220000), "median": 180000, "growth_rate": 6}
                },
                "management_path": {
                    "team_lead": {"range": (110000, 160000), "median": 135000, "growth_rate": 9},
                    "engineering_manager": {"range": (140000, 210000), "median": 170000, "growth_rate": 7},
                    "director_of_engineering": {"range": (175000, 250000), "median": 210000, "growth_rate": 5},
                    "vp_of_engineering": {"range": (200000, 300000), "median": 250000, "growth_rate": 4},
                    "cto": {"range": (250000, 400000), "median": 320000, "growth_rate": 3}
                }
            },
            
            # Finance industry
            "finance": {
                "analyst_path": {
                    "financial_analyst": {"range": (65000, 95000), "median": 80000, "growth_rate": 12},
                    "senior_financial_analyst": {"range": (90000, 135000), "median": 110000, "growth_rate": 9},
                    "finance_manager": {"range": (120000, 180000), "median": 145000, "growth_rate": 7},
                    "finance_director": {"range": (150000, 230000), "median": 185000, "growth_rate": 5},
                    "chief_financial_officer": {"range": (200000, 350000), "median": 270000, "growth_rate": 4}
                },
                "investment_path": {
                    "investment_analyst": {"range": (75000, 110000), "median": 90000, "growth_rate": 15},
                    "associate": {"range": (100000, 160000), "median": 130000, "growth_rate": 12},
                    "vice_president": {"range": (150000, 250000), "median": 190000, "growth_rate": 8},
                    "director": {"range": (200000, 350000), "median": 270000, "growth_rate": 6},
                    "managing_director": {"range": (300000, 500000), "median": 400000, "growth_rate": 4}
                }
            },
            
            # Healthcare industry
            "healthcare": {
                "nursing_path": {
                    "registered_nurse": {"range": (65000, 95000), "median": 75000, "growth_rate": 9},
                    "nurse_specialist": {"range": (80000, 115000), "median": 95000, "growth_rate": 7},
                    "nurse_practitioner": {"range": (100000, 140000), "median": 120000, "growth_rate": 6},
                    "nursing_director": {"range": (120000, 160000), "median": 140000, "growth_rate": 5}
                },
                "physician_path": {
                    "resident": {"range": (55000, 75000), "median": 65000, "growth_rate": 5},
                    "attending_physician": {"range": (180000, 300000), "median": 240000, "growth_rate": 7},
                    "specialist_physician": {"range": (250000, 400000), "median": 320000, "growth_rate": 5},
                    "chief_medical_officer": {"range": (300000, 500000), "median": 400000, "growth_rate": 3}
                }
            },
            
            # Marketing industry
            "marketing": {
                "marketing_path": {
                    "marketing_coordinator": {"range": (45000, 70000), "median": 55000, "growth_rate": 12},
                    "marketing_specialist": {"range": (60000, 90000), "median": 75000, "growth_rate": 10},
                    "marketing_manager": {"range": (80000, 120000), "median": 100000, "growth_rate": 8},
                    "marketing_director": {"range": (120000, 170000), "median": 145000, "growth_rate": 6},
                    "vp_of_marketing": {"range": (150000, 250000), "median": 200000, "growth_rate": 5}
                },
                "digital_path": {
                    "digital_marketing_specialist": {"range": (55000, 85000), "median": 70000, "growth_rate": 14},
                    "digital_marketing_manager": {"range": (80000, 120000), "median": 100000, "growth_rate": 10},
                    "digital_marketing_director": {"range": (115000, 165000), "median": 140000, "growth_rate": 7}
                }
            },
            
            # Default for other industries
            "default": {
                "standard_path": {
                    "entry_level": {"range": (40000, 70000), "median": 55000, "growth_rate": 10},
                    "mid_level": {"range": (65000, 100000), "median": 80000, "growth_rate": 8},
                    "senior_level": {"range": (90000, 140000), "median": 115000, "growth_rate": 6},
                    "management": {"range": (120000, 180000), "median": 150000, "growth_rate": 5},
                    "executive": {"range": (150000, 250000), "median": 200000, "growth_rate": 4}
                }
            }
        }
        
        return salary_progression
    
    def _load_learning_resources(self) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """
        Load recommended learning resources for different skills and industries.
        """
        learning_resources = {
            # Technology industry
            "technology": {
                "programming": [
                    {"type": "course", "name": "Complete Web Developer Bootcamp", "provider": "Udemy", "cost": "low", "time_investment": "3-6 months"},
                    {"type": "book", "name": "Clean Code", "author": "Robert C. Martin", "cost": "low", "time_investment": "1-2 months"},
                    {"type": "platform", "name": "freeCodeCamp", "cost": "free", "time_investment": "self-paced"},
                    {"type": "platform", "name": "LeetCode", "cost": "free/paid", "time_investment": "self-paced"}
                ],
                "data_science": [
                    {"type": "course", "name": "Data Science Specialization", "provider": "Coursera", "cost": "medium", "time_investment": "6-9 months"},
                    {"type": "platform", "name": "Kaggle", "cost": "free", "time_investment": "self-paced"},
                    {"type": "book", "name": "Python for Data Analysis", "author": "Wes McKinney", "cost": "low", "time_investment": "1-3 months"},
                    {"type": "course", "name": "Machine Learning", "provider": "Stanford Online", "cost": "free/paid", "time_investment": "3 months"}
                ],
                "product_management": [
                    {"type": "course", "name": "Product Management Certification", "provider": "Product School", "cost": "high", "time_investment": "2-3 months"},
                    {"type": "book", "name": "Inspired", "author": "Marty Cagan", "cost": "low", "time_investment": "1 month"},
                    {"type": "community", "name": "Product Hunt", "cost": "free", "time_investment": "ongoing"},
                    {"type": "blog", "name": "Mind the Product", "cost": "free", "time_investment": "ongoing"}
                ],
                "design": [
                    {"type": "course", "name": "UI/UX Design Bootcamp", "provider": "Designlab", "cost": "medium", "time_investment": "3-6 months"},
                    {"type": "platform", "name": "Dribbble", "cost": "free/paid", "time_investment": "ongoing"},
                    {"type": "book", "name": "Don't Make Me Think", "author": "Steve Krug", "cost": "low", "time_investment": "1 month"},
                    {"type": "tutorial", "name": "Figma Tutorials", "cost": "free", "time_investment": "1-2 months"}
                ]
            },
            
            # Finance industry
            "finance": {
                "financial_analysis": [
                    {"type": "course", "name": "Financial Analysis", "provider": "Corporate Finance Institute", "cost": "medium", "time_investment": "2-3 months"},
                    {"type": "certification", "name": "CFA Program", "provider": "CFA Institute", "cost": "high", "time_investment": "18-36 months"},
                    {"type": "book", "name": "Financial Statement Analysis", "author": "Martin Fridson", "cost": "low", "time_investment": "1-2 months"},
                    {"type": "platform", "name": "Wall Street Prep", "cost": "medium", "time_investment": "2-4 months"}
                ],
                "investment_banking": [
                    {"type": "course", "name": "Investment Banking Course", "provider": "Wall Street Prep", "cost": "high", "time_investment": "1-3 months"},
                    {"type": "book", "name": "Investment Banking", "author": "Joshua Rosenbaum", "cost": "low", "time_investment": "1-2 months"},
                    {"type": "certification", "name": "Series 79", "provider": "FINRA", "cost": "medium", "time_investment": "2-3 months"},
                    {"type": "platform", "name": "Breaking Into Wall Street", "cost": "high", "time_investment": "3-6 months"}
                ]
            },
            
            # Healthcare industry
            "healthcare": {
                "nursing": [
                    {"type": "certification", "name": "BLS Certification", "provider": "American Heart Association", "cost": "low", "time_investment": "1 day"},
                    {"type": "certification", "name": "ACLS Certification", "provider": "American Heart Association", "cost": "low", "time_investment": "2-3 days"},
                    {"type": "course", "name": "Nursing Continuing Education", "provider": "Various", "cost": "low to medium", "time_investment": "ongoing"},
                    {"type": "platform", "name": "Nurse.com", "cost": "low", "time_investment": "self-paced"}
                ],
                "medicine": [
                    {"type": "platform", "name": "UpToDate", "cost": "high", "time_investment": "ongoing"},
                    {"type": "journal", "name": "Medical journals (specialty-specific)", "cost": "medium", "time_investment": "ongoing"},
                    {"type": "conference", "name": "Specialty conferences", "cost": "high", "time_investment": "2-4 days per year"},
                    {"type": "course", "name": "Continuing Medical Education", "provider": "Various", "cost": "medium to high", "time_investment": "ongoing"}
                ]
            },
            
            # Marketing industry
            "marketing": {
                "digital_marketing": [
                    {"type": "certification", "name": "Google Digital Marketing Certification", "provider": "Google", "cost": "free", "time_investment": "1-2 months"},
                    {"type": "course", "name": "Digital Marketing Specialization", "provider": "Coursera", "cost": "medium", "time_investment": "3-6 months"},
                    {"type": "platform", "name": "HubSpot Academy", "cost": "free", "time_investment": "1-3 months"},
                    {"type": "book", "name": "Digital Marketing for Dummies", "author": "Ryan Deiss", "cost": "low", "time_investment": "1 month"}
                ],
                "content_strategy": [
                    {"type": "course", "name": "Content Strategy", "provider": "Northwestern/Coursera", "cost": "medium", "time_investment": "4-6 months"},
                    {"type": "book", "name": "Content Strategy for the Web", "author": "Kristina Halvorson", "cost": "low", "time_investment": "1 month"},
                    {"type": "conference", "name": "Content Marketing World", "cost": "high", "time_investment": "3-5 days"},
                    {"type": "platform", "name": "Content Marketing Institute", "cost": "free/paid", "time_investment": "ongoing"}
                ]
            },
            
            # Default for general career development
            "default": {
                "leadership": [
                    {"type": "course", "name": "Leadership Development", "provider": "Coursera", "cost": "medium", "time_investment": "2-3 months"},
                    {"type": "book", "name": "Leaders Eat Last", "author": "Simon Sinek", "cost": "low", "time_investment": "1 month"},
                    {"type": "coaching", "name": "Leadership Coaching", "cost": "high", "time_investment": "3-6 months"},
                    {"type": "workshop", "name": "Leadership Workshops", "provider": "Various", "cost": "medium", "time_investment": "1-5 days"}
                ],
                "project_management": [
                    {"type": "certification", "name": "PMP Certification", "provider": "PMI", "cost": "high", "time_investment": "3-6 months"},
                    {"type": "course", "name": "Project Management Professional Course", "provider": "Udemy", "cost": "low", "time_investment": "1-3 months"},
                    {"type": "book", "name": "A Guide to the Project Management Body of Knowledge", "author": "PMI", "cost": "low", "time_investment": "1-2 months"},
                    {"type": "software", "name": "Project Management Software Tutorials", "cost": "free/low", "time_investment": "1-4 weeks"}
                ],
                "communication": [
                    {"type": "course", "name": "Effective Communication", "provider": "LinkedIn Learning", "cost": "low", "time_investment": "1-2 months"},
                    {"type": "book", "name": "Crucial Conversations", "author": "Kerry Patterson", "cost": "low", "time_investment": "1 month"},
                    {"type": "workshop", "name": "Communication Workshops", "provider": "Various", "cost": "medium", "time_investment": "1-3 days"},
                    {"type": "organization", "name": "Toastmasters", "cost": "low", "time_investment": "ongoing"}
                ]
            }
        }
        
        return learning_resources
        
    def plan_career_path(self, current_role: str, current_industry: str = "technology", 
                         years_experience: int = 0, skills: List[str] = None, 
                         target_role: str = None, target_industry: str = None, 
                         timeframe_years: int = 5) -> Dict[str, Any]:
        """
        Generate a comprehensive career path plan based on current position and goals.
        
        Args:
            current_role (str): Current job title or role
            current_industry (str, optional): Current industry sector
            years_experience (int, optional): Years of experience in current role
            skills (List[str], optional): List of current skills
            target_role (str, optional): Desired future role (if known)
            target_industry (str, optional): Desired future industry (if different from current)
            timeframe_years (int, optional): Planning timeframe in years
            
        Returns:
            Dict[str, Any]: Comprehensive career path plan with multiple options, 
                           skill recommendations, learning resources, and timeline
        """
        try:
            self.logger.info(f"Planning career path for {current_role} in {current_industry} with {years_experience} years experience")
            
            # Normalize inputs
            normalized_role = self._normalize_role(current_role, current_industry)
            normalized_industry = self._normalize_industry(current_industry)
            
            # If target role is provided, normalize it
            normalized_target_role = None
            if target_role:
                target_industry = target_industry or current_industry
                normalized_target_role = self._normalize_role(target_role, target_industry)
                normalized_target_industry = self._normalize_industry(target_industry)
            else:
                normalized_target_industry = normalized_industry
            
            # Generate possible career paths
            if normalized_target_role:
                # Targeted path planning
                career_paths = self._generate_targeted_path(
                    normalized_role, normalized_industry, 
                    normalized_target_role, normalized_target_industry,
                    years_experience, timeframe_years
                )
            else:
                # Multiple path options
                career_paths = self._generate_multiple_paths(
                    normalized_role, normalized_industry, 
                    years_experience, timeframe_years
                )
            
            # Get current skill gaps
            skill_analysis = self._analyze_skills(normalized_role, normalized_industry, skills)
            
            # Get certification recommendations
            certification_recommendations = self._recommend_certifications(normalized_role, normalized_industry)
            
            # Get learning resources
            learning_resources = self._recommend_learning_resources(normalized_role, normalized_industry, skill_analysis['skill_gaps'])
            
            # Get industry transition information if target industry differs
            industry_transition = None
            if target_industry and target_industry != current_industry:
                industry_transition = self._get_industry_transition_info(
                    normalized_industry, self._normalize_industry(target_industry)
                )
                
            # Get salary progression information
            salary_info = self._get_salary_progression(normalized_role, normalized_industry, years_experience, career_paths)
                
            # Combine all information into comprehensive plan
            career_plan = {
                "current_position": {
                    "role": current_role,
                    "normalized_role": normalized_role,
                    "industry": current_industry,
                    "years_experience": years_experience,
                    "career_stage": self._determine_career_stage(years_experience, normalized_role)
                },
                "career_paths": career_paths,
                "skill_analysis": skill_analysis,
                "certification_recommendations": certification_recommendations,
                "learning_resources": learning_resources,
                "salary_progression": salary_info
            }
            
            # Add industry transition information if applicable
            if industry_transition:
                career_plan["industry_transition"] = industry_transition
                
            # Generate summary
            career_plan["summary"] = self._generate_plan_summary(career_plan)
            
            return career_plan
            
        except Exception as e:
            self.logger.error(f"Error in career path planning: {str(e)}")
            return self._get_fallback_plan(current_role, current_industry, years_experience)
    
    def _normalize_role(self, role: str, industry: str) -> str:
        """Normalize role name to match available data."""
        role = role.lower().replace(' ', '_')
        
        # Get industry data
        industry_data = self._career_paths.get(industry.lower(), self._career_paths["default"])
        
        # Check if role exists directly in industry data
        if role in industry_data:
            return role
        
        # Define common role mappings by industry
        role_mappings = {
            "technology": {
                # Developer roles
                "software_developer": "mid_level_developer",
                "programmer": "junior_developer",
                "developer": "mid_level_developer",
                "web_developer": "mid_level_developer",
                "frontend_developer": "mid_level_developer",
                "backend_developer": "mid_level_developer",
                "fullstack_developer": "mid_level_developer",
                "junior_software_engineer": "junior_developer",
                "software_engineer": "mid_level_developer",
                "senior_software_engineer": "senior_developer",
                "lead_developer": "technical_lead",
                "tech_lead": "technical_lead",
                "principal_engineer": "software_architect",
                
                # Data roles
                "data_analyst": "data_scientist",
                "machine_learning_engineer": "data_scientist",
                "ml_engineer": "data_scientist",
                "ai_engineer": "data_scientist",
                
                # Management roles
                "engineering_lead": "technical_lead",
                "development_manager": "engineering_manager",
                "it_manager": "engineering_manager",
                
                # Product roles
                "product_owner": "product_manager",
                
                # Design roles
                "ui_designer": "ux_designer",
                "user_experience_designer": "ux_designer",
                "product_designer": "ux_designer"
            },
            "finance": {
                "financial_advisor": "financial_analyst",
                "finance_analyst": "financial_analyst",
                "investment_analyst": "financial_analyst",
                "quantitative_analyst": "financial_analyst",
                "accountant": "financial_analyst",
                "senior_accountant": "senior_financial_analyst",
                "finance_lead": "finance_manager",
                "banking_associate": "investment_banker"
            },
            "healthcare": {
                "nurse": "registered_nurse",
                "rn": "registered_nurse",
                "doctor": "physician",
                "medical_doctor": "physician",
                "np": "nurse_practitioner",
                "pa": "nurse_practitioner"
            },
            "marketing": {
                "marketing_assistant": "marketing_coordinator",
                "digital_marketer": "marketing_specialist",
                "brand_specialist": "marketing_specialist",
                "social_media_manager": "marketing_specialist",
                "content_writer": "content_strategist",
                "content_manager": "content_strategist",
                "marketing_lead": "marketing_manager"
            }
        }
        
        # Get role mappings for the specific industry or use default
        industry_mappings = role_mappings.get(industry.lower(), {})
        
        # Check if role exists in mappings
        if role in industry_mappings:
            return industry_mappings[role]
        
        # Check for partial matches
        for key, mapped_role in industry_mappings.items():
            if key in role:
                return mapped_role
        
        # If junior/senior/lead prefixes are present, map accordingly
        if "junior" in role or "entry" in role or "associate" in role:
            if industry.lower() == "technology":
                return "junior_developer"
            return "entry_level"
        elif "senior" in role or "sr" in role:
            if industry.lower() == "technology":
                return "senior_developer"
            return "senior_level"
        elif "lead" in role or "head" in role or "manager" in role:
            if industry.lower() == "technology":
                return "technical_lead"
            return "management_track"
        
        # Return default role if no match is found
        return "default"
    
    def _normalize_industry(self, industry: str) -> str:
        """Normalize industry name to match available data."""
        industry = industry.lower()
        
        # Define common industry mappings
        industry_mappings = {
            # Technology
            "tech": "technology",
            "it": "technology",
            "software": "technology",
            "information_technology": "technology",
            "web": "technology",
            "internet": "technology",
            "computer": "technology",
            
            # Finance
            "banking": "finance",
            "financial_services": "finance",
            "investment": "finance",
            "accounting": "finance",
            "insurance": "finance",
            
            # Healthcare
            "medical": "healthcare",
            "health": "healthcare",
            "hospital": "healthcare",
            "pharmaceutical": "healthcare",
            "pharma": "healthcare",
            "biotech": "healthcare",
            
            # Marketing
            "advertising": "marketing",
            "pr": "marketing",
            "public_relations": "marketing",
            "digital_marketing": "marketing",
            "media": "marketing"
        }
        
        # Check if industry exists in mappings
        for key, mapped_industry in industry_mappings.items():
            if key in industry:
                return mapped_industry
        
        # Check if it's a main industry directly
        main_industries = ["technology", "finance", "healthcare", "marketing"]
        if industry in main_industries:
            return industry
        
        # Return default if no match is found
        return "default"
    
    def _determine_career_stage(self, years_experience: int, role: str) -> str:
        """Determine career stage based on experience and role."""
        # Extract level indicators from role
        role_lower = role.lower()
        
        if "junior" in role_lower or "entry" in role_lower:
            stage = "early"
        elif "senior" in role_lower or "lead" in role_lower:
            stage = "advanced"
        elif "manager" in role_lower or "director" in role_lower or "head" in role_lower:
            stage = "leadership"
        elif "architect" in role_lower or "principal" in role_lower:
            stage = "expert"
        else:
            # Determine by years of experience
            if years_experience < 2:
                stage = "early"
            elif years_experience < 5:
                stage = "mid"
            elif years_experience < 10:
                stage = "advanced"
            else:
                stage = "expert/leadership"
                
        return stage
    
    def _generate_multiple_paths(self, role: str, industry: str, 
                                years_experience: int, timeframe_years: int) -> Dict[str, Any]:
        """
        Generate multiple possible career path options.
        """
        # Get industry data
        industry_data = self._career_paths.get(industry, self._career_paths["default"])
        
        # Get role data
        role_data = industry_data.get(role, industry_data.get("default", {}))
        if not role_data:
            role_data = self._career_paths["default"]["default"]
        
        # Initialize paths
        technical_path = []
        management_path = []
        specialized_path = []
        
        # Add current role as starting point
        current_position = {
            "role": role.replace("_", " ").title(),
            "timeline": "Current",
            "description": role_data.get("description", "Your current position"),
            "is_current": True
        }
        
        technical_path.append(current_position)
        management_path.append(current_position)
        specialized_path.append(current_position)
        
        # Generate technical path (individual contributor)
        current_role = role
        current_data = role_data
        time_elapsed = 0
        
        while time_elapsed < timeframe_years:
            # Find next technical role
            next_roles = current_data.get("next_roles", [])
            if not next_roles:
                break
                
            # Filter for technical roles (avoid management roles)
            technical_next_roles = [r for r in next_roles if "manager" not in r and "director" not in r]
            if not technical_next_roles and next_roles:
                technical_next_roles = [next_roles[0]]
                
            if not technical_next_roles:
                break
                
            # Select next role (typically the first one)
            next_role = technical_next_roles[0]
            next_role_data = industry_data.get(next_role, industry_data.get("default", {}))
            
            # Calculate timeline
            duration_text = current_data.get("typical_duration", "1-2 years")
            min_duration, max_duration = self._parse_duration(duration_text)
            avg_duration = (min_duration + max_duration) / 2
            
            time_elapsed += avg_duration
            if time_elapsed > timeframe_years:
                break
                
            # Add to path
            technical_path.append({
                "role": next_role.replace("_", " ").title(),
                "timeline": f"In {self._format_years(time_elapsed)}",
                "description": next_role_data.get("description", f"Advanced technical position after {current_role}"),
                "is_current": False,
                "duration": duration_text
            })
            
            # Update current for next iteration
            current_role = next_role
            current_data = next_role_data
        
        # Generate management path
        current_role = role
        current_data = role_data
        time_elapsed = 0
        
        while time_elapsed < timeframe_years:
            # Find next management role
            next_roles = current_data.get("next_roles", [])
            if not next_roles:
                break
                
            # Filter for management roles
            management_next_roles = [r for r in next_roles if "manager" in r or "director" in r or "lead" in r]
            if not management_next_roles:
                # If no management roles found, take any role but look for management in the next step
                if next_roles:
                    next_role = next_roles[0]
                    next_role_data = industry_data.get(next_role, industry_data.get("default", {}))
                    
                    # Calculate timeline
                    duration_text = current_data.get("typical_duration", "1-2 years")
                    min_duration, max_duration = self._parse_duration(duration_text)
                    avg_duration = (min_duration + max_duration) / 2
                    
                    time_elapsed += avg_duration
                    if time_elapsed > timeframe_years:
                        break
                        
                    # Add to path
                    management_path.append({
                        "role": next_role.replace("_", " ").title(),
                        "timeline": f"In {self._format_years(time_elapsed)}",
                        "description": next_role_data.get("description", f"Advanced position after {current_role}"),
                        "is_current": False,
                        "duration": duration_text
                    })
                    
                    # Update current for next iteration
                    current_role = next_role
                    current_data = next_role_data
                    continue
                else:
                    break
            
            # Select next management role
            next_role = management_next_roles[0]
            next_role_data = industry_data.get(next_role, industry_data.get("default", {}))
            
            # Calculate timeline
            duration_text = current_data.get("typical_duration", "1-2 years")
            min_duration, max_duration = self._parse_duration(duration_text)
            avg_duration = (min_duration + max_duration) / 2
            
            time_elapsed += avg_duration
            if time_elapsed > timeframe_years:
                break
                
            # Add to path
            management_path.append({
                "role": next_role.replace("_", " ").title(),
                "timeline": f"In {self._format_years(time_elapsed)}",
                "description": next_role_data.get("description", f"Management position after {current_role}"),
                "is_current": False,
                "duration": duration_text
            })
            
            # Update current for next iteration
            current_role = next_role
            current_data = next_role_data
        
        # Generate specialized path (domain expert)
        current_role = role
        current_data = role_data
        time_elapsed = 0
        
        while time_elapsed < timeframe_years:
            # Find next specialized role
            next_roles = current_data.get("next_roles", [])
            if not next_roles:
                break
                
            # Filter for specialized roles (e.g., architect, specialist)
            specialized_next_roles = [r for r in next_roles if "architect" in r or "specialist" in r or "expert" in r]
            if not specialized_next_roles:
                # If no specialized roles found, take any non-management role
                non_management_roles = [r for r in next_roles if "manager" not in r and "director" not in r]
                if non_management_roles:
                    specialized_next_roles = [non_management_roles[0]]
                else:
                    specialized_next_roles = [next_roles[0]]
            
            # Select next role
            next_role = specialized_next_roles[0]
            next_role_data = industry_data.get(next_role, industry_data.get("default", {}))
            
            # Calculate timeline
            duration_text = current_data.get("typical_duration", "1-2 years")
            min_duration, max_duration = self._parse_duration(duration_text)
            avg_duration = (min_duration + max_duration) / 2
            
            time_elapsed += avg_duration
            if time_elapsed > timeframe_years:
                break
                
            # Add to path
            specialized_path.append({
                "role": next_role.replace("_", " ").title(),
                "timeline": f"In {self._format_years(time_elapsed)}",
                "description": next_role_data.get("description", f"Specialized position after {current_role}"),
                "is_current": False,
                "duration": duration_text
            })
            
            # Update current for next iteration
            current_role = next_role
            current_data = next_role_data
        
        # If any path is too short (only current role), try to add something generic
        if len(technical_path) <= 1:
            technical_path.append({
                "role": "Senior " + role.replace("_", " ").title(),
                "timeline": "In 2-4 years",
                "description": "Advanced technical position with deeper expertise and more responsibility",
                "is_current": False,
                "duration": "2-4 years"
            })
            
        if len(management_path) <= 1:
            management_path.append({
                "role": "Team Lead",
                "timeline": "In 2-4 years",
                "description": "Leadership position overseeing a small team and projects",
                "is_current": False,
                "duration": "2-4 years"
            })
            
        if len(specialized_path) <= 1:
            specialized_path.append({
                "role": role.replace("_", " ").title() + " Specialist",
                "timeline": "In 2-3 years",
                "description": "Domain expert position with specialized knowledge and skills",
                "is_current": False,
                "duration": "2-3 years"
            })
        
        # Combine all paths
        return {
            "technical_path": {
                "name": "Technical Growth Path",
                "description": "Advancing as an individual contributor with increasing technical depth and expertise",
                "path": technical_path
            },
            "management_path": {
                "name": "Leadership Path",
                "description": "Transitioning into management roles with team and organizational leadership",
                "path": management_path
            },
            "specialized_path": {
                "name": "Specialized Expertise Path",
                "description": "Developing deep specialization in a specific domain or technology area",
                "path": specialized_path
            }
        }
    
    def _generate_targeted_path(self, current_role: str, current_industry: str,
                               target_role: str, target_industry: str,
                               years_experience: int, timeframe_years: int) -> Dict[str, Any]:
        """
        Generate a targeted career path from current role to target role.
        """
        # Handle industry transition first if needed
        same_industry = current_industry == target_industry
        
        # Get industry data
        current_industry_data = self._career_paths.get(current_industry, self._career_paths["default"])
        target_industry_data = self._career_paths.get(target_industry, self._career_paths["default"])
        
        # Get role data
        current_role_data = current_industry_data.get(current_role, current_industry_data.get("default", {}))
        target_role_data = target_industry_data.get(target_role, target_industry_data.get("default", {}))
        
        if not current_role_data:
            current_role_data = self._career_paths["default"]["default"]
        if not target_role_data:
            target_role_data = self._career_paths["default"]["default"]
        
        # Initialize primary path
        primary_path = []
        
        # Add current role as starting point
        primary_path.append({
            "role": current_role.replace("_", " ").title(),
            "timeline": "Current",
            "description": current_role_data.get("description", "Your current position"),
            "is_current": True,
            "industry": current_industry.capitalize()
        })
        
        # If different industries, may need transition role
        if not same_industry:
            # Get industry transition data
            transition_data = self._get_industry_transition_info(current_industry, target_industry)
            
            # Add transition role if needed
            if transition_data and "transition_roles" in transition_data:
                transition_role = transition_data["transition_roles"][0]
                time_investment = transition_data.get("time_investment", "6-12 months")
                min_time, max_time = self._parse_duration(time_investment)
                avg_time = (min_time + max_time) / 2
                
                primary_path.append({
                    "role": transition_role.replace("_", " ").title(),
                    "timeline": f"In {self._format_years(avg_time)}",
                    "description": f"Transition role to bridge {current_industry} and {target_industry}",
                    "is_current": False,
                    "duration": time_investment,
                    "industry": target_industry.capitalize(),
                    "is_transition": True
                })
                
                # Update current role for path building
                years_experience = max(0, years_experience - avg_time)
                timeframe_years -= avg_time
                
                # Get corresponding role in target industry data
                current_role = self._find_closest_role(transition_role, target_industry_data)
                current_role_data = target_industry_data.get(current_role, target_industry_data.get("default", {}))
        
        # Build path from current to target
        if current_role == target_role:
            # Already at target role, add development within current role
            primary_path.append({
                "role": target_role.replace("_", " ").title() + " (Advanced)",
                "timeline": "In 1-2 years",
                "description": "Developing advanced skills and expertise in your current role",
                "is_current": False,
                "duration": "1-2 years",
                "industry": target_industry.capitalize()
            })
        else:
            # Find path to target role
            path_to_target = self._find_path_to_role(current_role, target_role, target_industry_data)
            
            if not path_to_target:
                # No direct path found, add target role directly
                required_exp = target_role_data.get("required_experience", 3)
                duration_needed = max(0, required_exp - years_experience)
                duration_text = f"{duration_needed}-{duration_needed + 2} years"
                
                primary_path.append({
                    "role": target_role.replace("_", " ").title(),
                    "timeline": f"In {self._format_years(duration_needed + 1)}",
                    "description": target_role_data.get("description", "Target position"),
                    "is_current": False,
                    "duration": duration_text,
                    "industry": target_industry.capitalize()
                })
            else:
                # Add each role in path
                time_elapsed = 0
                current = current_role
                
                for next_role in path_to_target:
                    next_role_data = target_industry_data.get(next_role, target_industry_data.get("default", {}))
                    
                    # Calculate timeline
                    duration_text = current_role_data.get("typical_duration", "1-2 years")
                    min_duration, max_duration = self._parse_duration(duration_text)
                    avg_duration = (min_duration + max_duration) / 2
                    
                    time_elapsed += avg_duration
                    
                    # Add to path
                    primary_path.append({
                        "role": next_role.replace("_", " ").title(),
                        "timeline": f"In {self._format_years(time_elapsed)}",
                        "description": next_role_data.get("description", f"Next position after {current}"),
                        "is_current": False,
                        "duration": duration_text,
                        "industry": target_industry.capitalize()
                    })
                    
                    # Update current for next iteration
                    current = next_role
                    current_role_data = next_role_data
        
        # If path is too short, add next logical step after target
        if len(primary_path) <= 2 and timeframe_years > 5:
            target_next_roles = target_role_data.get("next_roles", [])
            if target_next_roles:
                next_role = target_next_roles[0]
                next_role_data = target_industry_data.get(next_role, target_industry_data.get("default", {}))
                
                # Calculate timeline based on last role in path
                last_role_data = target_role_data
                duration_text = last_role_data.get("typical_duration", "2-3 years")
                min_duration, max_duration = self._parse_duration(duration_text)
                avg_duration = (min_duration + max_duration) / 2
                
                # Add to path
                time_elapsed = sum([self._avg_duration(r.get("duration", "1-2 years")) for r in primary_path if not r.get("is_current", False)])
                time_elapsed += avg_duration
                
                primary_path.append({
                    "role": next_role.replace("_", " ").title(),
                    "timeline": f"In {self._format_years(time_elapsed)}",
                    "description": next_role_data.get("description", f"Advanced position after {target_role}"),
                    "is_current": False,
                    "duration": duration_text,
                    "industry": target_industry.capitalize()
                })
        
        # Compile alternate paths
        alternate_paths = []
        
        # If in same industry, offer a different direction
        if same_industry and target_role and current_role != target_role:
            alternate_data = self._career_paths.get(current_industry, self._career_paths["default"])
            current_data = alternate_data.get(current_role, alternate_data.get("default", {}))
            
            next_roles = current_data.get("next_roles", [])
            alternate_options = [r for r in next_roles if (path_to_target and r != path_to_target[0]) or (not path_to_target)]
            
            if alternate_options:
                alternate_role = alternate_options[0]
                alternate_role_data = alternate_data.get(alternate_role, alternate_data.get("default", {}))
                
                alternate_path = []
                
                # Add current role
                alternate_path.append({
                    "role": current_role.replace("_", " ").title(),
                    "timeline": "Current",
                    "description": current_role_data.get("description", "Your current position"),
                    "is_current": True,
                    "industry": current_industry.capitalize()
                })
                
                # Add alternate next role
                duration_text = current_data.get("typical_duration", "1-2 years")
                min_duration, max_duration = self._parse_duration(duration_text)
                avg_duration = (min_duration + max_duration) / 2
                
                alternate_path.append({
                    "role": alternate_role.replace("_", " ").title(),
                    "timeline": f"In {self._format_years(avg_duration)}",
                    "description": alternate_role_data.get("description", f"Alternative position after {current_role}"),
                    "is_current": False,
                    "duration": duration_text,
                    "industry": current_industry.capitalize()
                })
                
                # Add one more step if possible
                alt_next_roles = alternate_role_data.get("next_roles", [])
                if alt_next_roles:
                    next_alt_role = alt_next_roles[0]
                    next_alt_data = alternate_data.get(next_alt_role, alternate_data.get("default", {}))
                    
                    duration_text = alternate_role_data.get("typical_duration", "2-3 years")
                    min_duration, max_duration = self._parse_duration(duration_text)
                    avg_duration2 = (min_duration + max_duration) / 2
                    
                    alternate_path.append({
                        "role": next_alt_role.replace("_", " ").title(),
                        "timeline": f"In {self._format_years(avg_duration + avg_duration2)}",
                        "description": next_alt_data.get("description", f"Advanced position after {alternate_role}"),
                        "is_current": False,
                        "duration": duration_text,
                        "industry": current_industry.capitalize()
                    })
                
                # Add to alternate paths
                alternate_paths.append({
                    "name": "Alternative Career Path",
                    "description": f"Another direction focusing on {alternate_role.replace('_', ' ').title()} instead of {target_role.replace('_', ' ').title()}",
                    "path": alternate_path
                })
        
        # If in different industry, offer path within current industry
        if not same_industry:
            current_ind_data = self._career_paths.get(current_industry, self._career_paths["default"])
            current_role_data = current_ind_data.get(current_role, current_ind_data.get("default", {}))
            
            same_industry_path = []
            
            # Add current role
            same_industry_path.append({
                "role": current_role.replace("_", " ").title(),
                "timeline": "Current",
                "description": current_role_data.get("description", "Your current position"),
                "is_current": True,
                "industry": current_industry.capitalize()
            })
            
            # Add next roles within same industry
            current = current_role
            current_data = current_role_data
            time_elapsed = 0
            
            for _ in range(2):  # Add up to 2 more roles
                next_roles = current_data.get("next_roles", [])
                if not next_roles:
                    break
                    
                next_role = next_roles[0]
                next_role_data = current_ind_data.get(next_role, current_ind_data.get("default", {}))
                
                duration_text = current_data.get("typical_duration", "2-3 years")
                min_duration, max_duration = self._parse_duration(duration_text)
                avg_duration = (min_duration + max_duration) / 2
                
                time_elapsed += avg_duration
                
                same_industry_path.append({
                    "role": next_role.replace("_", " ").title(),
                    "timeline": f"In {self._format_years(time_elapsed)}",
                    "description": next_role_data.get("description", f"Advanced position after {current}"),
                    "is_current": False,
                    "duration": duration_text,
                    "industry": current_industry.capitalize()
                })
                
                current = next_role
                current_data = next_role_data
            
            # Add to alternate paths
            alternate_paths.append({
                "name": f"Stay in {current_industry.capitalize()} Path",
                "description": f"Continuing career progression within {current_industry.capitalize()} industry",
                "path": same_industry_path
            })
        
        # Compile all paths
        return {
            "primary_path": {
                "name": f"Path to {target_role.replace('_', ' ').title()}",
                "description": f"Direct career progression to reach {target_role.replace('_', ' ').title()} position" +
                             (f" in {target_industry.capitalize()} industry" if not same_industry else ""),
                "path": primary_path
            },
            "alternate_paths": alternate_paths
        }
    
    def _find_path_to_role(self, start_role: str, target_role: str, 
                          industry_data: Dict[str, Any]) -> List[str]:
        """
        Find a path from current role to target role using BFS.
        """
        if start_role == target_role:
            return []
            
        # Initialize queue with starting role
        queue = [(start_role, [])]
        visited = set([start_role])
        
        while queue:
            current, path = queue.pop(0)
            
            # Get data for current role
            current_data = industry_data.get(current, industry_data.get("default", {}))
            next_roles = current_data.get("next_roles", [])
            
            for next_role in next_roles:
                if next_role == target_role:
                    return path + [next_role]
                
                if next_role not in visited:
                    visited.add(next_role)
                    queue.append((next_role, path + [next_role]))
        
        # No path found, return empty list
        return []
    
    def _find_closest_role(self, role: str, industry_data: Dict[str, Any]) -> str:
        """
        Find the closest matching role in the target industry.
        """
        # Check if role exists directly
        if role in industry_data:
            return role
            
        # Check for similar roles
        for existing_role in industry_data:
            if role in existing_role or existing_role in role:
                return existing_role
        
        # Return default role
        return "default"
    
    def _analyze_skills(self, role: str, industry: str, 
                       current_skills: List[str] = None) -> Dict[str, Any]:
        """
        Analyze current skills and identify gaps for career progression.
        """
        # Get industry data
        industry_data = self._skill_requirements.get(industry, self._skill_requirements["default"])
        
        # Get role data
        role_data = industry_data.get(role, industry_data.get("default", []))
        
        # Normalize current skills
        normalized_skills = set()
        if current_skills:
            for skill in current_skills:
                # Break down compound skills and add individual components
                parts = skill.lower().split()
                normalized_skills.add(skill.lower())
                if len(parts) > 1:
                    for part in parts:
                        if len(part) > 3:  # Avoid too short parts
                            normalized_skills.add(part)
        
        # Analyze current role requirements
        required_skills = []
        skill_gaps = []
        
        for skill_data in role_data:
            skill_name = skill_data["name"].lower()
            is_essential = skill_data["importance"] == "essential"
            
            skill_match = False
            for user_skill in normalized_skills:
                # Check for exact match or partial match for longer skills
                if skill_name == user_skill or (len(skill_name) > 5 and (skill_name in user_skill or user_skill in skill_name)):
                    skill_match = True
                    break
            
            # Add to appropriate list
            if skill_match:
                required_skills.append({
                    "name": skill_data["name"],
                    "importance": skill_data["importance"],
                    "status": "acquired"
                })
            else:
                skill_gaps.append({
                    "name": skill_data["name"],
                    "importance": skill_data["importance"],
                    "difficulty": skill_data["difficulty"],
                    "status": "gap"
                })
        
        # Calculate skill match percentage
        total_skills = len(role_data)
        essential_skills = len([s for s in role_data if s["importance"] == "essential"])
        acquired_skills = len(required_skills)
        acquired_essential = len([s for s in required_skills if s["importance"] == "essential"])
        
        if total_skills > 0:
            match_percentage = (acquired_skills / total_skills) * 100
        else:
            match_percentage = 100
            
        if essential_skills > 0:
            essential_match_percentage = (acquired_essential / essential_skills) * 100
        else:
            essential_match_percentage = 100
        
        # Check next role requirements
        next_steps = {}
        industry_data = self._career_paths.get(industry, self._career_paths["default"])
        role_data = industry_data.get(role, industry_data.get("default", {}))
        next_roles = role_data.get("next_roles", [])
        
        for next_role in next_roles[:2]:  # Check up to 2 potential next roles
            next_role_skills = self._skill_requirements.get(industry, {}).get(next_role, [])
            if not next_role_skills:
                continue
                
            needed_for_next = []
            
            for skill_data in next_role_skills:
                skill_name = skill_data["name"].lower()
                
                # Check if skill is already acquired
                skill_match = False
                for user_skill in normalized_skills:
                    if skill_name == user_skill or (len(skill_name) > 5 and (skill_name in user_skill or user_skill in skill_name)):
                        skill_match = True
                        break
                
                # Add to needed skills if not acquired and important
                if not skill_match and skill_data["importance"] in ["essential", "important"]:
                    needed_for_next.append({
                        "name": skill_data["name"],
                        "importance": skill_data["importance"],
                        "difficulty": skill_data["difficulty"]
                    })
            
            next_steps[next_role.replace("_", " ").title()] = needed_for_next
        
        # Sort skill gaps by importance
        skill_gaps = sorted(skill_gaps, key=lambda x: {"essential": 0, "important": 1, "helpful": 2}[x["importance"]])
        
        return {
            "role": role.replace("_", " ").title(),
            "industry": industry.capitalize(),
            "required_skills": required_skills,
            "skill_gaps": skill_gaps,
            "match_percentage": round(match_percentage, 1),
            "essential_match_percentage": round(essential_match_percentage, 1),
            "skills_for_next_roles": next_steps
        }
    
    def _recommend_certifications(self, role: str, industry: str) -> Dict[str, Any]:
        """
        Recommend certifications based on role and industry.
        """
        # Get industry data
        industry_data = self._certifications.get(industry, self._certifications["default"])
        
        # Get role data
        role_data = industry_data.get(role, industry_data.get("default", []))
        
        # If no specific role data available, try to find similar role
        if not role_data:
            for existing_role, cert_data in industry_data.items():
                if role in existing_role or existing_role in role:
                    role_data = cert_data
                    break
        
        # If still no data, use default
        if not role_data:
            role_data = self._certifications["default"]["default"]
        
        # Structure recommendations by value
        high_value = []
        medium_value = []
        optional = []
        
        for cert in role_data:
            if cert["value"] == "high" or cert["value"] == "very high" or cert["value"] == "essential":
                high_value.append(cert)
            elif cert["value"] == "medium":
                medium_value.append(cert)
            else:
                optional.append(cert)
        
        return {
            "high_value": high_value,
            "medium_value": medium_value,
            "optional": optional
        }
    
    def _recommend_learning_resources(self, role: str, industry: str, 
                                     skill_gaps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Recommend learning resources based on role, industry, and skill gaps.
        """
        # Get industry data
        industry_data = self._learning_resources.get(industry, self._learning_resources["default"])
        
        # Extract skill names from gaps
        gap_skills = [gap["name"].lower() for gap in skill_gaps]
        
        # Compile relevant resources
        recommended_resources = []
        
        # Add resources for specific skills
        for skill_category, resources in industry_data.items():
            # Check if category is relevant
            category_relevant = False
            for gap in gap_skills:
                if skill_category in gap or gap in skill_category:
                    category_relevant = True
                    break
            
            # If category is relevant or we don't have many recommendations yet
            if category_relevant or len(recommended_resources) < 3:
                # Add top resources from this category
                for resource in resources[:2]:  # Top 2 resources per category
                    # Check for duplicates
                    if not any(r["name"] == resource["name"] for r in recommended_resources):
                        recommended_resources.append(resource)
        
        # Add general career development resources
        general_resources = self._learning_resources["default"]["leadership"]
        for resource in general_resources[:2]:  # Top 2 leadership resources
            if not any(r["name"] == resource["name"] for r in recommended_resources):
                recommended_resources.append(resource)
        
        # Structure by resource type
        resources_by_type = {
            "courses": [],
            "books": [],
            "certifications": [],
            "platforms": [],
            "other": []
        }
        
        for resource in recommended_resources:
            resource_type = resource.get("type", "other")
            if resource_type == "course":
                resources_by_type["courses"].append(resource)
            elif resource_type == "book":
                resources_by_type["books"].append(resource)
            elif resource_type == "certification":
                resources_by_type["certifications"].append(resource)
            elif resource_type == "platform":
                resources_by_type["platforms"].append(resource)
            else:
                resources_by_type["other"].append(resource)
        
        return resources_by_type
    
    def _get_industry_transition_info(self, from_industry: str, to_industry: str) -> Dict[str, Any]:
        """
        Get information about transitioning between industries.
        """
        # Get transition data
        from_industry_data = self._industry_transitions.get(from_industry, self._industry_transitions["default"])
        transition_data = from_industry_data.get(to_industry, {})
        
        # If no direct transition data, use default
        if not transition_data:
            transition_data = self._industry_transitions["default"].get(to_industry, {})
        
        return transition_data
    
    def _get_salary_progression(self, role: str, industry: str, 
                               years_experience: int, career_paths: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get salary progression information for the career paths.
        """
        # Get industry data
        industry_data = self._salary_progression.get(industry, self._salary_progression["default"])
        
        # Determine most relevant path for role
        relevant_path_key = None
        if industry == "technology":
            if "developer" in role or "engineer" in role or "architect" in role:
                relevant_path_key = "developer_path"
            elif "data" in role:
                relevant_path_key = "data_path"
            elif "manager" in role or "lead" in role:
                relevant_path_key = "management_path"
        elif industry == "finance":
            if "analyst" in role:
                relevant_path_key = "analyst_path"
            elif "investment" in role or "banker" in role:
                relevant_path_key = "investment_path"
        elif industry == "healthcare":
            if "nurse" in role:
                relevant_path_key = "nursing_path"
            elif "doctor" in role or "physician" in role:
                relevant_path_key = "physician_path"
        elif industry == "marketing":
            relevant_path_key = "marketing_path"
        
        # Fall back to default if no specific path found
        if not relevant_path_key or relevant_path_key not in industry_data:
            relevant_path_key = next(iter(industry_data))
        
        # Get path data
        path_data = industry_data[relevant_path_key]
        
        # Determine current position in path based on experience
        current_position = None
        normalized_role = role.replace(" ", "_").lower()
        
        # Try direct role match first
        for position, salary_data in path_data.items():
            position_normalized = position.replace(" ", "_").lower()
            if position_normalized == normalized_role:
                current_position = position
                break
        
        # If no direct match, determine by experience
        if not current_position:
            positions_by_experience = sorted(
                [(pos, self._extract_min_salary(data)) for pos, data in path_data.items()],
                key=lambda x: x[1]
            )
            
            for i, (position, min_salary) in enumerate(positions_by_experience):
                if i < len(positions_by_experience) - 1:
                    next_position, next_min = positions_by_experience[i + 1]
                    if years_experience < 2:
                        current_position = positions_by_experience[0][0]
                        break
                    elif years_experience < 5:
                        current_position = positions_by_experience[min(1, len(positions_by_experience) - 1)][0]
                        break
                    elif years_experience < 10:
                        current_position = positions_by_experience[min(2, len(positions_by_experience) - 1)][0]
                        break
                    else:
                        current_position = positions_by_experience[min(3, len(positions_by_experience) - 1)][0]
                        break
            
            # If still no match, use the entry-level position
            if not current_position and positions_by_experience:
                current_position = positions_by_experience[0][0]
        
        # Get current salary data
        current_salary_data = path_data.get(current_position, {"range": (50000, 80000), "median": 65000, "growth_rate": 5})
        
        # Collect salary info for career paths
        career_salary_info = {
            "current": {
                "role": current_position.replace("_", " ").title() if current_position else role.replace("_", " ").title(),
                "salary_range": current_salary_data["range"],
                "median_salary": current_salary_data["median"]
            },
            "progression": []
        }
        
        # Add progression data for each path
        for path_name, path_info in career_paths.items():
            if "path" in path_info:
                for step in path_info["path"]:
                    if step.get("is_current", False):
                        continue
                    
                    step_role = step["role"].lower().replace(" ", "_")
                    step_industry = step.get("industry", industry).lower()
                    
                    # Get salary data for this step
                    step_salary = None
                    
                    # Try to find in appropriate industry
                    if step_industry != industry:
                        # Different industry
                        other_industry_data = self._salary_progression.get(step_industry, self._salary_progression["default"])
                        for path_key, path_values in other_industry_data.items():
                            for pos, pos_data in path_values.items():
                                if step_role == pos or step_role in pos or pos in step_role:
                                    step_salary = pos_data
                                    break
                            if step_salary:
                                break
                    else:
                        # Same industry, check current path first
                        for pos, pos_data in path_data.items():
                            if step_role == pos or step_role in pos or pos in step_role:
                                step_salary = pos_data
                                break
                        
                        # If not found, check other paths
                        if not step_salary:
                            for path_key, path_values in industry_data.items():
                                if path_key != relevant_path_key:
                                    for pos, pos_data in path_values.items():
                                        if step_role == pos or step_role in pos or pos in step_role:
                                            step_salary = pos_data
                                            break
                                    if step_salary:
                                        break
                    
                    # If still not found, estimate based on current salary
                    if not step_salary:
                        progression_index = len([s for s in path_info["path"] if not s.get("is_current", False) and path_info["path"].index(s) <= path_info["path"].index(step)])
                        salary_bump = 1.0 + (progression_index * 0.15)  # 15% increase per step
                        step_salary = {
                            "range": (int(current_salary_data["range"][0] * salary_bump), int(current_salary_data["range"][1] * salary_bump)),
                            "median": int(current_salary_data["median"] * salary_bump),
                            "growth_rate": current_salary_data["growth_rate"]
                        }
                    
                    # Add to progression data
                    career_salary_info["progression"].append({
                        "path": path_name,
                        "role": step["role"],
                        "timeline": step["timeline"],
                        "salary_range": step_salary["range"],
                        "median_salary": step_salary["median"],
                        "industry": step.get("industry", industry).capitalize()
                    })
        
        return career_salary_info
    
    def _generate_plan_summary(self, career_plan: Dict[str, Any]) -> str:
        """
        Generate a summary of the career plan.
        """
        current = career_plan["current_position"]
        role = current["role"]
        industry = current["industry"]
        years = current["years_experience"]
        stage = current["career_stage"]
        
        # Build summary
        summary = f"Career path plan for a {role} in the {industry} industry with {years} years of experience ({stage} career stage).\n\n"
        
        # Add skill analysis summary
        skill_analysis = career_plan["skill_analysis"]
        skill_match = skill_analysis["match_percentage"]
        skill_gaps = len(skill_analysis["skill_gaps"])
        
        summary += f"Your skills are {skill_match}% aligned with your current role. "
        if skill_gaps > 0:
            summary += f"There are {skill_gaps} skill gaps to address for optimal performance.\n\n"
        else:
            summary += "You have all the critical skills for your current role.\n\n"
        
        # Add path summaries
        if "primary_path" in career_plan["career_paths"]:
            # Targeted path
            primary_path = career_plan["career_paths"]["primary_path"]
            path_steps = len(primary_path["path"])
            
            summary += f"Primary career path: {primary_path['name']} with {path_steps - 1} steps to reach your goal.\n"
            
            if career_plan["career_paths"].get("alternate_paths"):
                alt_count = len(career_plan["career_paths"]["alternate_paths"])
                summary += f"Plus {alt_count} alternative path(s) to consider.\n\n"
        else:
            # Multiple paths
            summary += "Three potential career paths:\n"
            for path_key, path_info in career_plan["career_paths"].items():
                path_steps = len(path_info["path"])
                summary += f"- {path_info['name']}: {path_steps - 1} steps over the next several years\n"
            summary += "\n"
        
        # Add certification and learning summary
        high_value_certs = len(career_plan["certification_recommendations"]["high_value"])
        courses = len(career_plan["learning_resources"]["courses"])
        books = len(career_plan["learning_resources"]["books"])
        
        summary += f"Plan includes {high_value_certs} high-value certification recommendations, "
        summary += f"{courses} recommended courses, and {books} books to advance your skills.\n\n"
        
        # Add salary insight
        current_salary = career_plan["salary_progression"]["current"]["median_salary"]
        progression = career_plan["salary_progression"]["progression"]
        
        if progression:
            final_role = progression[-1]
            final_salary = final_role["median_salary"]
            growth_percent = round(((final_salary / current_salary) - 1) * 100, 1)
            summary += f"Potential salary growth from {current_salary:,} to {final_salary:,} ({growth_percent}% increase) "
            summary += f"by reaching {final_role['role']} position.\n"
        
        # Industry transition if applicable
        if "industry_transition" in career_plan:
            from_ind = current["industry"]
            to_ind = next(role.get("industry", from_ind) for role in progression if role.get("industry", from_ind) != from_ind)
            difficulty = career_plan["industry_transition"]["difficulty"]
            summary += f"\nPlan includes transition from {from_ind} to {to_ind} industry ({difficulty} difficulty).\n"
        
        return summary
    
    def _extract_min_salary(self, salary_data: Dict[str, Any]) -> int:
        """Extract minimum salary from salary data."""
        if "range" in salary_data:
            return salary_data["range"][0]
        return salary_data.get("median", 50000)
    
    def _parse_duration(self, duration_text: str) -> Tuple[float, float]:
        """Parse duration text (e.g., '1-2 years') into min and max values."""
        try:
            # Remove 'years' or other text
            duration_text = re.sub(r'[a-zA-Z]', '', duration_text)
            
            # Split on hyphen
            parts = duration_text.split('-')
            
            if len(parts) == 2:
                return float(parts[0].strip()), float(parts[1].strip())
            elif len(parts) == 1:
                return float(parts[0].strip()), float(parts[0].strip())
            else:
                return 1.0, 3.0
        except (ValueError, IndexError):
            return 1.0, 3.0
    
    def _avg_duration(self, duration_text: str) -> float:
        """Calculate average duration from duration text."""
        min_duration, max_duration = self._parse_duration(duration_text)
        return (min_duration + max_duration) / 2
    
    def _format_years(self, years: float) -> str:
        """Format years value into a readable string."""
        if years < 1.0:
            months = int(years * 12)
            return f"{months} months"
        elif years == int(years):
            return f"{int(years)} years"
        else:
            years_part = int(years)
            months_part = int((years - years_part) * 12)
            if months_part == 0:
                return f"{years_part} years"
            elif years_part == 0:
                return f"{months_part} months"
            else:
                return f"{years_part} years, {months_part} months"
    
    def generate_skill_development_plan(self, skills_to_develop: List[str], 
                                       timeframe_months: int = 6) -> Dict[str, Any]:
        """
        Generate a detailed skill development plan with learning resources and milestones.
        
        Args:
            skills_to_develop (List[str]): List of skills to develop
            timeframe_months (int, optional): Timeframe for development in months
            
        Returns:
            Dict[str, Any]: Detailed skill development plan
        """
        try:
            # Generate plans for each skill
            skill_plans = []
            total_effort_hours = 0
            
            for skill in skills_to_develop:
                # Get learning resources for this skill
                resources = self._find_learning_resources_for_skill(skill)
                
                # Estimate difficulty and time investment
                difficulty, time_investment = self._estimate_skill_difficulty(skill, resources)
                
                # Calculate milestone timeline based on difficulty
                milestones = self._generate_skill_milestones(skill, difficulty, timeframe_months)
                
                # Add to total effort hours
                total_effort_hours += time_investment
                
                # Create skill plan
                skill_plans.append({
                    "skill": skill,
                    "difficulty": difficulty,
                    "time_investment": time_investment,
                    "learning_resources": resources,
                    "milestones": milestones
                })
            
            # Check if total effort exceeds available time
            weekly_hours = total_effort_hours / (timeframe_months * 4.3)  # weeks in timeframe
            is_realistic = weekly_hours <= 20  # Assume max 20 hours per week for skill development
            
            # Revise timeline if not realistic
            revised_timeframe = None
            if not is_realistic:
                revised_timeframe = int(total_effort_hours / 80) + 1  # Assume 80 hours per month (20hrs/week) is max
            
            # Generate study plan
            weekly_schedule = self._generate_weekly_schedule(skill_plans, is_realistic)
            
            return {
                "skills": skill_plans,
                "total_effort_hours": total_effort_hours,
                "weekly_hours_required": round(weekly_hours, 1),
                "is_realistic": is_realistic,
                "revised_timeframe": revised_timeframe,
                "weekly_schedule": weekly_schedule,
                "learning_tips": self._generate_learning_tips(skill_plans)
            }
            
        except Exception as e:
            self.logger.error(f"Error generating skill development plan: {str(e)}")
            return {
                "skills": [{"skill": skill, "difficulty": "medium", "time_investment": 40, 
                           "learning_resources": [], "milestones": []} for skill in skills_to_develop],
                "total_effort_hours": len(skills_to_develop) * 40,
                "weekly_hours_required": 10,
                "is_realistic": True,
                "weekly_schedule": [],
                "learning_tips": ["Focus on one skill at a time", "Practice regularly", "Apply skills to real projects"]
            }
    
    def _find_learning_resources_for_skill(self, skill: str) -> List[Dict[str, Any]]:
        """Find learning resources for a specific skill."""
        resources = []
        
        # Normalize skill name
        skill_lower = skill.lower()
        
        # Search through all resources
        for industry, categories in self._learning_resources.items():
            for category, category_resources in categories.items():
                # Check if category matches skill
                if skill_lower in category.lower() or category.lower() in skill_lower:
                    # Add resources from this category
                    for resource in category_resources:
                        resources.append(resource)
                        if len(resources) >= 5:  # Limit to 5 resources
                            break
                
                # If we have enough resources, stop searching
                if len(resources) >= 5:
                    break
            
            # If we have enough resources, stop searching
            if len(resources) >= 5:
                break
        
        # If no resources found, add general ones
        if not resources:
            # Add general learning resources
            if "programming" in skill_lower or "coding" in skill_lower or "development" in skill_lower:
                resources = self._learning_resources.get("technology", {}).get("programming", [])[:3]
            elif "design" in skill_lower or "ux" in skill_lower or "ui" in skill_lower:
                resources = self._learning_resources.get("technology", {}).get("design", [])[:3]
            elif "data" in skill_lower or "analysis" in skill_lower:
                resources = self._learning_resources.get("technology", {}).get("data_science", [])[:3]
            elif "marketing" in skill_lower or "content" in skill_lower:
                resources = self._learning_resources.get("marketing", {}).get("digital_marketing", [])[:3]
            elif "finance" in skill_lower or "accounting" in skill_lower:
                resources = self._learning_resources.get("finance", {}).get("financial_analysis", [])[:3]
            elif "leadership" in skill_lower or "management" in skill_lower:
                resources = self._learning_resources.get("default", {}).get("leadership", [])[:3]
            elif "communication" in skill_lower:
                resources = self._learning_resources.get("default", {}).get("communication", [])[:3]
            else:
                # Generic learning resources
                resources = [
                    {"type": "course", "name": f"Introduction to {skill}", "provider": "Online platforms", "cost": "low to medium", "time_investment": "20-40 hours"},
                    {"type": "book", "name": f"{skill} fundamentals", "provider": "Various publishers", "cost": "low", "time_investment": "20-30 hours"},
                    {"type": "platform", "name": "LinkedIn Learning or Udemy", "cost": "low to medium", "time_investment": "self-paced"}
                ]
        
        return resources
    
    def _estimate_skill_difficulty(self, skill: str, 
                                  resources: List[Dict[str, Any]]) -> Tuple[str, int]:
        """Estimate skill difficulty and time investment."""
        # Look at time investment from resources
        time_investments = []
        for resource in resources:
            time_text = resource.get("time_investment", "")
            if "hours" in time_text:
                try:
                    hours = int(re.search(r'(\d+)', time_text).group(1))
                    time_investments.append(hours)
                except (AttributeError, ValueError):
                    pass
            elif "months" in time_text:
                try:
                    months = int(re.search(r'(\d+)', time_text).group(1))
                    time_investments.append(months * 40)  # Rough estimate: 40 hours per month
                except (AttributeError, ValueError):
                    pass
        
        # Estimate based on skill name
        skill_lower = skill.lower()
        
        # Determine default difficulty
        if any(term in skill_lower for term in ["advanced", "expert", "architect", "machine learning", "ai", "leadership"]):
            difficulty = "high"
            default_hours = 100
        elif any(term in skill_lower for term in ["intermediate", "professional", "development", "management"]):
            difficulty = "medium"
            default_hours = 60
        else:
            difficulty = "low"
            default_hours = 30
        
        # Calculate average time investment
        if time_investments:
            avg_time = sum(time_investments) / len(time_investments)
        else:
            avg_time = default_hours
        
        return difficulty, int(avg_time)
    
    def _generate_skill_milestones(self, skill: str, difficulty: str, 
                                  timeframe_months: int) -> List[Dict[str, Any]]:
        """Generate skill development milestones."""
        milestones = []
        
        # Determine number of milestones based on difficulty and timeframe
        if difficulty == "high":
            milestone_count = min(5, timeframe_months)
        elif difficulty == "medium":
            milestone_count = min(4, timeframe_months)
        else:
            milestone_count = min(3, timeframe_months)
        
        # Generate milestone templates based on skill type
        skill_lower = skill.lower()
        
        if "programming" in skill_lower or "coding" in skill_lower or "development" in skill_lower:
            templates = [
                {"name": "Fundamentals", "description": "Learn basic concepts and syntax", "percentage": 20},
                {"name": "Building simple applications", "description": "Apply fundamentals to create basic programs", "percentage": 40},
                {"name": "Intermediate concepts", "description": "Learn more advanced techniques", "percentage": 60},
                {"name": "Building complex applications", "description": "Create more sophisticated programs", "percentage": 80},
                {"name": "Advanced topics and optimization", "description": "Master advanced concepts and best practices", "percentage": 100}
            ]
        elif "design" in skill_lower or "ux" in skill_lower or "ui" in skill_lower:
            templates = [
                {"name": "Design fundamentals", "description": "Learn basic principles and tools", "percentage": 20},
                {"name": "Creating simple designs", "description": "Apply principles to create basic designs", "percentage": 40},
                {"name": "User research and testing", "description": "Learn to validate designs with users", "percentage": 60},
                {"name": "Advanced design techniques", "description": "Create more sophisticated designs", "percentage": 80},
                {"name": "Building a professional portfolio", "description": "Showcase your skills with polished projects", "percentage": 100}
            ]
        elif "leadership" in skill_lower or "management" in skill_lower:
            templates = [
                {"name": "Leadership fundamentals", "description": "Learn basic principles of effective leadership", "percentage": 20},
                {"name": "Team dynamics", "description": "Understand how to work with different personality types", "percentage": 40},
                {"name": "Conflict resolution", "description": "Learn to address and resolve team conflicts", "percentage": 60},
                {"name": "Strategic planning", "description": "Develop skills for setting goals and planning", "percentage": 80},
                {"name": "Advanced leadership", "description": "Master situational leadership and mentoring", "percentage": 100}
            ]
        else:
            templates = [
                {"name": "Fundamentals", "description": f"Learn basic concepts of {skill}", "percentage": 25},
                {"name": "Practical application", "description": f"Apply {skill} to simple scenarios", "percentage": 50},
                {"name": "Advanced techniques", "description": f"Master more complex aspects of {skill}", "percentage": 75},
                {"name": "Expert level", "description": f"Achieve professional proficiency in {skill}", "percentage": 100}
            ]
        
        # Select appropriate milestones based on count
        if milestone_count >= len(templates):
            selected_milestones = templates
        else:
            percentages = [100 * (i + 1) / milestone_count for i in range(milestone_count)]
            selected_milestones = []
            
            for percentage in percentages:
                # Find closest template
                closest = min(templates, key=lambda x: abs(x["percentage"] - percentage))
                selected_milestones.append(closest)
                
                # Avoid duplicates
                templates = [t for t in templates if t != closest]
        
        # Add timeline to milestones
        for i, milestone in enumerate(selected_milestones):
            # Calculate timeline based on position
            month = int((i + 1) * timeframe_months / len(selected_milestones))
            milestone["timeline"] = f"Month {month}"
            
            # Add to result
            milestones.append(milestone)
        
        return milestones
    
    def _generate_weekly_schedule(self, skill_plans: List[Dict[str, Any]], 
                                 is_realistic: bool) -> List[Dict[str, Any]]:
        """Generate a weekly study schedule."""
        weekly_schedule = []
        
        # Adjust based on realism
        hours_per_week = 20 if is_realistic else 10
        
        # Create schedule for 4 weeks
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for week in range(4):
            week_schedule = {
                "week": week + 1,
                "days": []
            }
            
            # Distribute hours across days
            remaining_hours = hours_per_week
            skill_index = 0
            
            for day in days:
                # Skip some weekdays if few hours needed
                if hours_per_week < 10 and day in ["Tuesday", "Thursday"]:
                    continue
                    
                # Determine hours for this day
                if day in ["Saturday", "Sunday"]:
                    day_hours = min(4, remaining_hours)  # More hours on weekends
                else:
                    day_hours = min(2, remaining_hours)  # Fewer hours on weekdays
                
                if day_hours <= 0:
                    continue
                    
                # Determine skill to study
                skill = skill_plans[skill_index % len(skill_plans)]["skill"]
                skill_index += 1
                
                # Add day to schedule
                week_schedule["days"].append({
                    "day": day,
                    "hours": day_hours,
                    "focus": skill,
                    "activity": self._generate_study_activity(skill, week)
                })
                
                remaining_hours -= day_hours
            
            weekly_schedule.append(week_schedule)
        
        return weekly_schedule
    
    def _generate_study_activity(self, skill: str, week: int) -> str:
        """Generate a study activity for a skill based on the week."""
        skill_lower = skill.lower()
        
        # Week-based activities
        if week == 0:
            # First week activities
            activities = [
                f"Learn the fundamentals of {skill}",
                f"Watch introductory videos on {skill}",
                f"Read the first chapters of {skill} textbook",
                f"Set up the necessary tools for learning {skill}"
            ]
        elif week == 1:
            # Second week activities
            activities = [
                f"Practice basic {skill} exercises",
                f"Complete interactive tutorials on {skill}",
                f"Solve simple problems using {skill}",
                f"Build a small project applying {skill} basics"
            ]
        elif week == 2:
            # Third week activities
            activities = [
                f"Study intermediate {skill} concepts",
                f"Work through more complex examples",
                f"Join online discussion groups about {skill}",
                f"Analyze case studies related to {skill}"
            ]
        else:
            # Fourth week activities
            activities = [
                f"Work on a challenging {skill} project",
                f"Review and consolidate {skill} knowledge",
                f"Teach someone else a {skill} concept",
                f"Research advanced {skill} techniques"
            ]
        
        # Skill-specific adjustments
        if "programming" in skill_lower or "coding" in skill_lower:
            programming_activities = [
                "Complete coding challenges",
                "Debug existing code",
                "Refactor a small application",
                "Contribute to an open-source project"
            ]
            activities.extend(programming_activities)
        elif "design" in skill_lower:
            design_activities = [
                "Analyze existing designs",
                "Create wireframes",
                "Conduct user testing",
                "Build a design portfolio"
            ]
            activities.extend(design_activities)
        elif "management" in skill_lower or "leadership" in skill_lower:
            leadership_activities = [
                "Role-play management scenarios",
                "Analyze leadership case studies",
                "Practice giving feedback",
                "Create a team development plan"
            ]
            activities.extend(leadership_activities)
        
        # Select a random activity
        import random
        return random.choice(activities)
    
    def _generate_learning_tips(self, skill_plans: List[Dict[str, Any]]) -> List[str]:
        """Generate learning tips based on skills."""
        general_tips = [
            "Focus on one skill at a time to avoid overwhelming yourself",
            "Use the 'Pomodoro Technique' - study for 25 minutes, then take a 5-minute break",
            "Apply what you learn immediately to real-world problems",
            "Teach concepts to others to reinforce your understanding",
            "Join communities related to the skills you're developing",
            "Create projects that combine multiple skills you're learning",
            "Schedule regular review sessions to reinforce your learning",
            "Track your progress to stay motivated"
        ]
        
        skill_specific_tips = []
        
        for plan in skill_plans:
            skill = plan["skill"].lower()
            
            if "programming" in skill or "coding" in skill or "development" in skill:
                skill_specific_tips.extend([
                    "Code every day, even if just for 30 minutes",
                    "Build projects instead of just following tutorials",
                    "Learn to read documentation effectively",
                    "Practice debugging and fixing errors",
                    "Contribute to open-source projects to gain experience"
                ])
            elif "design" in skill or "ux" in skill or "ui" in skill:
                skill_specific_tips.extend([
                    "Build a portfolio of your design work",
                    "Seek feedback from experienced designers",
                    "Study successful designs and analyze what makes them effective",
                    "Learn the principles behind good design, not just tools",
                    "Practice redesigning existing interfaces"
                ])
            elif "data" in skill or "analysis" in skill:
                skill_specific_tips.extend([
                    "Work with real datasets rather than just examples",
                    "Focus on understanding the problem before analyzing data",
                    "Learn to effectively communicate your findings",
                    "Master one visualization tool thoroughly",
                    "Practice cleaning and preparing messy data"
                ])
            elif "leadership" in skill or "management" in skill:
                skill_specific_tips.extend([
                    "Find opportunities to lead small projects or initiatives",
                    "Ask for feedback on your leadership style",
                    "Study different leadership approaches and their contexts",
                    "Practice active listening and effective communication",
                    "Learn from both good and bad managers you've had"
                ])
        
        # Combine and remove duplicates
        all_tips = general_tips + skill_specific_tips
        unique_tips = list(dict.fromkeys(all_tips))
        
        # Select a subset
        if len(unique_tips) > 10:
            import random
            return random.sample(unique_tips, 10)
        
        return unique_tips
    
    def _get_fallback_plan(self, current_role: str, current_industry: str, 
                          years_experience: int) -> Dict[str, Any]:
        """Provide a fallback career plan if the real implementation fails."""
        # Determine career stage
        if years_experience < 2:
            stage = "early"
        elif years_experience < 5:
            stage = "mid"
        elif years_experience < 10:
            stage = "advanced"
        else:
            stage = "expert/leadership"
            
        # Generate basic position info
        current_position = {
            "role": current_role,
            "normalized_role": current_role.lower().replace(" ", "_"),
            "industry": current_industry,
            "years_experience": years_experience,
            "career_stage": stage
        }
        
        # Generate basic career paths
        career_paths = {
            "technical_path": {
                "name": "Technical Growth Path",
                "description": "Advancing as an individual contributor with increasing technical depth",
                "path": [
                    {
                        "role": current_role,
                        "timeline": "Current",
                        "description": "Your current position",
                        "is_current": True
                    },
                    {
                        "role": f"Senior {current_role}",
                        "timeline": "In 2-3 years",
                        "description": "Advanced position with deeper expertise",
                        "is_current": False,
                        "duration": "2-3 years"
                    },
                    {
                        "role": f"Lead {current_role}",
                        "timeline": "In 4-6 years",
                        "description": "Leadership position guiding technical direction",
                        "is_current": False,
                        "duration": "2-3 years"
                    }
                ]
            },
            "management_path": {
                "name": "Leadership Path",
                "description": "Transitioning into management roles with team leadership",
                "path": [
                    {
                        "role": current_role,
                        "timeline": "Current",
                        "description": "Your current position",
                        "is_current": True
                    },
                    {
                        "role": "Team Lead",
                        "timeline": "In 2-3 years",
                        "description": "Leadership position managing a small team",
                        "is_current": False,
                        "duration": "2-3 years"
                    },
                    {
                        "role": "Department Manager",
                        "timeline": "In 5-7 years",
                        "description": "Management position overseeing department operations",
                        "is_current": False,
                        "duration": "3-4 years"
                    }
                ]
            }
        }
        
        # Generate basic skill analysis
        skill_analysis = {
            "role": current_role,
            "industry": current_industry.capitalize(),
            "required_skills": [],
            "skill_gaps": [
                {"name": f"{current_role} Advanced Techniques", "importance": "important", "difficulty": "medium", "status": "gap"},
                {"name": "Communication Skills", "importance": "essential", "difficulty": "medium", "status": "gap"},
                {"name": "Project Management", "importance": "important", "difficulty": "medium", "status": "gap"}
            ],
            "match_percentage": 70.0,
            "essential_match_percentage": 75.0,
            "skills_for_next_roles": {
                f"Senior {current_role}": [
                    {"name": "Advanced Technical Skills", "importance": "essential", "difficulty": "high"},
                    {"name": "Mentoring", "importance": "important", "difficulty": "medium"},
                    {"name": "Project Leadership", "importance": "important", "difficulty": "medium"}
                ],
                "Team Lead": [
                    {"name": "Team Management", "importance": "essential", "difficulty": "high"},
                    {"name": "Strategic Planning", "importance": "important", "difficulty": "high"},
                    {"name": "Performance Management", "importance": "important", "difficulty": "medium"}
                ]
            }
        }
        
        # Generate basic certification recommendations
        certification_recommendations = {
            "high_value": [
                {"name": f"{current_industry} Professional Certification", "value": "high", "difficulty": "medium", "time_investment": "3-6 months"}
            ],
            "medium_value": [
                {"name": "Project Management Certification", "value": "medium", "difficulty": "medium", "time_investment": "2-4 months"},
                {"name": "Leadership Training", "value": "medium", "difficulty": "medium", "time_investment": "1-3 months"}
            ],
            "optional": [
                {"name": "Communication Skills Workshop", "value": "low", "difficulty": "low", "time_investment": "2-4 weeks"}
            ]
        }
        
        # Generate basic learning resources
        learning_resources = {
            "courses": [
                {"type": "course", "name": f"Advanced {current_role} Techniques", "provider": "Online platforms", "cost": "medium", "time_investment": "2-3 months"}
            ],
            "books": [
                {"type": "book", "name": f"Mastering {current_role}", "author": "Industry Expert", "cost": "low", "time_investment": "1-2 months"}
            ],
            "certifications": [
                {"type": "certification", "name": f"{current_industry} Professional Certification", "provider": "Industry Association", "cost": "high", "time_investment": "3-6 months"}
            ],
            "platforms": [
                {"type": "platform", "name": "LinkedIn Learning", "cost": "medium", "time_investment": "ongoing"}
            ],
            "other": []
        }
        
        # Generate basic salary progression
        salary_progression = {
            "current": {
                "role": current_role,
                "salary_range": (70000, 90000),
                "median_salary": 80000
            },
            "progression": [
                {
                    "path": "technical_path",
                    "role": f"Senior {current_role}",
                    "timeline": "In 2-3 years",
                    "salary_range": (90000, 120000),
                    "median_salary": 105000,
                    "industry": current_industry.capitalize()
                },
                {
                    "path": "technical_path",
                    "role": f"Lead {current_role}",
                    "timeline": "In 4-6 years",
                    "salary_range": (110000, 150000),
                    "median_salary": 130000,
                    "industry": current_industry.capitalize()
                },
                {
                    "path": "management_path",
                    "role": "Team Lead",
                    "timeline": "In 2-3 years",
                    "salary_range": (95000, 125000),
                    "median_salary": 110000,
                    "industry": current_industry.capitalize()
                },
                {
                    "path": "management_path",
                    "role": "Department Manager",
                    "timeline": "In 5-7 years",
                    "salary_range": (120000, 160000),
                    "median_salary": 140000,
                    "industry": current_industry.capitalize()
                }
            ]
        }
        
        # Generate basic summary
        summary = f"Career path plan for a {current_role} in the {current_industry} industry with {years_experience} years of experience ({stage} career stage).\n\n"
        summary += "Your skills are 70% aligned with your current role. There are 3 skill gaps to address for optimal performance.\n\n"
        summary += "Two potential career paths:\n"
        summary += f"- Technical Growth Path: 2 steps over the next several years\n"
        summary += f"- Leadership Path: 2 steps over the next several years\n\n"
        summary += "Plan includes 1 high-value certification recommendation, 1 recommended course, and 1 book to advance your skills.\n\n"
        summary += f"Potential salary growth from 80,000 to 140,000 (75.0% increase) by reaching Department Manager position."
        
        # Combine all into comprehensive plan
        return {
            "current_position": current_position,
            "career_paths": career_paths,
            "skill_analysis": skill_analysis,
            "certification_recommendations": certification_recommendations,
            "learning_resources": learning_resources,
            "salary_progression": salary_progression,
            "summary": summary
        }