from dataclasses import dataclass
from decimal import Decimal
import logging

from networth.models.taxes import TaxBill

logger = logging.getLogger(__name__)


@dataclass
class TaxBracket:
    min: float
    max: float
    rate: float
    additional_from_previous: float


FEDERAL_TAX_BRACKETS = {
    2024: {
        "married_jointly": [
            TaxBracket(min=0, max=23_200, rate=0.10, additional_from_previous=0),
            TaxBracket(
                min=23_201, max=94_300, rate=0.12, additional_from_previous=2_320
            ),
            TaxBracket(
                min=94_301, max=201_050, rate=0.22, additional_from_previous=10_852
            ),
            TaxBracket(
                min=201_051, max=383_900, rate=0.24, additional_from_previous=34_337
            ),
            TaxBracket(
                min=383_901, max=487_450, rate=0.32, additional_from_previous=78_221
            ),
            TaxBracket(
                min=487_451, max=731_200, rate=0.35, additional_from_previous=111_357
            ),
            TaxBracket(
                min=731_201,
                max=float("inf"),
                rate=0.37,
                additional_from_previous=196_669.50,
            ),
        ]
    },
    2025: {
        "married_jointly": [
            TaxBracket(min=0, max=23_850, rate=0.10, additional_from_previous=0),
            TaxBracket(
                min=23_851, max=96_950, rate=0.12, additional_from_previous=2_385
            ),
            TaxBracket(
                min=96_951, max=206_700, rate=0.22, additional_from_previous=11_157
            ),
            TaxBracket(
                min=206_701, max=394_600, rate=0.24, additional_from_previous=35_302
            ),
            TaxBracket(
                min=394_601, max=501_050, rate=0.32, additional_from_previous=80_398
            ),
            TaxBracket(
                min=501_051, max=751_600, rate=0.35, additional_from_previous=114_462
            ),
            TaxBracket(
                min=751_601,
                max=float("inf"),
                rate=0.37,
                additional_from_previous=202_154.50,
            ),
        ]
    },
}

STATE_TAX_BRACKETS = {
    2024: {
        "CA": {
            "married_jointly": [
                TaxBracket(min=0, max=21_512, rate=0.01, additional_from_previous=0),
                TaxBracket(
                    min=21_513, max=50_998, rate=0.02, additional_from_previous=215.12
                ),
                TaxBracket(
                    min=50_999, max=80_490, rate=0.04, additional_from_previous=804.84
                ),
                TaxBracket(
                    min=80_491,
                    max=111_732,
                    rate=0.06,
                    additional_from_previous=1_984.52,
                ),
                TaxBracket(
                    min=111_733,
                    max=141_212,
                    rate=0.08,
                    additional_from_previous=3_859.04,
                ),
                TaxBracket(
                    min=141_213,
                    max=721_318,
                    rate=0.093,
                    additional_from_previous=6_217.44,
                ),
                TaxBracket(
                    min=721_319,
                    max=865_574,
                    rate=0.103,
                    additional_from_previous=60_167.30,
                ),
                TaxBracket(
                    min=865_575,
                    max=1_442_628,
                    rate=0.113,
                    additional_from_previous=75_025.67,
                ),
                TaxBracket(
                    min=1_442_629,
                    max=float("inf"),
                    rate=0.123,
                    additional_from_previous=140_232.77,
                ),
            ]
        }
    }
}

MIN_FEDERAL_YEAR = min(FEDERAL_TAX_BRACKETS.keys())
MAX_FEDERAL_YEAR = max(FEDERAL_TAX_BRACKETS.keys())


class TaxCalculator:
    def __init__(self, year: int, filing_status: str, state: str):
        self.year = year
        if self.year not in FEDERAL_TAX_BRACKETS:
            if self.year < MIN_FEDERAL_YEAR:
                self.year = MIN_FEDERAL_YEAR
            else:
                self.year = MAX_FEDERAL_YEAR
            logger.info(
                f"Using {self.year} tax brackets for {filing_status} because {year} has no tax configuration"
            )

        self.filing_status = filing_status
        if self.filing_status not in FEDERAL_TAX_BRACKETS[self.year]:
            raise ValueError(f"Invalid filing status: {filing_status}")

        self.federal_bracket = FEDERAL_TAX_BRACKETS[self.year][self.filing_status]

        self.state = state
        state_year = self.year
        if state_year not in STATE_TAX_BRACKETS:
            if state_year < min(STATE_TAX_BRACKETS.keys()):
                state_year = min(STATE_TAX_BRACKETS.keys())
            else:
                state_year = max(STATE_TAX_BRACKETS.keys())
        if self.state not in STATE_TAX_BRACKETS[state_year]:
            raise ValueError(f"Invalid state: {state}")
        if self.filing_status not in STATE_TAX_BRACKETS[state_year][self.state]:
            raise ValueError(f"Invalid filing status: {self.filing_status}")

        self.state_bracket = STATE_TAX_BRACKETS[state_year][self.state][
            self.filing_status
        ]

    def calculate_tax(self, income: Decimal) -> TaxBill:
        federal_tax = self._get_tax_amount(income, self.federal_bracket)
        state_tax = self._get_tax_amount(income, self.state_bracket)
        return TaxBill(federal=federal_tax, state=state_tax)

    def _get_tax_amount(self, income: Decimal, brackets: list[TaxBracket]) -> Decimal:
        for bracket in reversed(brackets):
            if income > bracket.min:
                return Decimal(
                    bracket.additional_from_previous
                    + (float(income) - bracket.min) * bracket.rate
                )
        return Decimal(0)
