import time

from django.conf import settings
from django.utils import translation

def get_session_timeout(request):
    try:
        has_plea_data = request.session["plea_data"]["case"]
    except KeyError:
        has_plea_data = False

    try:
        has_feedback_data = request.session["feedback_data"]["service"]
    except KeyError:
        has_feedback_data = False

    if has_plea_data or has_feedback_data:
        timeout = int(time.time() + getattr(settings, "SESSION_COOKIE_AGE", 3600))
        return timeout

class TimeoutRedirectMiddleware:

    def process_request(self, request):
        session_timeout = get_session_timeout(request);
        if session_timeout:
            request.session_timeout = session_timeout

    def process_response(self, request, response):

        if hasattr(request, "session_timeout"):
            response["Refresh"] = str(getattr(settings, "SESSION_COOKIE_AGE", 3600)) + "; url=/session-timeout/"

        return response


class AdminLocaleURLMiddleware:

    def process_request(self, request):
        if request.path.startswith('/admin'):
            request.LANG = getattr(settings, 'ADMIN_LANGUAGE_CODE', settings.LANGUAGE_CODE)
            translation.activate(request.LANG)
            request.LANGUAGE_CODE = request.LANG
