from django.conf import settings
from django.utils.translation import get_language
from django.utils.safestring import mark_safe

def globals(request):
    return {
        # Application Title (Populates <title>)
        'app_title': 'Make a Plea: Traffic offences - GOV.UK',

        # Proposition Title (Populates proposition header)
        'proposition_title': 'Make a Plea: Traffic offences',

        # Current Phase (Sets the current phase and the colour of phase tags). Presumed values: alpha, beta, live
        'phase': 'alpha',

        # Product Type (Adds class to body based on service type). Presumed values: information, service
        'product_type': 'service',

        # Google Analytics ID (Tracking ID for the service)
        'ga_id': 'UA-53811587-1',

        # Version number
        'version': settings.VERSION,

        'html_lang': get_language,

        'logo_link_title': 'Go to the GOV.UK homepage',

        'crown_copyright_message': mark_safe('&copy; Crown copyright')
        }
