import datetime
import json
from mock import patch
import socket
import unittest

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder

from ..email import send_plea_email
from ..models import CourtEmailPlea, CourtEmailCount


class EmailAuditTests(unittest.TestCase):
    def setUp(self):
        self.context_data = {
            'case': {u'urn': u'00/AA/0000000/00',
                      u'date_of_hearing': datetime.date(2015, 1, 1),
                      u'time_of_hearing': datetime.time(9, 15),
                      u'number_of_charges': 2},
            'your_details': {u'name': u'maverick cobain'},
            'complete': {},
            'review': {u'csrfmiddlewaretoken': [u'z6Pz8e3M1rX2c31M0YpZtGnIv1V74ml7']},
            'send_error': {},
            'plea': {u'PleaForms': [{u'mitigations': u'fdsfdsff\r\nds\r\nf',
                                     u'guilty': u'guilty'},
                                    {u'mitigations': u'fdsfd\r\nsf\r\n\r\n',
                                     u'guilty': u'not_guilty'}], u'understand': True}}

    def test_email_audit_is_created(self):
        result = send_plea_email(self.context_data)
        data = json.dumps(self.context_data, cls=DjangoJSONEncoder)
        self.assertTrue(result)

        audit = CourtEmailPlea.objects.latest('date_sent')
        self.assertEqual(audit.status, "sent")
        self.assertEqual(audit.dict_sent, data)
        self.assertEqual(audit.subject, settings.PLEA_EMAIL_SUBJECT.format(**self.context_data))

    @patch("apps.plea.email.TemplateAttachmentEmail.send")
    def test_email_failure_audit(self, send):
        send.side_effect = socket.error("Email failed to send, socket error")
        result = send_plea_email(self.context_data)
        data = json.dumps(self.context_data, cls=DjangoJSONEncoder)
        self.assertFalse(result)

        audit = CourtEmailPlea.objects.latest('date_sent')
        self.assertEqual(audit.status, "network_error")
        self.assertEqual(audit.status_info, u"Email failed to send, socket error")
        self.assertEqual(audit.dict_sent, data)
        self.assertEqual(audit.subject, settings.PLEA_EMAIL_SUBJECT.format(**self.context_data))

    def test_management_data_is_stored(self):
        result = send_plea_email(self.context_data)

        count = CourtEmailCount.objects.latest('date_sent')
        self.assertEqual(count.total_pleas, 2)
        self.assertEqual(count.total_guilty, 1)
        self.assertEqual(count.total_not_guilty, 1)