import datetime
from glob import glob
import json
import os
from mock import patch
import socket
import unittest

from django.conf import settings
from django.test import TestCase

from ..email import send_plea_email
from ..models import Case
from ..encrypt import clear_user_data, gpg


class CaseCreationTests(TestCase):
    def setUp(self):

        self.context_data = {
            'case': {u'urn': u'00/aa/0000000/00',
                      u'date_of_hearing': datetime.date(2015, 1, 1),
                      u'time_of_hearing': datetime.time(9, 15),
                      u'number_of_charges': 2},
            'your_details': {
                u'name': u'maverick cobain',
                u"national_insurance_number": u"test ni number",
                u"driving_licence_number": u"test driving license number",
                u"registration_number": u"reg number",
                u"email": u"test@test.com"},
            'complete': {},
            'review': {u'csrfmiddlewaretoken': [u'z6Pz8e3M1rX2c31M0YpZtGnIv1V74ml7']},
            'send_error': {},
            'plea': {u'PleaForms': [{u'mitigations': u'fdsfdsff\r\nds\r\nf',
                                     u'guilty': u'guilty'},
                                    {u'mitigations': u'fdsfd\r\nsf\r\n\r\n',
                                     u'guilty': u'not_guilty'}], u'understand': True}}


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
        self.assertEqual(case.status, "sent")

        file_glob = '{}*.gpg'.format(self.context_data['case']['urn'].replace('/', '-').upper())

        path = os.path.join(settings.USER_DATA_DIRECTORY, file_glob)

        files = glob(path)

        if not files:
            self.fail('Encrypted user data file not found')
        elif len(files) > 1:
            self.fail('More than one data file found for URN')

        file = open(files[0], "r")
        decrypt = gpg.decrypt_file(file)

        self.assertEquals(decrypt.status, "decryption ok")

        data = json.loads(str(decrypt))

        self.assertEquals(self.context_data['case']['urn'], data['case']['urn'])

    @patch("apps.plea.email.TemplateAttachmentEmail.send")
    def test_email_failure_audit(self, send):
        send.side_effect = socket.error("Email failed to send, socket error")
        result = send_plea_email(self.context_data)

        self.assertFalse(result)

        case = Case.objects.all().order_by('-id')[0]
        self.assertEqual(case.status, "network_error")
        self.assertEqual(case.status_info, u"Email failed to send, socket error")
