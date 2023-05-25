# Generated by Django 4.2.1 on 2023-05-24 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0009_traineeprofile_cv_score_traineeprofile_test_score"),
    ]

    operations = [
        migrations.AlterField(
            model_name="education",
            name="degree",
            field=models.CharField(
                choices=[
                    ("Bachelor", "Bachelor"),
                    ("Master", "Master"),
                    ("Doctorate", "Doctorate"),
                ],
                max_length=100,
                null=True,
                verbose_name="Degree",
            ),
        ),
    ]