# Generated by Django 5.0.6 on 2024-05-29 05:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0006_user_is_active_user_is_staff_user_is_superuser_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='descripcion',
            field=models.CharField(default=1, max_length=280),
            preserve_default=False,
        ),
    ]
