
import decimal
from unittest import TestCase, mock

from monon.currency import CurrenciesProvider, DefaultCurrenciesProvider, Currency
from monon.exceptions import InvalidCurrency


class CurrencyTestCase(TestCase):

    def setUp(self):
        self.mock_provider = mock.NonCallableMagicMock(spec=CurrenciesProvider)
        self.mock_isocode = mock.NonCallableMagicMock(spec=str)

    def test_new(self):
        currency = Currency('USD', self.mock_provider)

        self.assertIsInstance(currency, Currency)

    def test_init(self):
        currency = Currency('USD', self.mock_provider)

        self.assertEqual('USD', currency.isocode)
        self.assertEqual(self.mock_provider, currency._provider)

    def test_init_default_provider(self):
        with mock.patch.object(Currency, 'get_default_provider', return_value=self.mock_provider):
            currency = Currency('USD')
            self.assertEqual('USD', currency.isocode)
            self.assertEqual(self.mock_provider, currency._provider)

    def test_set_default_provider(self):
        class TestCurrency(Currency):
            pass

        TestCurrency.set_default_provider(self.mock_provider)
        currency = TestCurrency('USD')

        self.assertEqual(self.mock_provider, currency._provider)

    @mock.patch.object(Currency, 'clean_isocode', side_effect=InvalidCurrency)
    def test_init_invalid_currency(self, _):
        with self.assertRaises(InvalidCurrency):
            Currency(mock.Mock())

    @mock.patch.object(Currency, 'clean_isocode')
    def test_init_provider_invalid_currency(self, clean_isocode):
        self.mock_provider.validate_currency.side_effect = InvalidCurrency
        with self.assertRaises(InvalidCurrency):
            Currency(mock.Mock(spec=str), self.mock_provider)
        self.mock_provider.validate_currency.assert_called_once_with(clean_isocode.return_value)


class CurrencyCleanIsocode(TestCase):

    def test_clean_lowercase(self):
        self.assertEqual('USD', Currency.clean_isocode('usd'))

    def test_clean_mixeduppercase(self):
        self.assertEqual('MXN', Currency.clean_isocode('mXn'))

    def test_clean_lt_3_chars(self):
        with self.assertRaises(InvalidCurrency):
            Currency.clean_isocode('CL')

    def test_clean_gt_3_chars(self):
        with self.assertRaises(InvalidCurrency):
            Currency.clean_isocode('CLPF')


class CurrencyGetDefaultProvider(TestCase):

    def test_get_default_provider(self):
        self.assertIsInstance(Currency.get_default_provider(), DefaultCurrenciesProvider)

    def test_defined_default_provider(self):

        class CurrencyForTest(Currency):
            _default_provider = mock.NonCallableMagicMock(spec=CurrenciesProvider)

        self.assertEqual(CurrencyForTest._default_provider, CurrencyForTest.get_default_provider())


class CurrencyMethodTestCase(TestCase):

    def setUp(self):
        self.mock_provider = mock.NonCallableMagicMock(spec=CurrenciesProvider)
        self.currency = Currency('YEN', self.mock_provider)


class CurrencyFormatAmount(CurrencyMethodTestCase):

    def test_format_amount_from_provider(self):
        self.mock_provider.get_decimal_places.return_value = 2
        self.mock_provider.get_rounding.return_value = decimal.ROUND_UP
        amount = decimal.Decimal('4.20')

        result = self.currency.format_amount(amount)

        self.assertEqual(self.mock_provider.format_amount.return_value, result)

    def test_format_quantized_amount_from_provider(self):
        self.mock_provider.get_decimal_places.return_value = 2
        self.mock_provider.get_rounding.return_value = decimal.ROUND_UP
        amount = decimal.Decimal('4.191')

        self.currency.format_amount(amount)

        self.mock_provider.format_amount.assert_called_once_with(self.currency.isocode, decimal.Decimal('4.20'))

    def test_format_amount_as_is_from_provider(self):
        amount = mock.MagicMock(spec=decimal.Decimal)

        self.currency.format_amount_as_is(amount)

        self.mock_provider.format_amount.assert_called_once_with(self.currency.isocode, amount)


class CurrencyQuantizeAmount(CurrencyMethodTestCase):

    def assertQuantizeResult(self, expected, *args, **kwargs):
        self.assertEqual(
            expected,
            self.currency.quantize_amount(*args, **kwargs)
        )

    def test_quantize_down(self):
        self.mock_provider.get_decimal_places.return_value = 2
        self.mock_provider.get_rounding.return_value = decimal.ROUND_DOWN

        self.assertQuantizeResult(decimal.Decimal('4.20'), amount=decimal.Decimal('4.201'))

    def test_quantize_up(self):
        self.mock_provider.get_decimal_places.return_value = 2
        self.mock_provider.get_rounding.return_value = decimal.ROUND_UP

        self.assertQuantizeResult(decimal.Decimal('4.20'), amount=decimal.Decimal('4.191'))

    def test_quantize_zero(self):
        self.mock_provider.get_decimal_places.return_value = 0
        self.mock_provider.get_rounding.return_value = decimal.ROUND_UP

        self.assertQuantizeResult(decimal.Decimal('5'), amount=decimal.Decimal('4.191'))

    def test_quantize_force_rounding(self):
        self.mock_provider.get_decimal_places.return_value = 0
        self.mock_provider.get_rounding.return_value = decimal.ROUND_DOWN

        self.assertQuantizeResult(
            decimal.Decimal('5'), amount=decimal.Decimal('4.191'), force_rounding=decimal.ROUND_CEILING)


class CurrencySymbol(CurrencyMethodTestCase):

    def test_symbol_from_provider(self):
        self.assertEqual(self.mock_provider.get_symbol.return_value, self.currency.symbol)
        self.mock_provider.get_symbol.assert_called_once_with(self.currency.isocode)


class MagicCurrency(CurrencyMethodTestCase):
    def setUp(self):
        super(MagicCurrency, self).setUp()
        self.mock_provider.get_symbol.return_value = '¥'

    def test_str(self):
        self.assertEqual('¥', str(self.currency))

    def test_repr(self):
        self.assertEqual("Currency('YEN')", repr(self.currency))


class ComparissionCurrency(CurrencyMethodTestCase):
    def test_equals(self):
        yen1 = Currency('YEN')
        yen2 = Currency('yen')

        self.assertEqual(yen1, yen2)

    def test_different_codes(self):
        yen = Currency('YEN')
        clp = Currency('clp')

        self.assertNotEqual(yen, clp)

    def test_different_providers(self):
        provider1 = mock.NonCallableMagicMock(spec=CurrenciesProvider)
        yen1 = Currency('YEN', provider1)
        provider2 = mock.NonCallableMagicMock(spec=CurrenciesProvider)
        yen2 = Currency('yen', provider2)

        self.assertEqual(yen1, yen2)
