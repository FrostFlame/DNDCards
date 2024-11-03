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

class Component(models.TextChoices):
    V = 'V', 'В'
    S = 'S', 'С'
    M = 'M', 'М'
    VS = 'VS', 'В, С'
    VM = 'VM', 'В, М'
    SM = 'SM', 'С, М'
    VSM = 'VSM', 'В, С, М'

class Card(models.Model):
    title_eng = models.CharField(max_length=100)
    title_font_size = models.DecimalField(max_digits=4, decimal_places=2)
    name = models.CharField(max_length=100)
    font_size = models.DecimalField(max_digits=4, decimal_places=2)
    description = models.TextField()
    footer_font_size = models.DecimalField(max_digits=4, decimal_places=2)
    book = models.ForeignKey('Book', on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Spell(Card):
    circle = models.IntegerField(choices=Circle.choices)
    cast_time = models.ForeignKey('CastTime', on_delete=models.CASCADE)
    distance = models.ForeignKey('Distance', on_delete=models.CASCADE)
    components = models.TextField(choices=Component.choices)
    duration = models.ForeignKey('Duration', on_delete=models.CASCADE)
    material_component = models.CharField(max_length=100)
    class_race = models.ManyToManyField('ClassRace', related_name='spells')
    school = models.ManyToManyField('School', related_name='spells')

    def __str__(self):
        return self.name


class CastTime(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

class Distance(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

class Duration(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=100)
    short = models.CharField(max_length=10)

    def __str__(self):
        return self.title

class ClassRace(models.Model):
    name = models.CharField(max_length=20)
    style = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class School(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name
