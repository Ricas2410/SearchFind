from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SubscriptionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'subscriptions'
    verbose_name = _('Subscriptions & Pro Features')
    
    def ready(self):
        import subscriptions.signals
