from django.db.models import Q, Count
from django.utils import timezone
from .models import JobListing, SavedJob, JobApplication

def get_recommended_jobs(user, limit=10):
    """
    Get job recommendations for a job seeker based on their profile,
    saved jobs, and application history.

    Args:
        user: The user to get recommendations for
        limit: Maximum number of recommendations to return

    Returns:
        List of recommended JobListing objects with match scores
    """
    if not user.is_authenticated or user.user_type != 'job_seeker':
        return []

    # Start with all published jobs
    recommended_jobs = JobListing.objects.filter(
        status='published'
    ).exclude(
        # Exclude jobs that have expired
        Q(application_deadline__lt=timezone.now()) & ~Q(application_deadline=None)
    ).exclude(
        # Exclude jobs without slugs
        Q(slug='') | Q(slug=None)
    )

    # Exclude jobs the user has already applied to
    applied_job_ids = JobApplication.objects.filter(
        applicant=user
    ).values_list('job_id', flat=True)

    recommended_jobs = recommended_jobs.exclude(id__in=applied_job_ids)

    # Get user's saved jobs for reference
    saved_job_ids = SavedJob.objects.filter(
        user=user
    ).values_list('job_id', flat=True)

    # Get user's skills from profile
    user_skills = []
    if user.skills:
        user_skills = [skill.strip().lower() for skill in user.skills.split(',')]

    # If user has skills, prioritize jobs matching those skills
    if user_skills:
        skill_matches = []
        for job in recommended_jobs:
            if not job.skills_required:
                continue

            job_skills = [skill.strip().lower() for skill in job.skills_required.split(',')]
            matching_skills = set(user_skills).intersection(set(job_skills))

            # Calculate match percentage
            if matching_skills:
                skills_match = int((len(matching_skills) / len(job_skills)) * 100)
                skill_matches.append({
                    'job': job,
                    'skills_match': skills_match,
                    'overall_match': skills_match,
                    'matching_skills': list(matching_skills)
                })

        # Sort by match percentage (descending)
        skill_matches.sort(key=lambda x: x['overall_match'], reverse=True)

        # Return top matches
        return skill_matches[:limit]

    # If no skill matches or no skills in profile, try to use saved job categories
    if saved_job_ids:
        # Get categories of saved jobs
        saved_job_categories = JobListing.objects.filter(
            id__in=saved_job_ids
        ).values_list('category_id', flat=True).distinct()

        if saved_job_categories:
            # Prioritize jobs in those categories
            category_matches = recommended_jobs.filter(category_id__in=saved_job_categories)

            if category_matches:
                # Convert to list of dictionaries with match scores
                result = []
                for job in category_matches[:limit]:
                    result.append({
                        'job': job,
                        'skills_match': 0,
                        'overall_match': 60,  # Higher match score for category matches
                        'matching_skills': []
                    })
                return result

    # If no other criteria match, return newest jobs with default match scores
    result = []
    for job in recommended_jobs.order_by('-created_at')[:limit]:
        result.append({
            'job': job,
            'skills_match': 0,
            'overall_match': 50,  # Default match score
            'matching_skills': []
        })

    return result

def get_similar_jobs(job, limit=4):
    """
    Get jobs similar to the given job based on category, skills, and job type.

    Args:
        job: The job to find similar jobs for
        limit: Maximum number of similar jobs to return

    Returns:
        QuerySet of similar JobListing objects
    """
    # Start with all published jobs except the current one
    similar_jobs = JobListing.objects.filter(
        status='published'
    ).exclude(
        id=job.id
    ).exclude(
        # Exclude jobs that have expired
        Q(application_deadline__lt=timezone.now()) & ~Q(application_deadline=None)
    )

    # Get job skills
    job_skills = [skill.strip().lower() for skill in job.skills_required.split(',')]

    # Calculate skill similarity for each job
    skill_matches = []
    for similar_job in similar_jobs:
        similar_job_skills = [skill.strip().lower() for skill in similar_job.skills_required.split(',')]
        matching_skills = set(job_skills).intersection(set(similar_job_skills))
        skill_matches.append((similar_job.id, len(matching_skills)))

    # Sort by number of matching skills (descending)
    skill_matches.sort(key=lambda x: x[1], reverse=True)
    skill_match_ids = [job_id for job_id, _ in skill_matches if _ > 0]

    # If we have skill matches, prioritize those
    if skill_match_ids:
        from django.db.models import Case, When, Value, IntegerField

        # Create ordering based on skill matches
        preserved_order = Case(
            *[When(id=pk, then=Value(i)) for i, pk in enumerate(skill_match_ids)],
            default=Value(len(skill_match_ids)),
            output_field=IntegerField()
        )

        # Apply ordering
        skill_matched_jobs = similar_jobs.filter(id__in=skill_match_ids).order_by(preserved_order)

        # If we have enough skill matches, return those
        if skill_matched_jobs.count() >= limit:
            return skill_matched_jobs[:limit]

        # Otherwise, get remaining jobs from same category
        remaining = limit - skill_matched_jobs.count()
        category_matches = similar_jobs.filter(
            category=job.category
        ).exclude(
            id__in=skill_matched_jobs.values_list('id', flat=True)
        ).order_by('-created_at')[:remaining]

        # Combine the two querysets
        return list(skill_matched_jobs) + list(category_matches)

    # If no skill matches, prioritize jobs in the same category
    category_matches = similar_jobs.filter(category=job.category).order_by('-created_at')

    if category_matches.count() >= limit:
        return category_matches[:limit]

    # If we don't have enough category matches, add jobs of the same type
    remaining = limit - category_matches.count()
    type_matches = similar_jobs.filter(
        job_type=job.job_type
    ).exclude(
        id__in=category_matches.values_list('id', flat=True)
    ).order_by('-created_at')[:remaining]

    # Combine the two querysets
    return list(category_matches) + list(type_matches)
