# Generated by Django 4.2.8 on 2024-01-03 15:53

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("airadio", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="dashboardtopsongs",
            name="twitter",
        ),
        migrations.AddField(
            model_name="dashboardtopsongs",
            name="instagram",
            field=models.CharField(
                blank=True, max_length=200, null=True, verbose_name="Instagram Account"
            ),
        ),
    ]