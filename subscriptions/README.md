# SearchFind Pro Subscription System

This module implements a subscription system with AI-powered features for both job seekers and employers.

## Features

### For Job Seekers

- **AI Resume Builder**: Create tailored resumes that stand out to employers
- **Resume Analysis**: Get professional feedback on your resume with AI-powered suggestions
- **Job Match Scores**: See how well your profile matches job requirements with percentage scores
- **Company Match Recommendations**: Get recommended companies that match your skills and preferences

### For Employers

- **Featured Job Listings**: Make your job listings stand out in search results
- **Priority Placement**: Your jobs appear at the top of search results
- **AI Candidate Matching**: Find the best candidates for your job openings
- **Advanced Analytics**: Get detailed insights into your job performance

## Technical Implementation

### Models

- `SubscriptionPlan`: Defines available subscription plans and their features
- `UserSubscription`: Tracks user subscriptions, including status and expiry dates
- `PaystackConfig`: Stores configuration for Paystack payment integration
- `ResumeAnalysis`: Stores AI analysis of user resumes
- `JobMatchScore`: Tracks job match scores for users
- `CompanyMatchScore`: Tracks company match scores for users
- `ResumeBuilder`: Stores AI-generated resume content

### Payment Integration

The system uses Paystack for payment processing. The `PaystackConfig` model allows administrators to configure Paystack settings, including:

- Public and secret keys
- Webhook secret
- Currency settings
- Test/Live mode toggle

### Subscription Management

- Users can subscribe to plans based on their user type (job seeker or employer)
- Subscriptions have start and end dates
- Subscriptions can be cancelled or renewed
- Pro status is automatically updated based on subscription status

### AI Features Implementation

The AI features are implemented using a combination of:

1. **Skills Matching**: Compares user skills with job requirements
2. **Experience Matching**: Analyzes experience relevance to job requirements
3. **Education Matching**: Evaluates education background against job requirements
4. **Resume Analysis**: Provides feedback on resume content and structure
5. **Resume Generation**: Creates tailored resumes based on job requirements

## Setup Instructions

1. Add the app to `INSTALLED_APPS` in settings.py:
   ```python
   INSTALLED_APPS = [
       # ...
       'subscriptions.apps.SubscriptionsConfig',
   ]
   ```

2. Add the context processor to `TEMPLATES` in settings.py:
   ```python
   'context_processors': [
       # ...
       'subscriptions.context_processors.subscription_context',
   ]
   ```

3. Include the URLs in your main urls.py:
   ```python
   urlpatterns = [
       # ...
       path('subscriptions/', include('subscriptions.urls')),
   ]
   ```

4. Run migrations:
   ```
   python manage.py migrate
   ```

5. Create initial subscription plans:
   ```
   python manage.py create_subscription_plans
   ```

6. Configure Paystack settings in the admin panel

## Usage

### For Users

1. Users can view available subscription plans at `/subscriptions/plans/`
2. After subscribing, pro features are automatically enabled
3. Job seekers can access AI features from their dashboard
4. Employers can access pro features from their dashboard

### For Administrators

1. Manage subscription plans in the admin panel
2. Configure Paystack settings
3. View and manage user subscriptions
4. Monitor subscription metrics
