from django.conf import settings

class TimeoutRedirectMiddleware:

    def process_response(self, request, response):
        if (request.session.get('case', {}).get('urn', False)):
            response["Refresh"] = str(getattr(settings, "SESSION_COOKIE_AGE", 3600)) + "; url=/session-timeout/"
        
        return response