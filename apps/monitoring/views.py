import json
from urlparse import urljoin

from django.conf import settings
from django.http import HttpResponse
from django.views.generic import View

from .check_methods import *


class HealthCheckView(View):

    def get(self, request):

        url_base = settings.ENV_BASE_URL

        status = {
            "api": {
                "description": "the Map API endpoint",
                "ok": check_url(urljoin("https://api."+url_base, "v0/stats/"))
            },
            "database": {
                "description": "The app's database",
                "ok": check_database()
            },
            "mandrill": {
                "description": "Transactional inbound/outbound emails via mandrill",
                "ok": check_mandrill()
            },
            "dashboard": {
                "description": "The MaP dashboard",
                "ok": check_url(urljoin("http://dashboard."+url_base, "makeaplea"))
            }
        }

        status["ok"] = all(item[1]["ok"] for item in status.items())

        return HttpResponse(json.dumps(status), content_type="application/json")
