# Generated by Django 5.0 on 2024-02-28 13:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("airadio", "0010_positionprompts_station_topicprompts_station"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="positionprompts",
            options={
                "ordering": ["station", "position"],
                "verbose_name": "Position Prompt",
                "verbose_name_plural": "Position Prompts",
            },
        ),
    ]