import pytest
from internship.models import InternshipApplication


@pytest.fixture
def internship_application(user):
    return InternshipApplication.objects.create(applicant=user)
