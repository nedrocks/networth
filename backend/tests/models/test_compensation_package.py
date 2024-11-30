from datetime import date
from decimal import Decimal
import pytest
from networth.models.compensation_package import (
    VestingScheduleType,
    StockGrant,
    BaseSalaryChange,
    BonusPayment,
    SigningBonus,
    CompensationPackage,
)
from networth.models.currency import Currency, CurrencyCode


def test_vesting_schedule_type_months():
    assert VestingScheduleType.MONTHLY.months == 1
    assert VestingScheduleType.QUARTERLY.months == 3
    assert VestingScheduleType.ANNUAL.months == 12
    with pytest.raises(ValueError):
        VestingScheduleType.CUSTOM.months


def test_vesting_schedule_type_num_periods():
    assert VestingScheduleType.MONTHLY.num_periods(12) == 12
    assert VestingScheduleType.QUARTERLY.num_periods(12) == 4
    assert VestingScheduleType.ANNUAL.num_periods(12) == 1
    with pytest.raises(ValueError):
        VestingScheduleType.CUSTOM.num_periods(12)


def test_stock_grant_calculate_vesting_schedule_monthly():
    grant = StockGrant(
        grant_date=date(2024, 1, 1),
        total_shares=12000,
        price_per_share=Currency(amount=10_00, code=CurrencyCode.USD),
        vesting_schedule_type=VestingScheduleType.MONTHLY,
        vesting_start_date=date(2024, 1, 1),
        vesting_period_months=12,
        cliff_months=0,
    )

    events = grant.calculate_vesting_schedule()
    assert len(events) == 12
    print([e.num_shares for e in events])
    assert all(event.num_shares == 1000 for event in events)
    assert events[0].date == date(2024, 2, 1)
    assert events[-1].date == date(2025, 1, 1)


def test_stock_grant_with_cliff():
    grant = StockGrant(
        grant_date=date(2024, 1, 1),
        total_shares=12000,
        price_per_share=Currency(amount=10_00, code=CurrencyCode.USD),
        vesting_schedule_type=VestingScheduleType.MONTHLY,
        vesting_start_date=date(2024, 1, 1),
        vesting_period_months=12,
        cliff_months=6,
    )

    events = grant.calculate_vesting_schedule()
    assert len(events) == 7  # 1 cliff event + 6 monthly events
    assert events[0].num_shares == 6000  # Cliff vesting
    assert events[1].num_shares == 1000  # Regular monthly vesting
    assert sum(e.num_shares for e in events) == 12000


def test_compensation_package_calculate_total_compensation():
    package = CompensationPackage(
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

    total = package.calculate_total_compensation(
        start_date=date(2024, 1, 1),
        end_date=date(2025, 1, 1),
    )

    total_salary = package.calculate_total_income(
        start_date=date(2024, 1, 1),
        end_date=date(2025, 1, 1),
    )
    total_bonuses = package.calculate_total_bonuses(
        start_date=date(2024, 1, 1),
        end_date=date(2025, 1, 1),
    )
    total_stock_grants = package.calculate_total_stock_grants(
        start_date=date(2024, 1, 1),
        end_date=date(2025, 1, 1),
    )
    total_signing_bonuses = package.calculate_total_signing_bonuses(
        start_date=date(2024, 1, 1),
        end_date=date(2025, 1, 1),
    )

    assert (
        total
        == total_salary + total_bonuses + total_stock_grants + total_signing_bonuses
    )

    # Expected total:
    # Base salary: 100000
    # Bonus: 10000
    # Stock vesting: 12000 shares * $10 = 120000
    # Signing bonus: 20000
    # Total: 250000
    assert total == Decimal("250000.00")


def test_compensation_package_partial_year():
    package = CompensationPackage(
        employee_id="EMP123",
        start_date=date(2024, 1, 1),
        base_salary_history=[
            BaseSalaryChange(
                effective_date=date(2024, 1, 1),
                annual_amount=Currency(amount=120_000_00, code=CurrencyCode.USD),
            )
        ],
        bonus_payments=[],
        stock_grants=[],
        signing_bonuses=[],
    )

    # Test for 6 months
    total = package.calculate_total_compensation(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 7, 1),
    )

    # Expected: 59506.85 (Not exactly half a year. 181 days / 365 days)
    assert round(total, 2) == Decimal("59506.85")


def test_compensation_package_salary_change():
    package = CompensationPackage(
        employee_id="EMP123",
        start_date=date(2024, 1, 1),
        base_salary_history=[
            BaseSalaryChange(
                effective_date=date(2024, 1, 1),
                annual_amount=Currency(amount=100_000_00, code=CurrencyCode.USD),
            ),
            BaseSalaryChange(
                effective_date=date(2024, 7, 1),
                annual_amount=Currency(amount=120_000_00, code=CurrencyCode.USD),
            ),
        ],
        bonus_payments=[],
        stock_grants=[],
        signing_bonuses=[],
    )

    total = package.calculate_total_compensation(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
    )

    # Expected: ~50000 (first half) + ~60000 (second half) = 110000
    assert round(total, 2) == Decimal("109150.69")
