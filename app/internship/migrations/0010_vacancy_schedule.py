# Generated by Django 4.2.1 on 2023-05-26 20:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("internship", "0009_vacancy_response"),
    ]

    operations = [
        migrations.AddField(
            model_name="vacancy",
            name="schedule",
            field=models.CharField(
                choices=[("full-time", "Full-time"), ("part-time", "Part-time")],
                default="full-time",
                max_length=50,
                verbose_name="Status",
            ),
        ),
    ]
