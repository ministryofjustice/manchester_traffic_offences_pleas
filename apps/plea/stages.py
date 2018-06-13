from collections import OrderedDict
from dateutil.relativedelta import relativedelta

from django.contrib import messages
from django.core.exceptions import MultipleObjectsReturned, NON_FIELD_ERRORS
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _

from apps.forms.stages import FormStage, IndexedStage
from make_a_plea.sentry_logging import log_user_data

from .email import send_plea_email, get_plea_type
from .forms import (URNEntryForm,
                    AuthForm,
                    NoticeTypeForm,
                    CaseForm,
                    SJPCaseForm,
                    YourDetailsForm,
                    CompanyDetailsForm,
                    PleaForm,
                    SJPPleaForm,
                    YourStatusForm,
                    YourEmploymentForm,
                    YourSelfEmploymentForm,
                    YourOutOfWorkBenefitsForm,
                    AboutYourIncomeForm,
                    YourBenefitsForm,
                    YourPensionCreditForm,
                    YourIncomeForm,
                    HardshipForm,
                    HouseholdExpensesForm,
                    OtherExpensesForm,
                    CompanyFinancesForm,
                    ConfirmationForm)

from .fields import ERROR_MESSAGES
from .models import Court, Case, Offence, DataValidation
from .standardisers import standardise_urn, format_for_region
import re

def get_case(urn):
    try:
        return Case.objects.get(urn__iexact=urn, sent=False)
    except Case.DoesNotExist:
        return None
    except MultipleObjectsReturned:
        # If we've got multiple un-sent records in the database it may be a case
        # with more than one defendant for the URN, if that is the case we shouldn't
        # be showing data to the user due to the potential for showing the wrong
        # data to the user so the safest thing to do is return None so it looks as if
        # there is no data for the case.

        cases = Case.objects.filter(
            urn__iexact=urn,
            extra_data__isnull=False,
            extra_data__Surname__isnull=False,
            extra_data__Forename1__isnull=False,
            extra_data__DOB__isnull=False,
        ).exclude(
            extra_data__Surname="",
            extra_data__Forename1="",
            extra_data__DOB="",
            sent=False,
        )
        return cases[0] if cases else None


def get_offences(case_data):
    urn = case_data.get("urn")
    # TODO: change this to grabbing by case OU or a FK at some point

    offences = []
    if urn:
        case = get_case(urn)

        ou_code = case.ou_code if case else None
        court = Court.objects.get_court(urn, ou_code=ou_code)

        # offence_seq_number is a char field so best to cast and order by
        # rather than just grabbing case.offences.all() and hoping it's
        # in the right order
        if court.display_case_data:
            offences = Offence.objects.filter(case=case).extra(
                select={"seq_number": "cast(coalesce(nullif(offence_seq_number,''),'0') as float)"}
            ).order_by("seq_number", "id")

    return offences


def calculate_weekly_amount(amount, period="Weekly"):
    amount = float(amount)

    if period == "Monthly":
        return (amount*12)/52
    elif period == "Fortnightly":
        return amount/2
    else:
        return amount


class SJPChoiceBase(FormStage):
    def set_next_no_data(self, court):
        if court.notice_types == "both":
            self.all_data["notice_type"] = {}
            self.set_next_step("notice_type")
        else:
            self.all_data["notice_type"]["sjp"] = (court.notice_types == "sjp")
            self.all_data["notice_type"]["complete"] = True
            self.all_data["notice_type"]["auto_set"] = True
            self.set_next_step("case")


