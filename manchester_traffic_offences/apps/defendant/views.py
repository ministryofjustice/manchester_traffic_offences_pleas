from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from django.views.generic import FormView
from django.http import HttpResponseRedirect

from .forms import DefendantLoginForm

class DefendantLogin(FormView):
    form_class = DefendantLoginForm
    template_name = "defendant_login.html"
    success_url = reverse_lazy('plea_form')
    
    def form_valid(self, form):
        self.request.session['urn'] = form.cleaned_data['urn']
        return HttpResponseRedirect(self.get_success_url())