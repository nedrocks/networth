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


class Job(JobBase):
    pass