class URNEntryStage(SJPChoiceBase):
    name = "enter_urn"
    storage_key = "case"
    template = "urn_entry.html"
    form_class = URNEntryForm
    dependencies = []
    analytics_name = "urn_stage"

    @staticmethod
    def _create_data_validation(urn, std_urn):
        dv = DataValidation()
        dv.urn_entered = urn
        dv.urn_standardised = std_urn
        dv.urn_formatted = format_for_region(std_urn)
        cases = Case.objects.filter(urn=std_urn, imported=True)
        dv.case_match_count = len(cases)

        if len(cases) > 0:
            dv.case_match = cases[0]

        dv.save()

    def _save_with_validation(self, court, clean_data):

        case = Case.objects.get_case_for_urn(clean_data["urn"])

        if not case or not case.can_auth():
            self.add_message(
                messages.ERROR,
                u"""<h1>{}</h1>
                   <p>{}</p>
                   <p>{}</p>""".format(
                        _("You can't make a plea online"),
                        _("To make your plea, you need to complete the "
                          "paper form sent to you by the police."),
                        _("You must return the form within the time stated.")))
            self.next_step = None
        elif not case.has_valid_doh():
            self.add_message(
                messages.ERROR,
                u"""<h1>{}</h1>
                   <p>{}</p>""".format(
                        _("Unfortunately you cannot use this service as "
                          "your time limit for making a plea has now expired."),
                        _("You will receive a notification of the outcome of the hearing in due course")))
            self.next_step = None
        else:
            self.set_next_step("your_case_continued")

    def _save_unvalidated(self, court, clean_data):
        case = get_case(clean_data["urn"])

        if case and court.display_case_data and case.can_auth():
            self.set_next_step("your_case_continued")
        else:
            try:
                del self.all_data["case"]["postcode"]
            except KeyError:
                pass

            self.set_next_no_data(court)

    def save(self, form_data, next_step=None):

        clean_data = super(URNEntryStage, self).save(form_data, next_step)
        if "urn" in clean_data:
            std_urn = standardise_urn(clean_data["urn"])
            court = Court.objects.get_by_urn(std_urn)
            if court:
                #If urn corresponds to a court with court_language set to cy then
                if court.supports_language("cy"):
                    self.all_data["welsh_court"] = True
                else:
                    self.all_data["welsh_court"] = False

            self._create_data_validation(clean_data["urn"], std_urn)

            clean_data["urn"] = std_urn

            if court.validate_urn:
                self._save_with_validation(court, clean_data)
            else:
                self._save_unvalidated(court, clean_data)

            self.all_data["urn_entry_failure_count"] = 0
        else:
            self.all_data["urn_entry_failure_count"] = self.all_data.get("urn_entry_failure_count", 0) + 1
        return clean_data



class AuthenticationStage(SJPChoiceBase):
    name = "your_case_continued"
    storage_key = "case"
    template = "authenticate.html"
    form_class = AuthForm
    dependencies = []
    analytics_name = "auth_stage"

    def load_forms(self, data=None, initial=False):

        initial_data = None

        court = Court.objects.get_by_urn(self.all_data["case"]["urn"])
        if court.validate_urn:
            case = Case.objects.get_case_for_urn(self.all_data["case"]["urn"])
        else:
            case = get_case(self.all_data["case"]["urn"])

        if not case:
            raise Exception("Cannot continue without a case")

        auth_field = case.auth_field()

        if initial:
            self.form = self.form_class(auth_field=auth_field, initial=initial_data, label_suffix="")
        else:
            self.form = self.form_class(data, auth_field=auth_field, label_suffix="")

    def save(self, form_data, next_step=None):
        clean_data = super(AuthenticationStage, self).save(form_data, next_step)

        if "number_of_charges" in clean_data:
            court = Court.objects.get_by_urn(self.all_data["case"]["urn"])

            if court.validate_urn:
                case = Case.objects.get_case_for_urn(self.all_data["case"]["urn"])
            else:
                case = get_case(self.all_data["case"]["urn"])

            if case.authenticate(clean_data["number_of_charges"],
                                 clean_data.get("postcode", None),
                                 clean_data.get("date_of_birth", None)):

                self.all_data.update({"dx": True})

                self.all_data["notice_type"]["sjp"] = (case.initiation_type == "J")
                self.all_data["notice_type"]["complete"] = True
                self.all_data["notice_type"]["auto_set"] = True

                self.all_data["case"]["number_of_charges"] = clean_data["number_of_charges"]
                if case.initiation_type == "J":
                    self.all_data["case"]["posting_date"] = case.date_of_hearing
                else:
                    self.all_data["case"]["date_of_hearing"] = case.date_of_hearing
                self.all_data["case"]["contact_deadline"] = case.date_of_hearing

                if case.extra_data.get("OrganisationName", None):
                    plea_made_by = "Company representative"
                    self.set_next_step("company_details", skip=["your_details",
                                                                "your_status",
                                                                "your_employment",
                                                                "your_self_employment",
                                                                "your_out_of_work_benefits",
                                                                "about_your_income",
                                                                "your_benefits",
                                                                "your_pension_credit",
                                                                "your_income",
                                                                "hardship",
                                                                "household_expenses",
                                                                "other_expenses"])
                else:
                    plea_made_by = "Defendant"
                    self.set_next_step("your_details", skip=["company_details",
                                                             "company_finances"])

                self.all_data["case"]["plea_made_by"] = plea_made_by
                self.all_data["case"]["complete"] = True
            else:
                if court.validate_urn:
                    self.next_step = None
                    self.add_message(
                        messages.ERROR,
                        u"""<h1>{}</h1>
                             <p>{}</p>
                             <p>{}</p>""".format(
                            _("Check the details you've entered"),
                            _("The information you've entered does not match our records."),
                            _("Check the paper form sent by the police then enter the details exactly as shown on it.")
                        ))
                else:
                    self.all_data.update({"dx": False})
                    self.set_next_no_data(court)

        return clean_data


