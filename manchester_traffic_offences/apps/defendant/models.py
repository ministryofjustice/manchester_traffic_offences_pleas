import datetime

from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import CharField

from .utils import is_valid_urn_format

class URNField(CharField):
    # TODO Move this to somewhere sane
    def validate(self, value, model_instance):
        super(URNField, self).validate(value, model_instance)
        if not is_valid_urn_format(value):
            raise ValidationError("URN isn't valid")

# Because of this bug?
# http://stackoverflow.com/questions/14386536/instantiating-django-model-raises-typeerror-isinstance-arg-2-must-be-a-class
from django.db.models.loading import cache as model_cache
if not model_cache.loaded:
    model_cache._populate()

class Defendant(models.Model):
    urn = URNField(primary_key=True, max_length=100)
    case = models.ForeignKey("testing.Case")
    gender = models.CharField(blank=True, max_length=1)
    dob = models.DateField(default=datetime.datetime.today)
    phone = models.CharField(blank=True, max_length=100)
    email = models.EmailField()
    lawyer_name = models.TextField(blank=True)
    is_company = models.BooleanField(default=False)
    driver_number = models.CharField(blank=False, max_length=100)
    ni_number = models.CharField(blank=True, max_length=100)

