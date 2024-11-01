from django.urls import path

from . import views

urlpatterns = [
    path('', views.all_cards, name='all_cards'),
    path('test', views.test, name='test'),
]
