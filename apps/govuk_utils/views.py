from django.views.generic import TemplateView

class StorageView(TemplateView):

    def _get_storage(self, request, session_key):
        if not request.session.get(session_key):
            request.session[session_key] = {}

        return request.session[session_key]

    def _clear_storage(self, request, session_key):
        del request.session[session_key]
