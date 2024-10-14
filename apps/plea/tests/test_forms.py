import redgreenunittest as unittest

from ..forms import CompanyFinancesForm


class TestCompanyForm(unittest.TestCase):
    def test_trading_period_not_specified_other_fields_not_required(self):

        form = CompanyFinancesForm({})

        form.is_valid()

        self.assertIn('trading_period', form.errors)
        self.assertEqual(len(form.errors.items()), 1)

    def test_trading_period_specified_other_fields_required(self):
        form = CompanyFinancesForm({'trading_period': False})

        form.is_valid()

        self.assertEqual(len(form.errors.items()), 3)
        self.assertIn('number_of_employees', form.errors)
        self.assertIn('gross_turnover', form.errors)
        self.assertIn('net_turnover', form.errors)
