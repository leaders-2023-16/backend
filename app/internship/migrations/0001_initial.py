# Generated by Django 4.2.1 on 2023-05-18 21:17

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("accounts", "0004_remove_education_end_date_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="InternshipApplication",
            fields=[
                (
                    "applicant",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        related_name="applications",
                        serialize=False,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("pending", "Pending"),
                            ("rejected", "Rejected"),
                            ("next_stage", "Approved for next stage"),
                            ("approved", "Approved"),
                        ],
                        max_length=255,
                        null=True,
                    ),
                ),
                ("status_changed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "status_changed_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="reviewed_applications",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]