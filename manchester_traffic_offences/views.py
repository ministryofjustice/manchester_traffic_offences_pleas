from django.conf import settings
from django import http
from django.shortcuts import render
from django.utils.http import is_safe_url
from django.utils.translation import check_for_language, to_locale, get_language
from django.views.generic import TemplateView
from django.views.decorators.cache import never_cache

from waffle.decorators import waffle_switch



class HomeView(TemplateView):
    """
    Home page view.
    """
    template_name = "start.html"

    def get(self, request, *args, **kwargs):

        return super(HomeView, self).get(request, *args, **kwargs)


def set_language(request):
    """
    View taken verbatim from django/views/i18n.py as we need the switcher
    to work with GET not POST.

    A couple of minor amends have been made to enable the view to work
    with a ?lang=cy querystring.
    """
    next = request.GET.get('next')
    if not is_safe_url(url=next, host=request.get_host()):
        next = request.META.get('HTTP_REFERER')
        if not is_safe_url(url=next, host=request.get_host()):
            next = '/'
    response = http.HttpResponseRedirect(next)

    lang_code = request.GET.get('lang')
    if lang_code and check_for_language(lang_code):
        if hasattr(request, 'session'):
            request.session['_language'] = lang_code
        else:
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)

    return response


def server_error(request):
    response = render(request, "500.html")
    response.status_code = 500
    return response

@never_cache
@waffle_switch("test_template")
def test_template(request):
    """
    View used for working on individual templates that need a lot
    of different contexts checking.
    For instance, this avoids having to go through the whole service to
    check layout and styling of the 'Complete' screen using different
    sets of context data.

    Requires a Waffle switch named 'test_template' and enabled.
    """
    template = "plea/complete.html"

    complete_context = {"plea_type": "mixed",
                        "case": {"plea_made_by": "Company representative",
                                 "urn": "51/aa/00000/00",
                                 "number_of_charges": 1},
                        "court": {"court_address": "Court address\nSome Place\nT357TER",
                                  "court_email": "email@court.com"}}

    email_context = {"plea_type": "mixed",
                     "plea_made_by": "Company representative",
                     "number_of_charges": 3,
                     "urn": "51/aa/00000/00",
                     "court_address": "Some address\nSomeplace\nT357ER",
                     "court_email": "court@test.com"}

    response = render(request, template, complete_context)
    return response
