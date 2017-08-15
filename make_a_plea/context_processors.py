from django.conf import settings
from django.utils.translation import ugettext as _, get_language
from django.utils.safestring import mark_safe


def globals(request):
    return {
        # Google Analytics ID (Tracking ID for the service)
        'google_analytics_id': settings.GOOGLE_ANALYTICS_ID,

        # Version number
        'version': settings.VERSION,

        'html_lang': get_language,

        'skip_link_message': _('Skip to main content'),

        'logo_link_title': _('Go to the GOV.UK homepage'),

        'crown_copyright_message': mark_safe(_('&copy; Crown copyright'))
        }
