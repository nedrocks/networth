from datetime import date
from decimal import Decimal
from typing_extensions import override
from typing import Optional
from networth.models.compensation_package import CompensationPackage
from typing_extensions import Self
from pydantic import Field, model_validator

from networth.models.base import IncomeProvider, NWBase


class JobBase(NWBase, IncomeProvider):
    name: str = Field(..., description="Human readable name for this job")
    comp_package: CompensationPackage

    @override
    def calculate_total_income(self, start_date: date, end_date: date) -> Decimal:
        return self.comp_package.calculate_total_income(start_date, end_date)

    def __str__(self) -> str:
        return f"""
Job:
    Name: {self.name}
    Compensation Package: {self.comp_package}
"""


class Job(JobBase):
    pass
