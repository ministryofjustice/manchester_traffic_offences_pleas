import datetime as dt
from mock import patch

from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase, RequestFactory

from .models import UserRating, UserRatingAggregate
from .views import feedback_form


class FeedbackFormTestCase(TestCase):
    def setUp(self):

        mail.outbox = []

        self.request_factory = RequestFactory()

        self.test_form_data = {
            "feedback_question": "ra ra ra",
            "feedabck_email": "test@test.com",
            "feedback_satisfaction": 5
        }

    @patch("apps.feedback.views.messages")
    def test_redirect_to_next_url(self, messages):

        request = self.request_factory.post(reverse("feedback_form"),
                                            self.test_form_data,
                                            HTTP_USER_AGENT='Mozilla/5.0')

        response = feedback_form(request)

        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, reverse("home"))

    @patch("apps.feedback.views.messages")
    def test_email_is_sent(self, messages):

        request = self.request_factory.post(reverse("feedback_form"),
                                            self.test_form_data,
                                            HTTP_USER_AGENT='Mozilla/5.0')

        response = feedback_form(request)

        self.assertEquals(messages.add_message.call_count, 1)
        self.assertEquals(len(mail.outbox), 1)

    @patch("apps.feedback.views.messages")
    def test_user_satisfaction_is_recorded(self, messages):

        assert not UserRating.objects.all()

        request = self.request_factory.post(reverse("feedback_form"),
                                            self.test_form_data,
                                            HTTP_USER_AGENT='Mozilla/5.0')

        feedback_form(request)

        self.assertEquals(UserRating.objects.all().count(), 1)
        self.assertEquals(
            UserRating.objects.all()[0].rating,
            self.test_form_data["feedback_satisfaction"])

    @patch("apps.feedback.views.messages")
    def test_form_requires_validation(self, messages):

        request = self.request_factory.post(reverse("feedback_form"), {},
                                            HTTP_USER_AGENT='Mozilla/5.0')

        with self.assertTemplateUsed("feedback/feedback.html"):
            response = feedback_form(request)

            self.assertEquals(response.status_code, 200)


class UserRatingTestCase(TestCase):

    def test_weekly_aggregates(self):

        UserRating.objects.record(5)

        self.assertEquals(UserRating.objects.all().count(), 1)
        self.assertEquals(UserRatingAggregate.objects.all().count(), 1)

        rating = UserRating.objects.all()[0]
        aggregate = UserRatingAggregate.objects.all()[0]

        self.assertEquals(rating.rating, 5)
        self.assertEquals(aggregate.feedback_count, 1)
        self.assertEquals(aggregate.feedback_total, 5)
        self.assertEquals(aggregate.feedback_total, 5.0)

        UserRating.objects.record("1")

        self.assertEquals(UserRating.objects.all().count(), 2)
        self.assertEquals(UserRatingAggregate.objects.all().count(), 1)

        aggregate = UserRatingAggregate.objects.all()[0]

        self.assertEquals(aggregate.feedback_count, 2)
        self.assertEquals(aggregate.feedback_total, 6)
        self.assertEquals(aggregate.feedback_avg, 3.0)

    def test_submits_to_correct_week(self):

        UserRating.objects.record(5)
        UserRating.objects.record(1)

        rating_obj = UserRating.objects.create(rating=3)
        rating_obj.timestamp = dt.datetime.now() + dt.timedelta(7)
        rating_obj.save()

        UserRatingAggregate.objects.update_weekly_aggregate(rating_obj)

        self.assertEquals(UserRatingAggregate.objects.all().count(), 2)

        week1, week2 = UserRatingAggregate.objects.all()

        self.assertEquals(week1.feedback_count, 2)
        self.assertEquals(week1.feedback_total, 6)
        self.assertEquals(week1.feedback_avg, 3.0)

        self.assertEquals(week2.feedback_count, 1)
        self.assertEquals(week2.feedback_total, 3)
        self.assertEquals(week2.feedback_avg, 3.0)