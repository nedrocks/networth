from datetime import date, timedelta
from typing_extensions import Self
from pydantic import field_validator, model_validator

from networth.models.base import NWBase
from networth.models.currency import Currency


class BaseIncomeSource(NWBase):
    name: str
    description: str


class SingletonIncomeSource(BaseIncomeSource):
    income_date: date
    amt: "Currency"


class PeriodicIncomeSource(BaseIncomeSource):
    period: timedelta
    amt: "Currency"

    income_start_date: date
    income_end_date: date

    @model_validator(mode="after")
    def validate_period(self) -> Self:
        if self.period.days < 1 or self.period.days > 365:
            raise ValueError("Period must be between 1 day and 365 days")
        return self

    @model_validator(mode="after")
    def validate_dates(self) -> Self:
        if self.income_start_date > self.income_end_date:
            raise ValueError("Income start date must be before income end date")
        return self

    def per_month_amt(self) -> Currency:
        return self.amt.multiply(365 / self.period.days / 12)

    def per_year_amt(self) -> Currency:
        return self.amt.multiply(365 / self.period.days)


class ModifiablePeriodicIncomeSource(BaseIncomeSource):
    """A contiguous period of time with a recurring income. The amount may change over time.
    It is not valid to have gaps in time."""

    sources: list[PeriodicIncomeSource]

    @field_validator("sources")
    @classmethod
    def validate_ordered_soruces(
        cls,
        sources: list[PeriodicIncomeSource],
    ) -> list[PeriodicIncomeSource]:
        if not len(sources):
            raise ValueError("Must have at least one source")

        for i in range(1, len(sources)):
            if sources[i].income_start_date < sources[i - 1].income_end_date:
                raise ValueError("Sources must be in order and not overlap")
            if (sources[i].income_start_date - sources[i - 1].income_end_date).days > 1:
                raise ValueError("Sources must be contiguous")
        return sources

    def add_source(self, source: PeriodicIncomeSource) -> Self:
        self.sources[-1].income_end_date = source.income_start_date - timedelta(days=1)
        self.sources.append(source)
        return self
