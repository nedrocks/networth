from decimal import Decimal
from typing_extensions import Self
from pydantic import BaseModel, model_validator


class TaxBill(BaseModel):
    federal: Decimal
    state: Decimal

    @model_validator(mode="after")
    def validate_taxes(self) -> Self:
        if self.federal < 0 or self.state < 0:
            raise ValueError("Taxes cannot be negative")
        return self
