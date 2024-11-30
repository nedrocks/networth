import pytest
from networth.models.currency import Currency, CurrencyCode


def test_currency_creation():
    # Test default amount
    currency = Currency(code=CurrencyCode.USD)
    assert currency.amount == 0
    assert currency.code == CurrencyCode.USD

    # Test with specific amount
    currency = Currency(code=CurrencyCode.EUR, amount=150)
    assert currency.amount == 150
    assert currency.code == CurrencyCode.EUR


def test_get_base_units():
    # Test USD (cents to dollars)
    usd = Currency(code=CurrencyCode.USD, amount=1234)
    assert usd.get_base_units() == 12.34

    # Test JPY (no decimals)
    jpy = Currency(code=CurrencyCode.JPY, amount=1234)
    assert jpy.get_base_units() == 1234


def test_format():
    # Test USD formatting
    usd = Currency(code=CurrencyCode.USD, amount=123456)
    assert usd.format() == "$1,234.56"

    # Test JPY formatting (no decimals)
    jpy = Currency(code=CurrencyCode.JPY, amount=123456)
    assert jpy.format() == "¥123,456"

    # Test EUR formatting
    eur = Currency(code=CurrencyCode.EUR, amount=123456)
    assert eur.format() == "€1,234.56"


def test_from_base_units():
    # Test USD (dollars to cents)
    usd = Currency.from_base_units(CurrencyCode.USD, 12.34)
    assert usd.amount == 1234

    # Test JPY (no conversion)
    jpy = Currency.from_base_units(CurrencyCode.JPY, 1234)
    assert jpy.amount == 1234


def test_add():
    # Test successful addition
    curr1 = Currency(code=CurrencyCode.USD, amount=100)
    curr2 = Currency(code=CurrencyCode.USD, amount=200)
    result = curr1.add(curr2)
    assert result.amount == 300
    assert result.code == CurrencyCode.USD

    # Test addition with different currencies
    curr3 = Currency(code=CurrencyCode.EUR, amount=100)
    with pytest.raises(ValueError):
        curr1.add(curr3)


def test_multiply():
    curr = Currency(code=CurrencyCode.USD, amount=100)

    # Test multiplication with integer
    result = curr.multiply(2)
    assert result.amount == 200

    # Test multiplication with float
    result = curr.multiply(1.5)
    assert result.amount == 150
