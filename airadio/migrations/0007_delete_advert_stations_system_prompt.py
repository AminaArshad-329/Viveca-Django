# Generated by Django 4.2.8 on 2024-01-18 23:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('airadio', '0006_library_mark_clean'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Advert',
        ),
        migrations.AddField(
            model_name='stations',
            name='system_prompt',
            field=models.TextField(blank=True, null=True),
        ),
    ]