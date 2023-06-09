# Generated by Django 4.2.1 on 2023-05-27 14:06

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("internship", "0010_vacancy_schedule"),
    ]

    operations = [
        migrations.AlterField(
            model_name="vacancy",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("rejected", "Rejected"),
                    ("published", "Published"),
                    ("closed", "Closed"),
                ],
                default="pending",
                max_length=50,
                verbose_name="Status",
            ),
        ),
        migrations.CreateModel(
            name="WorkPlace",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255, verbose_name="Name")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Created at"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Updated at"),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="Is active"),
                ),
                (
                    "mentor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="mentor_on",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Mentor",
                    ),
                ),
                (
                    "trainee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="work_on",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Trainee",
                    ),
                ),
                (
                    "vacancy",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="work_place",
                        to="internship.vacancy",
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Work places",
                "db_table": "attendance_work_place",
            },
        ),
    ]
