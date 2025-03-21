# Generated by Django 4.1.7 on 2025-03-14 20:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tentaculus', '0003_remove_item_item_types_item_item_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='second_side_item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tentaculus.item'),
        ),
        migrations.AddField(
            model_name='spell',
            name='second_side_item',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tentaculus.item'),
        ),
        migrations.AlterField(
            model_name='item',
            name='second_side_spell',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tentaculus.spell'),
        ),
    ]
