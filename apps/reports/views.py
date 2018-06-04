# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.shortcuts import render
from ..plea.models import UsageStats
from django.db.models import Value, Sum
import datetime
# Create your views here.

@login_required(login_url=settings.ADMIN_LOGIN_URL)
def index(request):
    return render(request, 'reports.html', {'disable_language_switch': True})


@login_required(login_url=settings.ADMIN_LOGIN_URL)
def plea_report(request):

    # Ensure correct start and end dates for report
    if 'start_date' in request.GET:
        try:
            start_date = datetime.datetime.strptime(request.GET['start_date'], '%d/%m/%Y')
        except ValueError:
            start_date = None

    if 'end_date' in request.GET:
        try:
            end_date = datetime.datetime.strptime(request.GET['end_date'], '%d/%m/%Y')
        except ValueError:
            end_date = None
    change_date = datetime.date(day=21,month=5,year=2018)
    qs = UsageStats.objects.all()
    late_end_date = True  # Set to true if end date is after 21st May
    early_start_date = True
    if start_date:
        qs = qs.filter(start_date__gte=start_date)
        start_date = start_date.date()
        if start_date > change_date:
            early_start_date = False
    if end_date:
        qs = qs.filter(start_date__lt=end_date)
        end_date = end_date.date()
        if end_date < change_date:
            late_end_date = False
    pre_qs = qs.filter(start_date__lt=change_date)
    post_qs = qs.filter(start_date__gte=change_date)
    pre_totals = pre_qs.aggregate(Sum('online_submissions'),
                          Sum('online_guilty_pleas'),
                          Sum('online_not_guilty_pleas'))
    post_totals = post_qs.aggregate(Sum('online_submissions'),
                          Sum('online_guilty_pleas'),
                          Sum('online_not_guilty_pleas'),
                          Sum('online_guilty_attend_court_pleas'),
                          Sum('online_guilty_no_court_pleas'))
    totals = qs.aggregate(Sum('online_submissions'),
                          Sum('online_guilty_pleas'),
                          Sum('online_not_guilty_pleas'))
    all_online_submissions = totals["online_submissions__sum"] or 0
    all_online_guilty_pleas = totals["online_guilty_pleas__sum"] or 0
    all_online_not_guilty_pleas = totals["online_not_guilty_pleas__sum"] or 0
    all_online_pleas = all_online_guilty_pleas + all_online_not_guilty_pleas
    pre_online_submissions = pre_totals["online_submissions__sum"] or 0
    pre_online_guilty_pleas = pre_totals["online_guilty_pleas__sum"] or 0
    pre_online_not_guilty_pleas = pre_totals["online_not_guilty_pleas__sum"] or 0
    pre_online_pleas = pre_online_guilty_pleas + pre_online_not_guilty_pleas
    post_online_submissions = post_totals["online_submissions__sum"] or 0
    post_online_guilty_pleas = post_totals["online_guilty_pleas__sum"] or 0
    post_online_not_guilty_pleas = post_totals["online_not_guilty_pleas__sum"] or 0
    post_online_guilty_attend_court_pleas = post_totals["online_guilty_attend_court_pleas__sum"] or 0
    post_online_guilty_no_court_pleas = post_totals["online_guilty_no_court_pleas__sum"] or 0
    post_online_pleas = post_online_not_guilty_pleas + post_online_guilty_pleas
    return render(request, 'plea_report.html', {
        'start_date': start_date,
        'end_date': end_date,
        'late_end_date': late_end_date,
        'early_start_date': early_start_date,
        'all_online_submissions' : all_online_submissions,
        'all_online_guilty_pleas' : all_online_guilty_pleas,
        'all_online_not_guilty_pleas': all_online_not_guilty_pleas,
        'all_online_pleas': all_online_pleas,
        'pre_online_submissions': pre_online_submissions,
        'pre_online_guilty_pleas': pre_online_guilty_pleas,
        'pre_online_not_guilty_pleas': pre_online_not_guilty_pleas,
        'pre_online_pleas': pre_online_pleas,
        'post_online_submissions': post_online_submissions,
        'post_online_guilty_pleas': post_online_guilty_pleas,
        'post_online_not_guilty_pleas': post_online_not_guilty_pleas,
        'post_online_guilty_attend_court_pleas': post_online_guilty_attend_court_pleas,
        'post_online_guilty_no_court_pleas': post_online_guilty_no_court_pleas,
        'post_online_pleas': post_online_pleas,
        'disable_language_switch': True,
    })