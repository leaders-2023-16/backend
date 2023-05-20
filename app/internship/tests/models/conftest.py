import pytest
from accounts.models import Education
from django.conf import settings
from django.utils import timezone


@pytest.fixture
def recommended_trainee_profile(internship_application, user):
    education = Education.objects.create(
        profile=internship_application.applicant.trainee_profile,
        start_year=timezone.now().date().year
        - settings.REQUIRED_UNIVERSITY_YEARS,  # Required years ago
        type=Education.Type.UNIVERSITY,
        degree=Education.DegreeType.BACHELOR,
    )
    user.trainee_profile.educations.add(education)
    user.trainee_profile.citizenship_id = settings.PREFERABLE_CITIZENSHIP_ID
    user.trainee_profile.save()
    internship_application.set_recommendation()  # for recommendation calculation
    return user.trainee_profile
