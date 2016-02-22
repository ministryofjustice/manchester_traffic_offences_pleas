from django.db import models


class Result(models.Model):
    case = models.ForeignKey("plea.Case", related_name="results", null=True, blank=True)
    urn = models.CharField(max_length=30, db_index=True)

    case_number = models.CharField(max_length=12, null=True, blank=True,
                                   help_text="as supplied by DX")
    ou_code = models.CharField(max_length=10, null=True, blank=True)
    date_of_hearing = models.DateField()
    account_number = models.CharField(max_length=100, null=True, blank=True)
    division = models.CharField(max_length=100, null=True, blank=True)
    instalment_amount = models.CharField(max_length=100, null=True, blank=True)
    lump_sum_amount = models.CharField(max_length=100, null=True, blank=True)
    pay_by_date = models.DateField(null=True, blank=True)
    payment_type = models.CharField(max_length=10, null=True, blank=True)

    sent = models.BooleanField(default=False)
    sent_on = models.DateTimeField(null=True, blank=True)


class ResultOffence(models.Model):
    result = models.ForeignKey(Result, related_name="result_offences")

    offence_code = models.CharField(max_length=10, null=True, blank=True)
    offence_seq_number = models.CharField(max_length=10, null=True, blank=True)


class ResultOffenceData(models.Model):
    result_offence = models.ForeignKey(ResultOffence, related_name="offence_data")

    result_code = models.CharField(max_length=10, null=True, blank=True)
    result_short_title = models.CharField(max_length=120)
    result_short_title_welsh = models.CharField(max_length=120, null=True, blank=True)
    result_wording = models.TextField(max_length=4000)
    result_wording_welsh = models.TextField(max_length=4000, null=True, blank=True)
    result_seq_number = models.CharField(max_length=10, null=True, blank=True)

