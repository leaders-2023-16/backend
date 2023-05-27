import pytest
from attendance.models import Report
from django.urls import reverse


@pytest.mark.django_db
def test_create_report(api_client, work_place, trainee, mentor):
    url = reverse("reports-list")

    response = api_client.post(
        url, data={"status": Report.StatusType.ATTENDED, "date": "2023-05-27"}
    )
    assert response.status_code == 201
    assert Report.objects.count() == 1
    report = Report.objects.first()
    assert report.status == Report.StatusType.ATTENDED
    assert report.applicant == trainee
    assert report.work_place == work_place
    assert report.is_approved is False


@pytest.mark.django_db
def test_update_report(mentor_client, report, mentor):
    url = reverse("reports-detail", args=[report.id])

    response = mentor_client.patch(url, data={"is_approved": True})
    assert response.status_code == 200
    assert Report.objects.count() == 1
    actual_report = Report.objects.first()
    assert actual_report.status == report.status
    assert actual_report.applicant == report.applicant
    assert actual_report.work_place == report.work_place
    assert actual_report.is_approved is True
    assert actual_report.approved_by == mentor