class NoticeTypeStage(FormStage):
    name = "notice_type"
    template = "notice_type.html"
    form_class = NoticeTypeForm
    dependencies = []
    analytics_name = "notice_stage"

    def render(self, request, request_context):
        try:
            if self.all_data["notice_type"]["auto_set"]:
                return HttpResponseRedirect(self.all_urls["case"])
        except KeyError:
            pass

        return super(NoticeTypeStage, self).render(request, request_context)


class CaseStage(FormStage):
    name = "case"
    template = "case.html"
    form_class = CaseForm
    dependencies = ["notice_type"]
    analytics_name = "case_stage"

    def __init__(self, *args, **kwargs):
        super(CaseStage, self).__init__(*args, **kwargs)
        try:
            if self.all_data["notice_type"]["sjp"]:
                self.form_class = SJPCaseForm
        except KeyError:
            pass

    def save(self, form_data, next_step=None):
        clean_data = super(CaseStage, self).save(form_data, next_step)

        # Set the court contact deadline
        if "date_of_hearing" in clean_data:
            clean_data["contact_deadline"] = clean_data["date_of_hearing"]

        if "posting_date" in clean_data:
            clean_data["contact_deadline"] = clean_data["posting_date"] + relativedelta(days=+28)

        try:
            if len(self.all_data["plea"]["data"]) > clean_data["number_of_charges"]:
                del self.all_data["plea"]["data"][clean_data["number_of_charges"]:]
        except KeyError:
            pass

        if "complete" in clean_data:
            if clean_data.get("plea_made_by", "Defendant") == "Defendant":
                self.set_next_step("your_details", skip=["company_details",
                                                         "company_finances"])
            else:
                self.set_next_step("company_details", skip=["your_details",
                                                            "your_status",
                                                            "your_employment",
                                                            "your_self_employment",
                                                            "your_out_of_work_benefits",
                                                            "about_your_income",
                                                            "your_benefits",
                                                            "your_pension_credit",
                                                            "your_income",
                                                            "hardship",
                                                            "household_expenses",
                                                            "other_expenses"])

        return clean_data


class DetailsStage(FormStage):
    analytics_name = "details_stage"

    def save(self, form_data, next_step=None):

        contact_number= form_data.get("contact_number")
        if contact_number:
            contact_number = re.sub('\W', '', contact_number.replace('+', '00'))
        new_form_data = form_data.copy()
        new_form_data.update({"contact_number": contact_number})
        clean_data = super(DetailsStage,
                           self).save(new_form_data, next_step)
        return clean_data


class CompanyDetailsStage(DetailsStage):
    name = "company_details"
    template = "company_details.html"
    form_class = CompanyDetailsForm
    dependencies = ["notice_type", "case"]

    def save(self, form_data, next_step=None):
        clean_data = super(CompanyDetailsStage,
                           self).save(form_data, next_step)

        if Case.objects.filter(urn__iexact=self.all_data.get("case", {}).get("urn"),
                               sent=True).exists():
            self.form.errors[NON_FIELD_ERRORS] = [ERROR_MESSAGES["URN_ALREADY_USED"]]
            self.next_step = ""
            return {}
        else:
            if "complete" in clean_data:
                self.set_next_step("plea")

            return clean_data

    def render(self, request, request_context):
        if NON_FIELD_ERRORS in self.form.errors and ERROR_MESSAGES["URN_ALREADY_USED"] in self.form.errors[NON_FIELD_ERRORS]:
            self.context["urn_already_used"] = True

            try:
                self.context["court"] = Court.objects.get_by_urn(self.all_data.get("case", {}).get("urn"))
            except Court.DoesNotExist:
                pass

        return super(CompanyDetailsStage, self).render(request, request_context)


