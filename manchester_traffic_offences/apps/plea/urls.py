from django.conf.urls import patterns, url

from . import views

plea = views.PleaForms.as_view(
    views.PLEA_FORMS,
    url_name='plea_form_step',
    done_step_name='complete_step'
)

urlpatterns = patterns('',
    url(r'^(?P<step>.+)/$', plea, name='plea_form_step'),
    url(r'^$', plea, name='plea_form'),
    url(r'^complete$', views.CompleteStep.as_view(), name='complete_step'),
)