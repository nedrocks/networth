from datetime import date
from networth.models.compensation_package import (
    BaseSalaryChange,
    BonusPayment,
    CompensationPackage,
    SigningBonus,
    StockGrant,
    VestingScheduleType,
)
from networth.models.job import Job
import pytest

from networth.models.job import Job
from networth.models.currency import Currency, CurrencyCode


@pytest.fixture
def sample_comp_package() -> CompensationPackage:
    return CompensationPackage(
        employee_id="EMP123",
        start_date=date(2024, 1, 1),
        base_salary_history=[
            BaseSalaryChange(
                effective_date=date(2024, 1, 1),
                annual_amount=Currency(amount=100_000_00, code=CurrencyCode.USD),
            )
        ],
        bonus_payments=[
            BonusPayment(
                date=date(2024, 6, 1),
                amount=Currency(amount=10_000_00, code=CurrencyCode.USD),
                type="performance",
            )
        ],
        stock_grants=[
            StockGrant(
                grant_date=date(2024, 1, 1),
                total_shares=12000,
                price_per_share=Currency(amount=10_00, code=CurrencyCode.USD),
                vesting_schedule_type=VestingScheduleType.MONTHLY,
                vesting_start_date=date(2024, 1, 1),
                vesting_period_months=12,
                cliff_months=0,
            )
        ],
        signing_bonuses=[
            SigningBonus(
                payment_date=date(2024, 1, 1),
                amount=Currency(amount=20_000_00, code=CurrencyCode.USD),
            )
        ],
    )


def test_create_valid_job(sample_comp_package):
    job = Job(
        name="Software Engineer",
        comp_package=sample_comp_package,
    )

    assert job.name == "Software Engineer"
    assert job.comp_package == sample_comp_package


def test_required_fields():
    with pytest.raises(ValueError):
        Job(name="Missing Fields")  # type: ignore


def test_job_inheritance():
    """Test that Job inherits all properties from JobBase"""
    job_dict = Job.model_json_schema()["properties"]
    assert "name" in job_dict
    assert "comp_package" in job_dict
