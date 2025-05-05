from django.utils import timezone
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

def check_and_update_subscription_status(user, request=None):
    """
    Check and update a user's subscription status.
    
    Args:
        user: The user to check
        request: Optional request object for adding messages
        
    Returns:
        bool: True if the user has an active subscription, False otherwise
    """
    # First check if the user has the has_active_pro method
    if not hasattr(user, 'has_active_pro'):
        return False
        
    # Check if the user has an active subscription
    has_pro = user.has_active_pro()
    
    # If the user doesn't have an active subscription but is marked as pro,
    # update their status
    if not has_pro and user.is_pro:
        user.is_pro = False
        user.save(update_fields=['is_pro'])
        
        if request:
            messages.warning(
                request, 
                _('Your pro subscription has expired. Please renew to continue accessing pro features.')
            )
    
    # If the user has an active subscription but is not marked as pro,
    # update their status
    elif has_pro and not user.is_pro:
        user.update_pro_status()
        
        if request:
            messages.success(
                request, 
                _('Your pro subscription has been activated.')
            )
    
    return has_pro
