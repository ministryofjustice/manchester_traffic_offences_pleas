from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "start.html"

    def get(self, request, *args, **kwargs):
        request.session.clear()
        return super(HomeView, self).get(request, *args, **kwargs)
