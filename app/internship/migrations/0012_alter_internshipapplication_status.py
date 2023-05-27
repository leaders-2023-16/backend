# Generated by Django 4.2.1 on 2023-05-27 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("internship", "0011_workplace"),
    ]

    operations = [
        migrations.AlterField(
            model_name="internshipapplication",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("rejected", "Rejected"),
                    ("next_stage", "Approved for next stage"),
                    ("approved", "Approved"),
                    ("not_qualify", "Did not qualify for the application"),
                ],
                default="pending",
                max_length=255,
            ),
        ),
    ]
