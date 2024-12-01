from decimal import Decimal
import pytest

from networth.finance.taxes import TaxCalculator, TaxBracket
from networth.models.taxes import TaxBill


def test_tax_calculator_initialization():
    # Test valid initialization
    calculator = TaxCalculator(2024, "married_jointly", "CA")
    assert calculator.year == 2024
    assert calculator.filing_status == "married_jointly"
    assert calculator.state == "CA"

    # Test year adjustment when using future year
    calculator = TaxCalculator(2026, "married_jointly", "CA")
    assert calculator.year == 2025  # Should use max available year

    # Test year adjustment when using past year
    calculator = TaxCalculator(2023, "married_jointly", "CA")
    assert calculator.year == 2024  # Should use min available year


def test_tax_calculator_invalid_inputs():
    # Test invalid filing status
    with pytest.raises(ValueError, match="Invalid filing status"):
        TaxCalculator(2024, "invalid_status", "CA")

    # Test invalid state
    with pytest.raises(ValueError, match="Invalid state"):
        TaxCalculator(2024, "married_jointly", "XX")


@pytest.mark.parametrize(
    "income,expected_federal,expected_state",
    [
        # Test no income
        (Decimal("0"), Decimal("0"), Decimal("0")),
        # Test first federal bracket
        (Decimal("20000"), Decimal("2000"), Decimal("200")),
        # Test middle federal bracket
        (
            Decimal("250000"),
            Decimal("34337")
            + Decimal("48949") * Decimal("0.24"),  # Base + (income - min) * rate
            Decimal("6217.44") + Decimal("108787") * Decimal("0.093"),
        ),  # Base + (income - min) * rate
        # Test high income
        (
            Decimal("1000000"),
            Decimal("196669.50") + Decimal("268800") * Decimal("0.37"),
            Decimal("75025.67") + Decimal("134426") * Decimal("0.113"),
        ),
    ],
)
def test_tax_calculation(income, expected_federal, expected_state):
    calculator = TaxCalculator(2024, "married_jointly", "CA")
    result = calculator.calculate_tax(income)

    assert isinstance(result, TaxBill)
    assert pytest.approx(float(result.federal), rel=1e-4) == float(expected_federal)
    assert pytest.approx(float(result.state), rel=1e-4) == float(expected_state)


def test_tax_bracket_dataclass():
    bracket = TaxBracket(min=0, max=100, rate=0.1, additional_from_previous=0)
    assert bracket.min == 0
    assert bracket.max == 100
    assert bracket.rate == 0.1
    assert bracket.additional_from_previous == 0
