# Generated by Django 3.0.5 on 2020-10-27 22:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('OM_app', '0007_delete_offerimage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='city',
            name='voivodeship_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cities', to='OM_app.Voivodeship'),
        ),
    ]
