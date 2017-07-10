
from abc import ABCMeta, abstractmethod
from decimal import Decimal, ROUND_UP
from typing import Optional

from .exceptions import InvalidCurrency


class CurrenciesProvider(metaclass=ABCMeta):
    @abstractmethod
    def get_decimal_places(self, isocode: str) -> int:
        pass  # pragma: no cover

    @abstractmethod
    def get_symbol(self, isocode: str) -> str:
        pass  # pragma: no cover

    @abstractmethod
    def validate_currency(self, isocode: str) -> None:
        pass  # pragma: no cover

    @abstractmethod
    def format_amount(self, isocode: str, amount: Decimal) -> str:
        pass  # pragma: no cover

    def get_rounding(self, isocode: str) -> str:
        return ROUND_UP


class DefaultCurrenciesProvider(CurrenciesProvider):
    def get_decimal_places(self, isocode: str) -> int:
        return 2

    def get_symbol(self, isocode: str) -> str:
        return '$'

    def validate_currency(self, isocode: str) -> None:
        pass

    def format_amount(self, isocode: str, amount: Decimal) -> str:
        sign = '-' if amount < 0 else ''
        amount = abs(amount)
        return "{sign}{symbol}{amount}".format(
            sign=sign,
            symbol=self.get_symbol(isocode),
            amount=amount
        )


class Currency:
    _default_provider = DefaultCurrenciesProvider()  # type: CurrenciesProvider

    def __init__(self, isocode: str, provider: Optional[CurrenciesProvider]=None) -> None:
        self._set_provider(provider)

        cleaned_isocode = self.clean_isocode(isocode)
        self._provider.validate_currency(cleaned_isocode)
        self.isocode = cleaned_isocode

    @classmethod
    def set_default_provider(cls, provider: CurrenciesProvider) -> None:
        cls._default_provider = provider

    @classmethod
    def get_default_provider(cls) -> CurrenciesProvider:
        return cls._default_provider

    @classmethod
    def clean_isocode(cls, isocode: str) -> str:
        if not isinstance(isocode, str) or len(isocode) != 3:
            raise InvalidCurrency(isocode)
        return isocode.upper()

    def format_amount(self, amount: Decimal) -> str:
        return self.format_amount_as_is(self.quantize_amount(amount))

    def format_amount_as_is(self, amount: Decimal) -> str:
        return self._provider.format_amount(self.isocode, amount)

    def quantize_amount(self, amount: Decimal, force_rounding: Optional[str]=None) -> Decimal:
        rounding = force_rounding or self._provider.get_rounding(self.isocode)
        return amount.quantize(self._get_quantizer(), rounding=rounding)

    @property
    def symbol(self) -> str:
        return self._provider.get_symbol(self.isocode)

    def _get_quantizer(self) -> Decimal:
        decimal_places = self._provider.get_decimal_places(self.isocode)
        return Decimal(10) ** -decimal_places

    def _set_provider(self, provider: Optional[CurrenciesProvider]) -> None:
        if provider is not None:
            self._provider = provider
        else:
            self._provider = self.get_default_provider()

    def __repr__(self):
        return "Currency('{isocode}')".format(isocode=self.isocode)

    def __str__(self):
        return self.symbol

    def __eq__(self, other):
        return self.isocode == other.isocode
