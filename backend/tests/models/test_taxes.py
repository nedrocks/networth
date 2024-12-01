from decimal import Decimal
import pytest
from networth.models.taxes import TaxBill


class TestTaxBill:
    def test_create_tax_bill(self):
        # Test creating a valid TaxBill
        tax_bill = TaxBill(federal=Decimal("1000.50"), state=Decimal("500.25"))
        assert tax_bill.federal == Decimal("1000.50")
        assert tax_bill.state == Decimal("500.25")

    def test_create_tax_bill_with_integers(self):
        # Test creating a TaxBill with integer values
        tax_bill = TaxBill(federal=Decimal("1000"), state=Decimal("500"))
        assert isinstance(tax_bill.federal, Decimal)
        assert isinstance(tax_bill.state, Decimal)
        assert tax_bill.federal == Decimal("1000")
        assert tax_bill.state == Decimal("500")

    def test_create_tax_bill_with_strings(self):
        # Test creating a TaxBill with string values
        tax_bill = TaxBill(federal=Decimal("1000.50"), state=Decimal("500.25"))
        assert isinstance(tax_bill.federal, Decimal)
        assert isinstance(tax_bill.state, Decimal)
        assert tax_bill.federal == Decimal("1000.50")
        assert tax_bill.state == Decimal("500.25")

    def test_invalid_values(self):
        # Test that invalid values raise validation errors
        with pytest.raises(ValueError):
            TaxBill(federal=Decimal("-1"), state=Decimal("500"))

        with pytest.raises(ValueError):
            TaxBill(federal=Decimal("500"), state=Decimal("-1"))
