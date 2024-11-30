from datetime import date, datetime, timedelta
from typing import List, Optional
from typing_extensions import override
from networth.models.base import IncomeProvider, NWBase
from networth.models.currency import Currency
from pydantic import BaseModel, Field
from enum import Enum
from decimal import Decimal


class VestingScheduleType(str, Enum):
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    CUSTOM = "custom"

    @property
    def months(self) -> int:
        if self == VestingScheduleType.MONTHLY:
            return 1
        elif self == VestingScheduleType.QUARTERLY:
            return 3
        elif self == VestingScheduleType.ANNUAL:
            return 12
        else:
            raise ValueError(f"Invalid vesting schedule type: {self}")

    def num_periods(self, num_months: int) -> int:
        if self == VestingScheduleType.MONTHLY:
            return num_months
        elif self == VestingScheduleType.QUARTERLY:
            return int(num_months / 3)
        elif self == VestingScheduleType.ANNUAL:
            return int(num_months / 12)
        else:
            raise ValueError(f"Invalid vesting schedule type: {self}")


class VestingEvent(NWBase):
    date: date
    num_shares: int
    amount: Currency


class StockGrant(NWBase):
    grant_date: date
    total_shares: int
    price_per_share: Currency
    vesting_schedule_type: VestingScheduleType
    vesting_start_date: date
    vesting_period_months: int  # Total vesting period in months
    cliff_months: int = 0  # Cliff period in months
    vesting_events: List[VestingEvent] = Field(default_factory=list)

    def __str__(self) -> str:
        return f"""
Stock Grant:
    Grant Date: {self.grant_date.strftime("%Y-%m-%d")}
    Total Shares: {self.total_shares}
    Price Per Share: {self.price_per_share}
    Vesting Schedule Type: {self.vesting_schedule_type}
    Vesting Start Date: {self.vesting_start_date.strftime("%Y-%m-%d")}
    Vesting Period Months: {self.vesting_period_months}
    Cliff Months: {self.cliff_months}
"""

    def calculate_vesting_schedule(self) -> List[VestingEvent]:
        events = []
        if self.vesting_schedule_type == VestingScheduleType.CUSTOM:
            return self.vesting_events

        # Skip vesting during cliff period
        months_after_cliff = self.vesting_period_months - max(1, self.cliff_months)
        shares_vested_at_cliff = (
            self.total_shares * max(1, self.cliff_months) / self.vesting_period_months
        )
        shares_vested_after_cliff = self.total_shares - shares_vested_at_cliff
        shares_per_period = int(
            shares_vested_after_cliff
            / self.vesting_schedule_type.num_periods(months_after_cliff)
        )

        # Calculate monthly vesting dates
        for num_months_worked in range(
            max(self.cliff_months, 1),
            self.vesting_period_months + 1,
            self.vesting_schedule_type.months,
        ):
            vest_date = date(
                self.vesting_start_date.year
                + (self.vesting_start_date.month + num_months_worked - 1) // 12,
                ((self.vesting_start_date.month + num_months_worked - 1) % 12) + 1,
                self.vesting_start_date.day,
            )

            # For cliff vesting, all accumulated shares vest at once
            shares = shares_per_period
            if num_months_worked == self.cliff_months or (
                num_months_worked == 0 and self.cliff_months == 0
            ):
                shares = shares_vested_at_cliff

            events.append(
                VestingEvent(
                    date=vest_date,
                    amount=self.price_per_share.multiply(int(shares)),
                    num_shares=int(shares),
                )
            )

        return events


class BaseSalaryChange(NWBase):
    effective_date: date
    annual_amount: Currency
    bonus_percentage: Optional[Decimal] = None
    reason: Optional[str] = None

    def __str__(self) -> str:
        return f"""
Base Salary Change:
    Yearly Total: {self.annual_amount.multiply(float(Decimal(1) + (self.bonus_percentage or 0)))}
    Annual Amount: {self.annual_amount}
    Bonus Percentage: {self.bonus_percentage}
    Reason: {self.reason}
    Effective Date: {self.effective_date.strftime("%Y-%m-%d")}
"""


