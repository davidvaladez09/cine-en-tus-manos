# Generated by Django 5.0.6 on 2024-05-28 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fotosperfil',
            name='direccion',
            field=models.ImageField(upload_to='profiles/'),
        ),
    ]
