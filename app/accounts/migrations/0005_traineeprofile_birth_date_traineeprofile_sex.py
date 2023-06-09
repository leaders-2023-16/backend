# Generated by Django 4.2.1 on 2023-05-19 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_remove_education_end_date_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="traineeprofile",
            name="birth_date",
            field=models.DateField(blank=True, null=True, verbose_name="Birth date"),
        ),
        migrations.AddField(
            model_name="traineeprofile",
            name="sex",
            field=models.CharField(
                blank=True,
                choices=[("M", "MALE"), ("F", "FEMALE")],
                max_length=1,
                null=True,
                verbose_name="Sex",
            ),
        ),
    ]
