import calendar
import datetime
from typing import Iterable

from django.conf import settings
from django.utils import timezone
from internship.models import Vacancy, WorkPlace
from openpyxl import load_workbook


def form_report(qs: Iterable[WorkPlace], date: datetime.date = None):
    if not date:
        date = timezone.now().date()
    example_workbook = load_workbook(
        settings.BASE_DIR / "attendance" / "report_template.xlsx"
    )
    example_sheet = example_workbook.active

    for report in qs:
        example_sheet.append(form_row(report, date))
    filename = f'report_{date.strftime("%Y-%m-%d")}.xlsx'
    example_workbook.save(filename)
    return filename


def form_row(workplace: WorkPlace, date: datetime.date):
    cells = [
        *form_full_name(workplace),
        f"{workplace.mentor.last_name} {workplace.mentor.last_name}",
        40 if workplace.vacancy.schedule == Vacancy.ScheduleType.FULL_TIME else 20,
        workplace.name,
    ]
    report_cells = form_date_cells(workplace, date)

    return [*cells, *report_cells]


def form_full_name(workplace: WorkPlace):
    return [workplace.trainee.last_name, workplace.trainee.first_name, ""]


def form_date_cells(workplace, date):
    def get_idx(date_):
        return date_.day if date_.day > 15 else date_.day - 1

    reports = workplace.reports.filter(
        date__year=date.year, date__month=date.month
    ).order_by("date")
    report_cells: list = [""] * 33

    for non_working_date in get_non_working_days(date.year, date.month):
        idx = get_idx(non_working_date)
        report_cells[idx] = "В"

    for report in reports:
        idx = get_idx(report.date)
        report_cells[idx] = report.report_status

    report_cells[15] = len(
        [status for status in report_cells[:15] if status not in ("+", "В")]
    )
    report_cells[32] = len(
        [status for status in report_cells[16:32] if status not in ("+", "В")]
    )
    return report_cells


def get_non_working_days(year, month):
    non_working_days = []

    # Get the number of days in the month
    num_days = calendar.monthrange(year, month)[1]

    for day in range(1, num_days + 1):
        try:
            date = datetime.date(year, month, day)
            if date.weekday() >= 5:  # Saturday is 5, Sunday is 6
                non_working_days.append(date)
        except ValueError:
            # Handles cases where the day is out of range for the given month
            pass
    return non_working_days