class BonusPayment(NWBase):
    date: date
    amount: Currency
    type: str  # e.g., "performance", "holiday", etc.
    description: Optional[str] = None

    def __str__(self) -> str:
        return f"""
Bonus Payment:
    Date: {self.date.strftime("%Y-%m-%d")}
    Amount: {self.amount}
    Type: {self.type}
    Description: {self.description}
"""


class SigningBonus(NWBase):
    payment_date: date
    amount: Currency
    conditions: Optional[str] = None

    def __str__(self) -> str:
        return f"""
Signing Bonus:
    Payment Date: {self.payment_date.strftime("%Y-%m-%d")}
    Amount: {self.amount}
    Conditions: {self.conditions}
"""


class CompensationPackage(NWBase, IncomeProvider):
    employee_id: str
    start_date: date
    base_salary_history: List[BaseSalaryChange]
    bonus_payments: List[BonusPayment]
    stock_grants: List[StockGrant]
    signing_bonuses: List[SigningBonus]

    def __str__(self) -> str:
        return f"""
Compensation Package:
    Employee ID: {self.employee_id}
    Start Date: {self.start_date.strftime("%Y-%m-%d")}
    Base Salary: 
        {sorted(self.base_salary_history, key=lambda x: x.effective_date)}
    Bonus Payments:
        {sorted(self.bonus_payments, key=lambda x: x.date)}
    Stock Grants:
        {sorted(self.stock_grants, key=lambda x: x.grant_date)}
    Signing Bonuses:
        {sorted(self.signing_bonuses, key=lambda x: x.payment_date)}
"""

    @override
    def calculate_total_income(self, start_date: date, end_date: date) -> Decimal:
        """Total salary is based on a period where end_date is non-inclusive."""
        total = 0
        for salary in sorted(self.base_salary_history, key=lambda x: x.effective_date):
            if salary.effective_date < end_date:
                # Calculate prorated salary for the period
                period_start = max(start_date, salary.effective_date)
                next_salary = next(
                    (
                        s
                        for s in self.base_salary_history
                        if s.effective_date > salary.effective_date
                    ),
                    None,
                )
                period_end = min(
                    end_date,
                    (
                        next_salary.effective_date - timedelta(days=1)
                        if next_salary
                        else end_date
                    ),
                )

                days_in_period = (period_end - period_start).days - 1
                total += salary.annual_amount.multiply(days_in_period / 365).amount

        return Decimal(total / 100)

    def calculate_total_bonuses(self, start_date: date, end_date: date) -> Decimal:
        """Total salary is based on a period where end_date is non-inclusive."""
        total = 0
        for bonus in self.bonus_payments:
            if start_date <= bonus.date < end_date:
                total += bonus.amount.amount
        return Decimal(total / 100)

    def calculate_total_stock_grants(self, start_date: date, end_date: date) -> Decimal:
        """NOTE: end-date is inclusive. This is because the end_date is calculated based on
        the vesting date for work done prior to the vest date."""
        total = 0
        for grant in self.stock_grants:
            vesting_schedule = grant.calculate_vesting_schedule()
            total += sum(
                event.amount.amount
                for event in vesting_schedule
                if start_date <= event.date <= end_date
            )
        return Decimal(total / 100)

    def calculate_total_signing_bonuses(
        self, start_date: date, end_date: date
    ) -> Decimal:
        """Total salary is based on a period where end_date is non-inclusive."""
        total = 0
        for bonus in self.signing_bonuses:
            if start_date <= bonus.payment_date < end_date:
                total += bonus.amount.amount
        return Decimal(total / 100)

    def calculate_total_compensation(self, start_date: date, end_date: date) -> Decimal:
        total = Decimal(0)

        # Calculate base salary for the period
        total += self.calculate_total_income(start_date, end_date)

        # Add bonuses within the period
        total += self.calculate_total_bonuses(start_date, end_date)

        # Add vested stock grants
        total += self.calculate_total_stock_grants(start_date, end_date)

        # Add signing bonuses
        total += self.calculate_total_signing_bonuses(start_date, end_date)

        return total
