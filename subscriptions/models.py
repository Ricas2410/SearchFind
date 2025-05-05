from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class SubscriptionPlan(models.Model):
    """Model for subscription plans available to users."""
    PLAN_TYPE_CHOICES = (
        ('job_seeker', _('Job Seeker')),
        ('employer', _('Employer')),
    )

    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.PositiveIntegerField(default=30)

    # Job Seeker Features
    resume_builder = models.BooleanField(default=False, help_text=_('Access to AI resume builder'))
    resume_review = models.BooleanField(default=False, help_text=_('AI resume review and suggestions'))
    job_match_recommendations = models.BooleanField(default=False, help_text=_('AI job match recommendations'))
    company_recommendations = models.BooleanField(default=False, help_text=_('AI company match recommendations'))
    interview_preparation = models.BooleanField(default=False, help_text=_('AI interview preparation and practice'))
    salary_insights = models.BooleanField(default=False, help_text=_('Salary insights and negotiation tips'))
    career_path_planning = models.BooleanField(default=False, help_text=_('Career path planning and recommendations'))

    # Employer Features
    featured_jobs = models.BooleanField(default=False, help_text=_('Jobs appear as featured'))
    priority_listing = models.BooleanField(default=False, help_text=_('Jobs appear at top of search results'))
    candidate_matching = models.BooleanField(default=False, help_text=_('AI candidate matching'))
    advanced_analytics = models.BooleanField(default=False, help_text=_('Advanced job performance analytics'))
    unlimited_job_posts = models.BooleanField(default=False, help_text=_('Post unlimited job listings'))
    applicant_tracking = models.BooleanField(default=False, help_text=_('Advanced applicant tracking system'))

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Subscription Plan')
        verbose_name_plural = _('Subscription Plans')
        ordering = ['price']

    def __str__(self):
        return f"{self.name} ({self.get_plan_type_display()})"


class UserSubscription(models.Model):
    """Model for user subscriptions."""
    STATUS_CHOICES = (
        ('active', _('Active')),
        ('expired', _('Expired')),
        ('cancelled', _('Cancelled')),
        ('pending', _('Pending')),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, related_name='subscriptions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    # Payment details
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('User Subscription')
        verbose_name_plural = _('User Subscriptions')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.plan.name}"

    @property
    def is_active(self):
        """Check if subscription is active."""
        return (
            self.status == 'active' and
            self.start_date is not None and
            self.end_date is not None and
            self.start_date <= timezone.now() <= self.end_date
        )

    def activate(self, transaction_id=None):
        """Activate the subscription."""
        self.status = 'active'
        self.start_date = timezone.now()
        self.end_date = self.start_date + timezone.timedelta(days=self.plan.duration_days)
        if transaction_id:
            self.transaction_id = transaction_id
        self.save()

    def cancel(self):
        """Cancel the subscription."""
        self.status = 'cancelled'
        self.save()

        # Update user's pro status
        user = self.user
        if hasattr(user, 'is_pro'):
            user.is_pro = False
            user.save(update_fields=['is_pro'])

        # If using Paystack, cancel the subscription there too
        if self.payment_method == 'paystack' and self.transaction_id:
            try:
                # Get Paystack configuration
                paystack_config = PaystackConfig.get_config()

                # Cancel subscription with Paystack
                headers = {
                    'Authorization': f'Bearer {paystack_config.secret_key}',
                    'Content-Type': 'application/json'
                }

                url = f'https://api.paystack.co/subscription/{self.transaction_id}/disable'

                import requests
                response = requests.post(url, headers=headers)
                response_data = response.json()

                if not response.status_code == 200 or not response_data.get('status'):
                    # Log the error but continue with local cancellation
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error cancelling Paystack subscription: {response_data.get('message')}")
            except Exception as e:
                # Log the error but continue with local cancellation
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error cancelling Paystack subscription: {str(e)}")

    def renew(self, transaction_id=None):
        """Renew the subscription."""
        self.status = 'active'
        old_end_date = self.end_date

        # If subscription is expired, start from now
        if old_end_date < timezone.now():
            self.start_date = timezone.now()
        else:
            # Otherwise extend from the current end date
            self.start_date = old_end_date

        self.end_date = self.start_date + timezone.timedelta(days=self.plan.duration_days)

        if transaction_id:
            self.transaction_id = transaction_id
        self.save()


class Payment(models.Model):
    """Model for storing payment transaction information"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    subscription = models.ForeignKey(UserSubscription, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='NGN')
    reference = models.CharField(max_length=100, unique=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded')
    ], default='pending')
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    payment_gateway = models.CharField(max_length=50, default='paystack')
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payment {self.reference} - {self.user.email}"
    
    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')
        ordering = ['-created_at']


class PaystackConfig(models.Model):
    """Model for Paystack configuration settings."""
    public_key = models.CharField(max_length=255)
    secret_key = models.CharField(max_length=255)
    is_live = models.BooleanField(default=False, help_text=_('Use live mode instead of test mode'))
    webhook_secret = models.CharField(max_length=255, blank=True, null=True)

    # Currency settings - NGN is the only fully supported currency for most Paystack accounts
    # USD is only available for businesses with USD bank accounts
    CURRENCY_CHOICES = (
        ('NGN', _('Nigerian Naira (Default)')),
        ('GHS', _('Ghanaian Cedi')),
        ('ZAR', _('South African Rand')),
        ('USD', _('US Dollar (Requires USD account)')),
    )
    currency = models.CharField(max_length=3, default='NGN', choices=CURRENCY_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Paystack Configuration')
        verbose_name_plural = _('Paystack Configurations')

    def __str__(self):
        return f"Paystack Config ({'Live' if self.is_live else 'Test'} Mode)"

    @property
    def is_configured(self):
        """Check if Paystack is properly configured with valid API keys."""
        return (
            self.public_key and
            self.secret_key and
            self.public_key != 'pk_test_yourtestkeyhere' and
            self.secret_key != 'sk_test_yourtestkeyhere'
        )

    @property
    def default_currency(self):
        """Return the currency as the default currency."""
        # Always use GHS for test mode as that's what the merchant account supports
        if not self.is_live:
            return 'GHS'
        return self.currency

    @property
    def supported_currencies(self):
        """Return a list with the currency as the only supported currency."""
        # Always use GHS for test mode as that's what the merchant account supports
        if not self.is_live:
            return ['GHS']
        return [self.currency]

    @property
    def payment_currency(self):
        """Return the currency to use for payments."""
        # Always use GHS for test mode as that's what the merchant account supports
        if not self.is_live:
            return 'GHS'
        return self.currency

    @classmethod
    def get_config(cls):
        """Get the active Paystack configuration."""
        config, _ = cls.objects.get_or_create(
            id=1,
            defaults={
                'public_key': 'pk_test_3e58947994e1d69561d4f58adae8960f49fbdcae',
                'secret_key': 'sk_test_64854aaaedd7c3a36ccb741ddfd4b553e3f95901',
                'is_live': False,
                'currency': 'GHS'  # Ghanaian Cedi for this merchant account
            }
        )

        # Always update to the latest keys if they're still the default ones
        if config.public_key == 'pk_test_yourtestkeyhere' or not config.public_key:
            config.public_key = 'pk_test_3e58947994e1d69561d4f58adae8960f49fbdcae'
            config.secret_key = 'sk_test_64854aaaedd7c3a36ccb741ddfd4b553e3f95901'
            config.save()

        # Always ensure currency is GHS for Paystack compatibility with this merchant account
        if config.currency != 'GHS':
            config.currency = 'GHS'
            config.save()

        return config
