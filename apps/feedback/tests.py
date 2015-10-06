import datetime as dt
from mock import Mock, patch

from django.core import mail
from django.test import TestCase
from django.test.client import RequestFactory

from .models import UserRating, UserRatingAggregate
from .views import FeedbackForms, FeedbackViews

class FeedbackFormTestCase(TestCase):
    def setUp(self):

        mail.outbox = []

        self.request_context = {}

        self.empty_session_data = {}
        self.complete_session_data = {
            "feedback_redirect": "/court-finder/",
            "user_agent": "Mozilla/5.0",
            "service": {
                "complete": True,
                "used_call_centre": False,
                "service_satisfaction": 3,
                "call_centre_satisfaction": 5
            },
            "comments": {
                "complete": True,
                "comments": "ra ra ra",
                "email": "test@test.com"
            }
        }


    def get_request_mock(self, url, url_name="", url_kwargs=None):
        request_factory = RequestFactory()

        if not url_kwargs:
            url_kwargs = {}
        request = request_factory.get(url)
        request.resolver_match = Mock()
        request.resolver_match.url_name = url_name
        request.resolver_match.kwargs = url_kwargs

        request.META["HTTP_USER_AGENT"] = "Test User Agent"
        return request


    def test_service_stage_incomplete_data(self):
        form = FeedbackForms("service", "feedback_form_step", self.empty_session_data)
        form.load(self.request_context)
        form.save({}, self.request_context)

        self.assertEqual(len(form.current_stage.form.errors), 1)

    def test_service_stage_call_centre_used_incomplete_data(self):
        form = FeedbackForms("service", "feedback_form_step", self.empty_session_data)
        form.load(self.request_context)

        save_data = {
            "used_call_centre": True
        }
        form.save(save_data, self.request_context)

        response = form.render()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(form.current_stage.form.errors), 2)

    def test_service_stage_call_centre_not_used_incomplete_data(self):
        form = FeedbackForms("service", "feedback_form_step", self.empty_session_data)
        form.load(self.request_context)

        save_data = {
            "used_call_centre": False
        }
        form.save(save_data, self.request_context)

        response = form.render()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(form.current_stage.form.errors), 1)

    def test_comments_stage_shows_email(self):
        session_data = {
            "service": {
                "complete": True,
                "used_call_centre": False,
                "service_satisfaction": 3
            }
        }

        form = FeedbackForms("comments", "feedback_form_step", session_data)
        form.load(self.request_context)

        response = form.render()
        self.assertIn("Email address", response.content)

    def test_comments_stage_hides_email(self):
        session_data = {
            "service": {
                "complete": True,
                "used_call_centre": True,
                "call_centre_satisfaction": 5,
                "service_satisfaction": 3
            }
        }

        form = FeedbackForms("comments", "feedback_form_step", session_data)
        form.load(self.request_context)

        with self.assertTemplateUsed("comments.html"):
            response = form.render()
            self.assertNotIn("Email address", response.content)

    def test_email_is_sent(self):
        form = FeedbackForms("comments", "feedback_form_step", self.complete_session_data)
        form.save({}, self.request_context)

        form.render()

        self.assertEquals(len(mail.outbox), 1)

    @patch("apps.forms.stages.messages")
    def test_success_message_is_added(self, messages):
        form = FeedbackForms("comments", "feedback_form_step", self.complete_session_data)
        form.save({}, self.request_context)

        form.process_messages({})

        self.assertEquals(messages.add_message.call_count, 1)


    def test_redirect_is_set(self):
        fake_request = self.get_request_mock("/feedback/?next=terms")
        fake_request.session = {}
        fake_request.session["feedback_data"] = self.complete_session_data

        view = FeedbackViews()
        response = view.get(fake_request, stage="complete")

        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/terms-and-conditions-and-privacy-policy/")

    def test_user_rating_is_recorded(self):
        form = FeedbackForms("comments", "feedback_form_step", self.complete_session_data)
        form.save({}, self.request_context)

        self.assertEquals(UserRating.objects.all().count(), 1)


class UserRatingTestCase(TestCase):

    def test_weekly_aggregates(self):

        # Only Service rating
        UserRating.objects.record(5, "")

        self.assertEquals(UserRating.objects.all().count(), 1)
        self.assertEquals(UserRatingAggregate.objects.all().count(), 1)

        rating = UserRating.objects.all()[0]
        aggregate = UserRatingAggregate.objects.all()[0]

        self.assertEquals(rating.service_rating, 5)
        self.assertEquals(aggregate.rating_1, 0)
        self.assertEquals(aggregate.rating_2, 0)
        self.assertEquals(aggregate.rating_3, 0)
        self.assertEquals(aggregate.rating_4, 0)
        self.assertEquals(aggregate.rating_5, 1)
        self.assertEquals(aggregate.total, 1)

        # Inlude Call Centre rating
        UserRating.objects.record(1, 3)

        self.assertEquals(UserRating.objects.all().count(), 2)
        self.assertEquals(UserRatingAggregate.objects.all().count(), 2)

        aggregate = UserRatingAggregate.objects.all()[0]

        self.assertEquals(aggregate.rating_1, 1)
        self.assertEquals(aggregate.rating_2, 0)
        self.assertEquals(aggregate.rating_3, 0)
        self.assertEquals(aggregate.rating_4, 0)
        self.assertEquals(aggregate.rating_5, 1)
        self.assertEquals(aggregate.total, 2)

        call_centre_aggregate = UserRatingAggregate.objects.all()[1]

        self.assertEquals(call_centre_aggregate.rating_1, 0)
        self.assertEquals(call_centre_aggregate.rating_2, 0)
        self.assertEquals(call_centre_aggregate.rating_3, 1)
        self.assertEquals(call_centre_aggregate.rating_4, 0)
        self.assertEquals(call_centre_aggregate.rating_5, 0)
        self.assertEquals(call_centre_aggregate.total, 1)

    def test_submits_to_correct_week(self):

        UserRating.objects.record(5, "")
        UserRating.objects.record(1, "")

        rating_obj = UserRating.objects.create(service_rating=3)
        rating_obj.timestamp = dt.datetime.now() + dt.timedelta(7)
        rating_obj.save()

        UserRatingAggregate.objects.update_weekly_aggregate(rating_obj)

        self.assertEquals(UserRatingAggregate.objects.all().count(), 2)

        week1, week2 = UserRatingAggregate.objects.all()

        self.assertEquals(week1.rating_1, 1)
        self.assertEquals(week1.rating_2, 0)
        self.assertEquals(week1.rating_3, 0)
        self.assertEquals(week1.rating_4, 0)
        self.assertEquals(week1.rating_5, 1)
        self.assertEquals(week1.total, 2)

        self.assertEquals(week2.rating_1, 0)
        self.assertEquals(week2.rating_2, 0)
        self.assertEquals(week2.rating_3, 1)
        self.assertEquals(week2.rating_4, 0)
        self.assertEquals(week2.rating_5, 0)
        self.assertEquals(week2.total, 1)
