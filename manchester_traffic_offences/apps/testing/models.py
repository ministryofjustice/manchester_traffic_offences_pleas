import datetime

from django.db import models

class Plea(models.Model):
    urn = models.CharField(primary_key=True, max_length=100)
    charge = models.ForeignKey('Charge')
    defendant = models.ForeignKey('defendant.Defendant')
    plea = models.CharField(blank=True, max_length=100)
    mitigations = models.TextField(blank=True)
    

class Charge(models.Model):
    urn = models.CharField(primary_key=True, max_length=100)
    case = models.ForeignKey('Case')
    charge = models.TextField(blank=True)
    charge_type = models.CharField(blank=True, max_length=100)
    endorsable = models.BooleanField(default=False)

class Case(models.Model):
    urn = models.CharField(primary_key=True, max_length=100)
    logged_in = models.BooleanField(default=False)
    date = models.DateField(default=datetime.datetime.today)
    cost = models.DecimalField(max_digits=6, decimal_places=2)

class Witness(models.Model):
    plea = models.ForeignKey(Plea)
    name = models.CharField(blank=True, max_length=100)
    dob = models.DateField(default=datetime.datetime.today)
    address = models.TextField(blank=True)

class WitnessDates(models.Model):
    witness = models.ForeignKey(Witness)
    date = models.DateField(default=datetime.datetime.today)
    

class Prosecutor(models.Model):
    case = models.ForeignKey('Case')
    date = models.DateField(default=datetime.datetime.today)
    contact = models.TextField(blank=True)

class Hearing(models.Model):
    urn = models.CharField(primary_key=True, max_length=100)
    case = models.ForeignKey('Case')
    court = models.ForeignKey('Court')
    date = models.DateField(default=datetime.datetime.today)

class Court(models.Model):
    contact = models.TextField(blank=True)

class CourtUser(models.Model):
    court = models.ForeignKey(Court)


