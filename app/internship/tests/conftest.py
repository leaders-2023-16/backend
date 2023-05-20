import pytest
from internship.models import InternshipApplication


@pytest.fixture
def internship_application(user):
    internship = InternshipApplication.objects.create(applicant=user)
    internship.set_recommendation()
    return internship
