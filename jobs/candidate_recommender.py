from django.db.models import Q
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import JobListing, JobApplication

User = get_user_model()

def get_recommended_candidates(job, limit=10):
    """
    Get recommended candidates for a job based on skills, experience, and education.
    
    Args:
        job: The JobListing to find candidates for
        limit: Maximum number of candidates to return
        
    Returns:
        List of recommended User objects with match scores
    """
    # Get job skills
    job_skills = [skill.strip().lower() for skill in job.skills_required.split(',') if skill.strip()]
    
    if not job_skills:
        return []
    
    # Get all job seekers with public profiles who haven't applied yet
    candidates = User.objects.filter(
        user_type='job_seeker',
        is_profile_public=True
    ).exclude(
        applications__job=job
    )
    
    # Calculate match scores for each candidate
    candidate_matches = []
    for candidate in candidates:
        # Skip candidates without skills
        if not candidate.skills:
            continue
        
        # Get candidate skills
        candidate_skills = [skill.strip().lower() for skill in candidate.skills.split(',') if skill.strip()]
        
        # Calculate skill match
        matching_skills = set(candidate_skills).intersection(set(job_skills))
        if not matching_skills:
            continue
            
        skills_match = int((len(matching_skills) / len(job_skills)) * 100)
        
        # Calculate experience match (simplified)
        experience_match = 0
        if candidate.experience and job.experience_level:
            # Simple heuristic based on experience text length and job level
            exp_length = len(candidate.experience)
            if job.experience_level == 'entry' and exp_length > 0:
                experience_match = 80
            elif job.experience_level == 'mid' and exp_length > 100:
                experience_match = 85
            elif job.experience_level == 'senior' and exp_length > 200:
                experience_match = 90
            elif job.experience_level == 'executive' and exp_length > 300:
                experience_match = 95
        
        # Calculate education match (simplified)
        education_match = 0
        if candidate.education:
            # Simple presence check
            education_match = 80
        
        # Calculate overall match
        if experience_match == 0 and education_match == 0:
            overall_match = skills_match
        else:
            overall_match = (skills_match + experience_match + education_match) // 3
        
        # Only include candidates with at least 50% match
        if overall_match >= 50:
            candidate_matches.append({
                'user': candidate,
                'skills_match': skills_match,
                'experience_match': experience_match,
                'education_match': education_match,
                'overall_match': overall_match,
                'matching_skills': list(matching_skills)
            })
    
    # Sort by overall match (descending)
    candidate_matches.sort(key=lambda x: x['overall_match'], reverse=True)
    
    # Return top matches
    return candidate_matches[:limit]

def get_candidate_recommendations_for_employer(employer, limit=20):
    """
    Get candidate recommendations across all of an employer's active jobs.
    
    Args:
        employer: The employer User to find candidates for
        limit: Maximum number of candidates to return
        
    Returns:
        Dictionary mapping jobs to recommended candidates
    """
    # Get all active jobs posted by the employer
    active_jobs = JobListing.objects.filter(
        posted_by=employer,
        status='published'
    ).exclude(
        Q(application_deadline__lt=timezone.now()) & ~Q(application_deadline=None)
    )
    
    recommendations = {}
    
    for job in active_jobs:
        candidates = get_recommended_candidates(job, limit=5)
        if candidates:
            recommendations[job] = candidates
    
    return recommendations
