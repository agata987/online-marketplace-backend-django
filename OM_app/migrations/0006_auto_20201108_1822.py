# Generated by Django 3.0.5 on 2020-11-08 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OM_app', '0005_auto_20201108_1802'),
    ]

    operations = [
        migrations.AlterField(
            model_name='joboffer',
            name='company',
            field=models.CharField(blank=True, max_length=30),
        ),
    ]