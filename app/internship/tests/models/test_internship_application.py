import pytest
from accounts.models import Country
from django.conf import settings


@pytest.mark.django_db
def test_is_recommended(internship_application, recommended_trainee_profile):
    assert internship_application.is_recommended is True


@pytest.mark.django_db
def test_is_recommended_without_preferable_citizenship(
    internship_application, recommended_trainee_profile
):
    recommended_trainee_profile.citizenship = Country.objects.exclude(
        id=settings.PREFERABLE_CITIZENSHIP_ID
    ).first()
    recommended_trainee_profile.save()
    internship_application.set_recommendation()  # for recommendation calculation
    assert internship_application.is_recommended is False


@pytest.mark.django_db
def test_is_recommended_without_required_university_years(
    internship_application, recommended_trainee_profile
):
    # Create a test education object that does not satisfy the university criteria
    education = recommended_trainee_profile.educations.first()
    education.end_year = education.start_year + settings.REQUIRED_UNIVERSITY_YEARS - 1
    education.save()
    internship_application.set_recommendation()  # for recommendation calculation
    assert internship_application.is_recommended is False
