from django.conf.urls import patterns, url
from django.http import HttpResponse, HttpRequest
from django.template import Template, RequestContext
from django.views.decorators.cache import never_cache

from defendant.decorators import urn_required

@never_cache
def public_page(request):
    t = Template("Public Page")
    c = RequestContext(request, {})
    return HttpResponse(t.render(c))

@never_cache
@urn_required
def private_page(request):
    t = Template("Private Page")
    c = RequestContext(request, {})
    return HttpResponse(t.render(c))

# special urls for defendant test cases
urlpatterns = patterns('',
    (r'^$', public_page),
    (r'^urn_required/$', urn_required(private_page)),
)
