from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .models import UserSubscription
from .models_pro_features import InterviewPrep, SalaryInsights, CareerPath
from .enhanced_ai_services import EnhancedInterviewPrepService, EnhancedAIService
from jobs.models import JobListing


@login_required
def interview_preparation(request):
    """View for AI interview preparation feature."""
    # Check if user has an active pro subscription
    has_pro = False

    # First check if the user has an active subscription with interview prep feature
    has_specific_feature = UserSubscription.objects.filter(
        user=request.user,
        status='active',
        end_date__gt=timezone.now(),
        plan__interview_preparation=True
    ).exists()

    # If not, check if the user has any active pro subscription
    if not has_specific_feature:
        has_pro = UserSubscription.objects.filter(
            user=request.user,
            status='active',
            end_date__gt=timezone.now()
        ).exists()
    else:
        has_pro = True

    # Also check the user's is_pro flag as a fallback
    if not has_pro and hasattr(request.user, 'is_pro') and request.user.is_pro:
        has_pro = True

    if not has_pro:
        messages.error(request, _('This feature is only available for Pro users. Please upgrade your subscription.'))
        return redirect('subscriptions:plans')

    # Get user's job applications or saved jobs
    from jobs.models import JobApplication, SavedJob

    applied_jobs = JobApplication.objects.filter(
        applicant=request.user
    ).select_related('job').order_by('-applied_at')[:5]

    saved_jobs = SavedJob.objects.filter(
        user=request.user
    ).select_related('job').order_by('-created_at')[:5]

    # Get user's previous interview preps
    previous_preps = InterviewPrep.objects.filter(
        user=request.user
    ).select_related('job_listing').order_by('-created_at')[:5]

    context = {
        'applied_jobs': applied_jobs,
        'saved_jobs': saved_jobs,
        'previous_preps': previous_preps
    }

    return render(request, 'subscriptions/interview_preparation.html', context)


@login_required
def generate_interview_questions(request, job_id):
    """View for generating interview questions for a specific job."""
    # Check if user has an active pro subscription
    has_pro = False

    # First check if the user has an active subscription with interview prep feature
    has_specific_feature = UserSubscription.objects.filter(
        user=request.user,
        status='active',
        end_date__gt=timezone.now(),
        plan__interview_preparation=True
    ).exists()

    # If not, check if the user has any active pro subscription
    if not has_specific_feature:
        has_pro = UserSubscription.objects.filter(
            user=request.user,
            status='active',
            end_date__gt=timezone.now()
        ).exists()
    else:
        has_pro = True

    # Also check the user's is_pro flag as a fallback
    if not has_pro and hasattr(request.user, 'is_pro') and request.user.is_pro:
        has_pro = True

    if not has_pro:
        messages.error(request, _('This feature is only available for Pro users. Please upgrade your subscription.'))
        return redirect('subscriptions:plans')

    job = get_object_or_404(JobListing, id=job_id, status='published')

    # Check if we already have interview prep for this job
    interview_prep, created = InterviewPrep.objects.get_or_create(
        user=request.user,
        job_listing=job
    )

    # If this is a new interview prep or the user requested regeneration
    if created or request.GET.get('regenerate') == 'true':
        # Get user skills for better question generation
        user_skills = request.user.skills if hasattr(request.user, 'skills') else None

        # Generate interview questions using enhanced AI
        questions = EnhancedInterviewPrepService.generate_interview_questions(job, {'skills': user_skills})

        if questions:
            # Update the interview prep with the generated questions
            interview_prep.technical_questions = questions.get('technical_questions', [])
            interview_prep.behavioral_questions = questions.get('behavioral_questions', [])
            interview_prep.company_questions = questions.get('company_questions', [])
            interview_prep.save()

    context = {
        'job': job,
        'interview_prep': interview_prep
    }

    return render(request, 'subscriptions/interview_questions.html', context)


