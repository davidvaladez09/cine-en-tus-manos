# Generated by Django 5.0.6 on 2024-05-30 21:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0013_rename_tipo_critica_tipo_id_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='critica',
            name='tipo_id',
        ),
        migrations.AddField(
            model_name='critica',
            name='tipo',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='criticas', to='mainapp.tipo'),
            preserve_default=False,
        ),
    ]