class YourDetailsStage(DetailsStage):
    name = "your_details"
    template = "your_details.html"
    form_class = YourDetailsForm
    dependencies = ["notice_type", "case"]

    def __init__(self, *args, **kwargs):
        super(YourDetailsStage, self).__init__(*args, **kwargs)

    def save(self, form_data, next_step=None):
        clean_data = super(
            YourDetailsStage,
            self).save(form_data, next_step)

        urn, first_name, last_name = (
            self.all_data.get("case", {}).get("urn"),
            clean_data.get("first_name"),
            clean_data.get("last_name"))

        if not Case.objects.can_use_urn(urn, first_name, last_name):
            self.form.errors[NON_FIELD_ERRORS] = [ERROR_MESSAGES["URN_ALREADY_USED"]]
            self.next_step = ""
            return {}
        else:
            if "complete" in clean_data:
                self.set_next_step("plea")
            return clean_data

    def render(self, request, request_context):
        if NON_FIELD_ERRORS in self.form.errors and ERROR_MESSAGES["URN_ALREADY_USED"] in self.form.errors[NON_FIELD_ERRORS]:
            self.context["urn_already_used"] = True

            try:
                self.context["court"] = Court.objects.get_by_urn(self.all_data.get("case", {}).get("urn"))
            except Court.DoesNotExist:
                pass

        return super(YourDetailsStage, self).render(request, request_context)

    def load_forms(self, data=None, initial=False):

        exclude_dob = "date_of_birth" in self.all_data["case"]

        if initial:
            self.form = self.form_class(
                initial=self.all_data[self.name],
                exclude_dob=exclude_dob,
                label_suffix="")
        else:
            self.form = self.form_class(
                data,
                exclude_dob=exclude_dob,
                label_suffix="")


