from django.contrib import admin

from tentaculus.models import (
    Book,
    CastTime,
    ClassRace,
    Distance,
    Duration,
    School,
    Spell,
)


# Register your models here.

class SpellAdmin(admin.ModelAdmin):
    pass

class BookAdmin(admin.ModelAdmin):
    pass

class CastTimeAdmin(admin.ModelAdmin):
    pass

class DistanceAdmin(admin.ModelAdmin):
    pass

class DurationAdmin(admin.ModelAdmin):
    pass

class ClassRaceAdmin(admin.ModelAdmin):
    pass

class SchoolAdmin(admin.ModelAdmin):
    pass


admin.site.register(Spell, SpellAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(CastTime, CastTimeAdmin)
admin.site.register(Distance, DistanceAdmin)
admin.site.register(Duration, DurationAdmin)
admin.site.register(ClassRace, ClassRaceAdmin)
admin.site.register(School, SchoolAdmin)