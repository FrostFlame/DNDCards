from django.shortcuts import render

from tentaculus.models import Item, Spell, Card


# Create your views here.


def all_cards(request):
    """
    Вообще все карты
    """
    cards = Card.objects.filter(is_face_side=True)
    context = {
        'cards': cards
    }
    return render(request, 'cards.html', context)


def all_spells(request):
    """
    Все заклинания
    """
    spells = Spell.objects.filter(is_face_side=True)
    context = {
        'cards': spells
    }
    return render(request, 'cards.html', context)


def all_items(request):
    """
    Все предметы
    """
    items = Item.objects.filter(is_face_side=True)
    context = {
        'cards': items
    }
    return render(request, 'cards.html', context)


def test(request):
    cards = Card.objects.filter(is_face_side=True)
    context = {
        'cards': [card for card in cards]
    }
    return render(request, 'cards.html', context)
