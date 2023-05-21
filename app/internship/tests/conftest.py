import pytest
from internship.models import InternshipApplication, Qualification, Vacancy


@pytest.fixture
def qualification():
    return Qualification.objects.create(name="Qualification 1")


@pytest.fixture
def internship_application(user):
    internship = InternshipApplication.objects.create(applicant=user)
    internship.set_recommendation()
    return internship


@pytest.fixture
def vacancy_data():
    return {
        "name": "Test Vacancy",
        "description": "Test Description",
        "status": Vacancy.Status.PUBLISHED,
    }


@pytest.fixture
def create_vacancy(vacancy_data):
    def _create_vacancy(qualification_names=None, **kwargs):
        data = vacancy_data.copy()
        data.update(kwargs)
        vacancy = Vacancy.objects.create(**data)

        if qualification_names:
            qualifications = []
            for qualification_name in qualification_names:
                qualification = Qualification.objects.create(name=qualification_name)
                qualifications.append(qualification)
            vacancy.required_qualifications.set(qualifications)

        return vacancy

    return _create_vacancy


@pytest.fixture
def not_published_vacancy(
    qualification, curator, mentor, personnel, direction, department
):
    vacancy = Vacancy.objects.create(
        name="Test vacancy",
        description="Test description",
        status=Vacancy.Status.PENDING,
        mentor=mentor,
        owner=personnel,
        direction=direction,
        department=department,
    )
    vacancy.required_qualifications.add(qualification)
    return vacancy
