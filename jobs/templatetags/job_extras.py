from django import template
from subscriptions.job_qualification_checker import JobQualificationChecker
from subscriptions.candidate_matching import CandidateMatchingSystem
import logging

register = template.Library()
logger = logging.getLogger(__name__)

@register.filter
def get_item(dictionary, key):
    """
    Template filter to get an item from a dictionary by key.
    Usage: {{ my_dict|get_item:key_variable }}
    """
    return dictionary.get(key, 0)

@register.filter
def split(value, delimiter=','):
    """
    Split a string into a list using the specified delimiter.
    Usage: {{ my_string|split:',' }}
    """
    if value:
        return value.split(delimiter)
    return []

@register.filter
def trim(value):
    """
    Trim whitespace from a string.
    Usage: {{ my_string|trim }}
    """
    if value:
        return value.strip()
    return value

@register.filter
def subtract(value, arg):
    """
    Subtract the arg from the value.
    Usage: {{ value|subtract:arg }}
    """
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def divide(value, arg):
    """
    Divide the value by the arg.
    Usage: {{ value|divide:arg }}
    """
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def widthratio(value, max_value, max_width):
    """
    Calculate a width based on a value and a maximum value.
    Usage: {{ value|widthratio:max_value:max_width }}
    """
    try:
        return int(float(value) / float(max_value) * int(max_width))
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def abs(value):
    """
    Return the absolute value of a number.
    Usage: {{ value|abs }}
    """
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return value

@register.filter
def multiply(value, arg):
    """
    Multiply the value by the arg.
    Usage: {{ value|multiply:arg }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value
        
@register.filter
def qualification_match(job, user):
    """
    Calculate the qualification match percentage between a job and a user.
    Usage: {{ job|qualification_match:user }}
    
    Returns:
        int: Match percentage (0-100)
    """
    if not user or not user.is_authenticated or user.user_type != 'job_seeker':
        return None
        
    try:
        checker = JobQualificationChecker()
        match_percentage = checker.calculate_job_match_percentage(user, job)
        return int(match_percentage)
    except Exception as e:
        logger.error(f"Error calculating match percentage: {str(e)}")
        return None

@register.filter
def match_color_class(percentage):
    """
    Return the appropriate color class based on match percentage.
    Usage: {{ percentage|match_color_class }}
    
    Returns:
        str: CSS color class
    """
    if percentage is None:
        return "bg-gray-200 text-gray-700"
        
    if percentage >= 85:
        return "bg-green-100 text-green-800"
    elif percentage >= 70:
        return "bg-blue-100 text-blue-800"
    elif percentage >= 50:
        return "bg-yellow-100 text-yellow-700"
    else:
        return "bg-red-100 text-red-800"

@register.inclusion_tag('jobs/partials/match_percentage_badge.html')
def match_percentage_badge(job, user):
    """
    Render a match percentage badge for a job listing.
    Usage: {% match_percentage_badge job user %}
    """
    if not user or not user.is_authenticated or user.user_type != 'job_seeker':
        return {'display': False}
        
    try:
        checker = JobQualificationChecker()
        match_data = checker.get_detailed_match_data(user, job)
        
        return {
            'display': True,
            'percentage': int(match_data['overall_percentage']),
            'skill_match': int(match_data['skill_match_percentage']),
            'experience_match': int(match_data['experience_match_percentage']),
            'education_match': int(match_data['education_match_percentage']),
            'job_id': job.id
        }
    except Exception as e:
        logger.error(f"Error calculating detailed match: {str(e)}")
        return {'display': False}
