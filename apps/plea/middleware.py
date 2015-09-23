from django.conf import settings

class TimeoutRedirectMiddleware:

    def process_response(self, request, response):
        try:
            if (request.session.get("plea_data", {}).get("case", {}).get("urn", False)):
                response["Refresh"] = str(getattr(settings, "SESSION_COOKIE_AGE", 3600)) + "; url=/session-timeout/"
        except AttributeError:
            pass

        return response
