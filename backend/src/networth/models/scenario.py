from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional
from datetime import date
from enum import Enum
import pandas as pd
from decimal import Decimal


class ExpenseCategory(str, Enum):
    HOUSING = "housing"
    TRANSPORTATION = "transportation"
    FOOD = "food"
    UTILITIES = "utilities"
    HEALTHCARE = "healthcare"
    ENTERTAINMENT = "entertainment"
    OTHER = "other"


class Expense(BaseModel):
    category: ExpenseCategory
    amount: Decimal = Field(ge=0)
    is_monthly: bool = True
    description: Optional[str] = None

    @property
    def annual_amount(self) -> Decimal:
        return self.amount * 12 if self.is_monthly else self.amount


class Income(BaseModel):
    source: str
    amount: Decimal = Field(ge=0)
    is_monthly: bool = True
    tax_rate: Decimal = Field(ge=0, le=1)

    @property
    def annual_amount(self) -> Decimal:
        base_amount = self.amount * 12 if self.is_monthly else self.amount
        return base_amount * (1 - self.tax_rate)


class Investment(BaseModel):
    name: str
    initial_amount: Decimal = Field(ge=0)
    monthly_contribution: Decimal = Field(ge=0)
    expected_return_rate: Decimal = Field(ge=-1)  # Allow for potential losses

    def project_value(self, years: int) -> Dict[int, Decimal]:
        values = {}
        current_value = self.initial_amount

        for year in range(years + 1):
            values[year] = current_value
            # Compound interest with monthly contributions
            current_value = (
                current_value * (1 + self.expected_return_rate)
                + self.monthly_contribution * 12
            )

        return values


class FinancialScenario(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: date
    incomes: List[Income]
    expenses: List[Expense]
    investments: List[Investment]

    @property
    def annual_net_income(self) -> Decimal:
        total_income = sum(income.annual_amount for income in self.incomes)
        total_expenses = sum(expense.annual_amount for expense in self.expenses)
        return total_income - total_expenses

    def project_net_worth(self, years: int) -> Dict[int, Decimal]:
        net_worth = {}
        for year in range(years + 1):
            investment_values = sum(
                inv.project_value(year)[year] for inv in self.investments
            )
            savings = self.annual_net_income * year
            net_worth[year] = investment_values + savings
        return net_worth


class FinancialModel(BaseModel):
    base_scenario: FinancialScenario
    alternative_scenarios: Dict[str, FinancialScenario] = {}

    def compare_scenarios(self, years: int) -> pd.DataFrame:
        """Compare net worth projections across all scenarios."""
        data = {"base": list(self.base_scenario.project_net_worth(years).values())}

        for name, scenario in self.alternative_scenarios.items():
            data[name] = list(scenario.project_net_worth(years).values())

        return pd.DataFrame(data, index=range(years + 1))
