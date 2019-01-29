from ..plea.models import CaseTracker


def safe_div(x, y):
    if y == 0:
        return 0
    return float(x) / float(y)


def safe_percentage(x, y):
    return round(safe_div(x, y) * 100, 2)


class ChartMaker():
    bar_chart = []
    all_cases = None

    def __init__(self, start_date=None, end_date=None):
        self.bar_chart = []
        self.all_cases = CaseTracker.objects.all()
        if start_date:
            self.all_cases = self.all_cases.filter(last_update__gte=start_date)
        if end_date:
            self.all_cases = self.all_cases.filter(last_update__lte=end_date)
        self.calculate_counts()
        self.prepare_chart()

    def calculate_counts(self):
        self.case_count = self.all_cases.count()
        self.complete_count = self.all_cases.filter(complete=True).count()

    def get_case_count(self):
        return self.case_count

    def get_complete_count(self):
        return self.complete_count

    def get_completion_percentage(self):
        completion_rate = safe_div(self.complete_count,self.case_count)
        completion_percentage = round(completion_rate, 2) * 100
        return completion_percentage

    def get_bar_chart(self):
        return self.bar_chart

    def prepare_chart(self):
        pass
    
    
class DropoutsChart(ChartMaker):

    def prepare_chart(self):
        for current_stage_number, current_stage_name in enumerate(self.stage_names):
            current_stage_set = self.all_cases.filter(**{current_stage_name:True})

            current_stage_count = current_stage_set.count()
            dropout_set = current_stage_set

            for future_stage_name in self.future_options[current_stage_number]:
                dropout_set = dropout_set.filter(**{future_stage_name:False})

            dropout_count = dropout_set.count()
            dropout_percentage = safe_div(dropout_count, current_stage_count) * 100
            self.bar_chart.append([current_stage_name.encode('ascii','ignore'), int(dropout_percentage)])


class NumbersChart(ChartMaker):

    def prepare_chart(self):
        for stage_number, stage_name in enumerate(self.stage_names):

            current_stage_set = self.all_cases.filter(**{stage_name: True})

            if self.required_previous_stages[stage_number]:
                past_stage_name = self.required_previous_stages[stage_number]
                current_stage_set = current_stage_set.filter(**{past_stage_name: True})

            if self.prohibited_stages[stage_number]:
                prohibited_stage_name = self.prohibited_stages[stage_number]
                current_stage_set = current_stage_set.filter(**{prohibited_stage_name: False})

            current_stage_count = current_stage_set.count()

            self.bar_chart.append([stage_name.encode('ascii', 'ignore'), int(current_stage_count)])


class RequiredStagesChart(NumbersChart):
    stage_names = ["authentication", "details", "plea", "review"]
    required_previous_stages = [None, None, None, None]
    prohibited_stages = [None, None, None, None]


class FinancialSituationChart(NumbersChart):
    stage_names = ["your_status", "your_income", "review"]
    required_previous_stages = [None, None, "your_income"]
    prohibited_stages = [None, None, None]


class HardshipChart(NumbersChart):
    stage_names = ["hardship", "household_expenses", "other_expenses", "review"]
    required_previous_stages = [None, None, None, "other_expenses"]
    prohibited_stages = [None, None, None, None]


class AllStagesDropoutsChart(DropoutsChart):

    stage_names = ["authentication", "details", "plea", "your_status", "your_self_employment",
                   "your_out_of_work_benefits", "about_your_income", "your_benefits", "your_pension_credits",
                   "your_income", "hardship", "household_expenses", "other_expenses", "review"]
    future_options = [["details"], ["plea"], ["your_status", "review"],
                     ["your_self_employment", "your_out_of_work_benefits", "about_your_income"],
                     ["your_benefits", "your_income"], ["your_income"], ["your_pension_credits", "your_income"],
                     ["your_income"], ["your_income"], ["hardship", "review"], ["household_expenses"],
                     ["other_expenses"], ["review"], ["complete"]]


class IncomeSourcesDropoutsChart(DropoutsChart):

    # Not all stage options are included, since these lead to your_income eventually.
    stage_names = ["your_self_employment", "your_out_of_work_benefits", "about_your_income"]
    future_options = [["your_income"], ["your_income"], ["your_income"]]