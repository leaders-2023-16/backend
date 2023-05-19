# Generated by Django 4.2.1 on 2023-05-18 21:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_add_user_roles"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="education",
            name="end_date",
        ),
        migrations.RemoveField(
            model_name="education",
            name="start_date",
        ),
        migrations.AddField(
            model_name="education",
            name="end_year",
            field=models.IntegerField(blank=True, null=True, verbose_name="End year"),
        ),
        migrations.AddField(
            model_name="education",
            name="start_year",
            field=models.IntegerField(default=2023, verbose_name="Start year"),
            preserve_default=False,
        ),
    ]
