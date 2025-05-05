from django.db import models
from django.utils.translation import gettext_lazy as _

class AdminDashboardStat(models.Model):
    """Model for storing dashboard statistics."""
    name = models.CharField(max_length=100)
    value = models.IntegerField(default=0)
    icon = models.CharField(max_length=50, help_text=_('Font Awesome icon class'))
    color = models.CharField(max_length=20, default='blue', help_text=_('Color theme for the stat card'))
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Dashboard Statistic')
        verbose_name_plural = _('Dashboard Statistics')
        ordering = ['order']

    def __str__(self):
        return self.name
