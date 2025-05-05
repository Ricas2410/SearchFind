from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.utils.translation import gettext_lazy as _

class CustomUserAdmin(UserAdmin):
    """Admin configuration for the CustomUser model."""
    list_display = ('email', 'username', 'first_name', 'last_name', 'user_type', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_active')
    search_fields = ('email', 'username', 'first_name', 'last_name', 'company_name')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone_number', 'bio', 'profile_picture')}),
        (_('User type'), {'fields': ('user_type',)}),
        (_('Job seeker info'), {'fields': ('resume', 'skills')}),
        (_('Employer info'), {'fields': ('company_name', 'company_website', 'company_description', 'company_logo')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'user_type'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
