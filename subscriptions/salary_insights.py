"""
Salary Insights System

This module provides comprehensive salary analysis and insights for Pro users.
It offers data-driven salary information based on job titles, locations, experience levels,
and industries, with negotiation guidance and future earnings projections.

Key features:
- Salary estimation based on multiple factors
- Industry and regional comparisons
- Negotiation strategy recommendations
- Benefits evaluation
- Career growth projections
"""

import logging
import json
import re
import os
import math
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any, Tuple, Optional

from .data_resources import DataResources
from .text_processor import TextProcessor

class SalaryInsights:
    """
    Provides advanced salary analysis and recommendations for Pro users.
    
    This class leverages comprehensive salary data and industry trends to provide
    accurate salary estimates, comparisons, and negotiation guidance.
    """
    
    def __init__(self):
        """Initialize the SalaryInsights with necessary resources."""
        self.logger = logging.getLogger(__name__)
        self.data_resources = DataResources()
        self.text_processor = TextProcessor()
        
        # Load salary data from resources
        self._salary_data = self._load_salary_data()
        self._benefits_data = self._load_benefits_data()
        self._industry_growth_data = self._load_industry_growth_data()
        self._cost_of_living_data = self._load_cost_of_living_data()
        self._negotiation_strategies = self._load_negotiation_strategies()
        
    def _load_salary_data(self) -> Dict[str, Any]:
        """
        Load and return the salary data for different job titles, industries, and locations.
        
        In a production environment, this would load from a database or external API.
        For this implementation, we use synthetic data based on research.
        """
        # Simplified representation of salary data with averages by title, industry, location
        # Structure: {industry: {job_title: {location: {experience_level: salary}}}}
        salary_data = {
            # Technology industry
            "technology": {
                "software_engineer": {
                    "San Francisco": {"entry": 120000, "mid": 150000, "senior": 200000, "lead": 250000},
                    "New York": {"entry": 110000, "mid": 140000, "senior": 180000, "lead": 230000},
                    "Remote": {"entry": 100000, "mid": 130000, "senior": 160000, "lead": 200000},
                    "Default": {"entry": 90000, "mid": 120000, "senior": 150000, "lead": 180000}
                },
                "data_scientist": {
                    "San Francisco": {"entry": 130000, "mid": 160000, "senior": 210000, "lead": 260000},
                    "New York": {"entry": 120000, "mid": 150000, "senior": 190000, "lead": 240000},
                    "Remote": {"entry": 110000, "mid": 140000, "senior": 170000, "lead": 210000},
                    "Default": {"entry": 100000, "mid": 130000, "senior": 160000, "lead": 190000}
                },
                "product_manager": {
                    "San Francisco": {"entry": 125000, "mid": 155000, "senior": 205000, "lead": 255000},
                    "New York": {"entry": 115000, "mid": 145000, "senior": 185000, "lead": 235000},
                    "Remote": {"entry": 105000, "mid": 135000, "senior": 165000, "lead": 205000},
                    "Default": {"entry": 95000, "mid": 125000, "senior": 155000, "lead": 185000}
                },
                "ux_designer": {
                    "San Francisco": {"entry": 110000, "mid": 140000, "senior": 180000, "lead": 220000},
                    "New York": {"entry": 100000, "mid": 130000, "senior": 160000, "lead": 200000},
                    "Remote": {"entry": 90000, "mid": 120000, "senior": 140000, "lead": 180000},
                    "Default": {"entry": 80000, "mid": 110000, "senior": 130000, "lead": 160000}
                },
                "Default": {
                    "Default": {"entry": 95000, "mid": 125000, "senior": 155000, "lead": 185000}
                }
            },
            # Finance industry
            "finance": {
                "financial_analyst": {
                    "New York": {"entry": 95000, "mid": 125000, "senior": 165000, "lead": 215000},
                    "Chicago": {"entry": 85000, "mid": 115000, "senior": 145000, "lead": 195000},
                    "Remote": {"entry": 80000, "mid": 110000, "senior": 135000, "lead": 175000},
                    "Default": {"entry": 75000, "mid": 105000, "senior": 125000, "lead": 165000}
                },
                "investment_banker": {
                    "New York": {"entry": 150000, "mid": 250000, "senior": 400000, "lead": 750000},
                    "Chicago": {"entry": 130000, "mid": 220000, "senior": 350000, "lead": 650000},
                    "Remote": {"entry": 120000, "mid": 200000, "senior": 320000, "lead": 600000},
                    "Default": {"entry": 110000, "mid": 180000, "senior": 290000, "lead": 550000}
                },
                "Default": {
                    "Default": {"entry": 90000, "mid": 120000, "senior": 150000, "lead": 180000}
                }
            },
            # Healthcare industry
            "healthcare": {
                "registered_nurse": {
                    "Boston": {"entry": 75000, "mid": 90000, "senior": 110000, "lead": 130000},
                    "California": {"entry": 85000, "mid": 100000, "senior": 120000, "lead": 140000},
                    "Remote": {"entry": 70000, "mid": 85000, "senior": 100000, "lead": 115000},
                    "Default": {"entry": 65000, "mid": 80000, "senior": 95000, "lead": 110000}
                },
                "physician": {
                    "Boston": {"entry": 180000, "mid": 220000, "senior": 280000, "lead": 350000},
                    "California": {"entry": 200000, "mid": 240000, "senior": 300000, "lead": 380000},
                    "Remote": {"entry": 170000, "mid": 210000, "senior": 260000, "lead": 320000},
                    "Default": {"entry": 160000, "mid": 200000, "senior": 250000, "lead": 300000}
                },
                "Default": {
                    "Default": {"entry": 85000, "mid": 110000, "senior": 140000, "lead": 170000}
                }
            },
            # Marketing industry
            "marketing": {
                "marketing_manager": {
                    "New York": {"entry": 90000, "mid": 120000, "senior": 150000, "lead": 200000},
                    "Chicago": {"entry": 80000, "mid": 110000, "senior": 140000, "lead": 180000},
                    "Remote": {"entry": 75000, "mid": 100000, "senior": 130000, "lead": 170000},
                    "Default": {"entry": 70000, "mid": 95000, "senior": 120000, "lead": 160000}
                },
                "content_strategist": {
                    "New York": {"entry": 75000, "mid": 95000, "senior": 125000, "lead": 165000},
                    "Chicago": {"entry": 65000, "mid": 85000, "senior": 115000, "lead": 145000},
                    "Remote": {"entry": 60000, "mid": 80000, "senior": 110000, "lead": 140000},
                    "Default": {"entry": 55000, "mid": 75000, "senior": 100000, "lead": 130000}
                },
                "Default": {
                    "Default": {"entry": 70000, "mid": 95000, "senior": 120000, "lead": 150000}
                }
            },
            # Default for other industries
            "Default": {
                "Default": {
                    "Default": {"entry": 60000, "mid": 80000, "senior": 100000, "lead": 120000}
                }
            }
        }
        return salary_data
    
    def _load_benefits_data(self) -> Dict[str, Dict[str, Any]]:
        """
        Load and return data on common benefits by industry.
        """
        benefits_data = {
            "technology": {
                "standard": ["Health insurance", "Dental insurance", "Vision insurance", 
                             "401(k) matching", "Paid time off"],
                "premium": ["Unlimited PTO", "Remote work options", "Stock options", 
                            "Professional development stipend", "Home office stipend",
                            "Wellness programs", "Company equity"],
                "rare": ["Sabbatical leave", "Student loan repayment", "On-site childcare",
                         "Free meals", "Unlimited learning budget"],
                "monetary_value": {
                    "Health insurance": 7000,
                    "401(k) matching": 5000,
                    "Stock options": 10000,
                    "Remote work": 5000,
                    "Professional development": 2000
                }
            },
            "finance": {
                "standard": ["Health insurance", "Dental insurance", "Vision insurance", 
                             "401(k) matching", "Paid time off"],
                "premium": ["Performance bonuses", "Profit sharing", "Stock options",
                            "Financial planning services", "Executive health programs"],
                "rare": ["Concierge services", "First-class travel", "Club memberships",
                         "Executive retirement packages"],
                "monetary_value": {
                    "Health insurance": 7000,
                    "401(k) matching": 8000,
                    "Performance bonuses": 20000,
                    "Profit sharing": 15000
                }
            },
            "healthcare": {
                "standard": ["Health insurance", "Dental insurance", "Vision insurance", 
                             "Retirement plans", "Paid time off"],
                "premium": ["Continuing education credits", "License fee coverage",
                            "Malpractice insurance", "Flexible scheduling"],
                "rare": ["Housing stipends", "Relocation assistance", "Student loan forgiveness"],
                "monetary_value": {
                    "Health insurance": 7000,
                    "Retirement plans": 6000,
                    "Continuing education": 3000,
                    "Malpractice insurance": 10000
                }
            },
            "Default": {
                "standard": ["Health insurance", "Dental insurance", "Vision insurance", 
                             "Retirement plans", "Paid time off"],
                "premium": ["Flexible scheduling", "Professional development", 
                            "Wellness programs"],
                "rare": ["Remote work options", "Performance bonuses", "Stock options"],
                "monetary_value": {
                    "Health insurance": 7000,
                    "Retirement plans": 5000,
                    "Professional development": 2000
                }
            }
        }
        return benefits_data
    
    def _load_industry_growth_data(self) -> Dict[str, Dict[str, float]]:
        """
        Load and return data on industry and role growth projections.
        """
        growth_data = {
            "technology": {
                "industry_growth": 15.0,  # Annual percentage growth
                "software_engineer": 22.0,
                "data_scientist": 28.0,
                "product_manager": 18.0,
                "ux_designer": 20.0,
                "Default": 15.0
            },
            "finance": {
                "industry_growth": 8.0,
                "financial_analyst": 10.0,
                "investment_banker": 6.0,
                "Default": 8.0
            },
            "healthcare": {
                "industry_growth": 14.0,
                "registered_nurse": 12.0,
                "physician": 7.0,
                "Default": 14.0
            },
            "marketing": {
                "industry_growth": 10.0,
                "marketing_manager": 8.0,
                "content_strategist": 12.0,
                "Default": 10.0
            },
            "Default": {
                "industry_growth": 7.0,
                "Default": 7.0
            }
        }
        return growth_data
    
    def _load_cost_of_living_data(self) -> Dict[str, float]:
        """
        Load and return cost of living index data for different locations.
        
        The index is relative to a baseline of 100 (national average).
        Includes African regions and international locations.
        """
        cost_of_living_data = {
            # United States
            "San Francisco": 205.0,
            "New York": 187.0,
            "Boston": 162.0,
            "Chicago": 123.0,
            "Los Angeles": 173.0,
            "Seattle": 172.0,
            "Austin": 119.0,
            "Denver": 128.0,
            "Atlanta": 107.0,
            "Miami": 123.0,
            "Dallas": 103.0,
            "Phoenix": 107.0,
            "Remote": 100.0,  # Baseline for remote work
            
            # African Regions
            "Lagos": 45.0,
            "Nigeria": 40.0,
            "Accra": 38.0,
            "Ghana": 35.0,
            "Nairobi": 42.0,
            "Kenya": 38.0,
            "Johannesburg": 55.0,
            "Cape Town": 58.0,
            "South Africa": 52.0,
            "Cairo": 32.0,
            "Egypt": 30.0,
            "Casablanca": 45.0,
            "Morocco": 42.0,
            
            # European Regions
            "London": 160.0,
            "Paris": 155.0,
            "Berlin": 130.0,
            "Madrid": 110.0,
            
            # Asian Regions
            "Tokyo": 145.0,
            "Singapore": 138.0,
            "Hong Kong": 158.0,
            "Dubai": 120.0,
            
            "Default": 100.0  # Global baseline
        }
        return cost_of_living_data
    
    def _load_negotiation_strategies(self) -> Dict[str, Dict[str, Any]]:
        """
        Load and return negotiation strategies by career level and industry.
        Includes region-specific negotiation approaches.
        """
        negotiation_strategies = {
            "entry": {
                "key_points": [
                    "Research industry standards for your position and location",
                    "Highlight relevant education and internship experience",
                    "Focus on potential and eagerness to learn",
                    "Be flexible but don't undervalue yourself"
                ],
                "african_key_points": [
                    "Research both multinational and local company pay scales",
                    "Highlight any international qualifications or training",
                    "Emphasize willingness to learn local business practices",
                    "Consider total compensation including training opportunities"
                ],
                "phrases": [
                    "Based on my research for similar roles in this area...",
                    "While I'm early in my career, my skills in X directly align with your needs...",
                    "I'm excited about the opportunity and believe my background in X would bring value..."
                ],
                "african_phrases": [
                    "Based on my research of market rates for this position in [city]...",
                    "My degree from [university] has prepared me with relevant skills for this role...",
                    "I am particularly interested in this opportunity to gain experience with a respected organization like yours..."
                ],
                "avoid": [
                    "Taking the first offer without discussion",
                    "Focusing only on salary and ignoring benefits package",
                    "Apologizing for negotiating",
                    "Mentioning personal financial needs"
                ],
                "african_avoid": [
                    "Using only Western salary benchmarks without local context",
                    "Appearing too aggressive in early career negotiations",
                    "Overlooking non-monetary benefits like training or advancement",
                    "Failing to research local salary customs and practices"
                ]
            },
            "mid": {
                "key_points": [
                    "Demonstrate specific achievements and their business impact",
                    "Research both company and industry compensation trends",
                    "Consider the full compensation package beyond base salary",
                    "Prepare specific examples of your value"
                ],
                "phrases": [
                    "In my current role, I've achieved X resulting in Y value...",
                    "My experience with X has prepared me to make immediate contributions...",
                    "The market rate for professionals with my skill set and experience is..."
                ],
                "avoid": [
                    "Making demands without substantiation",
                    "Sharing current salary before receiving an offer",
                    "Focusing on years of experience rather than achievements",
                    "Neglecting to research the company's compensation structure"
                ]
            },
            "senior": {
                "key_points": [
                    "Emphasize leadership and strategic impact",
                    "Negotiate for equity, bonuses, and other performance incentives",
                    "Consider long-term growth opportunities",
                    "Discuss specific ways you'll drive business results"
                ],
                "phrases": [
                    "My leadership in X resulted in Y growth/savings for my current company...",
                    "I'd be bringing unique expertise in X which directly addresses your challenges with Y...",
                    "Given the scope of responsibility and my track record of success..."
                ],
                "avoid": [
                    "Focusing only on technical skills rather than leadership impact",
                    "Neglecting to negotiate beyond base salary",
                    "Being inflexible on non-monetary benefits",
                    "Undervaluing your market position"
                ]
            },
            "lead": {
                "key_points": [
                    "Focus on executive-level impact and transformation abilities",
                    "Negotiate comprehensive executive compensation packages",
                    "Discuss performance metrics and success criteria",
                    "Consider exit packages and long-term incentives"
                ],
                "phrases": [
                    "In my executive capacity at X, I transformed Y resulting in Z...",
                    "My track record of building and leading teams has delivered X value...",
                    "Let's discuss how my compensation can align with measurable business outcomes..."
                ],
                "avoid": [
                    "Focusing on day-to-day responsibilities instead of strategic vision",
                    "Neglecting to negotiate performance-based incentives",
                    "Underestimating your market value",
                    "Rushing negotiations without proper due diligence"
                ]
            }
        }
        return negotiation_strategies
        
    def analyze_salary(self, job_title: str, location: str = "Default", 
                      years_experience: int = 0, industry: str = "Default",
                      education_level: str = "bachelor",
                      skills: List[str] = None) -> Dict[str, Any]:
        """
        Analyze and provide comprehensive salary insights for a given job.
        
        Args:
            job_title: The job title to analyze
            location: The job location
            years_experience: Years of relevant experience
            industry: The industry sector
            education_level: Highest education level (high_school, associate, bachelor, master, phd)
            skills: List of skills the candidate possesses
            
        Returns:
            Dictionary containing salary insights including:
            - Estimated salary range
            - Percentile breakdown
            - Regional comparison
            - Industry comparison
            - Benefits analysis
            - Negotiation guidance
            - Future earnings projection
        """
        try:
            self.logger.info(f"Analyzing salary for {job_title} in {location} with {years_experience} years experience")
            
            # Normalize inputs
            normalized_title = self._normalize_job_title(job_title)
            normalized_industry = self._normalize_industry(industry)
            normalized_location = self._normalize_location(location)
            experience_level = self._categorize_experience(years_experience)
            
            # Get base salary estimation
            salary_estimate = self._calculate_base_salary(
                normalized_title, normalized_location, experience_level, normalized_industry)
            
            # Apply adjustments
            adjusted_salary = self._apply_adjustments(
                salary_estimate, education_level, skills, years_experience)
            
            # Generate insights
            insights = {
                "salary_estimate": {
                    "min": int(adjusted_salary * 0.9),
                    "median": int(adjusted_salary),
                    "max": int(adjusted_salary * 1.1)
                },
                "percentiles": self._calculate_percentiles(adjusted_salary, normalized_industry, normalized_title),
                "regional_comparison": self._generate_regional_comparison(
                    normalized_title, normalized_location, experience_level, normalized_industry),
                "industry_comparison": self._generate_industry_comparison(
                    normalized_title, experience_level, normalized_industry),
                "benefits_analysis": self._analyze_benefits(normalized_industry),
                "negotiation_guidance": self._generate_negotiation_guidance(experience_level),
                "future_projection": self._project_future_earnings(
                    adjusted_salary, normalized_industry, normalized_title, years_experience),
                "position_analysis": {
                    "job_title": job_title,
                    "normalized_title": normalized_title,
                    "experience_level": experience_level,
                    "location": location,
                    "industry": industry,
                    "cost_of_living_index": self._get_cost_of_living_index(normalized_location)
                }
            }
            
            # Add total compensation estimate (salary + benefits)
            insights["total_compensation"] = self._calculate_total_compensation(
                adjusted_salary, insights["benefits_analysis"])
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error in salary analysis: {str(e)}")
            return self._get_fallback_analysis(job_title, location, years_experience, industry)
    
    def _normalize_job_title(self, job_title: str) -> str:
        """Normalize job title to match available data."""
        job_title = job_title.lower().replace(' ', '_')
        
        # Map common variations to standard titles
        title_mapping = {
            # Software engineering roles
            "software_developer": "software_engineer",
            "software_engineer": "software_engineer",
            "programmer": "software_engineer",
            "web_developer": "software_engineer",
            "full_stack_developer": "software_engineer",
            "backend_developer": "software_engineer",
            "frontend_developer": "software_engineer",
            
            # Data science roles
            "data_scientist": "data_scientist",
            "machine_learning_engineer": "data_scientist",
            "ai_engineer": "data_scientist",
            "data_analyst": "data_scientist",
            
            # Product roles
            "product_manager": "product_manager",
            "product_owner": "product_manager",
            "project_manager": "product_manager",
            
            # Design roles
            "ux_designer": "ux_designer",
            "ui_designer": "ux_designer",
            "product_designer": "ux_designer",
            "user_experience_designer": "ux_designer",
            
            # Finance roles
            "financial_analyst": "financial_analyst",
            "finance_manager": "financial_analyst",
            "financial_advisor": "financial_analyst",
            "investment_banker": "investment_banker",
            "investment_analyst": "investment_banker",
            
            # Healthcare roles
            "registered_nurse": "registered_nurse",
            "nurse": "registered_nurse",
            "physician": "physician",
            "doctor": "physician",
            "medical_doctor": "physician",
            
            # Marketing roles
            "marketing_manager": "marketing_manager",
            "digital_marketer": "marketing_manager",
            "marketing_director": "marketing_manager",
            "content_strategist": "content_strategist",
            "content_manager": "content_strategist",
            "content_writer": "content_strategist"
        }
        
        # Return mapped title or default
        for key in title_mapping:
            if key in job_title:
                return title_mapping[key]
        
        return "Default"
    
    def _normalize_industry(self, industry: str) -> str:
        """Normalize industry to match available data."""
        industry = industry.lower()
        
        # Map common variations to standard industries
        industry_mapping = {
            # Technology
            "tech": "technology",
            "software": "technology",
            "it": "technology",
            "information technology": "technology",
            
            # Finance
            "banking": "finance",
            "financial services": "finance",
            "investment": "finance",
            "accounting": "finance",
            
            # Healthcare
            "medical": "healthcare",
            "health": "healthcare",
            "hospital": "healthcare",
            "pharma": "healthcare",
            "pharmaceutical": "healthcare",
            
            # Marketing
            "advertising": "marketing",
            "pr": "marketing",
            "public relations": "marketing",
            "media": "marketing"
        }
        
        # Return mapped industry or default
        for key in industry_mapping:
            if key in industry:
                return industry_mapping[key]
        
        # Check if it matches a main category directly
        main_categories = ["technology", "finance", "healthcare", "marketing"]
        for category in main_categories:
            if category in industry:
                return category
        
        return "Default"
    
    def _normalize_location(self, location: str) -> str:
        """Normalize location to match available data."""
        location = location.lower()
        
        # Map common variations to standard locations
        location_mapping = {
            # San Francisco
            "san francisco": "San Francisco",
            "sf": "San Francisco",
            "bay area": "San Francisco",
            "silicon valley": "San Francisco",
            
            # New York
            "new york": "New York",
            "nyc": "New York",
            "manhattan": "New York",
            
            # Boston
            "boston": "Boston",
            "cambridge": "Boston",
            
            # Chicago
            "chicago": "Chicago",
            
            # Remote
            "remote": "Remote",
            "work from home": "Remote",
            "wfh": "Remote",
            
            # Los Angeles
            "los angeles": "Los Angeles",
            "la": "Los Angeles",
            
            # Seattle
            "seattle": "Seattle",
            
            # States/regions
            "california": "California",
            "ca": "California"
        }
        
        # Return mapped location or default
        for key in location_mapping:
            if key in location:
                return location_mapping[key]
        
        # Check if it matches a main location directly
        main_locations = ["San Francisco", "New York", "Boston", "Chicago", "Los Angeles", 
                         "Seattle", "Austin", "Denver", "Atlanta", "Miami", "Dallas", "Phoenix", "Remote"]
        for loc in main_locations:
            if loc.lower() in location:
                return loc
        
        return "Default"
    
    def _categorize_experience(self, years_experience: int) -> str:
        """Categorize years of experience into experience level."""
        if years_experience < 3:
            return "entry"
        elif years_experience < 7:
            return "mid"
        elif years_experience < 12:
            return "senior"
        else:
            return "lead"
    
    def _calculate_base_salary(self, job_title: str, location: str, 
                              experience_level: str, industry: str) -> float:
        """Calculate base salary estimation based on key factors."""
        # Get industry data, defaulting if necessary
        industry_data = self._salary_data.get(industry, self._salary_data["Default"])
        
        # Get job title data, defaulting if necessary
        job_data = industry_data.get(job_title, industry_data.get("Default", {}))
        
        # Get location data, defaulting if necessary
        location_data = job_data.get(location, job_data.get("Default", {}))
        
        # Get salary by experience, defaulting if necessary
        base_salary = location_data.get(experience_level, 0)
        
        # If no salary found, use industry default
        if base_salary == 0:
            default_data = self._salary_data["Default"]["Default"]["Default"]
            base_salary = default_data.get(experience_level, 70000)  # Absolute fallback
        
        return base_salary
    
    def _apply_adjustments(self, base_salary: float, education_level: str, 
                          skills: List[str] = None, years_experience: int = 0) -> float:
        """Apply various adjustments to refine the salary estimate."""
        adjusted_salary = base_salary
        
        # Education adjustment
        education_multipliers = {
            "high_school": 0.9,
            "associate": 0.95,
            "bachelor": 1.0,  # baseline
            "master": 1.1,
            "phd": 1.15,
            "mba": 1.15
        }
        education_multiplier = education_multipliers.get(education_level.lower(), 1.0)
        adjusted_salary *= education_multiplier
        
        # Skills adjustment
        if skills and len(skills) > 0:
            # More advanced adjustment would evaluate skill relevance and rarity
            # For simplicity, we use a basic multiplier based on skill count
            skill_count = min(len(skills), 10)  # Cap at 10 skills
            skill_multiplier = 1.0 + (skill_count * 0.01)  # 1% per skill up to 10%
            adjusted_salary *= skill_multiplier
            
        # Fine-tune experience adjustment
        # Already accounted for in broad categories, but add granularity
        experience_factor = 1.0
        
        # Within each experience category, apply small adjustments
        if years_experience < 3:  # entry
            experience_factor = 0.9 + (years_experience * 0.033)  # 0.9 to 1.0
        elif years_experience < 7:  # mid
            experience_factor = 1.0 + ((years_experience - 3) * 0.025)  # 1.0 to 1.1
        elif years_experience < 12:  # senior
            experience_factor = 1.1 + ((years_experience - 7) * 0.02)  # 1.1 to 1.2
        else:  # lead
            experience_factor = 1.2 + (min(years_experience - 12, 8) * 0.0125)  # 1.2 to 1.3
            
        adjusted_salary *= experience_factor
        
        return adjusted_salary
    
    def _calculate_percentiles(self, salary: float, industry: str, job_title: str) -> Dict[str, int]:
        """Calculate salary percentiles (10th, 25th, 50th, 75th, 90th)."""
        # Get industry and role specific variance factors
        industry_variances = {
            "technology": {"variance": 0.4, "skew": 0.1},  # high variance, right skew
            "finance": {"variance": 0.5, "skew": 0.15},    # very high variance, right skew
            "healthcare": {"variance": 0.3, "skew": 0.05}, # moderate variance, slight skew
            "marketing": {"variance": 0.35, "skew": 0.08}, # moderate-high variance
            "Default": {"variance": 0.3, "skew": 0.05}     # moderate variance, slight skew
        }
        
        role_variance_adjustments = {
            "software_engineer": 0.05,
            "data_scientist": 0.08,
            "product_manager": 0.03,
            "ux_designer": 0.02,
            "financial_analyst": 0.04,
            "investment_banker": 0.12,
            "registered_nurse": 0.0,
            "physician": 0.08,
            "marketing_manager": 0.03,
            "content_strategist": 0.02,
            "Default": 0.0
        }
        
        # Get variance parameters
        variance_data = industry_variances.get(industry, industry_variances["Default"])
        base_variance = variance_data["variance"]
        skew = variance_data["skew"]
        
        # Adjust variance for specific roles
        role_adjustment = role_variance_adjustments.get(job_title, role_variance_adjustments["Default"])
        adjusted_variance = base_variance + role_adjustment
        
        # Calculate percentiles with skew
        p10 = int(salary * (1 - adjusted_variance - skew))
        p25 = int(salary * (1 - (adjusted_variance * 0.5) - (skew * 0.5)))
        p50 = int(salary)  # Median
        p75 = int(salary * (1 + (adjusted_variance * 0.5) + (skew * 0.5)))
        p90 = int(salary * (1 + adjusted_variance + skew))
        
        return {
            "10th": p10,
            "25th": p25,
            "50th": p50,
            "75th": p75,
            "90th": p90
        }
    
    def _generate_regional_comparison(self, job_title: str, current_location: str,
                                     experience_level: str, industry: str) -> Dict[str, Any]:
        """Generate comparison of salaries across different regions."""
        # List of locations to compare
        locations_to_compare = [
            "San Francisco", "New York", "Boston", "Chicago", 
            "Los Angeles", "Seattle", "Austin", "Remote"
        ]
        
        # Ensure current location is in the list
        if current_location not in locations_to_compare and current_location != "Default":
            locations_to_compare.append(current_location)
            
        # Calculate salaries for each location
        regional_data = {}
        for location in locations_to_compare:
            base_salary = self._calculate_base_salary(job_title, location, experience_level, industry)
            col_index = self._get_cost_of_living_index(location)
            
            # If location is Default, calculate national average
            if location == "Default":
                location_label = "National Average"
            else:
                location_label = location
                
            regional_data[location_label] = {
                "salary": int(base_salary),
                "cost_of_living_index": col_index,
                "adjusted_salary": int(base_salary / (col_index / 100))  # Adjust for cost of living
            }
            
        # Add summary insights
        current_salary = regional_data.get(current_location, 
                                          regional_data.get("Remote", next(iter(regional_data.values()))))["salary"]
        
        highest_location = max(regional_data.items(), key=lambda x: x[1]["salary"])
        lowest_location = min(regional_data.items(), key=lambda x: x[1]["salary"])
        
        best_value_location = max(regional_data.items(), key=lambda x: x[1]["adjusted_salary"])
        
        summary = {
            "highest_paying": {
                "location": highest_location[0],
                "salary": highest_location[1]["salary"],
                "difference": highest_location[1]["salary"] - current_salary,
                "percent_difference": round(((highest_location[1]["salary"] / current_salary) - 1) * 100, 1)
            },
            "lowest_paying": {
                "location": lowest_location[0],
                "salary": lowest_location[1]["salary"],
                "difference": lowest_location[1]["salary"] - current_salary,
                "percent_difference": round(((lowest_location[1]["salary"] / current_salary) - 1) * 100, 1)
            },
            "best_value": {
                "location": best_value_location[0],
                "salary": best_value_location[1]["salary"],
                "adjusted_salary": best_value_location[1]["adjusted_salary"],
                "cost_of_living_index": best_value_location[1]["cost_of_living_index"]
            }
        }
        
        return {
            "regions": regional_data,
            "summary": summary
        }
    
    def _generate_industry_comparison(self, job_title: str, experience_level: str, 
                                     current_industry: str) -> Dict[str, Any]:
        """Generate comparison of salaries across different industries."""
        # List of industries to compare
        industries_to_compare = ["technology", "finance", "healthcare", "marketing"]
        
        # Ensure current industry is in the list
        if current_industry not in industries_to_compare and current_industry != "Default":
            industries_to_compare.append(current_industry)
            
        # Calculate salaries for each industry in the default location
        industry_data = {}
        for industry in industries_to_compare:
            base_salary = self._calculate_base_salary(job_title, "Default", experience_level, industry)
            growth_rate = self._get_industry_growth_rate(industry)
            
            industry_data[industry.capitalize()] = {
                "salary": int(base_salary),
                "growth_rate": growth_rate,
                "five_year_projection": int(base_salary * (1 + (growth_rate/100) * 5))
            }
            
        # Add summary insights
        current_industry_cap = current_industry.capitalize()
        current_salary = industry_data.get(current_industry_cap, next(iter(industry_data.values())))["salary"]
        
        highest_industry = max(industry_data.items(), key=lambda x: x[1]["salary"])
        lowest_industry = min(industry_data.items(), key=lambda x: x[1]["salary"])
        
        fastest_growing = max(industry_data.items(), key=lambda x: x[1]["growth_rate"])
        
        summary = {
            "highest_paying": {
                "industry": highest_industry[0],
                "salary": highest_industry[1]["salary"],
                "difference": highest_industry[1]["salary"] - current_salary,
                "percent_difference": round(((highest_industry[1]["salary"] / current_salary) - 1) * 100, 1)
            },
            "lowest_paying": {
                "industry": lowest_industry[0],
                "salary": lowest_industry[1]["salary"],
                "difference": lowest_industry[1]["salary"] - current_salary,
                "percent_difference": round(((lowest_industry[1]["salary"] / current_salary) - 1) * 100, 1)
            },
            "fastest_growing": {
                "industry": fastest_growing[0],
                "growth_rate": fastest_growing[1]["growth_rate"],
                "five_year_projection": fastest_growing[1]["five_year_projection"]
            }
        }
        
        return {
            "industries": industry_data,
            "summary": summary
        }
    
    def _analyze_benefits(self, industry: str) -> Dict[str, Any]:
        """Analyze typical benefits package for the industry."""
        industry_benefits = self._benefits_data.get(industry, self._benefits_data["Default"])
        
        # Calculate monetary value of benefits
        total_value = sum(industry_benefits["monetary_value"].values())
        
        return {
            "standard_benefits": industry_benefits["standard"],
            "premium_benefits": industry_benefits["premium"],
            "rare_benefits": industry_benefits["rare"],
            "monetary_values": industry_benefits["monetary_value"],
            "estimated_annual_value": total_value,
            "percentage_of_compensation": round((total_value / 100000) * 100, 1)  # Assuming $100k base for percentage
        }
    
    def _generate_negotiation_guidance(self, experience_level: str) -> Dict[str, Any]:
        """Generate negotiation guidance based on experience level."""
        negotiation_tips = self._negotiation_strategies.get(experience_level, self._negotiation_strategies["mid"])
        
        return {
            "key_points": negotiation_tips["key_points"],
            "recommended_phrases": negotiation_tips["phrases"],
            "mistakes_to_avoid": negotiation_tips["avoid"],
            "specific_guidance": [
                "Research the company's compensation structure and funding status",
                "Prepare a specific case for your value based on achievements and skills",
                "Consider the full compensation package, not just base salary",
                "Be prepared to discuss specific metrics and achievements",
                "Have a clear understanding of your minimum acceptable offer"
            ]
        }
    
    def _project_future_earnings(self, current_salary: float, industry: str, 
                                job_title: str, years_experience: int) -> Dict[str, Any]:
        """Project future earnings potential over 1, 3, 5, and 10 years."""
        # Get growth rates
        industry_growth = self._get_industry_growth_rate(industry)
        role_growth = self._get_role_growth_rate(industry, job_title)
        
        # Calculate average annual growth rate (industry + role + experience curve)
        experience_curve = max(0, (10 - years_experience)) * 0.5  # Higher growth early in career
        annual_growth_rate = (industry_growth + role_growth + experience_curve) / 100
        
        # Project future earnings
        one_year = int(current_salary * (1 + annual_growth_rate))
        three_year = int(current_salary * (1 + annual_growth_rate) ** 3)
        five_year = int(current_salary * (1 + annual_growth_rate) ** 5)
        ten_year = int(current_salary * (1 + annual_growth_rate) ** 10)
        
        # Calculate career progression
        next_level = self._get_next_career_level(years_experience)
        years_to_next_level = max(1, next_level["years_to_reach"] - years_experience)
        
        salary_at_next_level = int(current_salary * (1 + annual_growth_rate) ** years_to_next_level * 
                                  next_level["salary_multiplier"])
        
        return {
            "projected_salary": {
                "1_year": one_year,
                "3_year": three_year,
                "5_year": five_year,
                "10_year": ten_year
            },
            "annual_growth_rate": round(annual_growth_rate * 100, 1),
            "career_progression": {
                "current_level": self._categorize_experience(years_experience),
                "next_level": next_level["title"],
                "estimated_years_to_reach": years_to_next_level,
                "estimated_salary_at_next_level": salary_at_next_level
            },
            "factors_affecting_growth": {
                "industry_growth": industry_growth,
                "role_specific_growth": role_growth,
                "experience_curve": round(experience_curve, 1)
            }
        }
    
    def _calculate_total_compensation(self, salary: float, 
                                     benefits_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate total compensation including benefits value."""
        benefits_value = benefits_analysis["estimated_annual_value"]
        total = int(salary + benefits_value)
        
        return {
            "base_salary": int(salary),
            "benefits_value": benefits_value,
            "total_annual_compensation": total,
            "monthly_compensation": int(total / 12),
            "benefits_percentage": round((benefits_value / total) * 100, 1)
        }
        
    def _get_cost_of_living_index(self, location: str) -> float:
        """Get cost of living index for a location."""
        return self._cost_of_living_data.get(location, self._cost_of_living_data["Default"])
    
    def _get_industry_growth_rate(self, industry: str) -> float:
        """Get annual growth rate for an industry."""
        industry_data = self._industry_growth_data.get(industry, self._industry_growth_data["Default"])
        return industry_data["industry_growth"]
    
    def _get_role_growth_rate(self, industry: str, job_title: str) -> float:
        """Get annual growth rate for a specific role."""
        industry_data = self._industry_growth_data.get(industry, self._industry_growth_data["Default"])
        return industry_data.get(job_title, industry_data["Default"])
    
    def _get_next_career_level(self, years_experience: int) -> Dict[str, Any]:
        """Determine the next career level and years to reach it."""
        current_level = self._categorize_experience(years_experience)
        
        if current_level == "entry":
            return {
                "title": "mid-level",
                "years_to_reach": 3,
                "salary_multiplier": 1.2
            }
        elif current_level == "mid":
            return {
                "title": "senior",
                "years_to_reach": 7,
                "salary_multiplier": 1.25
            }
        elif current_level == "senior":
            return {
                "title": "lead/manager",
                "years_to_reach": 12,
                "salary_multiplier": 1.3
            }
        else:  # already at lead level
            return {
                "title": "executive",
                "years_to_reach": years_experience + 3,
                "salary_multiplier": 1.4
            }
    
    def _get_fallback_analysis(self, job_title: str, location: str, 
                              years_experience: int, industry: str) -> Dict[str, Any]:
        """Provide a simplified fallback analysis when detailed analysis fails."""
        # Base salary estimation based on years of experience
        if years_experience < 3:
            base_salary = 60000
        elif years_experience < 7:
            base_salary = 85000
        elif years_experience < 12:
            base_salary = 110000
        else:
            base_salary = 140000
            
        # Simple adjustments
        if "senior" in job_title.lower() or "lead" in job_title.lower():
            base_salary *= 1.2
        if "manager" in job_title.lower() or "director" in job_title.lower():
            base_salary *= 1.3
            
        # Location adjustment
        high_col_locations = ["san francisco", "new york", "seattle", "boston", "los angeles"]
        if any(loc in location.lower() for loc in high_col_locations):
            base_salary *= 1.3
            
        # Return simplified analysis
        return {
            "salary_estimate": {
                "min": int(base_salary * 0.9),
                "median": int(base_salary),
                "max": int(base_salary * 1.1)
            },
            "note": "This is a simplified estimate. Our detailed analysis couldn't be completed with the provided information."
        }

    def generate_summary_report(self, analysis_results: Dict[str, Any]) -> str:
        """
        Generate a human-readable summary report from salary analysis results.
        
        Args:
            analysis_results: The results from analyze_salary method
            
        Returns:
            A formatted string with key salary insights
        """
        try:
            # Extract key information
            salary_range = analysis_results["salary_estimate"]
            position = analysis_results["position_analysis"]
            benefits = analysis_results["benefits_analysis"]
            future = analysis_results["future_projection"]
            total_comp = analysis_results["total_compensation"]
            
            # Format currency values
            def format_currency(amount):
                return f"${amount:,}"
            
            # Build report
            report = []
            report.append(f"# SALARY INSIGHTS REPORT FOR: {position['job_title'].upper()}")
            report.append(f"\n## SUMMARY")
            report.append(f"Position: {position['job_title']} ({position['experience_level']} level)")
            report.append(f"Industry: {position['industry']}")
            report.append(f"Location: {position['location']}")
            
            report.append(f"\n## SALARY RANGE")
            report.append(f"Estimated salary range: {format_currency(salary_range['min'])} - {format_currency(salary_range['max'])}")
            report.append(f"Median expected salary: {format_currency(salary_range['median'])}")
            
            report.append(f"\n## TOTAL COMPENSATION")
            report.append(f"Base salary: {format_currency(total_comp['base_salary'])}")
            report.append(f"Benefits value: {format_currency(total_comp['benefits_value'])} ({total_comp['benefits_percentage']}% of total)")
            report.append(f"Total annual compensation: {format_currency(total_comp['total_annual_compensation'])}")
            report.append(f"Monthly compensation: {format_currency(total_comp['monthly_compensation'])}")
            
            report.append(f"\n## COMMON BENEFITS")
            report.append("Standard benefits:")
            for benefit in benefits['standard_benefits'][:5]:  # Limit to first 5
                report.append(f"- {benefit}")
            
            report.append("\nPremium benefits often available:")
            for benefit in benefits['premium_benefits'][:3]:  # Limit to first 3
                report.append(f"- {benefit}")
            
            report.append(f"\n## FUTURE OUTLOOK")
            report.append(f"Expected annual growth rate: {future['annual_growth_rate']}%")
            report.append(f"Projected 1-year salary: {format_currency(future['projected_salary']['1_year'])}")
            report.append(f"Projected 5-year salary: {format_currency(future['projected_salary']['5_year'])}")
            
            # Career progression
            career = future['career_progression']
            report.append(f"\nCareer progression: {career['current_level']} → {career['next_level']} (est. {career['estimated_years_to_reach']} years)")
            report.append(f"Estimated salary at next level: {format_currency(career['estimated_salary_at_next_level'])}")
            
            # Regional comparison if available
            if "regional_comparison" in analysis_results:
                regional = analysis_results["regional_comparison"]["summary"]
                highest = regional["highest_paying"]
                report.append(f"\n## REGIONAL INSIGHTS")
                report.append(f"Highest paying location: {highest['location']} at {format_currency(highest['salary'])} ({highest['percent_difference']}% higher)")
                
                if "best_value" in regional:
                    best = regional["best_value"]
                    report.append(f"Best value location: {best['location']} (adjusted for cost of living)")
            
            # Negotiation tips
            if "negotiation_guidance" in analysis_results:
                neg = analysis_results["negotiation_guidance"]
                report.append(f"\n## NEGOTIATION TIPS")
                for tip in neg["key_points"][:3]:  # Limit to first 3
                    report.append(f"- {tip}")
            
            return "\n".join(report)
            
        except Exception as e:
            self.logger.error(f"Error generating summary report: {str(e)}")
            return f"Unable to generate detailed salary report. Basic estimate: ${analysis_results['salary_estimate']['median']:,}"

    def generate_negotiation_script(self, analysis_results: Dict[str, Any]) -> str:
        """
        Generate a personalized negotiation script based on analysis results.
        
        Args:
            analysis_results: The results from analyze_salary method
            
        Returns:
            A formatted string with a negotiation script template
        """
        try:
            # Extract key information
            position = analysis_results["position_analysis"]
            salary = analysis_results["salary_estimate"]["median"]
            negotiation = analysis_results["negotiation_guidance"]
            percentiles = analysis_results["percentiles"]
            total_comp = analysis_results["total_compensation"]
            
            # Target a bit above the median (between median and 75th percentile)
            target_salary = int((salary + percentiles["75th"]) / 2)
            min_acceptable = percentiles["25th"]
            
            # Format currency values
            def format_currency(amount):
                return f"${amount:,}"
            
            # Build negotiation script
            script = []
            script.append(f"# SALARY NEGOTIATION SCRIPT: {position['job_title'].upper()}")
            script.append(f"\n## PREPARATION NOTES")
            script.append(f"Position: {position['job_title']}")
            script.append(f"Industry: {position['industry']}")
            script.append(f"Market value: {format_currency(salary)}")
            script.append(f"Target salary: {format_currency(target_salary)}")
            script.append(f"Minimum acceptable: {format_currency(min_acceptable)}")
            script.append(f"Full compensation target: {format_currency(total_comp['total_annual_compensation'])}")
            
            script.append(f"\n## OPENING STATEMENT")
            script.append(f"Thank you for the offer. I'm excited about the opportunity to join [Company Name] ")
            script.append(f"as a {position['job_title']}. Based on my research and experience, I was expecting ")
            script.append(f"a base salary in the range of {format_currency(target_salary)} to {format_currency(percentiles['75th'])}. ")
            script.append(f"This aligns with the market rate for someone with my background and skills in this industry.")
            
            script.append(f"\n## KEY TALKING POINTS")
            # Add one random phrase from negotiation guidance
            if negotiation["recommended_phrases"]:
                import random
                script.append(f"• {random.choice(negotiation['recommended_phrases'])}")
            
            script.append(f"• The skills and experience I bring include [list 2-3 key skills relevant to the role]")
            script.append(f"• In my previous role, I [mention specific achievement with measurable results]")
            script.append(f"• I'm particularly excited about contributing to [specific company project or goal]")
            
            script.append(f"\n## DISCUSSING BENEFITS")
            script.append(f"In addition to base salary, I'd like to discuss the overall compensation package, including:")
            for benefit in analysis_results["benefits_analysis"]["standard_benefits"][:3]:
                script.append(f"• {benefit}")
            script.append(f"• [Any other specific benefits important to you]")
            
            script.append(f"\n## HANDLING PUSHBACK")
            script.append(f"If they can't meet your salary expectations:")
            script.append(f"'I understand there may be budget constraints. Would you be open to:")
            script.append(f"• A performance review in 6 months with salary adjustment potential")
            script.append(f"• Additional PTO or flexible working arrangements")
            script.append(f"• A signing bonus or equity compensation")
            script.append(f"• Professional development or educational opportunities'")
            
            script.append(f"\n## CLOSING THE NEGOTIATION")
            script.append(f"'Thank you for considering my request. I'm very enthusiastic about this role and ")
            script.append(f"confident that I can bring significant value to [Company Name]. ")
            script.append(f"I look forward to reaching an agreement that works for both of us.'")
            
            script.append(f"\n## THINGS TO AVOID")
            for mistake in negotiation["mistakes_to_avoid"][:3]:
                script.append(f"• {mistake}")
            
            return "\n".join(script)
            
        except Exception as e:
            self.logger.error(f"Error generating negotiation script: {str(e)}")
            return "Unable to generate a personalized negotiation script with the provided information."