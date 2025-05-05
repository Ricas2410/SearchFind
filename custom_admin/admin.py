from django.contrib import admin
from .models import AdminDashboardStat

@admin.register(AdminDashboardStat)
class AdminDashboardStatAdmin(admin.ModelAdmin):
    list_display = ('name', 'value', 'icon', 'color', 'order', 'is_active')
    list_filter = ('is_active', 'color')
    search_fields = ('name',)
    list_editable = ('value', 'icon', 'color', 'order', 'is_active')
