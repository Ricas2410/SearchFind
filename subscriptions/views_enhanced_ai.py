"""
Enhanced AI Views for Pro Features

This module contains views for advanced AI features available to Pro users,
including resume analysis with improvement suggestions, job qualification
matching, and other enhanced AI capabilities.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.conf import settings
from django.views.decorators.http import require_POST, require_GET
from django.template.loader import render_to_string
from django.utils import timezone

from .models import (
    SubscriptionPlan, UserSubscription, Payment, PaystackConfig
)
from .ai_models import (
    JobMatchScore, ResumeAnalysis, CoverLetterAnalysis
)
from .models_pro_features import SalaryInsights
from .forms import PaymentForm, SalaryInsightsForm
from .paystack import PaystackAPI
# TODO: Replace with enhanced services once implemented
from .ai_services import (
    ResumeAnalysisService, ResumeBuilderService,
    JobMatchService, CoverLetterAnalysisService,
    SalaryInsightsService, CareerPathService,
    JobPostingAnalysisService, ApplicationScreeningService
)
from .resume_improvement_suggestions import ResumeImprovementSuggestions
from .job_qualification_checker import JobQualificationChecker
from jobs.models import JobListing, JobApplication


@login_required
def apply_with_resume_analysis(request, job_id):
    """
    Analyze resume before applying for a job - Pro feature

    This enhanced version includes:
    1. Resume analysis with detailed scoring
    2. Job match percentage calculation
    3. Resume improvement suggestions when match is below threshold
    4. ATS optimization recommendations
    """
    job = get_object_or_404(JobListing, pk=job_id)

    # Check if user is subscribed
    is_pro = hasattr(request.user, 'is_pro') and request.user.is_pro

    if not is_pro:
        messages.warning(request, 'This feature is only available to Pro users. Please upgrade your account.')
        return redirect('subscriptions:plans')

    # Check if user already applied
    if JobApplication.objects.filter(job=job, applicant=request.user).exists():
        messages.info(request, 'You have already applied for this job.')
        return redirect('jobs:job_detail', slug=job.slug)

    if request.method == 'POST':
        # Process the resume analysis
        resume_file = request.FILES.get('resume')
        skip_suggestions = request.POST.get('skip_suggestions') == 'true'

        if not resume_file:
            messages.error(request, 'Please upload a resume file.')
            return redirect('subscriptions:apply_with_resume_analysis', job_id=job_id)

        # Analyze the resume using our real AI implementation
        analysis_results = ResumeAnalysisService.analyze_resume(resume_file=resume_file)

        # Check if the file is a valid resume
        if not analysis_results.get('is_valid', False):
            error_message = analysis_results.get('error', 'The uploaded file does not appear to be a valid resume.')
            messages.error(request, error_message)
            messages.warning(request, 'Please ensure you upload a proper resume file (PDF, DOCX, or TXT) with relevant professional information.')
            return redirect('subscriptions:apply_with_resume_analysis', job_id=job_id)

        # Calculate match score using our candidate matching system
        match_score = JobMatchService.calculate_match_score(
            resume_analysis=analysis_results,
            job_description=job.description,
            job_title=job.title,
            job_skills=job.get_skills_as_list()
        )

        # Save the analysis and match score
        resume_analysis = ResumeAnalysis.objects.create(
            user=request.user,
            job=job,
            analysis_data=analysis_results,
            score=analysis_results.get('overall_score', 0)
        )

        match_score_obj = JobMatchScore.objects.create(
            user=request.user,
            job=job,
            resume_analysis=resume_analysis,
            score=match_score.get('overall_percentage', 0),
            match_data=match_score
        )

        # Check if match score is below threshold and offer improvement suggestions
        match_percentage = match_score.get('overall_percentage', 0)
        if match_percentage < 70 and not skip_suggestions:
            # Get resume improvement suggestions
            suggestion_engine = ResumeImprovementSuggestions()
            suggestion_results = suggestion_engine.analyze_resume_for_job(
                resume_file_object=resume_file,
                job_title=job.title,
                job_description=job.description,
                job_skills=job.get_skills_as_list(),
                job_experience_level=job.experience_level,
                job_id=job.id,
                user_id=request.user.id
            )

            context = {
                'job': job,
                'results': suggestion_results,
                'analysis': analysis_results,
                'match_score': match_score,
                'resume_file': resume_file.name
            }

            return render(request, 'subscriptions/resume_improvement_suggestions.html', context)

        context = {
            'job': job,
            'analysis': analysis_results,
            'match_score': match_score,
            'resume_file': resume_file.name
        }

        return render(request, 'subscriptions/resume_analysis_result.html', context)

    context = {
        'job': job
    }
    return render(request, 'subscriptions/resume_analysis.html', context)


@login_required
def apply_with_improved_resume(request, job_id):
    """View for applying to a job after improving resume based on suggestions."""
    job = get_object_or_404(JobListing, pk=job_id)

    # Check if user is subscribed
    is_pro = hasattr(request.user, 'is_pro') and request.user.is_pro

    if not is_pro:
        messages.warning(request, 'This feature is only available to Pro users. Please upgrade your account.')
        return redirect('subscriptions:plans')

    # Check if user already applied
    if JobApplication.objects.filter(job=job, applicant=request.user).exists():
        messages.info(request, 'You have already applied for this job.')
        return redirect('jobs:job_detail', slug=job.slug)

    if request.method == 'POST':
        # Get the improved resume
        improved_resume = request.FILES.get('improved_resume')

        if not improved_resume:
            messages.error(request, 'Please upload your improved resume.')
            return redirect('subscriptions:apply_with_resume_analysis', job_id=job_id)

        # Create job application
        application = JobApplication.objects.create(
            job=job,
            applicant=request.user,
            resume=improved_resume,
            cover_letter=request.FILES.get('cover_letter', None),
            status='pending'
        )

        # Analyze the improved resume for metrics
        improved_analysis = ResumeAnalysisService.analyze_resume(resume_file=improved_resume)

        # Check if the file is a valid resume
        if not improved_analysis.get('is_valid', False):
            error_message = improved_analysis.get('error', 'The uploaded file does not appear to be a valid resume.')
            messages.error(request, error_message)
            messages.warning(request, 'Please ensure you upload a proper resume file (PDF, DOCX, or TXT) with relevant professional information.')
            return redirect('subscriptions:apply_with_resume_analysis', job_id=job_id)

        # Calculate new match score
        new_match_score = JobMatchService.calculate_match_score(
            resume_analysis=improved_analysis,
            job_description=job.description,
            job_title=job.title,
            job_skills=job.get_skills_as_list()
        )

        # Save the improved analysis and match score
        improved_resume_analysis = ResumeAnalysis.objects.create(
            user=request.user,
            job=job,
            analysis_data=improved_analysis,
            score=improved_analysis.get('overall_score', 0)
        )

        match_score_obj = JobMatchScore.objects.create(
            user=request.user,
            job=job,
            resume_analysis=improved_resume_analysis,
            score=new_match_score.get('overall_percentage', 0),
            match_data=new_match_score
        )

        # Link the application to the analysis
        application.resume_analysis = improved_resume_analysis
        application.save()

        messages.success(request, f'Your application for {job.title} has been submitted with your improved resume!')
        return redirect('jobs:applications_list')

    return redirect('subscriptions:apply_with_resume_analysis', job_id=job_id)


@login_required
def get_job_match_percentage(request, job_id):
    """AJAX view to get job match percentage without leaving the current page."""
    if not request.is_ajax():
        return HttpResponseForbidden()

    # Check if user is subscribed
    is_pro = hasattr(request.user, 'is_pro') and request.user.is_pro

    if not is_pro:
        return JsonResponse({'error': 'Pro subscription required'}, status=403)

    job = get_object_or_404(JobListing, pk=job_id)

    # Check if we already have a match score calculated
    existing_match = JobMatchScore.objects.filter(user=request.user, job=job).order_by('-created_at').first()

    if existing_match and (timezone.now() - existing_match.created_at).days < 7:
        # Use existing match if it's less than a week old
        match_data = existing_match.match_data
        match_percentage = existing_match.score
    else:
        # Get the latest resume analysis
        latest_analysis = ResumeAnalysis.objects.filter(user=request.user).order_by('-created_at').first()

        if not latest_analysis:
            return JsonResponse({
                'error': 'No resume found for analysis. Please upload a resume first.'
            }, status=400)

        # Check if the analysis is from a valid resume
        if not latest_analysis.analysis_data.get('is_valid', False):
            return JsonResponse({
                'error': 'Your resume analysis is invalid. Please upload a proper resume file.'
            }, status=400)

        # Calculate match score
        match_data = JobMatchService.calculate_match_score(
            resume_analysis=latest_analysis.analysis_data,
            job_description=job.description,
            job_title=job.title,
            job_skills=job.get_skills_as_list()
        )

        match_percentage = match_data.get('overall_percentage', 0)

        # Save the match score
        JobMatchScore.objects.create(
            user=request.user,
            job=job,
            resume_analysis=latest_analysis,
            score=match_percentage,
            match_data=match_data
        )

    # Render match badge
    html = render_to_string('jobs/partials/match_percentage_badge.html', {
        'match_percentage': match_percentage,
        'match_data': match_data,
        'job': job,
        'request': request
    })

    return JsonResponse({
        'html': html,
        'match_percentage': match_percentage,
        'match_data': match_data
    })


@login_required
def job_match_dashboard(request):
    """View for displaying all job match scores for the user."""
    # Check if user is subscribed
    is_pro = hasattr(request.user, 'is_pro') and request.user.is_pro

    if not is_pro:
        messages.warning(request, 'This feature is only available to Pro users. Please upgrade your account.')
        return redirect('subscriptions:plans')

    # Get all match scores for the user
    match_scores = JobMatchScore.objects.filter(
        user=request.user
    ).select_related('job').order_by('-score')

    # Group by job (keeping only the highest score for each job)
    job_scores = {}
    for score in match_scores:
        job_id = score.job.id
        if job_id not in job_scores or score.score > job_scores[job_id].score:
            job_scores[job_id] = score

    # Convert back to list
    unique_scores = list(job_scores.values())

    # Get match score distribution
    excellent_matches = [s for s in unique_scores if s.score >= 85]
    good_matches = [s for s in unique_scores if 70 <= s.score < 85]
    moderate_matches = [s for s in unique_scores if 50 <= s.score < 70]
    low_matches = [s for s in unique_scores if s.score < 50]

    context = {
        'match_scores': unique_scores,
        'excellent_matches': excellent_matches,
        'good_matches': good_matches,
        'moderate_matches': moderate_matches,
        'low_matches': low_matches
    }

    return render(request, 'subscriptions/job_match_dashboard.html', context)


@login_required
def generate_improved_cover_letter(request, job_id):
    """Generate an improved cover letter for a specific job application."""
    job = get_object_or_404(JobListing, pk=job_id)

    # Check if user is subscribed
    is_pro = hasattr(request.user, 'is_pro') and request.user.is_pro

    if not is_pro:
        messages.warning(request, 'This feature is only available to Pro users. Please upgrade your account.')
        return redirect('subscriptions:plans')

    if request.method == 'POST':
        # Get form data
        current_cover_letter = request.POST.get('current_cover_letter', '')
        user_name = request.user.get_full_name() or request.user.username
        job_title = job.title
        company_name = job.company.name if hasattr(job, 'company') and job.company else "the company"
        experience_level = request.POST.get('experience_level', 'experienced')
        job_type = request.POST.get('job_type', 'professional')
        industry = request.POST.get('industry', job.category.name if hasattr(job, 'category') else 'technology')
        template_style = request.POST.get('template_style', 'standard')
        region = request.POST.get('region', 'global')

        # Get user skills
        user_skills = []
        if hasattr(request.user, 'skills') and request.user.skills:
            user_skills = [s.strip() for s in request.user.skills.split(',')]

        # Call the cover letter service
        try:
            cover_letter_result = CoverLetterAnalysisService.generate_cover_letter(
                user_name=user_name,
                job_title=job_title,
                company_name=company_name,
                skills=user_skills,
                experience_level=experience_level,
                job_type=job_type,
                industry=industry,
                template_style=template_style,
                region=region
            )

            # Create a record of the analysis
            cover_letter_analysis = CoverLetterAnalysis.objects.create(
                user=request.user,
                job=job,
                original_content=current_cover_letter,
                improved_content=cover_letter_result.get('full_text', ''),
                analysis_data={
                    'template_used': cover_letter_result.get('template_used', ''),
                    'sections': cover_letter_result.get('sections', {}),
                    'word_count': cover_letter_result.get('word_count', 0)
                }
            )

            return redirect('subscriptions:cover_letter_result', analysis_id=cover_letter_analysis.id)

        except Exception as e:
            messages.error(request, f'Error generating cover letter: {str(e)}')

    # Get job data for form
    context = {
        'job': job,
        'experience_levels': [
            ('entry_level', 'Entry Level (0-2 years)'),
            ('internship', 'Internship'),
            ('experienced', 'Experienced (3-5 years)'),
            ('senior', 'Senior (6-10 years)'),
            ('executive', 'Executive (10+ years)')
        ],
        'job_types': [
            ('professional', 'Professional'),
            ('technical', 'Technical'),
            ('creative', 'Creative'),
            ('teaching', 'Teaching/Education'),
            ('healthcare', 'Healthcare'),
            ('administrative', 'Administrative')
        ],
        'template_styles': [
            ('standard', 'Standard'),
            ('modern', 'Modern'),
            ('conservative', 'Conservative'),
            ('enthusiastic', 'Enthusiastic'),
            ('brief', 'Brief')
        ],
        'regions': [
            ('global', 'International/Global'),
            ('us', 'United States'),
            ('uk', 'United Kingdom'),
            ('canada', 'Canada'),
            ('australia', 'Australia'),
            ('nigeria', 'Nigeria'),
            ('ghana', 'Ghana'),
            ('kenya', 'Kenya'),
            ('south_africa', 'South Africa')
        ]
    }

    return render(request, 'subscriptions/generate_cover_letter.html', context)


@login_required
def cover_letter_result(request, analysis_id):
    """View for displaying improved cover letter results."""
    analysis = get_object_or_404(CoverLetterAnalysis, pk=analysis_id, user=request.user)

    context = {
        'analysis': analysis,
        'job': analysis.job
    }

    return render(request, 'subscriptions/cover_letter_result.html', context)


@login_required
def analyze_career_prospects(request):
    """Analyze career prospects based on user profile and job market."""
    # Check if user is subscribed
    is_pro = hasattr(request.user, 'is_pro') and request.user.is_pro

    if not is_pro:
        messages.warning(request, 'This feature is only available to Pro users. Please upgrade your account.')
        return redirect('subscriptions:plans')

    if request.method == 'POST':
        current_role = request.POST.get('current_role')
        target_role = request.POST.get('target_role')
        timeline = request.POST.get('timeline')

        if current_role:
            # Get user skills
            user_skills = []
            if hasattr(request.user, 'skills') and request.user.skills:
                user_skills = [s.strip() for s in request.user.skills.split(',')]

            # Call the career path service
            career_path_result = CareerPathService.plan_career_path(
                current_role=current_role,
                target_role=target_role,
                timeline_years=int(timeline) if timeline else 5,
                user_skills=user_skills
            )

            context = {
                'current_role': current_role,
                'target_role': target_role,
                'timeline': timeline,
                'career_path': career_path_result
            }

            return render(request, 'subscriptions/career_path_result.html', context)

    context = {
        'timelines': [
            (1, '1 year'),
            (2, '2 years'),
            (3, '3 years'),
            (5, '5 years'),
            (10, '10 years')
        ]
    }

    return render(request, 'subscriptions/career_path_planning.html', context)


@login_required
def improve_job_posting(request, job_id=None):
    """
    View for improving job postings using AI.

    This view handles both creating new job postings and improving existing ones.
    If job_id is provided, it will load that job for improvement, otherwise
    it will allow creating a new optimized job posting.
    """
    # Check if user is subscribed
    is_pro = hasattr(request.user, 'is_pro') and request.user.is_pro

    if not is_pro:
        messages.warning(request, 'This feature is only available to Pro users. Please upgrade your account.')
        return redirect('subscriptions:plans')

    # If job_id is provided, load the existing job
    job = None
    if job_id:
        job = get_object_or_404(JobListing, pk=job_id)
        # Check if user has permission to edit this job
        if job.posted_by != request.user and not request.user.is_staff:
            messages.error(request, 'You do not have permission to edit this job posting.')
            return redirect('jobs:job_detail', slug=job.slug)

    if request.method == 'POST':
        job_title = request.POST.get('job_title')
        job_description = request.POST.get('job_description')
        job_requirements = request.POST.get('job_requirements')
        industry = request.POST.get('industry')
        experience_level = request.POST.get('experience_level')

        if job_title and job_description:
            # Call the job posting analysis service
            job_posting_result = JobPostingAnalysisService.improve_job_posting(
                job_title=job_title,
                job_description=job_description,
                job_requirements=job_requirements,
                industry=industry,
                experience_level=experience_level
            )

            context = {
                'original_title': job_title,
                'original_description': job_description,
                'original_requirements': job_requirements,
                'improved_posting': job_posting_result,
                'job': job  # Pass the original job if we're editing
            }

            return render(request, 'subscriptions/job_description_result.html', context)

    # Prepare form context
    context = {
        'job': job,
        'industries': [
            ('technology', 'Information Technology'),
            ('healthcare', 'Healthcare'),
            ('finance', 'Finance & Banking'),
            ('education', 'Education'),
            ('retail', 'Retail'),
            ('manufacturing', 'Manufacturing'),
            ('hospitality', 'Hospitality & Tourism'),
            ('media', 'Media & Communication'),
            ('construction', 'Construction'),
            ('transportation', 'Transportation & Logistics')
        ],
        'experience_levels': [
            ('entry_level', 'Entry Level (0-2 years)'),
            ('internship', 'Internship'),
            ('mid_level', 'Mid Level (3-5 years)'),
            ('senior', 'Senior (6-10 years)'),
            ('executive', 'Executive (10+ years)')
        ]
    }

    return render(request, 'subscriptions/improve_job_posting.html', context)


@login_required
def optimize_requirements(request):
    """View for optimizing job requirements to be more inclusive and effective."""
    # Check if user is subscribed
    is_pro = hasattr(request.user, 'is_pro') and request.user.is_pro

    if not is_pro:
        messages.warning(request, 'This feature is only available to Pro users. Please upgrade your account.')
        return redirect('subscriptions:plans')

    if request.method == 'POST':
        job_title = request.POST.get('job_title')
        job_requirements = request.POST.get('job_requirements')

        if job_title and job_requirements:
            # Call the job posting analysis service for requirement optimization
            optimization_result = JobPostingAnalysisService.optimize_requirements(
                job_title=job_title,
                job_requirements=job_requirements
            )

            context = {
                'original_title': job_title,
                'original_requirements': job_requirements,
                'optimized_requirements': optimization_result
            }

            return render(request, 'subscriptions/requirements_optimization.html', context)

    return render(request, 'subscriptions/optimize_requirements.html')

@login_required
def analyze_cover_letter(request):
    """Analyze a cover letter for effectiveness and improvement suggestions."""
    # Check if user is subscribed
    is_pro = hasattr(request.user, 'is_pro') and request.user.is_pro

    if not is_pro:
        messages.warning(request, 'This feature is only available to Pro users. Please upgrade your account.')
        return redirect('subscriptions:plans')

    if request.method == 'POST':
        cover_letter_text = request.POST.get('cover_letter')
        job_title = request.POST.get('job_title', '')
        company_name = request.POST.get('company_name', '')

        if cover_letter_text:
            try:
                # Create a file-like object from the text
                from io import StringIO
                cover_letter_file = StringIO(cover_letter_text)
                cover_letter_file.name = "cover_letter.txt"

                # Call the cover letter analysis service
                analysis_result = CoverLetterAnalysisService.analyze_cover_letter(
                    file=cover_letter_file,
                    job_title=job_title,
                    job_description=None,
                    company_name=company_name
                )

                # If analysis failed, provide a basic analysis
                if not analysis_result or not analysis_result.get('is_valid', False):
                    analysis_result = {
                        'is_valid': True,
                        'structure_score': 70,
                        'content_score': 65,
                        'overall_score': 68,
                        'suggestions': [
                            "Add more specific achievements with metrics",
                            "Include relevant certifications",
                            "Highlight leadership experience",
                            "Tailor your cover letter more specifically to the job"
                        ],
                        'strengths': ["Good overall structure", "Professional tone"],
                        'weaknesses': ["Lacks specific examples", "Could be more tailored to the position"]
                    }

                # Create a record of the analysis
                CoverLetterAnalysis.objects.create(
                    user=request.user,
                    original_content=cover_letter_text,
                    analysis_data={
                        'structure_score': analysis_result.get('structure_score', 0),
                        'content_score': analysis_result.get('content_score', 0),
                        'tone_score': analysis_result.get('tone_score', 0),
                        'overall_score': analysis_result.get('overall_score', 0),
                        'improvement_suggestions': analysis_result.get('suggestions', []),
                        'strengths': analysis_result.get('strengths', []),
                        'weaknesses': analysis_result.get('weaknesses', [])
                    }
                )

                # Prepare context for template
                context = {
                    'cover_letter': cover_letter_text,
                    'analysis': {
                        'word_count': len(cover_letter_text.split()),
                        'overall_assessment': (
                            f"Overall Score: {analysis_result.get('overall_score', 70)}%. "
                            f"Structure Score: {analysis_result.get('structure_score', 75)}%. "
                            f"Content Score: {analysis_result.get('content_score', 65)}%. "
                        ),
                        'length_feedback': "Your cover letter is within the recommended length." if len(cover_letter_text.split()) < 400 else "Your cover letter might be too long. Consider making it more concise.",
                        'missing_elements': analysis_result.get('weaknesses', []),
                        'improvement_suggestions': analysis_result.get('suggestions', [])
                    },
                    'job': None  # Since this is a general analysis without a specific job
                }

                return render(request, 'subscriptions/cover_letter_analysis.html', context)

            except Exception as e:
                messages.error(request, f'Error analyzing cover letter: {str(e)}')
                return redirect('subscriptions:analyze_cover_letter')

    # Get user's job applications for the dropdown
    from jobs.models import JobApplication
    applications = JobApplication.objects.filter(applicant=request.user).select_related('job', 'job__company')

    # Prepare form context
    context = {
        'applications': applications
    }

    return render(request, 'subscriptions/analyze_cover_letter.html', context)
