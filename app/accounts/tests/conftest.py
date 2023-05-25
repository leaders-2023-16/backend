import pytest
from accounts.models import User
from internship.models import Qualification, TestTask, Vacancy, VacancyResponse


@pytest.fixture
def user2():
    return User.objects.create_user(
        username="user2@user.com",
        password="password",
        first_name="Johny",
        last_name="Doel",
    )


@pytest.fixture
def test_task(department):
    return TestTask.objects.create(
        title="Simple test task",
        type=TestTask.Type.TEXT,
        description="Test description",
        department=department,
    )


@pytest.fixture
def qualification():
    return Qualification.objects.create(name="Qualification 1")


@pytest.fixture
def published_vacancy(
    qualification, curator, mentor, personnel, direction, department, test_task
):
    vacancy = Vacancy.objects.create(
        name="Test vacancy",
        description="Test description",
        status=Vacancy.Status.PUBLISHED,
        mentor=mentor,
        owner=personnel,
        direction=direction,
        department=department,
        test_task=test_task,
    )
    vacancy.required_qualifications.add(qualification)
    return vacancy


@pytest.fixture
def vacancy_response(published_vacancy, trainee, trainee_profile):
    return VacancyResponse.objects.create(
        vacancy=published_vacancy, applicant=trainee_profile, text_answer="Answer"
    )
