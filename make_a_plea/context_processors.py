from django.conf import settings
from django.utils.translation import ugettext as _, get_language
from django.utils.safestring import mark_safe

def globals(request):
    return {
        # Application Title (Populates <title>)
        'app_title': _('Make a Plea: Traffic offences') + ' - GOV.UK',

        # Proposition Title (Populates proposition header)
        'proposition_title': _('Make a Plea: Traffic offences'),

        # Current Phase (Sets the current phase and the colour of phase tags). Presumed values: alpha, beta, live
        'phase': 'beta',

        # Product Type (Adds class to body based on service type). Presumed values: information, service
        'product_type': 'service',

        # Google Analytics ID (Tracking ID for the service)
        'google_analytics_id': getattr(settings, "GOOGLE_ANALYTICS_ID", None),

        # Version number
        'version': settings.VERSION,

        'html_lang': get_language,

        'skip_link_message': _('Skip to main content'),

        'logo_link_title': _('Go to the GOV.UK homepage'),

        'crown_copyright_message': mark_safe(_('&copy; Crown copyright'))
        }
