# Generated by Django 3.2.25 on 2024-12-23 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tentaculus', '0009_book_title_eng'),
    ]

    operations = [
        migrations.AlterField(
            model_name='casttime',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]
