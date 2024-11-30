from datetime import date
from decimal import Decimal
from typing_extensions import override, Self
from networth.models.base import IncomeProvider, NWBase
from networth.models.job import Job
from pydantic import BaseModel, model_validator


class JobIncome(BaseModel, IncomeProvider):
    job: Job
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_dates(self) -> Self:
        if self.end_date and self.end_date < self.start_date:
            raise ValueError("End date must be after start date")
        return self

    @override
    def calculate_total_income(self, start_date: date, end_date: date) -> Decimal:
        return self.job.calculate_total_income(start_date, end_date)

    def __str__(self) -> str:
        return f"""
Job Income:
    Job: {self.job}
    Start Date: {self.start_date.strftime("%Y-%m-%d")}
    End Date: {self.end_date.strftime("%Y-%m-%d")}
"""


class Income(NWBase, IncomeProvider):
    job_income: list[JobIncome]

    @override
    def calculate_total_income(self, start_date: date, end_date: date) -> Decimal:
        return Decimal(
            sum(
                job_income.calculate_total_income(start_date, end_date)
                for job_income in self.job_income
            )
        )
