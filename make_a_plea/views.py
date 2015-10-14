from django.conf import settings
from django import http
from django.shortcuts import render
from django.utils.http import is_safe_url
from django.utils.translation import check_for_language, get_language
from django.views.generic import TemplateView

from waffle.decorators import waffle_switch


class TranslatedView(TemplateView):
    """
    Return a fully translated template when a language is set,
    or fallback to the default.
    """

    def get_template_names(self):
        templates_list = [self.template_name]
        lang_code = get_language()

        if lang_code:
            templates_list.insert(0, lang_code + "/" + self.template_name)

        return templates_list


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


@waffle_switch("enable_a11y_testing")
def set_a11y_testing(request):
    """
    Enable accessibility debugging using tota11y and/or
    Google Developers Accessibility Tools.

    The querystring works with 3 possible values for the mode param:
    ?mode=off - turn off accessibility debug
    ?mode=google - turn on Google Tools
    ?mode=tota11y - turn on tota11y
    """

    response = http.HttpResponseRedirect('/')

    a11y_code = request.GET.get('mode')

    if a11y_code == "google" or a11y_code == "tota11y":
        request.session["a11y_testing"] = a11y_code
    else:
        request.session.pop("a11y_testing", None)

    return response


@waffle_switch("test_template")
def test_template(request):
    """
    View used for working on individual templates that need a lot
    of different contexts checking.
    For instance, this avoids having to go through the whole service to
    check layout and styling of the 'Complete' screen using different
    sets of context data.

    Requires a Waffle switch named 'test_template' and enabled.

    Some parameters can be toggled in the query string:
    - template: complete|email_html|email_txt
    - plea_made_by: defendant|company
    - plea_type: guilty|not_guilty|mixed
    - number_of_charges: (int)
    """

    options = {"template": {"complete": "complete.html",
                            "email_html": "emails/user_plea_confirmation.html",
                            "email_txt": "emails/user_plea_confirmation.txt"},
               "plea_made_by": {"defendant": "Defendant",
                                "company": "Company representative"}}

    # get query string params with some defaults
    template_name = request.GET.get("template", "complete")
    plea_made_by = request.GET.get("plea_made_by", "defendant")
    plea_type = request.GET.get("plea_type", "guilty")
    number_of_charges = request.GET.get("number_of_charges", 1)

    template = options["template"][template_name]

    context = {"plea_type": plea_type}

    case_data = {"plea_made_by": options["plea_made_by"][plea_made_by],
                 "urn": "51/aa/00000/00",
                 "number_of_charges": int(number_of_charges),
                 "contact_deadline": "2015-11-17"}

    court_data = {"court_address": "Court address\nSome Place\nT357TER",
                  "court_email": "email@court.com"}

    content_type = "text/html"

    if template_name == "complete":
        context.update({"case": case_data, "court": court_data})
    else:
        context.update(case_data)
        context.update(court_data)

        if template_name == "email_txt":
            content_type = "text/plain"

    response = render(request, template, context, content_type=content_type)
    return response
