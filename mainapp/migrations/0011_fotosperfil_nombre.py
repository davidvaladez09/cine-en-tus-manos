# Generated by Django 5.0.6 on 2024-05-29 19:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0010_permisos_alter_user_permisos'),
    ]

    operations = [
        migrations.AddField(
            model_name='fotosperfil',
            name='nombre',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
    ]
