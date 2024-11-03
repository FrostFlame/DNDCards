# Generated by Django 4.1.7 on 2024-11-03 20:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tentaculus', '0011_alter_item_attunement'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attunement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
            ],
        ),
        migrations.AlterField(
            model_name='item',
            name='attunement',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tentaculus.attunement'),
        ),
    ]
