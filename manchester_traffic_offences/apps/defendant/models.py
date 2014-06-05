import datetime

from django.db import models

# from testing.models import Case

class Defendant(models.Model):
    urn = models.CharField(primary_key=True, max_length=100)
    case = models.ForeignKey("testing.Case")
    gender = models.CharField(blank=True, max_length=1)
    dob = models.DateField(default=datetime.datetime.today)
    phone = models.CharField(blank=True, max_length=100)
    email = models.EmailField()
    lawyer_name = models.TextField(blank=True)
    is_company = models.BooleanField(default=False)
    driver_number = models.CharField(blank=False, max_length=100)
    ni_number = models.CharField(blank=True, max_length=100)