class PleaStage(IndexedStage):
    name = "plea"
    template = "plea.html"
    form_class = PleaForm
    dependencies = ["notice_type", "case", "your_details", "company_details"]
    analytics_name = "plea_stage"

    def __init__(self, *args, **kwargs):
        super(PleaStage, self).__init__(*args, **kwargs)
        try:
            if self.all_data["notice_type"]["sjp"]:
                self.form_class = SJPPleaForm
        except KeyError:
            pass

    def load_forms(self, data=None, initial=False):

        initial_data = None

        # Only show offence data for DX cases
        if self.all_data.get("dx", False):
            offences = get_offences(self.all_data["case"])
        else:
            offences = False
        welsh_questions = self.all_data.get("welsh_court", False)
        if initial:
            data = self.all_data.get(self.name, {}).get("data", [])
            try:
                initial_data = data[self.index - 1]
            except IndexError:
                pass

            if self.form_class:
                self.form = self.form_class(initial=initial_data, welsh_questions=welsh_questions, label_suffix="")
        else:
            if self.form_class:
                self.form = self.form_class(data, welsh_questions=welsh_questions, label_suffix="")

        if offences:
            try:
                self.form.case_data = offences[self.index - 1]
            except IndexError:
                pass

        self.show_interpreter_question = True

        previous_charges = self.all_data["plea"].get("data", [])
        previous_charges = previous_charges[:self.index - 1]

        for charge in previous_charges:
            if charge.get("interpreter_needed", None) is not None or charge.get("sjp_interpreter_needed", None) is not None:
                self.show_interpreter_question = False

                del self.form.fields["interpreter_needed"]
                del self.form.fields["interpreter_language"]

                if self.all_data["notice_type"]["sjp"]:
                    del self.form.fields["sjp_interpreter_needed"]
                    del self.form.fields["sjp_interpreter_language"]

                break

    def save(self, form_data, next_step=None):
        clean_data = super(PleaStage, self).save(form_data, next_step)
        plea_count = self.all_data["case"]["number_of_charges"]
        stage_data = self.all_data[self.name]
        stage_data["none_guilty"] = True
        offences = get_offences(self.all_data["case"])

        if "data" not in stage_data:
            stage_data["data"] = []

        if len(stage_data["data"]) < self.index:
            stage_data["data"].append({})

        if clean_data.get("guilty") == "guilty_no_court" or clean_data.get("guilty") == "guilty_court":
            try:
                del clean_data["interpreter_needed"]
                del clean_data["interpreter_language"]
            except KeyError:
                pass

        if clean_data.get("guilty") == "not_guilty" or clean_data.get("guilty") == "guilty_no_court":
            try:
                del clean_data["sjp_interpreter_needed"]
                del clean_data["sjp_interpreter_language"]
            except KeyError:
                pass

        #Converts the new come to court options to the same format within the form data as before
        if clean_data.get("guilty") == "guilty_court":
            try:
                clean_data["come_to_court"] = True
            except KeyError:
                pass
        else:
            try:
                clean_data["come_to_court"] = False
            except KeyError:
                pass

        clean_data["show_interpreter_question"] = self.show_interpreter_question

        stage_data["data"][self.index - 1] = clean_data

        for plea in stage_data["data"]:
            if plea.get("guilty") == "guilty_court" or plea.get("guilty") == "guilty_no_court":
                stage_data["none_guilty"] = False
                break

        try:
            stage_data["data"][self.index - 1]["title"] = offences[self.index - 1].offence_short_title
        except IndexError:
            pass

        if "guilty" not in stage_data["data"][self.index - 1]:
            return clean_data

        if self.split_form is None or self.split_form == "split_form_last_step":
            if self.index < plea_count:
                self.next_step = reverse("plea_form_step", kwargs={"stage": self.name, "index": self.index+1})
            else:
                if self.all_data["case"].get("plea_made_by", "Defendant") == "Company representative":
                    if stage_data["none_guilty"]:
                        self.set_next_step("review", skip=["company_finances"])
                    else:
                        self.set_next_step("company_finances")
                else:
                    if stage_data["none_guilty"]:
                        self.set_next_step("review", skip=["your_status",
                                                           "your_employment",
                                                           "your_self_employment",
                                                           "your_out_of_work_benefits",
                                                           "about_your_income",
                                                           "your_benefits",
                                                           "your_pension_credit",
                                                           "your_income",
                                                           "hardship",
                                                           "household_expenses",
                                                           "other_expenses",
                                                           "company_finances"])
                    else:
                        self.set_next_step("your_status")

        return stage_data

    def render(self, request, request_context):
        self.context["index"] = self.index

        return super(PleaStage, self).render(request, request_context)


class CompanyFinancesStage(FormStage):
    name = "company_finances"
    template = "company_finances.html"
    form_class = CompanyFinancesForm
    dependencies = ["notice_type", "case", "company_details", "plea"]
    analytics_name = "company_finance_stage"


class IncomeBaseStage(FormStage):
    analytics_name = "income_stage"

    def add_income_source(self, label, period, amount):
        try:
            sources = self.all_data["your_income"]["sources"]
        except KeyError:
            sources = OrderedDict()

        if period == "Other":
            period = "Weekly"

        sources[self.name] = {"label": label,
                              "pay_period": period,
                              "pay_amount": amount}

        weekly_total = 0
        for source in sources:
            weekly_total += calculate_weekly_amount(sources[source]["pay_amount"],
                                                    sources[source]["pay_period"])

        self.all_data["your_income"]["sources"] = sources
        self.all_data["your_income"]["weekly_total"] = weekly_total

    def remove_income_sources(self, sources):
        for source in sources:
            try:
                del self.all_data["your_income"]["sources"][source]
            except KeyError:
                pass


