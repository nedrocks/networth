import pytest
from datetime import date, timedelta

import networth.models.income_source
from networth.models.income_source import (
    SingletonIncomeSource,
    PeriodicIncomeSource,
    ModifiablePeriodicIncomeSource,
)
from networth.models.currency import Currency, CurrencyCode


sample_currency = Currency(code=CurrencyCode.USD, amount=1000)  # $10.00


def test_singleton_income_source():
    # Test valid creation
    income = SingletonIncomeSource(
        amt=sample_currency,
        name="Bonus",
        description="Year-end bonus",
        income_date=date(2024, 12, 31),
    )
    assert income.name == "Bonus"
    assert income.amt == sample_currency
    assert income.income_date == date(2024, 12, 31)


def test_periodic_income_source():
    # Test valid creation
    income = PeriodicIncomeSource(
        amt=sample_currency,
        name="Salary",
        description="Monthly salary",
        period=timedelta(days=30),
        income_start_date=date(2024, 1, 1),
        income_end_date=date(2024, 12, 31),
    )
    assert income.name == "Salary"
    assert income.period == timedelta(days=30)

    # Test date validation
    with pytest.raises(
        ValueError, match="Income start date must be before income end date"
    ):
        PeriodicIncomeSource(
            amt=sample_currency,
            name="Invalid",
            description="Invalid dates",
            period=timedelta(days=30),
            income_start_date=date(2024, 12, 31),
            income_end_date=date(2024, 1, 1),
        )

    for days in [0, 366]:
        with pytest.raises(
            ValueError, match="Period must be between 1 day and 365 days"
        ):
            PeriodicIncomeSource(
                amt=sample_currency,
                name="Invalid",
                description="Invalid period",
                period=timedelta(days=366),
                income_start_date=date(2024, 1, 1),
                income_end_date=date(2024, 12, 31),
            )

    # Test per_month_amt calculation
    monthly_amt = income.per_month_amt()
    assert isinstance(monthly_amt, Currency)
    assert monthly_amt.code == CurrencyCode.USD

    # Test per_year_amt calculation
    yearly_amt = income.per_year_amt()
    assert isinstance(yearly_amt, Currency)
    assert yearly_amt.code == CurrencyCode.USD


def test_modifiable_periodic_income_source():
    source1 = PeriodicIncomeSource(
        amt=sample_currency,
        name="Salary 2024",
        description="2024 salary",
        period=timedelta(days=30),
        income_start_date=date(2024, 1, 1),
        income_end_date=date(2024, 12, 31),
    )

    source2 = PeriodicIncomeSource(
        amt=Currency(code=CurrencyCode.USD, amount=1200),  # $12.00
        name="Salary 2025",
        description="2025 salary",
        period=timedelta(days=30),
        income_start_date=date(2025, 1, 1),
        income_end_date=date(2025, 12, 31),
    )

    # Test valid creation
    income = ModifiablePeriodicIncomeSource(
        amt=sample_currency,
        name="Career",
        description="Career progression",
        sources=[source1, source2],
    )
    assert len(income.sources) == 2

    # Test overlapping dates validation
    overlapping_source = PeriodicIncomeSource(
        amt=sample_currency,
        name="Overlap",
        description="Overlapping period",
        period=timedelta(days=30),
        income_start_date=date(2024, 6, 1),
        income_end_date=date(2024, 12, 31),
    )

    with pytest.raises(ValueError, match="Sources must be in order and not overlap"):
        ModifiablePeriodicIncomeSource(
            amt=sample_currency,
            name="Invalid",
            description="Invalid sources",
            sources=[source1, overlapping_source],
        )

    # Test non-contiguous dates validation
    gap_source = PeriodicIncomeSource(
        amt=sample_currency,
        name="Gap",
        description="Gap in dates",
        period=timedelta(days=30),
        income_start_date=date(2025, 1, 3),  # Gap of one day
        income_end_date=date(2025, 12, 31),
    )

    with pytest.raises(ValueError, match="Sources must be contiguous"):
        ModifiablePeriodicIncomeSource(
            amt=sample_currency,
            name="Invalid",
            description="Invalid sources",
            sources=[source1, gap_source],
        )
