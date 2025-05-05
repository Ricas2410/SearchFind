from django.db.models import Q
from django.utils import timezone
from .models import JobListing

def get_recommended_jobs(user, limit=10):
    """
    Get recommended jobs for a job seeker based on skills, experience, and education.

    Args:
        user: The User to find jobs for
        limit: Maximum number of jobs to return

    Returns:
        List of recommended JobListing objects with match scores
    """
    # Get user skills
    user_skills = []
    if user.skills:
        user_skills = [skill.strip().lower() for skill in user.skills.split(',') if skill.strip()]

    if not user_skills:
        return []

    # Get all active jobs that the user hasn't applied to yet
    active_jobs = JobListing.objects.filter(
        status='published'
    ).exclude(
        Q(application_deadline__lt=timezone.now()) & ~Q(application_deadline=None)
    ).exclude(
        applications__applicant=user
    )

    # Calculate match scores for each job
    job_matches = []
    for job in active_jobs:
        # Skip jobs without skills or slug
        if not job.skills_required or not job.slug:
            continue

        # Get job skills
        job_skills = [skill.strip().lower() for skill in job.skills_required.split(',') if skill.strip()]

        # Calculate skill match
        matching_skills = set(user_skills).intersection(set(job_skills))
        if not matching_skills:
            continue

        skills_match = int((len(matching_skills) / len(job_skills)) * 100)

        # Calculate experience match (simplified)
        experience_match = 0
        if user.experience and job.experience_level:
            # Simple heuristic based on experience text length and job level
            exp_length = len(user.experience)
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
        if user.education:
            # Simple presence check
            education_match = 80

        # Calculate overall match
        if experience_match == 0 and education_match == 0:
            overall_match = skills_match
        else:
            overall_match = (skills_match + experience_match + education_match) // 3

        # Only include jobs with at least 50% match
        if overall_match >= 50:
            job_matches.append({
                'job': job,
                'skills_match': skills_match,
                'experience_match': experience_match,
                'education_match': education_match,
                'overall_match': overall_match,
                'matching_skills': list(matching_skills)
            })

    # Sort by overall match (descending)
    job_matches.sort(key=lambda x: x['overall_match'], reverse=True)

    # Return top matches
    return job_matches[:limit]