class YourStatusStage(IncomeBaseStage):
    name = "your_status"
    template = "your_status.html"
    form_class = YourStatusForm
    dependencies = ["notice_type", "case", "your_details", "plea"]

    def save(self, form_data, next_step=None):
        clean_data = super(YourStatusStage, self).save(form_data, next_step)

        if "complete" in clean_data:
            if clean_data["you_are"] == "Employed":
                next_stage = "your_employment"
                skip_stages = ["your_self_employment",
                               "your_out_of_work_benefits",
                               "about_your_income",
                               "your_benefits",
                               "your_pension_credit"]

            if clean_data["you_are"] == "Employed and also receiving benefits":
                next_stage = "your_employment"
                skip_stages = ["your_self_employment",
                               "your_out_of_work_benefits",
                               "about_your_income",
                               "your_pension_credit"]

            if clean_data["you_are"] == "Self-employed":
                next_stage = "your_self_employment"
                skip_stages = ["your_employment",
                               "your_out_of_work_benefits",
                               "about_your_income",
                               "your_benefits",
                               "your_pension_credit"]

            if clean_data["you_are"] == "Self-employed and also receiving benefits":
                next_stage = "your_self_employment"
                skip_stages = ["your_employment",
                               "your_out_of_work_benefits",
                               "about_your_income",
                               "your_pension_credit"]

            if clean_data["you_are"] == "Receiving out of work benefits":
                next_stage = "your_out_of_work_benefits"
                skip_stages = ["your_employment",
                               "your_self_employment",
                               "about_your_income",
                               "your_benefits",
                               "your_pension_credit"]

            if clean_data["you_are"] == "Other":
                next_stage = "about_your_income"
                skip_stages = ["your_employment",
                               "your_self_employment",
                               "your_out_of_work_benefits",
                               "your_benefits"]

            self.remove_income_sources(skip_stages)
            self.set_next_step(next_stage, skip=skip_stages)

        return clean_data


class YourEmploymentStage(IncomeBaseStage):
    name = "your_employment"
    form_class = YourEmploymentForm
    template = "your_employment.html"
    dependencies = ["notice_type", "case", "your_details", "plea", "your_status"]

    def save(self, form_data, next_step=None):
        clean_data = super(YourEmploymentStage, self).save(form_data, next_step)

        if "complete" in clean_data:
            self.add_income_source("Employment", clean_data["pay_period"], clean_data["pay_amount"])

            if self.all_data["your_status"]["you_are"] == "Employed":
                self.set_next_step("your_income")
            else:
                self.set_next_step("your_benefits")

        return clean_data


class YourSelfEmploymentStage(IncomeBaseStage):
    name = "your_self_employment"
    form_class = YourSelfEmploymentForm
    template = "your_self_employment.html"
    dependencies = ["notice_type", "case", "your_details", "plea", "your_status"]

    def save(self, form_data, next_step=None):
        clean_data = super(YourSelfEmploymentStage, self).save(form_data, next_step)

        if "complete" in clean_data:
            self.add_income_source("Self-employment", clean_data["pay_period"], clean_data["pay_amount"])

            if self.all_data["your_status"]["you_are"] == "Self-employed":
                self.set_next_step("your_income")
            else:
                self.set_next_step("your_benefits")

        return clean_data


class YourOutOfWorkBenefitsStage(IncomeBaseStage):
    name = "your_out_of_work_benefits"
    form_class = YourOutOfWorkBenefitsForm
    template = "your_out_of_work_benefits.html"
    dependencies = ["notice_type", "case", "your_details", "plea", "your_status"]

    def save(self, form_data, next_step=None):
        clean_data = super(YourOutOfWorkBenefitsStage, self).save(form_data, next_step)

        if "complete" in clean_data:
            self.add_income_source("Benefits", clean_data["pay_period"], clean_data["pay_amount"])

            self.all_data["your_income"]["sources"]["your_out_of_work_benefits"].update({"benefit_type": clean_data["benefit_type"]})

            self.set_next_step("your_income")

        return clean_data


class AboutYourIncomeStage(IncomeBaseStage):
    name = "about_your_income"
    form_class = AboutYourIncomeForm
    template = "about_your_income.html"
    dependencies = ["notice_type", "case", "your_details", "plea", "your_status"]

    def save(self, form_data, next_step=None):
        clean_data = super(AboutYourIncomeStage, self).save(form_data, next_step)

        if "complete" in clean_data:
            if clean_data["pension_credit"] is False:
                self.remove_income_sources(["pension_credit"])
                self.set_next_step("your_income", skip=["your_pension_credit"])
            else:
                self.set_next_step("your_pension_credit")

            self.add_income_source(clean_data["income_source"], clean_data["pay_period"], clean_data["pay_amount"])

        return clean_data