@login_required
def practice_interview_answer(request, prep_id, question_type, question_index):
    """View for practicing answers to interview questions."""
    # Check if user has an active pro subscription
    has_pro = False

    # First check if the user has an active subscription with interview prep feature
    has_specific_feature = UserSubscription.objects.filter(
        user=request.user,
        status='active',
        end_date__gt=timezone.now(),
        plan__interview_preparation=True
    ).exists()

    # If not, check if the user has any active pro subscription
    if not has_specific_feature:
        has_pro = UserSubscription.objects.filter(
            user=request.user,
            status='active',
            end_date__gt=timezone.now()
        ).exists()
    else:
        has_pro = True

    # Also check the user's is_pro flag as a fallback
    if not has_pro and hasattr(request.user, 'is_pro') and request.user.is_pro:
        has_pro = True

    if not has_pro:
        messages.error(request, _('This feature is only available for Pro users. Please upgrade your subscription.'))
        return redirect('subscriptions:plans')

    interview_prep = get_object_or_404(InterviewPrep, id=prep_id, user=request.user)

    # Get the question based on type and index
    question = None
    if question_type == 'technical' and len(interview_prep.technical_questions) > question_index:
        question = interview_prep.technical_questions[question_index]
    elif question_type == 'behavioral' and len(interview_prep.behavioral_questions) > question_index:
        question = interview_prep.behavioral_questions[question_index]
    elif question_type == 'company' and len(interview_prep.company_questions) > question_index:
        question = interview_prep.company_questions[question_index]

    if not question:
        messages.error(request, _('Question not found.'))
        return redirect('subscriptions:interview_questions', job_id=interview_prep.job_listing.id)

    # Get practice answers from the interview prep
    practice_answers = interview_prep.practice_answers
    answer_key = f"{question_type}_{question_index}"

    if request.method == 'POST':
        # Save the practice answer
        answer = request.POST.get('answer', '')

        if answer:
            # Generate feedback using enhanced AI
            user_skills = request.user.skills if hasattr(request.user, 'skills') else None

            # Prepare context for AI
            job_context = {
                'job_title': interview_prep.job_listing.title,
                'company_name': interview_prep.job_listing.company.name if hasattr(interview_prep.job_listing, 'company') else '',
                'industry': interview_prep.job_listing.category.name if hasattr(interview_prep.job_listing, 'category') else ''
            }

            # Get personalized feedback using enhanced AI
            feedback = EnhancedAIService.get_ai_response(
                f"Generate interview answer tips for: {question}",
                user_data={'skills': user_skills},
                context=job_context
            )

            # Update the practice answers and feedback
            practice_answers[answer_key] = answer

            # Update feedback
            feedback_dict = interview_prep.feedback
            feedback_dict[answer_key] = feedback

            # Save the updates
            interview_prep.practice_answers = practice_answers
            interview_prep.feedback = feedback_dict
            interview_prep.save()

            messages.success(request, _('Your answer has been saved and feedback generated.'))

            # Redirect to the feedback page
            return redirect('subscriptions:interview_feedback',
                           prep_id=prep_id,
                           question_type=question_type,
                           question_index=question_index)

    context = {
        'interview_prep': interview_prep,
        'question_type': question_type,
        'question_index': question_index,
        'question': question,
        'previous_answer': practice_answers.get(answer_key, '')
    }

    return render(request, 'subscriptions/practice_answer.html', context)


@login_required
def interview_feedback(request, prep_id, question_type, question_index):
    """View for displaying feedback on interview answers."""
    # Check if user has an active pro subscription
    has_pro = False

    # First check if the user has an active subscription with interview prep feature
    has_specific_feature = UserSubscription.objects.filter(
        user=request.user,
        status='active',
        end_date__gt=timezone.now(),
        plan__interview_preparation=True
    ).exists()

    # If not, check if the user has any active pro subscription
    if not has_specific_feature:
        has_pro = UserSubscription.objects.filter(
            user=request.user,
            status='active',
            end_date__gt=timezone.now()
        ).exists()
    else:
        has_pro = True

    # Also check the user's is_pro flag as a fallback
    if not has_pro and hasattr(request.user, 'is_pro') and request.user.is_pro:
        has_pro = True

    if not has_pro:
        messages.error(request, _('This feature is only available for Pro users. Please upgrade your subscription.'))
        return redirect('subscriptions:plans')

    interview_prep = get_object_or_404(InterviewPrep, id=prep_id, user=request.user)

    # Get the question based on type and index
    question = None
    if question_type == 'technical' and len(interview_prep.technical_questions) > question_index:
        question = interview_prep.technical_questions[question_index]
    elif question_type == 'behavioral' and len(interview_prep.behavioral_questions) > question_index:
        question = interview_prep.behavioral_questions[question_index]
    elif question_type == 'company' and len(interview_prep.company_questions) > question_index:
        question = interview_prep.company_questions[question_index]

    if not question:
        messages.error(request, _('Question not found.'))
        return redirect('subscriptions:interview_questions', job_id=interview_prep.job_listing.id)

    # Get practice answer and feedback
    answer_key = f"{question_type}_{question_index}"
    practice_answer = interview_prep.practice_answers.get(answer_key, '')
    feedback = interview_prep.feedback.get(answer_key, '')

    context = {
        'interview_prep': interview_prep,
        'question_type': question_type,
        'question_index': question_index,
        'question': question,
        'practice_answer': practice_answer,
        'feedback': feedback
    }

    return render(request, 'subscriptions/interview_feedback.html', context)


