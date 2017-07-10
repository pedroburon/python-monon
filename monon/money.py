
from enum import Enum
from decimal import Decimal, DecimalException
from typing import List, Tuple, Union  # noqa
from copy import copy
from numbers import Number

from .currency import Currency
from .exceptions import CurrencyMismatch, InvalidAmount, InvalidOperand


class MoneyOperator(Enum):
    ADDITION = '+'
    SUBSTRACTION = '-'
    MULTIPLICATION = '*'
    DIVISION = '/'
    INITIALIZATION = 'init'


class MoneyOperation:
    def __init__(self, operator: MoneyOperator, *operands: Union['Money', Decimal]) -> None:
        self.operands = [copy(operand) for operand in operands]
        self.operator = operator

    def __repr__(self):
        return "({operator} {operands})".format(
            operator=self.operator.value,
            operands=" ".join(repr(operand) for operand in self.operands)
        )


class Money:

    @classmethod
    def clean_amount(cls, amount: Union[str, Number, Decimal], currency: Currency) -> Decimal:
        '''
        Convert numeric into Decimal based on currency decimal places.

        >>> USD = Currency('USD')
        >>> Money.clean_amount('123.456', USD)
        Decimal('123.46')

        >>> Money.clean_amount(123, USD)
        Decimal('123.00')

        >>> Money.clean_amount(Decimal('123.456'), USD)
        Decimal('123.46')
        '''
        try:
            cleaned_amount = Decimal(str(amount))
        except DecimalException:
            raise InvalidAmount(amount)
        else:
            return currency.quantize_amount(cleaned_amount)

    @classmethod
    def clean_currency(cls, currency: Union[str, Currency]) -> Currency:
        '''
        Returns Currency from str or same if Currency.

        >>> Money.clean_currency('usd')
        Currency('USD')

        >>> Money.clean_currency(Currency('YEN'))
        Currency('YEN')
        '''
        if isinstance(currency, Currency):
            return currency
        return Currency(currency)

    def __init__(self, amount: Union[str, Number, Decimal], currency: Union[str, Currency]) -> None:
        self.currency = self.clean_currency(currency)
        self.amount = self.clean_amount(amount, self.currency)
        self.operations = [MoneyOperation(MoneyOperator.INITIALIZATION, self)]  # type: List[MoneyOperation]

    def formatted(self) -> str:
        return self.currency.format_amount_as_is(self.amount)

    def _add_operation(self, operator: MoneyOperator, *operands: Union['Money', Decimal]) -> None:
        self.operations.append(MoneyOperation(operator, *operands))

    def _clean_operand(self, other):
        if isinstance(other, Number):
            return Money(other, self.currency)

        if not isinstance(other, (Money, Number)):
            raise InvalidOperand(other)

        if other.currency != self.currency:
            raise CurrencyMismatch(self.currency, other.currency)

        return other

    def __add__(self, other):
        '''
        >>> Money("1", 'USD') + Money("5", 'USD')
        USD$6.00
        >>> Money("2.02", 'USD') + Decimal("2.18")
        USD$4.20
        '''
        other = self._clean_operand(other)
        result = Money(self.amount + other.amount, self.currency)
        result._add_operation(MoneyOperator.ADDITION, self, other)
        return result

    def __radd__(self, other):
        '''
        >>> 1 + Money("5", 'USD')
        USD$6.00
        '''
        return self.__add__(other)

    def __iadd__(self, other):
        '''
        >>> m = Money("5", 'USD')
        >>> m += Money(1, 'USD')
        >>> m
        USD$6.00
        '''
        other = self._clean_operand(other)
        self._add_operation(MoneyOperator.ADDITION, self, other)
        self.amount += other.amount
        return self

    def __sub__(self, other):
        '''
        >>> Money("5.22", 'USD') - Money("1.02", 'USD')
        USD$4.20
        >>> Money("5.22", 'USD') - Decimal("1.02")
        USD$4.20
        '''
        other = self._clean_operand(other)
        result = Money(self.amount - other.amount, self.currency)
        result._add_operation(MoneyOperator.SUBSTRACTION, self, other)
        return result

    def __rsub__(self, other):
        '''
        >>> 5 - Money("0.80", 'USD')
        USD$4.20
        '''
        other = self._clean_operand(other)
        return other.__sub__(self)

    def __isub__(self, other):
        '''
        >>> m = Money("5.22", Currency('USD'))
        >>> m -= Money("1.02", Currency('USD'))
        >>> m
        USD$4.20
        '''
        other = self._clean_operand(other)
        self._add_operation(MoneyOperator.SUBSTRACTION, self, other)
        self.amount -= other.amount
        return self

    def __mul__(self, other: Number):
        '''
        >>> Money(5, 'USD') * 5
        USD$25.00
        '''
        if not isinstance(other, Number):
            raise InvalidOperand(other)
        cleaned_amount = self.clean_amount(other, self.currency)
        result = Money(self.amount * cleaned_amount, self.currency)
        result._add_operation(MoneyOperator.MULTIPLICATION, self, cleaned_amount)
        return result

    def __rmul__(self, other: Number):
        '''
        >>> 5 * Money(5, Currency('USD'))
        USD$25.00
        '''
        return self.__mul__(other)

    def __truediv__(self, other: Number):
        '''
        >>> Money(25, Currency('USD')) / 5
        USD$5.00
        '''
        cleaned_amount = self.clean_amount(other, self.currency)
        result = Money(self.amount / cleaned_amount, self.currency)
        result._add_operation(MoneyOperator.DIVISION, self, cleaned_amount)
        return result

    def __neg__(self):
        '''
        >>> -Money(25, 'USD')
        USD-$25.00
        >>> -Money(-25, 'USD')
        USD$25.00
        '''
        return self * -1

    def __eq__(self, other):
        return isinstance(other, Money) and self.amount == other.amount and self.currency == other.currency

    def __repr__(self):
        return "{isocode}{formatted_amount}".format(
            isocode=self.currency.isocode,
            formatted_amount=self.formatted()
        )

    def __str__(self):
        return self.formatted()
