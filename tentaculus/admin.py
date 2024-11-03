from django.contrib import admin

from tentaculus.models import Spell, Book


# Register your models here.

class SpellAdmin(admin.ModelAdmin):
    pass

class BookAdmin(admin.ModelAdmin):
    pass


admin.site.register(Spell, SpellAdmin)
admin.site.register(Book, BookAdmin)