@login_required
def salary_insights(request):
    """View for salary insights feature."""
    # Check if user has an active pro subscription
    has_pro = False

    # First check if the user has an active subscription with salary insights feature
    has_specific_feature = UserSubscription.objects.filter(
        user=request.user,
        status='active',
        end_date__gt=timezone.now(),
        plan__salary_insights=True
    ).exists()

    # If not, check if the user has any active pro subscription
    if not has_specific_feature:
        has_pro = UserSubscription.objects.filter(
            user=request.user,
            status='active',
            end_date__gt=timezone.now()
        ).exists()
    else:
        has_pro = True

    # Also check the user's is_pro flag as a fallback
    if not has_pro and hasattr(request.user, 'is_pro') and request.user.is_pro:
        has_pro = True

    if not has_pro:
        messages.error(request, _('This feature is only available for Pro users. Please upgrade your subscription.'))
        return redirect('subscriptions:plans')

    # Get user's previous salary insights
    previous_insights = SalaryInsights.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]

    if request.method == 'POST':
        job_title = request.POST.get('job_title')
        location = request.POST.get('location')
        experience_level = request.POST.get('experience_level')

        if job_title and location and experience_level:
            # Get user skills for better insights
            user_skills = request.user.skills if hasattr(request.user, 'skills') else None

            # Get salary insights using enhanced AI
            # Prepare context for AI
            job_context = {
                'job_title': job_title,
                'industry': experience_level
            }

            # Get user experience for better insights
            user_experience = []
            if hasattr(request.user, 'jobseeker') and hasattr(request.user.jobseeker, 'experience'):
                user_experience = request.user.jobseeker.experience

            # Get personalized salary insights using enhanced AI
            insights_json = EnhancedAIService.get_ai_response(
                f"Provide salary insights for {job_title} in {location} with {experience_level} experience level",
                user_data={'skills': user_skills, 'experience': user_experience},
                context=job_context
            )

            # Parse the JSON response
            import json
            try:
                insights = json.loads(insights_json)
            except json.JSONDecodeError:
                insights = None

            if insights:
                # Create a new salary insights record
                salary_insight = SalaryInsights.objects.create(
                    user=request.user,
                    job_title=job_title,
                    location=location,
                    experience_level=experience_level,
                    salary_range_min=insights.get('salary_range', {}).get('min', 0),
                    salary_range_max=insights.get('salary_range', {}).get('max', 0),
                    median_salary=insights.get('median_salary', 0),
                    factors=insights.get('factors', []),
                    negotiation_tips=insights.get('negotiation_tips', []),
                    industry_trends=insights.get('industry_trends', '')
                )

                return redirect('subscriptions:salary_insights_result', insight_id=salary_insight.id)
            else:
                messages.error(request, _('Failed to generate salary insights. Please try again.'))

    context = {
        'previous_insights': previous_insights
    }

    return render(request, 'subscriptions/salary_insights.html', context)


