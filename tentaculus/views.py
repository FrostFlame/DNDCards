from django.shortcuts import render

from tentaculus.forms import SearchForm
from tentaculus.models import Item, Spell, Card


# Create your views here.


def all_cards(request):
    """
    Вообще все карты
    """

    form = SearchForm(request.GET)

    cards = Card.objects.filter(is_face_side=True)
    context = {
        'cards': cards,
        'form': form,
    }
    return render(request, 'cards.html', context)


def all_spells(request):
    """
    Все заклинания
    """

    form = SearchForm(request.GET)

    spells = Spell.objects.filter(is_face_side=True)
    context = {
        'cards': spells,
        'form': form,
    }
    return render(request, 'cards.html', context)


def all_items(request):
    """
    Все предметы
    """

    form = SearchForm(request.GET)

    items = Item.objects.filter(is_face_side=True)
    context = {
        'cards': items,
        'form': form,
    }
    return render(request, 'cards.html', context)


def search(request):
    """
    Поиск
    """

    form = SearchForm(request.GET)
    dnd_class = request.GET.get('dnd_class')
    if dnd_class:
        cards = Spell.objects.filter(is_face_side=True, name__icontains=request.GET.get('name'), class_race=dnd_class)
    else:
        cards = Card.objects.filter(is_face_side=True, name__icontains=request.GET.get('name'))
    context = {
        'cards': cards,
        'form': form,
    }

    return render(request, 'cards.html', context)


def test(request):
    form = SearchForm(request.GET)

    cards = Card.objects.filter(is_face_side=True)
    context = {
        'cards': [card for card in cards],
        'form': form,
    }

    return render(request, 'cards.html', context)
