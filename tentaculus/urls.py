from django.urls import path

from . import views

urlpatterns = [
    path('', views.all_cards, name='all_cards'),
    path('spells', views.all_spells, name='all_spells'),
    path('items', views.all_items, name='all_items'),
    path('print_pdf/', views.print_pdf, name='print_pdf'),
    path('cards_block/', views.cards_block, name='cards_block'),

    path('ajax-subclasses', views.load_subclasses, name='ajax_load_subclasses'),
    path('ajax-subraces', views.load_subraces, name='ajax_load_subraces'),
    path('ajax-search', views.search, name='ajax_search'),
    path('ajax-locked-block', views.update_locked_block, name='ajax_locked_block'),
    path('ajax-convert-file', views.convert_file, name='convert_file'),

    path('test', views.test, name='test'),
]
