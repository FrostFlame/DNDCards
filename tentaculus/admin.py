from django.contrib import admin
from polymorphic.admin import (
    PolymorphicParentModelAdmin,
    PolymorphicChildModelAdmin, PolymorphicChildModelFilter,
)

from tentaculus.models import (
    Attunement,
    Book,
    Card,
    CastTime,
    ClassRace,
    Distance,
    Duration,
    Item,
    ItemType,
    School,
    Spell,
)


# Register your models here.

class CardChildAdmin(PolymorphicChildModelAdmin):
    base_model = Card


@admin.register(Spell)
class SpellAdmin(CardChildAdmin):
    base_model = Spell
    show_in_index = True


@admin.register(Item)
class ItemAdmin(CardChildAdmin):
    base_model = Item
    show_in_index = True


@admin.register(Card)
class CardParentAdmin(PolymorphicParentModelAdmin):
    base_model = Card
    child_models = (Spell, Item)
    list_filter = (PolymorphicChildModelFilter,)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    pass


@admin.register(CastTime)
class CastTimeAdmin(admin.ModelAdmin):
    pass


@admin.register(Distance)
class DistanceAdmin(admin.ModelAdmin):
    pass


@admin.register(Duration)
class DurationAdmin(admin.ModelAdmin):
    pass


@admin.register(ClassRace)
class ClassRaceAdmin(admin.ModelAdmin):
    pass


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    pass


@admin.register(Attunement)
class AttunementAdmin(admin.ModelAdmin):
    pass

@admin.register(ItemType)
class ItemTypeAdmin(admin.ModelAdmin):
    pass
