import datetime

from django.conf import settings
from django import http
from django.shortcuts import render
from django.utils.http import is_safe_url
from django.utils.translation import check_for_language, get_language, activate
from django.views.generic import TemplateView

from waffle.decorators import waffle_switch


def start(request):
    if getattr(settings, "REDIRECT_START_PAGE", ""):
        return http.HttpResponseRedirect(settings.REDIRECT_START_PAGE)

    return render(request, "start.html")


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
    - notice: map|sjp
    - plea_made_by: defendant|company
    - plea_type: guilty|not_guilty|mixed
    - number_of_charges: (int)
    - language: en|cy
    """

    options = {"template": {"map": {"complete": "complete.html",
                                    "email_html": "emails/user_plea_confirmation.html",
                                    "email_txt": "emails/user_plea_confirmation.txt"},
                            "sjp": {"complete": "complete_sjp.html",
                                    "email_html": "emails/user_plea_confirmation_sjp.html",
                                    "email_txt": "emails/user_plea_confirmation_sjp.txt"}},
               "plea_made_by": {"defendant": "Defendant",
                                "company": "Company representative"}}

    # get query string params with some defaults
    template_name = request.GET.get("template", "complete")
    notice = request.GET.get("notice", "map")
    plea_made_by = request.GET.get("plea_made_by", "defendant")
    plea_type = request.GET.get("plea_type", "guilty")
    number_of_charges = request.GET.get("number_of_charges", 1)
    language = request.GET.get("language", "en")

    activate(language)

    template = options["template"][notice][template_name]

    context = {"plea_type": plea_type}

    case_data = {"plea_made_by": options["plea_made_by"][plea_made_by],
                 "urn": "51/aa/00000/00",
                 "number_of_charges": int(number_of_charges),
                 "contact_deadline": "2015-11-17"}

    court_data = {"court_name": "Test Magistrates' court",
                  "court_address": "Test Magistrates' court\nTest address\nSomewhere\nTE57ER",
                  "court_email": "court@example.org"}

    if template_name == "complete":
        context.update({"case": case_data, "court": court_data})
    else:
        context.update(case_data)
        context.update(court_data)

    content_type = "text/plain; charset=utf-8" if template_name == "email_txt" else "text/html"

    response = render(request, template, context, content_type=content_type)
    return response

@waffle_switch("test_template")
def test_email_attachment(request):
    template = "emails/attachments/plea_email.html"
    context = {"notice_type": {"sjp": False},
               "case": {"urn": "51/AA/0000000/15",
                        "date_of_hearing": "2015-10-20",
                        "contact_deadline": "2015-10-20",
                        "number_of_charges": 2,
                        "plea_made_by": "Company representative"},
               "your_details": {"updated_address": "Some place",
                                "first_name": "John",
                                "last_name": "Smith",
                                "contact_number": "07000000000",
                                "date_of_birth": "1970-01-01",
                                "email": "user@example.org"},
               "company_details": {"company_name": "Some company Plc",
                                   "updated_address": "Some place plc\nNew Street\nNew Town\nTE57ER",
                                   "first_name": "John",
                                   "last_name": "Smith",
                                   "position_in_company": "a director",
                                   "contact_number": "0800 SOMECOMPANY"},
               "plea": {"data": [{"guilty": "guilty", "guilty_extra": "Lorem ipsum dolor sit amet, consectetur adipisicing elit. Rerum, totam."},
                                 {"guilty": "not_guilty",
                                  "not_guilty_extra": "Lorem ipsum dolor sit amet, consectetur adipisicing elit. Veritatis pariatur ab, fugit.",
                                  "interpreter_needed": True,
                                  "interpreter_language": "French"}]},
               "your_finances": {},
               "company_finances": {"trading_period": True,
                                    "number_of_employees": "9000",
                                    "gross_turnover": "120000",
                                    "net_turnover": "9999"},
               "review": {"understand": True},
               "welsh_language": True}

    response = render(request, template, context)
    return response


@waffle_switch("test_template")
def test_resulting_email(request):
    """
    View to render a dummy version of the resulting email.

    Some parameters can be toggled in the query string:
    - template: html|txt
    - language: en|cy
    """

    templates = {"html": "emails/user_resulting.html",
                 "txt": "emails/user_resulting.txt"}

    context = {"name": "Frank Marsh",
               "urn": "51AA000000015",
               "fines": ["Fine - &amp;440",
                         "Victim surcharge - To pay victim surcharge of &amp;44",
                         "To pay costs of &amp;4"],
               "total": 569,
               "pay_by": datetime.date(2016, 2, 13),
               "endorsements": ["Driving record endorsed with 6 points."],
               "payment_details": {"division": "104",
                                   "account_number": "15083002"}}

    email_type = request.GET.get("template", "html")
    language = request.GET.get("language", "en")

    context["court"] = {
        "court_language": language,
        "court_name": "Manchester and Salford Magistrates' Court",
        "enforcement_email": "test@test.com",
        "enforcement_telephone": "0800 FINES TEAM"
    }

    template = templates[email_type]

    activate(language)

    content_type = "text/plain; charset=utf-8" if email_type == "txt" else "text/html"

    return render(request, template, context, content_type=content_type)
