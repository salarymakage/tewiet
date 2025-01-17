# Generated by Django 5.0.6 on 2024-08-01 03:27

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Student",
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
                ("FirstName", models.CharField(max_length=100)),
                ("LastName", models.CharField(max_length=100)),
                ("Gender", models.CharField(max_length=10)),
                ("MedicalCondition", models.CharField(max_length=255)),
                ("Address", models.CharField(max_length=255)),
                ("EmergencyContact", models.CharField(max_length=20)),
            ],
        ),
    ]
