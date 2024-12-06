from django.urls import path

from . import views

urlpatterns = [
    path('', views.all_cards, name='all_cards'),
    path('spells', views.all_spells, name='all_spells'),
    path('items', views.all_items, name='all_items'),
    path('search/', views.search, name='search'),
    path('cards_block/', views.cards_block, name='cards_block'),
    path('test', views.test, name='test'),

    path('ajax-subclasses', views.load_subclasses, name='ajax_load_subclasses'),
]
