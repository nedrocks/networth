from datetime import date, timedelta
import pytest

from networth.models.job import Job
from networth.models.income_source import (
    ModifiablePeriodicIncomeSource,
    PeriodicIncomeSource,
    SingletonIncomeSource,
)
from networth.models.currency import Currency, CurrencyCode


@pytest.fixture
def sample_periodic_source():
    return PeriodicIncomeSource(
        amt=Currency(code=CurrencyCode.USD, amount=1000000),  # $10,000
        name="Base Salary 2024",
        description="2024 base salary",
        period=timedelta(days=14),  # Biweekly
        income_start_date=date(2024, 1, 1),
        income_end_date=date(2024, 12, 31),
    )


@pytest.fixture
def sample_base_salary(sample_periodic_source):
    return ModifiablePeriodicIncomeSource(
        amt=Currency(code=CurrencyCode.USD, amount=1000000),  # $10,000
        name="Base Salary",
        description="Base salary progression",
        sources=[sample_periodic_source],
    )


@pytest.fixture
def sample_signing_bonus():
    return SingletonIncomeSource(
        amt=Currency(code=CurrencyCode.USD, amount=1000000),  # $10,000
        name="Sign-on Bonus",
        description="One-time signing bonus",
        income_date=date(2024, 1, 1),
    )


def test_job_creation_minimal(sample_base_salary):
    # Test creation with only required fields
    job = Job(
        name="Software Engineer",
        start_date=date(2024, 1, 1),
        base_salary=sample_base_salary,
    )

    assert job.name == "Software Engineer"
    assert job.start_date == date(2024, 1, 1)
    assert job.end_date is None
    assert job.base_salary == sample_base_salary
    assert job.bonus_salary is None
    assert len(job.stock_income) == 0
    assert len(job.signing_bonus) == 0


def test_job_creation_full(
    sample_base_salary, sample_signing_bonus, sample_periodic_source
):
    # Create bonus salary
    bonus_salary = ModifiablePeriodicIncomeSource(
        amt=Currency(code=CurrencyCode.USD, amount=200000),  # $2,000
        name="Annual Bonus",
        description="Annual performance bonus",
        sources=[sample_periodic_source],
    )

    # Create stock grant
    stock_grant = PeriodicIncomeSource(
        amt=Currency(code=CurrencyCode.USD, amount=500000),  # $5,000
        name="RSU Grant",
        description="Restricted Stock Units",
        period=timedelta(days=365),  # Annual vesting
        income_start_date=date(2024, 1, 1),
        income_end_date=date(2027, 12, 31),
    )

    # Test creation with all fields
    job = Job(
        name="Senior Software Engineer",
        start_date=date(2024, 1, 1),
        end_date=date(2027, 12, 31),
        base_salary=sample_base_salary,
        bonus_salary=bonus_salary,
        stock_income=[stock_grant],
        signing_bonus=[sample_signing_bonus],
    )

    assert job.name == "Senior Software Engineer"
    assert job.start_date == date(2024, 1, 1)
    assert job.end_date == date(2027, 12, 31)
    assert job.base_salary == sample_base_salary
    assert job.bonus_salary == bonus_salary
    assert len(job.stock_income) == 1
    assert job.stock_income[0] == stock_grant
    assert len(job.signing_bonus) == 1
    assert job.signing_bonus[0] == sample_signing_bonus


def test_job_invalid_dates():
    # Test that end_date cannot be before start_date
    with pytest.raises(ValueError):
        Job(
            name="Invalid Job",
            start_date=date(2024, 12, 31),
            end_date=date(2024, 1, 1),
            base_salary=ModifiablePeriodicIncomeSource(
                amt=Currency(code=CurrencyCode.USD, amount=100000),
                name="Base",
                description="Base salary",
                sources=[],
            ),
        )
