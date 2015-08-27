import datetime as dt
from mock import Mock, patch

from django.contrib import messages
from django.core import mail
from django.core.urlresolvers import reverse
from django.template.context import RequestContext
from django.test import TestCase, RequestFactory


from .models import UserRating, UserRatingAggregate
from .views import FeedbackForms

class FeedbackFormTestCase(TestCase):
    def setUp(self):

        mail.outbox = []

        self.session_data = {}
        self.request_context = {}

        self.test_session_data = {
            "feedback_redirect": "/court-finder/",
            "user_agent": "Mozilla/5.0",
            "service": {
                "complete": True,
                "used_call_centre": False,
                "satisfaction": 3
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
        return request

    
    def test_service_stage_bad_data(self):
        form = FeedbackForms("service", "feedback_form_step", self.session_data)
        form.load(self.request_context)
        form.save({}, self.request_context)

        self.assertEqual(len(form.current_stage.form.errors), 1)

    def test_service_stage_incomplete_data(self):
        form = FeedbackForms("service", "feedback_form_step", self.session_data)
        form.load(self.request_context)

        save_data = {
            "used_call_centre": True
        }

        form.save(save_data, self.request_context)

        self.assertEqual(len(form.current_stage.form.errors), 1)

    def test_comments_stage_shows_email(self):
        session_data = {
            "service": {
                "complete": True,
                "used_call_centre": False,
                "satisfaction": 3
            }
        }

        form = FeedbackForms("comments", "feedback_form_step", session_data)
        form.load(self.request_context)

        with self.assertTemplateUsed("comments.html"):
            response = form.render()
            self.assertIn("Email address", response.content)

    def test_comments_stage_hides_email(self):
        session_data = {
            "service": {
                "complete": True,
                "used_call_centre": True,
                "satisfaction": 3
            }
        }

        form = FeedbackForms("comments", "feedback_form_step", session_data)
        form.load(self.request_context)

        with self.assertTemplateUsed("comments.html"):
            response = form.render()
            self.assertNotIn("Email address", response.content)
    
    
    def test_email_is_sent(self):
        form = FeedbackForms("comments", "feedback_form_step", self.test_session_data)
        form.save({"comments": "ra ra ra", "email": "test@test.com"}, self.request_context)

        response = form.render()

        self.assertEquals(len(mail.outbox), 1)


    # @patch("apps.govuk_utils.stages.messages")
    # def test_redirect_to_next_url(self, messages):
    #     form = FeedbackForms("comments", "feedback_form_step", self.test_session_data)
    #     form.save(self.test_session_data, self.request_context)
    #     form.process_messages({})

    #     response = form.render()

    #     self.assertEquals(messages.add_message.call_count, 1)
    #     self.assertEquals(response.status_code, 302)

    # @patch("apps.feedback.views.messages")
    # def test_email_is_sent(self, messages):

    #     request = self.request_factory.post(reverse("feedback_form"),
    #                                         self.test_form_data,
    #                                         HTTP_USER_AGENT='Mozilla/5.0')

    #     response = feedback_form(request)

    #     self.assertEquals(messages.add_message.call_count, 1)
    #     self.assertEquals(len(mail.outbox), 1)

    # @patch("apps.feedback.views.messages")
    # def test_user_satisfaction_is_recorded(self, messages):

    #     assert not UserRating.objects.all()

    #     request = self.request_factory.post(reverse("feedback_form"),
    #                                         self.test_form_data,
    #                                         HTTP_USER_AGENT='Mozilla/5.0')

    #     feedback_form(request)

    #     self.assertEquals(UserRating.objects.all().count(), 1)
    #     self.assertEquals(
    #         UserRating.objects.all()[0].rating,
    #         self.test_form_data["feedback_satisfaction"])


class UserRatingTestCase(TestCase):

    def test_weekly_aggregates(self):

        UserRating.objects.record(5)

        self.assertEquals(UserRating.objects.all().count(), 1)
        self.assertEquals(UserRatingAggregate.objects.all().count(), 1)

        rating = UserRating.objects.all()[0]
        aggregate = UserRatingAggregate.objects.all()[0]

        self.assertEquals(rating.rating, 5)
        self.assertEquals(aggregate.rating_1, 0)
        self.assertEquals(aggregate.rating_2, 0)
        self.assertEquals(aggregate.rating_3, 0)
        self.assertEquals(aggregate.rating_4, 0)
        self.assertEquals(aggregate.rating_5, 1)
        self.assertEquals(aggregate.total, 1)

        UserRating.objects.record(1)

        self.assertEquals(UserRating.objects.all().count(), 2)
        self.assertEquals(UserRatingAggregate.objects.all().count(), 1)

        aggregate = UserRatingAggregate.objects.all()[0]

        self.assertEquals(aggregate.rating_1, 1)
        self.assertEquals(aggregate.rating_2, 0)
        self.assertEquals(aggregate.rating_3, 0)
        self.assertEquals(aggregate.rating_4, 0)
        self.assertEquals(aggregate.rating_5, 1)
        self.assertEquals(aggregate.total, 2)

    def test_submits_to_correct_week(self):

        UserRating.objects.record(5)
        UserRating.objects.record(1)

        rating_obj = UserRating.objects.create(rating=3)
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
