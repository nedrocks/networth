from pydantic import Field
from enum import Enum

from networth.models.base import NWBase


class CurrencyCode(str, Enum):
    """Common currency codes following ISO 4217"""

    USD = "USD"  # United States Dollar
    EUR = "EUR"  # Euro
    GBP = "GBP"  # British Pound Sterling
    JPY = "JPY"  # Japanese Yen
    CNY = "CNY"  # Chinese Yuan
    INR = "INR"  # Indian Rupee


# Currency configuration: minimum unit in base units and display properties
CURRENCY_CONFIGS = {
    CurrencyCode.USD: {"decimals": 2, "symbol": "$"},  # 100 cents = 1 USD
    CurrencyCode.EUR: {"decimals": 2, "symbol": "€"},  # 100 cents = 1 EUR
    CurrencyCode.GBP: {"decimals": 2, "symbol": "£"},  # 100 pence = 1 GBP
    CurrencyCode.JPY: {"decimals": 0, "symbol": "¥"},  # 1 yen = 1 JPY
    CurrencyCode.CNY: {"decimals": 2, "symbol": "¥"},  # 100 fen = 1 CNY
    CurrencyCode.INR: {"decimals": 2, "symbol": "₹"},  # 100 paise = 1 INR
}


class Currency(NWBase):
    """
    Represents a currency with its code and amount in minimum units (e.g., cents for USD)
    """

    code: CurrencyCode
    amount: int = Field(
        default=0,
        description="The monetary amount in minimum currency units (e.g., cents for USD)",
    )

    def get_base_units(self) -> float:
        """Convert the amount from minimum units to base units (e.g., dollars from cents)"""
        config = CURRENCY_CONFIGS[self.code]
        return self.amount / (10 ** config["decimals"])

    def format(self) -> str:
        """Format the currency amount with its symbol"""
        config = CURRENCY_CONFIGS[self.code]
        base_amount = self.get_base_units()

        if config["decimals"] == 0:
            return f"{config['symbol']}{int(base_amount):,}"
        else:
            return f"{config['symbol']}{base_amount:,.{config['decimals']}f}"

    @classmethod
    def from_base_units(cls, code: CurrencyCode, amount: float) -> "Currency":
        """
        Create a Currency instance from base units (e.g., dollars instead of cents)

        Args:
            code: The currency code
            amount: The amount in base units (e.g., dollars for USD)

        Returns:
            A new Currency instance with the amount converted to minimum units
        """
        config = CURRENCY_CONFIGS[code]
        min_units = round(amount * (10 ** config["decimals"]))
        return cls(code=code, amount=min_units)

    def add(self, other: "Currency") -> "Currency":
        """Add two currencies of the same type"""
        if self.code != other.code:
            raise ValueError(f"Cannot add {self.code} to {other.code}")
        return Currency(code=self.code, amount=self.amount + other.amount)

    def multiply(self, factor: float) -> "Currency":
        """Multiply currency by a factor"""
        return Currency(code=self.code, amount=round(self.amount * factor))
