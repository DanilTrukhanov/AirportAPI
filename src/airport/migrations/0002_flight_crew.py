# Generated by Django 5.1.6 on 2025-02-24 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("airport", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="flight",
            name="crew",
            field=models.ManyToManyField(
                blank=True, related_name="flights", to="airport.crew"
            ),
        ),
    ]
