from datetime import date
from typing import Optional
from typing_extensions import Self
from pydantic import BaseModel, Field, model_validator
from uuid import UUID

from networth.models.base import NWBase
from networth.models.income_source import (
    ModifiablePeriodicIncomeSource,
    PeriodicIncomeSource,
    SingletonIncomeSource,
)


class JobBase(NWBase):
    name: str = Field(..., description="Human readable name for this job")
    start_date: date = Field(..., description="Date when this job starts")
    end_date: Optional[date] = Field(
        default=None, description="Optional date when this job ends"
    )

    base_salary: "ModifiablePeriodicIncomeSource"
    bonus_salary: "ModifiablePeriodicIncomeSource | None" = None
    stock_income: list["PeriodicIncomeSource"] = Field(default=[])
    signing_bonus: list["SingletonIncomeSource"] = Field(default=[])

    @model_validator(mode="after")
    def validate_dates(self) -> Self:
        if self.end_date and self.end_date < self.start_date:
            raise ValueError("End date must be after start date")
        return self

    def add_base_salary(self, salary: PeriodicIncomeSource) -> Self:
        self.base_salary.add_source(salary)
        return self

    def add_bonus_salary(self, bonus_salary: PeriodicIncomeSource) -> Self:
        if self.bonus_salary is None:
            self.bonus_salary = ModifiablePeriodicIncomeSource(
                name="Bonus",
                description="Bonus salary",
                sources=[bonus_salary],
            )
        self.bonus_salary.add_source(bonus_salary)
        return self

    def add_stock_income(self, stock_income: PeriodicIncomeSource) -> Self:
        self.stock_income.append(stock_income)
        return self

    def add_signing_bonus(self, signing_bonus: SingletonIncomeSource) -> Self:
        self.signing_bonus.append(signing_bonus)
        return self


class Job(JobBase):
    pass
