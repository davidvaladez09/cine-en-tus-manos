# Generated by Django 5.0.6 on 2024-05-30 20:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0012_alter_critica_categoria_genero_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='critica',
            old_name='tipo',
            new_name='tipo_id',
        ),
        migrations.RemoveField(
            model_name='critica',
            name='id_foto_critica',
        ),
        migrations.AddField(
            model_name='critica',
            name='ruta_foto_critica',
            field=models.ImageField(default=1, upload_to='review/'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='critica',
            name='ano',
            field=models.CharField(max_length=4),
        ),
        migrations.AlterField(
            model_name='critica',
            name='categoria_genero',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='critica',
            name='director',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='critica',
            name='donde_ver',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='critica',
            name='escritor',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='critica',
            name='link_trailer',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='critica',
            name='no_capitulos',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='critica',
            name='nombre',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='critica',
            name='nombre_espanol',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='critica',
            name='reparto',
            field=models.CharField(max_length=255),
        ),
    ]