class YourBenefitsStage(IncomeBaseStage):
    name = "your_benefits"
    form_class = YourBenefitsForm
    template = "your_benefits.html"
    dependencies = ["notice_type", "case", "your_details", "plea", "your_status",
                    "your_employment", "your_self_employment"]

    def save(self, form_data, next_step=None):
        clean_data = super(YourBenefitsStage, self).save(form_data, next_step)

        if "complete" in clean_data:
            self.add_income_source("Benefits", clean_data["pay_period"], clean_data["pay_amount"])

            self.all_data["your_income"]["sources"]["your_benefits"].update({"benefit_type": clean_data["benefit_type"]})

            self.set_next_step("your_income")

        return clean_data


class YourPensionCreditStage(IncomeBaseStage):
    name = "your_pension_credit"
    form_class = YourPensionCreditForm
    template = "your_pension_credit.html"
    dependencies = ["notice_type", "case", "your_details", "plea", "your_status",
                    "about_your_income"]

    def save(self, form_data, next_step=None):
        clean_data = super(YourPensionCreditStage, self).save(form_data, next_step)

        if "complete" in clean_data:
            self.add_income_source("Pension Credit", clean_data["pay_period"], clean_data["pay_amount"])
            self.set_next_step("your_income")

        return clean_data


class YourIncomeStage(IncomeBaseStage):
    name = "your_income"
    form_class = YourIncomeForm
    template = "your_income.html"
    dependencies = ["notice_type", "case", "your_details", "plea", "your_status",
                    "your_employment", "your_self_employment", "your_out_of_work_benefits", "about_your_income",
                    "your_benefits", "your_pension_credit"]

    def save(self, form_data, next_step=None):
        clean_data = super(YourIncomeStage, self).save(form_data, next_step)

        if "complete" in clean_data:
            if not clean_data["hardship"]:
                self.set_next_step("review", skip=["hardship", "household_expenses", "other_expenses"])

        return clean_data

    def render(self, request, request_context):
        sources = self.all_data["your_income"]["sources"]
        sources_order = ["your_employment",
                         "your_self_employment",
                         "your_out_of_work_benefits",
                         "about_your_income",
                         "your_benefits",
                         "your_pension_credit"]

        self.context["income_sources"] = OrderedDict([(k, sources[k]) for k in sources_order if k in sources])

        return super(YourIncomeStage, self).render(request, request_context)


class HardshipStage(FormStage):
    name = "hardship"
    template = "hardship.html"
    form_class = HardshipForm
    dependencies = ["notice_type",
                    "case",
                    "your_details",
                    "plea",
                    "your_status",
                    "your_employment",
                    "your_self_employment",
                    "your_out_of_work_benefits",
                    "about_your_income",
                    "your_benefits",
                    "your_pension_credit",
                    "your_income"]
    analytics_name = "hardship_stage"


class HouseholdExpensesStage(FormStage):
    name = "household_expenses"
    template = "household_expenses.html"
    form_class = HouseholdExpensesForm
    dependencies = ["notice_type",
                    "case",
                    "your_details",
                    "plea",
                    "your_status",
                    "your_employment",
                    "your_self_employment",
                    "your_out_of_work_benefits",
                    "about_your_income",
                    "your_benefits",
                    "your_pension_credit",
                    "your_income",
                    "hardship"]
    analytics_name = "household_expenses_stage"

    def save(self, form_data, next_step=None):

        household_expense_fields = ["household_accommodation",
                                    "household_utility_bills",
                                    "household_insurance",
                                    "household_council_tax"]

        clean_data = super(HouseholdExpensesStage, self).save(form_data, next_step)

        if "complete" in clean_data:
            total_household = sum(float(clean_data[field] or 0) for field in household_expense_fields)
            self.all_data["your_expenses"] = {"total_household_expenses": total_household}

        return clean_data


