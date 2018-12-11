from django.conf import settings
from django.conf.urls import include, url
from django.views.generic.base import RedirectView
import views

urlpatterns = [
    url(r'^index$', views.index, name='index'),
    url(r'^plea_report_entry$', views.PleaReportEntry.as_view(), name='plea_report_entry'),
    url(r'^stage_report_entry$', views.StageReportEntry.as_view(), name='stage_report_entry'),
    url(r'^rating_report_entry$', views.RatingReportEntry.as_view(), name='rating_report_entry'),
    url(r'^plea_report$', views.PleaReportView.as_view(), name='plea_report'),
    url(r'^stage_report$', views.StageReportView.as_view(), name='stage_report'),
    url(r'^stage_report/required_stages_report$', views.RequiredStagesNumbersView.as_view(),
        name='required_stages_report'),
    url(r'^stage_report/financial_situation_report$', views.FinancialSituationNumbersView.as_view(),
        name='financial_situation_report'),
    url(r'^stage_report/hardship_report$', views.HardshipStagesNumbersView.as_view(),
        name='hardship_report'),
    url(r'^stage_report/dropouts_all_stages_report$', views.AllStagesDropoutsView.as_view(),
        name='dropouts_all_stages_report'),
    url(r'^stage_report/income_sources_dropouts_report$', views.IncomeSourcesDropoutsView.as_view(),
        name='income_sources_dropouts_report'),
    url(r'^rating_report$', views.RatingReportView.as_view(), name='rating_report'),
    url(r'^$', views.index, name='index')
]