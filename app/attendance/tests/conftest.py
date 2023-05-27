import pytest
from attendance.models import Report
from django.utils import timezone
from internship.models import WorkPlace


@pytest.fixture
def work_place(trainee, mentor, department):
    return WorkPlace.objects.create(
        name="Test", trainee=trainee, mentor=mentor, department=department
    )


@pytest.fixture
def report(trainee, work_place):
    return Report.objects.create(
        applicant=trainee, work_place=work_place, date=timezone.now().date()
    )
