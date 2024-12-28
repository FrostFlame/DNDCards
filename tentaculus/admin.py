from django.contrib import admin
from polymorphic.admin import (
    PolymorphicParentModelAdmin,
    PolymorphicChildModelAdmin,
    PolymorphicChildModelFilter,
)

from tentaculus.models import (
    Attunement,
    Book,
    Card,
    CastTime,
    Distance,
    DndClass,
    Duration,
    Item,
    ItemType,
    Race,
    School,
    Source,
    Spell,
    SubClass,
    SubRace,
)


# Register your models here.

class CardChildAdmin(PolymorphicChildModelAdmin):
    base_model = Card
    save_as = True
    save_on_top = True


@admin.register(Spell)
class SpellAdmin(CardChildAdmin):
    base_model = Spell
    show_in_index = True
    list_display = ['name', 'circle']
    ordering = ('circle', 'name')
    search_fields = ['name']
    autocomplete_fields = ['second_side']


@admin.register(Item)
class ItemAdmin(CardChildAdmin):
    base_model = Item
    show_in_index = True
    search_fields = ['name']
    autocomplete_fields = ['second_side']


@admin.register(Card)
class CardParentAdmin(PolymorphicParentModelAdmin):
    base_model = Card
    child_models = (Spell, Item)
    list_filter = (PolymorphicChildModelFilter,)
    search_fields = ['name']
    autocomplete_fields = ['second_side']


class SourceChildAdmin(PolymorphicChildModelAdmin):
    base_model = Source


@admin.register(DndClass)
class DndClassAdmin(SourceChildAdmin):
    base_model = DndClass
    show_in_index = True


@admin.register(SubClass)
class SubClassAdmin(SourceChildAdmin):
    base_model = SubClass
    show_in_index = True


@admin.register(Race)
class RaceAdmin(SourceChildAdmin):
    base_model = Race
    show_in_index = True


@admin.register(SubRace)
class SubRaceAdmin(SourceChildAdmin):
    base_model = SubRace
    show_in_index = True


@admin.register(Source)
class SourceParentAdmin(PolymorphicParentModelAdmin):
    base_model = Source
    child_models = (DndClass, SubClass, Race, SubRace)
    list_filter = (PolymorphicChildModelFilter,)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    pass


@admin.register(CastTime)
class CastTimeAdmin(admin.ModelAdmin):
    ordering = ('name',)


@admin.register(Distance)
class DistanceAdmin(admin.ModelAdmin):
    ordering = ('name',)


@admin.register(Duration)
class DurationAdmin(admin.ModelAdmin):
    ordering = ('name',)


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    ordering = ('name',)


@admin.register(Attunement)
class AttunementAdmin(admin.ModelAdmin):
    pass

@admin.register(ItemType)
class ItemTypeAdmin(admin.ModelAdmin):
    pass
