

class InvalidCurrency(Exception):
    pass


class InvalidAmount(Exception):
    pass


class InvalidMoneyOperation(Exception):
    pass


class InvalidOperand(InvalidMoneyOperation):
    pass


class CurrencyMismatch(InvalidMoneyOperation):
    pass
