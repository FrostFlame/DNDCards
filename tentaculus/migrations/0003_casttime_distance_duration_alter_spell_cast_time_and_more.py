# Generated by Django 4.1.7 on 2024-11-03 12:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tentaculus', '0002_alter_spell_components'),
    ]

    operations = [
        migrations.CreateModel(
            name='CastTime',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Distance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Duration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=40)),
            ],
        ),
        migrations.AlterField(
            model_name='spell',
            name='cast_time',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tentaculus.casttime'),
        ),
        migrations.AlterField(
            model_name='spell',
            name='distance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tentaculus.distance'),
        ),
        migrations.AlterField(
            model_name='spell',
            name='duration',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tentaculus.duration'),
        ),
    ]
