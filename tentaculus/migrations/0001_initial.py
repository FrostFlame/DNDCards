# Generated by Django 4.1.7 on 2024-11-03 12:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('short', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Spell',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('style', models.CharField(max_length=10, null=True)),
                ('title', models.CharField(max_length=100)),
                ('title_font_size', models.DecimalField(decimal_places=2, max_digits=4)),
                ('name', models.CharField(max_length=100)),
                ('font_size', models.DecimalField(decimal_places=2, max_digits=4)),
                ('description', models.TextField()),
                ('source', models.CharField(max_length=20)),
                ('footer_font_size', models.DecimalField(decimal_places=2, max_digits=4)),
                ('circle', models.IntegerField(choices=[(0, 'Заговор'), (1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'), (7, '7'), (8, '8'), (9, '9')])),
                ('cast_time', models.TextField(choices=[('action', '1 действие'), ('bonus action', '1 бонусное действие'), ('reaction', '1 реакция'), ('10 minutes', '10 минут')])),
                ('distance', models.TextField(choices=[('self', 'На себя'), ('touch', 'Касание')])),
                ('components', models.TextField(choices=[('В', 'V'), ('С', 'S'), ('М', 'M'), ('В, С', 'Vs'), ('В, М', 'Vm'), ('С, М', 'Sm'), ('В, С, М', 'Vsm')])),
                ('duration', models.TextField(choices=[('instant', 'Мгновенно'), ('1 minute', '1 минута')])),
                ('material_component', models.CharField(max_length=100)),
                ('school', models.TextField(choices=[('Ограждение', 'Abjuration'), ('Биомантия', 'Biomancy'), ('Хрономантия', 'Chronomancy'), ('Вызов', 'Conjuration'), ('Прорицание', 'Divination'), ('Гравитургия', 'Graviturgy'), ('Очарование', 'Enchantment'), ('Воплощение', 'Evocation'), ('Гемокрафт', 'Hemocraft'), ('Некромантия', 'Necromancy'), ('Преобразование', 'Transmutation')])),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tentaculus.book')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
