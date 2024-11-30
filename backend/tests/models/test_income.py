from datetime import date
from networth.models.income import Income, JobIncome

from .test_util.factories import JobFactory


def test_multiple_job_income():
    job1 = JobFactory()
    job2 = JobFactory()

    job_income_1 = JobIncome(
        job=job1, start_date=date(2023, 1, 1), end_date=date(2025, 1, 1)
    )
    job_income_2 = JobIncome(
        job=job2, start_date=date(2024, 1, 1), end_date=date(2025, 1, 1)
    )

    income = Income(job_income=[job_income_1, job_income_2])

    total_1 = job_income_1.calculate_total_income(
        start_date=date(2023, 1, 1), end_date=date(2025, 1, 1)
    )
    total_2 = job_income_2.calculate_total_income(
        start_date=date(2023, 1, 1), end_date=date(2025, 1, 1)
    )

    grand_total = income.calculate_total_income(
        start_date=date(2023, 1, 1), end_date=date(2025, 1, 1)
    )

    assert round(grand_total, 2) == round(total_1 + total_2, 2)