class OtherExpensesStage(FormStage):
    name = "other_expenses"
    template = "other_expenses.html"
    form_class = OtherExpensesForm
    dependencies = ["notice_type",
                    "case",
                    "your_details",
                    "plea",
                    "your_status",
                    "your_employment",
                    "your_self_employment",
                    "your_out_of_work_benefits",
                    "about_your_income",
                    "your_benefits",
                    "your_pension_credit",
                    "your_income",
                    "hardship",
                    "household_expenses"]
    analytics_name = "other_expenses_stage"

    def save(self, form_data, next_step=None):

        other_expense_fields = ["other_tv_subscription",
                                "other_travel_expenses",
                                "other_telephone",
                                "other_loan_repayments",
                                "other_court_payments",
                                "other_child_maintenance"]

        clean_data = super(OtherExpensesStage, self).save(form_data, next_step)

        if "complete" in clean_data:
            self.set_next_step("review")

            total_household = self.all_data["your_expenses"]["total_household_expenses"]

            if clean_data["other_not_listed"]:
                other_expense_fields.append("other_not_listed_amount")

            total_other = sum(float(clean_data[field] or 0) for field in other_expense_fields)
            total_expenses = total_household + total_other

            self.all_data["your_expenses"].update({"total_other_expenses": total_other,
                                                   "total_expenses": total_expenses})

        return clean_data


class ReviewStage(FormStage):
    name = "review"
    template = "review.html"
    form_class = ConfirmationForm
    dependencies = ["notice_type",
                    "case",
                    "your_details",
                    "company_details",
                    "plea",
                    "your_status",
                    "your_employment",
                    "your_self_employment",
                    "your_out_of_work_benefits",
                    "about_your_income",
                    "your_benefits",
                    "your_pension_credit",
                    "your_income",
                    "hardship",
                    "household_expenses",
                    "other_expenses",
                    "company_finances"]
    analytics_name = "review_stage"

    def save(self, form_data, next_step=None):
        clean_data = super(ReviewStage, self).save(form_data, next_step)

        log_user_data(self.all_data, {"stage": "review"})

        try:
            self.all_data["case"]["urn"]
        except KeyError:
            # session has timed out
            self.add_message(messages.ERROR, _("Your session has timed out"), extra_tags="session_timeout")

            self.set_next_step("case")
            return clean_data

        if clean_data.get("complete", False):
            email_data = {k: v for k, v in self.all_data.items()}
            email_data.update({"review": clean_data})

            email_result = send_plea_email(email_data)

            if email_result:
                self.set_next_step("complete")
            else:
                self.add_message(messages.ERROR, '<h1>{}</h1><p>{}</p>'.format(
                    _("Submission Error"),
                    _("There seems to have been a problem submitting your plea. Please try again.")))
                self.set_next_step("review")

        return clean_data


class CompleteStage(FormStage):
    name = "complete"
    template = "complete.html"
    form_class = None
    dependencies = ["notice_type",
                    "case",
                    "your_details",
                    "company_details",
                    "plea",
                    "your_status",
                    "your_employment",
                    "your_self_employment",
                    "your_out_of_work_benefits",
                    "about_your_income",
                    "your_benefits",
                    "your_pension_credit",
                    "your_income",
                    "hardship",
                    "household_expenses",
                    "other_expenses",
                    "company_finances",
                    "review"]
    analytics_name = "complete_stage"

    def __init__(self, *args, **kwargs):
        super(CompleteStage, self).__init__(*args, **kwargs)
        try:
            if self.all_data["notice_type"]["sjp"]:
                self.template = "complete_sjp.html"
        except KeyError:
            pass

    def render(self, request, request_context):

        self.context["plea_type"] = get_plea_type(self.all_data)
        try:
            self.context["court"] = Court.objects.get_court_dx(self.all_data["case"]["urn"])
        except Court.DoesNotExist:
            pass

        # Build an array of events to send to analytics now the journey is complete
        def is_entered(field):
            if len(self.all_data.get("your_details", {}).get(field, "")) > 0:
                return "Yes"
            else:
                return "No"

        self.context["analytics_events"] = [{"action": "Plea made by",
                                             "label": self.all_data.get("case").get("plea_made_by")}]

        if self.all_data["case"]["plea_made_by"] == "Defendant":
            self.context["analytics_events"].extend([{"action": "NI number",
                                                      "label": is_entered("ni_number")},
                                                     {"action": "Driving licence number",
                                                      "label": is_entered("driving_licence_number")}])

        return super(CompleteStage, self).render(request, request_context)
