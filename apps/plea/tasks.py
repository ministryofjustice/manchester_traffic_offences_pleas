from __future__ import absolute_import

from manchester_traffic_offences.celery import app


@app.task
def send_user_email(email_data, template_name):
    pass


@app.task
def send_court_email(email_data, template):
    pass


@app.task
def send_prosecutor_email(email_data, template):
    pass