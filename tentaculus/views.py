from django.db.models import Prefetch
from django.db.models.query_utils import subclasses
from django.shortcuts import render

from tentaculus.forms import SearchForm
from tentaculus.models import Item, Spell, Card, DndClass, SubClass, Source, Circle


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

    form = SearchForm(request.GET, initial={'circle_to': Circle.NINTH})

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
    subclass = request.GET.get('subclass')
    circle_from = int(request.GET.get('circle_from'))
    circle_to = int(request.GET.get('circle_to'))

    if dnd_class or (circle_from >=0 and circle_to >= 0):
        ### Блок обработки заклинаний
        cards = Spell.objects.filter(is_face_side=True, name__icontains=request.GET.get('name'))
        if subclass:
            ### Если известен сабкласс
            cards = cards.prefetch_related(
                Prefetch('class_race', queryset=Source.objects.filter(id__in=(dnd_class, subclass)))
            ).filter(class_race__in=(dnd_class, subclass))

            form.fields['subclass'].initial = subclass
        elif dnd_class:
            ### Если известен класс
            cards = cards.prefetch_related(
                Prefetch('class_race', queryset=Source.objects.filter(id=dnd_class))
            ).filter(class_race=dnd_class)

            class_object = DndClass.objects.get(id=dnd_class)
            form.fields['subclass'].queryset = class_object.subclasses.all()
        else:
            ### Все классы
            pass

        if circle_from >=0 and circle_to >= 0:
            cards = cards.filter(circle__gte=circle_from, circle__lte=circle_to)

    else:
        ### Блок обработки всего вместе
        cards = Card.objects.filter(is_face_side=True, name__icontains=request.GET.get('name'))

    context = {
        'cards': cards,
        'form': form,
    }

    return render(request, 'cards.html', context)


def load_subclasses(request):
    class_id = request.GET.get('class')
    subclasses = DndClass.objects.get(id=class_id).subclasses.all()
    return render(request, 'tentaculus/subclasses.html', {'subclasses': subclasses})


def test(request):
    form = SearchForm(request.GET)

    cards = Card.objects.filter(is_face_side=True)
    context = {
        'cards': [card for card in cards],
        'form': form,
    }

    return render(request, 'cards.html', context)
