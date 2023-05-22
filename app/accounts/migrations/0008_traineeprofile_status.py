# Generated by Django 4.2.1 on 2023-05-22 16:20

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
                    ("P", "PASSED"),
                    ("I", "IN PROGRESS OF QUALIFICATION"),
                    ("F", "DID NOT PASS QUALIFICATION"),
                ],
                max_length=1,
                null=True,
            ),
        ),
    ]
