from faker import Faker
import factory
from factory.fuzzy import FuzzyChoice, FuzzyInteger
from networth.models.compensation_package import (
    BaseSalaryChange,
    BonusPayment,
    CompensationPackage,
    SigningBonus,
    StockGrant,
    VestingScheduleType,
)
from networth.models.currency import Currency, CurrencyCode
from networth.models.income import JobIncome
from networth.models.job import Job


class CurrencyFactory(factory.Factory):
    """Factory for generating Currency instances for testing"""

    class Meta:
        model = Currency

    class Params:
        min_amount = 0
        max_amount = 1_000_000_00

    code = FuzzyChoice(CurrencyCode)
    # Generate random amounts between 0 and 1,000,000 in dollars
    amount = factory.LazyAttribute(
        lambda o: FuzzyInteger(o.min_amount, o.max_amount).fuzz()
    )

    @staticmethod
    def with_code(code: CurrencyCode, **kwargs) -> Currency:
        """Create a Currency instance with a specific currency code"""
        return Currency(code=code, **kwargs)

    @staticmethod
    def dollars(amount: float, **kwargs) -> Currency:
        """Create a USD Currency instance with the specified dollar amount"""
        return Currency.from_base_units(CurrencyCode.USD, amount)


class BaseSalaryChangeFactory(factory.Factory):
    class Meta:
        model = BaseSalaryChange

    effective_date = factory.Faker("date_between", start_date="-3y", end_date="-1m")
    annual_amount = factory.SubFactory(CurrencyFactory)
    bonus_percentage = factory.Faker(
        "pydecimal", left_digits=0, right_digits=3, positive=True
    )
    reason = factory.Faker("sentence", nb_words=3)


class BonusPaymentFactory(factory.Factory):
    class Meta:
        model = BonusPayment

    date = factory.Faker("date_between", start_date="-1y", end_date="-1m")
    amount = factory.SubFactory(CurrencyFactory)
    type = factory.Faker("word")
    description = factory.Faker("sentence", nb_words=5)


class SigningBonusFactory(factory.Factory):
    class Meta:
        model = SigningBonus

    class Params:
        min_amount = 0
        max_amount = 1_000_000_00

    payment_date = factory.Faker("date_between", start_date="-2y", end_date="now")
    amount = factory.SubFactory(
        CurrencyFactory,
        min_amount=factory.SelfAttribute("..min_amount"),
        max_amount=factory.SelfAttribute("..max_amount"),
    )
    conditions = factory.Faker("sentence", nb_words=5)


class StockGrantFactory(factory.Factory):
    class Meta:
        model = StockGrant

    grant_date = factory.Faker("date_between", start_date="-2y", end_date="now")
    total_shares = factory.Faker("pyint", min_value=1000, max_value=100_000)
    price_per_share = factory.SubFactory(
        CurrencyFactory, amount=FuzzyInteger(1, 1000_00)
    )
    vesting_schedule_type = FuzzyChoice(VestingScheduleType)
    vesting_start_date = factory.Faker(
        "date_between", start_date=grant_date, end_date="now"
    )
    cliff_months = factory.Faker("pyint", min_value=0, max_value=12)
    vesting_period_months = factory.Faker("pyint", min_value=12, max_value=60)


class CompensationPackageFactory(factory.Factory):
    class Meta:
        model = CompensationPackage

    employee_id = factory.Faker("uuid4")
    start_date = factory.Faker("date_between", start_date="-3y", end_date="now")
    base_salary_history = factory.List(
        [factory.SubFactory(BaseSalaryChangeFactory) for _ in range(3)]
    )
    bonus_payments = factory.List(
        [factory.SubFactory(BonusPaymentFactory) for _ in range(3)]
    )
    signing_bonuses = factory.List(
        [factory.SubFactory(SigningBonusFactory) for _ in range(3)]
    )
    stock_grants = factory.List(
        [factory.SubFactory(StockGrantFactory) for _ in range(3)]
    )


class JobFactory(factory.Factory):
    class Meta:
        model = Job

    name = factory.Faker("sentence", nb_words=3)

    start_date = factory.Faker("date_between", start_date="-3y", end_date="now")
    end_date = factory.LazyAttribute(
        lambda o: Faker().date_between(start_date=o.start_date, end_date="now")
    )
    comp_package = factory.SubFactory(CompensationPackageFactory)


class JobIncomeFactory(factory.Factory):
    class Meta:
        model = JobIncome

    job = factory.SubFactory(JobFactory)
    start_date = factory.Faker("date_between", start_date="-3y", end_date="now")
    end_date = factory.LazyAttribute(
        lambda o: Faker().date_between(start_date=o.start_date, end_date="now")
    )
