from django.contrib import admin

from tentaculus.models import (
    Attunement,
    Book,
    CastTime,
    Distance,
    DndClass,
    Duration,
    Item,
    ItemType,
    Race,
    School,
    Spell,
    SubClass,
    SubRace,
    ItemRequirements,
)


# Register your models here.
@admin.register(Spell)
class SpellAdmin(admin.ModelAdmin):
    base_model = Spell
    show_in_index = True
    list_filter = ('circle',)
    list_display = ['name', 'circle', 'schools']
    ordering = ('circle', 'name')
    search_fields = ['name']
    autocomplete_fields = ['second_side_spell']
    save_as = True
    save_on_top = True

    def schools(self, obj):
        return ' '.join(obj.school.values_list('name', flat=True))


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    base_model = Item
    show_in_index = True
    search_fields = ['name']
    autocomplete_fields = ['second_side_spell']
    save_as = True
    save_on_top = True


@admin.register(DndClass)
class DndClassAdmin(admin.ModelAdmin):
    base_model = DndClass
    show_in_index = True


@admin.register(SubClass)
class SubClassAdmin(admin.ModelAdmin):
    base_model = SubClass
    show_in_index = True
    ordering = ('base_class__name', 'name',)
    list_filter = ('base_class__name',)


@admin.register(Race)
class RaceAdmin(admin.ModelAdmin):
    base_model = Race
    show_in_index = True


@admin.register(SubRace)
class SubRaceAdmin(admin.ModelAdmin):
    base_model = SubRace
    show_in_index = True


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'short')
    ordering = ('title', 'short')


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

@admin.register(ItemRequirements)
class ItemRequirementsAdmin(admin.ModelAdmin):
    pass
