from django.shortcuts import render

from tentaculus.models import Item, Spell


# Create your views here.


def all_cards(request):
    """
    Вообще все карты
    """
    items = Item.objects.all()
    spells = Spell.objects.all()
    context = {
        'cards': [*items, *spells]
    }
    return render(request, 'cards.html', context)


def all_spells(request):
    """
    Все заклинания
    """
    spells = Spell.objects.all()
    context = {
        'cards': spells
    }
    return render(request, 'cards.html', context)


def all_items(request):
    """
    Все предметы
    """
    items = Item.objects.all()
    context = {
        'cards': items
    }
    return render(request, 'cards.html', context)


def test(request):
    cards = Item.objects.all()
    context = {
        'cards': cards
    }
    return render(request, 'cards.html', context)
