from django.db import models
from polymorphic.models import PolymorphicModel


# Create your models here.

class Circle(models.IntegerChoices):
    INITIAL = -1, '---'
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
    V = 'В', 'В'
    S = 'С', 'С'
    M = 'М', 'М'
    VS = 'В, С', 'В, С'
    VM = 'В, М', 'В, М'
    SM = 'С, М', 'С, М'
    VSM = 'В, С, М', 'В, С, М'

class Rarity(models.TextChoices):
    COMMON = 'Обычный', 'Обычный'
    UNCOMMON = 'Необычный', 'Необычный'
    RARE = 'Редкий', 'Редкий'
    VERY_RARE =  'Очень редкий',  'Очень редкий'
    LEGENDARY = 'Легендарный', 'Легендарный'
    ARTIFACT = 'Артифакт', 'Артифакт'


class Card(PolymorphicModel):
    title_eng = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    name_font_size = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    font_size = models.DecimalField(default=11.25, max_digits=4, decimal_places=2)
    description = models.TextField()
    footer_font_size = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    second_side = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    is_face_side = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def __len__(self):
        return 1 if self.is_face_side and not self.second_side else 2


class Spell(Card):
    style = 'Default'
    circle = models.IntegerField(choices=Circle.choices)
    is_ritual = models.BooleanField(default=False)
    cast_time = models.ForeignKey('CastTime', on_delete=models.CASCADE)
    distance = models.ForeignKey('Distance', on_delete=models.CASCADE)
    components = models.TextField(choices=Component.choices)
    duration = models.ForeignKey('Duration', on_delete=models.CASCADE)
    material_component = models.CharField(max_length=100, null=True, blank=True)
    classes = models.ManyToManyField('DndClass', null=True, blank=True)
    subclasses = models.ManyToManyField('Subclass', null=True, blank=True)
    race = models.ManyToManyField('Race', null=True, blank=True)
    subrace = models.ManyToManyField('SubRace', null=True, blank=True)
    school = models.ManyToManyField('School', related_name='spells')

    def __str__(self):
        return self.name

    def get_school(self):
        return self.school.order_by('priority')[0]


class Item(Card):
    style = 'Item'
    attunement = models.ForeignKey('Attunement', on_delete=models.CASCADE)
    item_types = models.ManyToManyField('ItemType', related_name='items')
    rarity = models.TextField(choices=Rarity.choices)

    def __str__(self):
        return self.name

    def types(self):
        return ', '.join([item_type.name for item_type in self.item_types.all()])

class CastTime(models.Model):
    name = models.CharField(max_length=100)

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
    title_eng = models.CharField(max_length=100)
    short = models.CharField(max_length=10)

    def __str__(self):
        return self.title

class Source(PolymorphicModel):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)

class DndClass(Source):
    style = models.CharField(max_length=20, null=True, blank=True)

class SubClass(Source):
    base_class = models.ForeignKey(DndClass, related_name='subclasses', on_delete=models.CASCADE, blank=True, null=True)

    @property
    def style(self):
        return self.base_class.style  # noqa

    def __str__(self):
        return f'{self.name} ({self.base_class.name})'

class Race(Source):
    style = models.CharField(max_length=20, null=True, blank=True)

class SubRace(Source):
    base_race = models.ForeignKey(Race, related_name='subraces', on_delete=models.CASCADE, blank=True, null=True)

class School(models.Model):
    name = models.CharField(max_length=20)
    priority = models.IntegerField()

    def __str__(self):
        return self.name

class Attunement(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class ItemType(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name
