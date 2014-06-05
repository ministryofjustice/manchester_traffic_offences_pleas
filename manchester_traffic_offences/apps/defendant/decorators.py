from defendant.utils import is_valid_urn_format
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect


from functools import wraps

def urn_required(f):
    def wrap(request, *args, **kwargs):
        if 'urn' in request.session:
            if is_valid_urn_format(request.session['urn']):
                return f(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse_lazy('urn'))
    wrap.__doc__=f.__doc__
    wrap.__name__=f.__name__
    return wrap