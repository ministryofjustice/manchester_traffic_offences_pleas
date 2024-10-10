from django.urls import reverse


def feedback(request):
    feedback_url = reverse("feedback_form")
    #using url names so that people can't just put arbitrary urls in the next field
    if request.resolver_match is not None:
        url_name = request.resolver_match.url_name
        url_kwargs = request.resolver_match.kwargs
    else:
        url_name = "home"
        url_kwargs = {}

    if url_kwargs:
        url_kwargs = "&".join(["{0}={1}".format(k, v) for k, v in url_kwargs.items()])
        full_url = "{0}?next={1}&{2}".format(feedback_url, url_name, url_kwargs)
    else:
        full_url = "{0}?next={1}".format(feedback_url, url_name)

    return {
        # Feedback URL (URL for feedback link in phase banner)
        'feedback_url': full_url
    }