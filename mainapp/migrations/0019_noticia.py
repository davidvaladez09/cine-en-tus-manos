# Generated by Django 5.0.6 on 2024-07-02 03:43

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0018_alter_critica_calificacion'),
    ]

    operations = [
        migrations.CreateModel(
            name='Noticia',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('ruta_foto_critica', models.ImageField(upload_to='review/')),
                ('nombre', models.CharField(max_length=255)),
                ('descripcion', models.TextField()),
                ('datetime', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
