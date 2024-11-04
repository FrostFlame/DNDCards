from django.urls import path

from . import views

urlpatterns = [
    path('', views.all_cards, name='all_cards'),
    path('spells', views.all_spells, name='all_spells'),
    path('items', views.all_items, name='all_items'),
    path('test', views.test, name='test'),
]
