from django.db import models

# Create your models here.

class Circle(models.IntegerChoices):
    CANTRIP = 0, 'Заговор'
    FIRST = 1, '1'
    SECOND = 2, '2'
    THIRD = 3, '3'
    FOURTH = 4, '4'
    FIFTH = 5, '5'
    SIXTH = 6, '6'
    SEVENTH = 7, '7'
    EIGHTS = 8, '8'
    NINTH = 9, '9'


class CastTime(models.TextChoices):
    ACTION = 'action', '1 действие'
    BONUS_ACTION = 'bonus action', '1 бонусное действие'
    REACTION = 'reaction', '1 реакция'
    MINUTES_10 = '10 minutes', '10 минут'


class Distance(models.TextChoices):
    SELF = 'self', 'На себя'
    TOUCH = 'touch', 'Касание'


class Component(models.TextChoices):
    V = 'V', 'В'
    S = 'S', 'С'
    M = 'M', 'М'
    VS = 'VS', 'В, С'
    VM = 'VM', 'В, М'
    SM = 'SM', 'С, М'
    VSM = 'VSM', 'В, С, М'


class Duration(models.TextChoices):
    instant = 'instant', 'Мгновенно'
    minute = '1 minute', '1 минута'


class School(models.TextChoices):
    ABJURATION = 'Ограждение'
    BIOMANCY = 'Биомантия'
    CHRONOMANCY = 'Хрономантия'
    CONJURATION = 'Вызов'
    DIVINATION = 'Прорицание'
    GRAVITURGY = 'Гравитургия'
    ENCHANTMENT = 'Очарование'
    EVOCATION = 'Воплощение'
    HEMOCRAFT = 'Гемокрафт'
    NECROMANCY = 'Некромантия'
    TRANSMUTATION = 'Преобразование'


class Book(models.Model):
    title = models.CharField(max_length=100)
    short = models.CharField(max_length=10)


class Card(models.Model):
    style = models.CharField(null=True, max_length=10)
    title = models.CharField(max_length=100)
    title_font_size = models.DecimalField(max_digits=4, decimal_places=2)
    name = models.CharField(max_length=100)
    font_size = models.DecimalField(max_digits=4, decimal_places=2)
    description = models.TextField()
    source = models.CharField(max_length=20)
    footer_font_size = models.DecimalField(max_digits=4, decimal_places=2)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)


    class Meta:
        abstract = True


class Spell(Card):
    circle = models.IntegerField(choices=Circle.choices)
    cast_time = models.TextField(choices=CastTime.choices)
    distance = models.TextField(choices=Distance.choices)
    components = models.TextField(choices=Component.choices)
    duration = models.TextField(choices=Duration.choices)
    material_component = models.CharField(max_length=100)
    school = models.TextField(choices=School.choices)
