# Generated by Django 3.0.5 on 2020-11-08 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('OM_app', '0002_joboffer'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobOfferCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
            ],
        ),
    ]