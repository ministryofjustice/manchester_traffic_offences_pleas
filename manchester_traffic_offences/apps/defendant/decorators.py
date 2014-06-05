from django.contrib.auth.decorators import user_passes_test

from defendant.utils import is_valid_urn_format

def urn_required(function=None):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    
    actual_decorator = user_passes_test(
        lambda u: hasattr(u, 'urn') and is_valid_urn_format(u.urn),
        login_url="/"
    )
    if function:
        return actual_decorator(function)
    return actual_decorator