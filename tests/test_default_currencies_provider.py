
from unittest import TestCase
from decimal import Decimal, ROUND_UP

from monon.currency import DefaultCurrenciesProvider


class DefaultCurrenciesProviderTestCase(TestCase):
    def setUp(self):
        self.provider = DefaultCurrenciesProvider()
        self.isocode = 'USD'

    def test_decimal_places(self):
        self.assertEqual(2, self.provider.get_decimal_places(self.isocode))

    def test_symbol(self):
        self.assertEqual('$', self.provider.get_symbol(self.isocode))

    def test_validate_currency(self):
        self.assertIsNone(self.provider.validate_currency(self.isocode))

    def test_format_positive_amount(self):
        amount = Decimal('43321.123')
        expected = '$43321.123'

        self.assertEqual(expected, self.provider.format_amount(self.isocode, amount))

    def test_format_negative_amount(self):
        amount = Decimal('-1234.123')
        expected = '-$1234.123'

        self.assertEqual(expected, self.provider.format_amount(self.isocode, amount))    

    def test_rounding(self):
        self.assertEqual(ROUND_UP, self.provider.get_rounding(self.isocode))
