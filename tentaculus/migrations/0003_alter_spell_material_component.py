# Generated by Django 4.1.7 on 2024-11-04 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tentaculus', '0002_attunement_card_casttime_classrace_distance_duration_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spell',
            name='material_component',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
