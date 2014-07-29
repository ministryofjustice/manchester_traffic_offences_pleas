from django.views.generic import TemplateView
from django.shortcuts import render
from django.template import RequestContext


class HomeView(TemplateView):
    """
    Home page view, clears the session so that the user's session data
    doesn't persist if they quit the process and start again. Otherwise
    the form wizard automatically takes them to the success (or network
    failure) page when they return to the form.
    """
    template_name = "start.html"

    def get(self, request, *args, **kwargs):
        request.session.clear()
        return super(HomeView, self).get(request, *args, **kwargs)


def server_error(request):
    response = render(request, "500.html")
    response.status_code = 500
    return response
