from django.db import models


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


class SearchType(models.TextChoices):
    ALL = 'Всё', 'Всё'
    SPELLS = 'Заклинания', 'Заклинания'
    ITEMS = 'Предметы', 'Предметы'
    ABILITIES = 'Способности', 'Способности'


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


class Card(models.Model):
    class Meta:
        abstract = True

    title_eng = models.CharField(max_length=100)
    name = models.CharField(max_length=100, unique=True)
    second_side_spell = models.ForeignKey('Spell', on_delete=models.SET_NULL, blank=True, null=True)
    second_side_item = models.ForeignKey('Item', on_delete=models.SET_NULL, blank=True, null=True)
    is_face_side = models.BooleanField(default=True)
    name_font_size = models.DecimalField(default=14, max_digits=4, decimal_places=2)
    font_size = models.DecimalField(default=11.25, max_digits=4, decimal_places=2)
    description = models.TextField()
    footer_font_size = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    book = models.ForeignKey('Book', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def __len__(self):
        return 1 if self.is_face_side and not self.second_side else 2

    @property
    def second_side(self):
        if self.second_side_spell:
            return self.second_side_spell
        elif self.second_side_item:
            return self.second_side_item


class Spell(Card):
    style = 'Default'
    is_ability = models.BooleanField(default=False)
    circle = models.IntegerField(choices=Circle.choices, blank=True, null=True)
    is_ritual = models.BooleanField(default=False)
    cast_time = models.ForeignKey('CastTime', on_delete=models.CASCADE, blank=True, null=True)
    distance = models.ForeignKey('Distance', on_delete=models.CASCADE, blank=True, null=True)
    components = models.TextField(choices=Component.choices, blank=True, null=True)
    duration = models.ForeignKey('Duration', on_delete=models.CASCADE, blank=True, null=True)
    material_component = models.CharField(max_length=100, null=True, blank=True)
    classes = models.ManyToManyField('DndClass', blank=True)
    subclasses = models.ManyToManyField('Subclass', blank=True)
    race = models.ManyToManyField('Race', blank=True)
    subrace = models.ManyToManyField('SubRace', blank=True)
    school = models.ManyToManyField('School', related_name='spells')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.second_side_spell:
            if '*' not in self.name:
                if self.second_side_spell.name == self.name:
                    try:
                        second_side_spell = Spell.objects.get(name=self.name + '*')
                        self.second_side_spell = second_side_spell
                    except Spell.DoesNotExist:
                        self.second_side_spell = None
            else:
                self.second_side_spell = None
        return super(Spell, self).save(*args, **kwargs)


class Item(Card):
    style = 'Item'
    attunement = models.ForeignKey('Attunement', on_delete=models.CASCADE)
    item_type = models.ForeignKey('ItemType', related_name='items', null=True, on_delete=models.SET_NULL)
    rarity = models.TextField(choices=Rarity.choices)
    requirements = models.ForeignKey('ItemRequirements', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class CastTime(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Distance(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


class Duration(models.Model):
    name = models.CharField(max_length=40, unique=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        return super(Duration, self).save(*args, **kwargs)


class Book(models.Model):
    title = models.CharField(max_length=100, unique=True)
    title_eng = models.CharField(max_length=100, unique=True)
    short = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.title


class Source(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        ordering = ('name',)


class DndClass(Source):
    style = models.CharField(max_length=20, unique=True, null=True, blank=True)


class SubClass(Source):
    base_class = models.ForeignKey(DndClass, related_name='subclasses', on_delete=models.CASCADE, blank=True, null=True)

    @property
    def style(self):
        return self.base_class.style  # noqa

    def __str__(self):
        return f'{self.name} ({self.base_class.name})'


class Race(Source):
    style = models.CharField(max_length=20, unique=True, null=True, blank=True)


class SubRace(Source):
    base_race = models.ForeignKey(Race, related_name='subraces', on_delete=models.CASCADE, blank=True, null=True)


class School(models.Model):
    name = models.CharField(max_length=20, unique=True)
    priority = models.IntegerField()

    def __str__(self):
        return self.name


class Attunement(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class ItemType(models.Model):
    name = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name


class ItemRequirements(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
