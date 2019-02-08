from celery.exceptions import Retry
import datetime
from glob import glob
import os
import json
from mock import patch
import socket

from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings

from ..email import send_plea_email
from ..models import Case, CourtEmailCount, Court
from ..encrypt import clear_user_data, gpg
from ..tasks import email_send_user


class CaseCreationTests(TestCase):
    def setUp(self):

        self.court = Court.objects.create(
            court_code="0000",
            region_code="06",
            court_name="test court",
            court_address="test address",
            court_telephone="0800 MAKEAPLEA",
            court_email="court@example.org",
            submission_email="court@example.org",
            plp_email="plp@example.org",
            enabled=True,
            test_mode=False)

        self.context_data = {
            'notice_type': {u'sjp': False},
            'case': {u'urn': u'06AA000000000',
                     u'date_of_hearing': datetime.date(2015, 1, 1),
                     u'contact_deadline': datetime.date(2015, 1, 1),
                     u'number_of_charges': 2,
                     u'plea_made_by': "Defendant"},
            'your_details': {
                u'first_name': u'maverick',
                u'middle_name': u'',
                u'last_name': u'cobain',
                u"national_insurance_number": u"test ni number",
                u"driving_licence_number": u"test driving license number",
                u"registration_number": u"reg number"},
            'complete': {},
            'review': {u'csrfmiddlewaretoken': [u'z6Pz8e3M1rX2c31M0YpZtGnIv1V74ml7'],
                       u'receive_email_updates': u'True',
                       u'email': u'user@example.org'},
            'send_error': {},
            'plea': {u'data': [{u'guilty_extra': u'fdsfdsff\r\nds\r\nf',
                                 u'guilty': u'guilty_no_court'},
                                {u'not_guilty_extra': u'fdsfd\r\nsf\r\n\r\n',
                                 u'guilty': u'not_guilty'}], u'understand': True}}

    @override_settings(STORE_USER_DATA=True)
    def test_user_data_is_persisted(self):
        """
        Verify that the data is written to the user data folder.
        """

        clear_user_data()
        result = send_plea_email(self.context_data)

        self.assertTrue(result)

        self.assertEqual(Case.objects.all().count(), 1)

        case = Case.objects.all()[0]
        self.assertEqual(Case.objects.all()[0].urn, self.context_data['case']['urn'].upper())
        self.assertTrue(case.sent)

        count_obj = CourtEmailCount.objects.all().order_by('-id')[0]
        self.assertEqual(case.sent, count_obj.sent)

        file_glob = '{}*.gpg'.format(self.context_data['case']['urn'].replace('/', '-').upper())

        path = os.path.join(settings.USER_DATA_DIRECTORY, file_glob)

        files = glob(path)

        if not files:
            self.fail('Encrypted user data file not found')
        elif len(files) > 1:
            self.fail('More than one data file found for URN')

        # file = open(files[0], "r")
        with open(files[0], 'rb') as file:
            b_data = file.read()
        str_data = b_data.decode('utf8')
        decrypt = gpg.decrypt(str_data)
        # decrypt = gpg.decrypt_file(file)

        self.assertEquals(decrypt.status, "decryption ok")

        data = json.loads(str(decrypt))

        self.assertEquals(self.context_data['case']['urn'], data['case']['urn'])

    @override_settings(STORE_USER_DATA=True)
    @patch("apps.plea.attachment.TemplateAttachmentEmail.send")
    def test_email_failure_audit(self, send):
        send.side_effect = OSError("Email failed to send, socket error")

        clear_user_data()

        try:
            send_plea_email(self.context_data)
        except Retry:
            pass
        except OSError:
            pass

        case = Case.objects.all().order_by('-id')[0]
        action = case.get_actions("Court email network error")
        self.assertTrue(len(action) > 0)
        self.assertEqual(action[0].status_info, u"<class 'OSError'>: Email failed to send, socket error")

        count_obj = CourtEmailCount.objects.all().order_by('-id')[0]
        self.assertEqual(case.sent, count_obj.sent)
        self.assertEqual(case.processed, count_obj.processed)

        # confirm we have a new file:

        file_glob = '{}*.gpg'.format(self.context_data['case']['urn'].replace('/', '-').upper())

        path = os.path.join(settings.USER_DATA_DIRECTORY, file_glob)

        files = glob(path)

        if len(files) != 1:
            self.fail('Should be one file in {}'.format(file_glob))

    @override_settings(STORE_USER_DATA=True)
    @patch("apps.plea.tasks.EmailMultiAlternatives.send")
    def test_user_email_failure(self, send):
        send.side_effect = iter([OSError("Email failed to send, socket error"), True])

        case = Case.objects.create(
            urn="00/AA/00000/00")

        try:
            email_send_user.delay(case.id, "ian.george@digital.justice.gov.uk",
                                  "User email test", "<strong>Test email body</strong>",
                                  "Test email body")

        except OSError:
            pass
        except Retry:
            pass

        case = Case.objects.all().order_by('-id')[0]

        correct_actions = [u'User email started',
                           u'User email network error',
                           u'User email started',
                           u'User email sent']

        for i, action in enumerate(case.actions.all()):
            if correct_actions[i] != action.status:
                self.fail("Wrong action got {} expected {}".format(
                    action.status, correct_actions[i]))

    @override_settings(STORE_USER_DATA=True)
    @patch("apps.plea.tasks.EmailMultiAlternatives.send")
    def test_user_email_not_requested(self, send):
        send.side_effect = iter([OSError("Email failed to send, socket error"), True])

        case = Case.objects.create(urn="00AA0000000")

        self.context_data.update({u"review": {"receive_email_updates": False,
                                              "email": ""}})

        try:
            send_plea_email(self.context_data)
        except OSError:
            pass
        except Retry:
            pass

        case = Case.objects.all().order_by('-id')[0]

        correct_action = u'No email entered, user email not sent'

        actions = list(case.actions.all())
        if correct_action != actions[-1].status:
                self.fail("Wrong action got {} expected {}".format(
                    actions[-1].status, correct_action))

    @override_settings(STORE_USER_DATA=False)
    def test_data_not_stored(self):

        clear_user_data()

        result = send_plea_email(self.context_data)

        self.assertTrue(result)

        path = os.path.join(settings.USER_DATA_DIRECTORY, '*.gpg')

        files = glob(path)

        if len(files) > 0:
            self.fail('User data directory is not empty')

    def test_completed_on_timestamp_is_set(self):

        assert Case.objects.all().count() == 0

        clear_user_data()

        send_plea_email(self.context_data)

        case = Case.objects.all()[0]

        self.assertIsNotNone(case.completed_on)
        self.assertIsInstance(case.completed_on, datetime.datetime)

