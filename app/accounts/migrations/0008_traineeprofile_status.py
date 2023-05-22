# Generated by Django 4.2.1 on 2023-05-22 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0007_user_department"),
    ]

    operations = [
        migrations.AddField(
            model_name="traineeprofile",
            name="status",
            field=models.CharField(
                choices=[
                    ("PASSED", "Passed"),
                    ("IN_PROGRESS", "In progress of qualification"),
                    ("FAILED", "Did not pass qualification"),
                ],
                default="IN_PROGRESS",
                max_length=11,
            ),
        ),
    ]