@login_required
def salary_insights_result(request, insight_id):
    """View for displaying salary insights results."""
    # Check if user has an active pro subscription
    has_pro = False

    # First check if the user has an active subscription with salary insights feature
    has_specific_feature = UserSubscription.objects.filter(
        user=request.user,
        status='active',
        end_date__gt=timezone.now(),
        plan__salary_insights=True
    ).exists()

    # If not, check if the user has any active pro subscription
    if not has_specific_feature:
        has_pro = UserSubscription.objects.filter(
            user=request.user,
            status='active',
            end_date__gt=timezone.now()
        ).exists()
    else:
        has_pro = True

    # Also check the user's is_pro flag as a fallback
    if not has_pro and hasattr(request.user, 'is_pro') and request.user.is_pro:
        has_pro = True

    if not has_pro:
        messages.error(request, _('This feature is only available for Pro users. Please upgrade your subscription.'))
        return redirect('subscriptions:plans')

    insight = get_object_or_404(SalaryInsights, id=insight_id, user=request.user)

    # Handle experience level update
    if request.method == 'POST':
        new_experience_level = request.POST.get('experience_level')

        if new_experience_level and new_experience_level != insight.experience_level:
            # Get user skills for better insights
            user_skills = request.user.skills if hasattr(request.user, 'skills') else None

            # Get user experience for better insights
            user_experience = []
            if hasattr(request.user, 'jobseeker') and hasattr(request.user.jobseeker, 'experience'):
                user_experience = request.user.jobseeker.experience

            # Prepare context for AI
            job_context = {
                'job_title': insight.job_title,
                'industry': new_experience_level
            }

            # Get personalized salary insights using enhanced AI
            insights_json = EnhancedAIService.get_ai_response(
                f"Provide salary insights for {insight.job_title} in {insight.location} with {new_experience_level} experience level",
                user_data={'skills': user_skills, 'experience': user_experience},
                context=job_context
            )

            # Parse the JSON response
            import json
            try:
                insights_data = json.loads(insights_json)

                if insights_data:
                    # Create a new salary insights record
                    new_insight = SalaryInsights.objects.create(
                        user=request.user,
                        job_title=insight.job_title,
                        location=insight.location,
                        experience_level=new_experience_level,
                        salary_range_min=insights_data.get('salary_range', {}).get('min', 0),
                        salary_range_max=insights_data.get('salary_range', {}).get('max', 0),
                        median_salary=insights_data.get('median_salary', 0),
                        factors=insights_data.get('factors', []),
                        negotiation_tips=insights_data.get('negotiation_tips', []),
                        industry_trends=insights_data.get('industry_trends', '')
                    )

                    # Redirect to the new insight
                    return redirect('subscriptions:salary_insights_result', insight_id=new_insight.id)
                else:
                    messages.error(request, _('Failed to update salary insights. Please try again.'))
            except json.JSONDecodeError:
                messages.error(request, _('Failed to update salary insights. Please try again.'))

    context = {
        'insight': insight,
        'experience_levels': [
            {'value': 'entry', 'label': _('Entry Level (0-2 years)')},
            {'value': 'mid', 'label': _('Mid Level (3-5 years)')},
            {'value': 'senior', 'label': _('Senior Level (6-10 years)')},
            {'value': 'expert', 'label': _('Expert Level (10+ years)')}
        ]
    }

    return render(request, 'subscriptions/salary_insights_result.html', context)


@login_required
def career_path_planning(request):
    """View for career path planning feature."""
    # Check if user has an active pro subscription
    has_pro = False

    # First check if the user has an active subscription with career path planning feature
    has_specific_feature = UserSubscription.objects.filter(
        user=request.user,
        status='active',
        end_date__gt=timezone.now(),
        plan__career_path_planning=True
    ).exists()

    # If not, check if the user has any active pro subscription
    if not has_specific_feature:
        has_pro = UserSubscription.objects.filter(
            user=request.user,
            status='active',
            end_date__gt=timezone.now()
        ).exists()
    else:
        has_pro = True

    # Also check the user's is_pro flag as a fallback
    if not has_pro and hasattr(request.user, 'is_pro') and request.user.is_pro:
        has_pro = True

    if not has_pro:
        messages.error(request, _('This feature is only available for Pro users. Please upgrade your subscription.'))
        return redirect('subscriptions:plans')

    # Get user's previous career paths
    previous_paths = CareerPath.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]

    if request.method == 'POST':
        current_role = request.POST.get('current_role')
        target_role = request.POST.get('target_role')

        if current_role:
            # Generate career path using enhanced AI
            # Prepare context for AI
            job_context = {
                'job_title': current_role,
                'target_role': target_role
            }

            # Get user skills and experience for better career path planning
            user_skills = request.user.skills if hasattr(request.user, 'skills') else []
            user_experience = []
            if hasattr(request.user, 'jobseeker') and hasattr(request.user.jobseeker, 'experience'):
                user_experience = request.user.jobseeker.experience

            # Get personalized career path using enhanced AI
            path_data_json = EnhancedAIService.get_ai_response(
                f"Generate career path from {current_role} to {target_role}",
                user_data={'skills': user_skills, 'experience': user_experience},
                context=job_context
            )

            # Parse the JSON response
            import json
            try:
                path_data = json.loads(path_data_json)
            except json.JSONDecodeError:
                path_data = None

            if path_data:
                # Create a new career path record
                career_path = CareerPath.objects.create(
                    user=request.user,
                    current_role=current_role,
                    target_role=target_role,
                    path_steps=path_data.get('path_steps', []),
                    skills_to_acquire=path_data.get('skills_to_acquire', []),
                    certifications=path_data.get('certifications', []),
                    estimated_timeline=path_data.get('estimated_timeline', {})
                )

                return redirect('subscriptions:career_path_result', path_id=career_path.id)
            else:
                messages.error(request, _('Failed to generate career path. Please try again.'))

    context = {
        'previous_paths': previous_paths
    }

    return render(request, 'subscriptions/career_path_planning.html', context)
