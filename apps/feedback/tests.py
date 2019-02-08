import datetime as dt
from mock import Mock

from django.core import mail
from django.test import TestCase
from django.test.client import RequestFactory

from .models import UserRating, UserRatingAggregate
from .views import FeedbackForms, FeedbackViews


class FeedbackFormTestCase(TestCase):
    def setUp(self):

        mail.outbox = []

        self.request_context = Mock()
        self.request_context.request = self.get_request_mock('/dummy')

        self.empty_session_data = {}
        self.complete_session_data = {
            "feedback_redirect": "/court-finder/",
            "user_agent": "Mozilla/5.0",
            "service": {
                "complete": True,
                "used_call_centre": False,
                "service_satisfaction": 3
            },
            "comments": {
                "complete": True,
                "comments": "ra ra ra",
                "email": "user@example.org"
            }
        }

    def get_request_mock(self, url="/", url_name="", url_kwargs=None):
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
        form = FeedbackForms(self.empty_session_data, "service")
        form.load(self.request_context)
        form.save({}, self.request_context)

        self.assertEqual(len(form.current_stage.form.errors), 1)

    def test_service_stage_call_centre_used_incomplete_data(self):
        form = FeedbackForms(self.empty_session_data, "service")
        form.load(self.request_context)

        save_data = {
            "used_call_centre": True
        }
        form.save(save_data, self.request_context)

        response = form.render(self.get_request_mock())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(form.current_stage.form.errors), 2)

    def test_service_stage_call_centre_not_used_incomplete_data(self):
        form = FeedbackForms(self.empty_session_data, "service")
        form.load(self.request_context)

        save_data = {
            "used_call_centre": False
        }
        form.save(save_data, self.request_context)

        response = form.render(self.get_request_mock())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(form.current_stage.form.errors), 1)

    def test_service_stage_redirects_to_comments(self):
        form = FeedbackForms(self.empty_session_data, "service")
        form.load(self.request_context)

        save_data = {
            "used_call_centre": False,
            "service_satisfaction": 3
        }
        form.save(save_data, self.request_context)

        response = form.render(self.get_request_mock())

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/feedback/comments/")

    def test_comments_stage_loads(self):
        session_data = {
            "service": {
                "complete": True,
                "used_call_centre": False,
                "service_satisfaction": 3
            }
        }

        form = FeedbackForms(session_data, "comments")
        form.load(self.request_context)

        response = form.render(self.get_request_mock())
        self.assertContains(response, 'id="id_comments"')
        self.assertContains(response, 'id="id_email"')

    def test_email_is_sent(self):
        form = FeedbackForms(self.complete_session_data, "comments")

        save_data = {
            "comments": "ra ra ra",
            "email": "user@example.org"
        }

        form.save(save_data, self.request_context)

        form.render(self.get_request_mock())

        self.assertEquals(len(mail.outbox), 1)

    def test_email_is_not_sent_if_user_does_not_provide_a_comment(self):

        self.complete_session_data["comments"]["comments"] = ""

        form = FeedbackForms(self.complete_session_data, "comments")
        form.save({}, self.request_context)

        form.render(self.get_request_mock())

        self.assertEquals(len(mail.outbox), 0)

    def test_comments_stage_redirects_to_complete(self):
        session_data = {
            "service": {
                "complete": True,
                "used_call_centre": False,
                "service_satisfaction": 3
            }
        }

        form = FeedbackForms(session_data, "comments")
        form.load(self.request_context)

        save_data = {
            "comments": "ra ra ra",
            "email": "user@example.org"
        }
        form.save(save_data, self.request_context)

        response = form.render(self.get_request_mock())

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/feedback/complete/")

    def test_complete_stage_resets_data(self):
        session_data = {
            "service": {
                "complete": True,
                "used_call_centre": False,
                "service_satisfaction": 3
            },
            "comments": {
                "complete": True
            }
        }

        fake_request = self.get_request_mock("/feedback/complete/")
        fake_request.session = {"feedback_data": session_data}

        view = FeedbackViews()
        view.get(fake_request, stage="complete")

        self.assertNotIn("service", view.storage)
        self.assertNotIn("comments", view.storage)

    def test_complete_stage_has_correct_finish_button_url(self):
        form = FeedbackForms(self.complete_session_data, "complete")
        form.load(self.request_context)

        response = form.render(self.get_request_mock())

        self.assertContains(response, 'href="/court-finder/"')

    def test_redirect_is_set(self):
        fake_request = self.get_request_mock("/feedback/?next=terms")

        view = FeedbackViews()
        view.get(fake_request, stage="service")

        self.assertEquals(view.storage["feedback_redirect"], "/terms-and-conditions-and-privacy-policy/")

    def test_redirect_is_set_to_home_for_complete_stage(self):
        fake_request = self.get_request_mock("/feedback/?next=plea_form_step&stage=complete")

        view = FeedbackViews()
        view.get(fake_request, stage="complete")

        self.assertEquals(view.storage["feedback_redirect"], "/")

    def test_complete_stage_redirects_to_start_if_no_session_feedback_data(self):
        form = FeedbackForms({}, "complete")
        response = form.load(self.request_context)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")

    def test_user_rating_is_recorded(self):
        form = FeedbackForms(self.complete_session_data, "comments")
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

        # Include Call Centre rating
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
