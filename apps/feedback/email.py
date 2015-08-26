from datetime import datetime

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

def send_feedback_email(email_data):
    email_context = {"used_call_centre": email_data["service"]["used_call_centre"],
                     "satisfaction": email_data["service"]["satisfaction"],
                     "comments": email_data["comments"]["comments"],
                     "email": email_data["comments"]["email"],
                     "date_sent": datetime.now(),
                     "referrer": email_data.get("feedback_redirect", "/"),
                     "user_agent": email_data.get("user_agent", "")}

    email = EmailMessage("Feedback from makeaplea.justice.gov.uk",
                         render_to_string("emails/feedback_summary.html",
                                          email_context),
                         settings.FEEDBACK_EMAIL_FROM,
                         settings.FEEDBACK_EMAIL_TO)
    
    email.content_subtype = "html"
    email.send(fail_silently=False)

    return True
