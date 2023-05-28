import datetime

import pytest
from accounts.models import WorkExperience
from internship.tests.conftest import *  # noqa


@pytest.fixture
def work_experience1(trainee_profile):
    return WorkExperience.objects.create(
        profile=trainee_profile,
        employer="Company 1",
        position="Job 1",
        start_date=datetime.date(2020, 1, 1),
        end_date=datetime.date(2021, 1, 1),
    )


@pytest.fixture
def work_experience2(trainee_profile):
    return WorkExperience.objects.create(
        profile=trainee_profile,
        employer="Company 2",
        position="Job 2",
        start_date=datetime.date(2019, 1, 1),
        end_date=datetime.date(2020, 1, 1),
    )
