from django.db.models import Prefetch
from django.db.models.query_utils import subclasses, Q
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
    style = ''
    source_class = ''
    source_subclass = ''
    schools = request.GET.getlist('schools')
    books = request.GET.getlist('books')
    cast_times = request.GET.getlist('cast_times')

    if dnd_class or (circle_from >=0 and circle_to >= 0) or schools or cast_times:
        ### Блок обработки заклинаний
        cards = Spell.objects.filter(is_face_side=True, name__icontains=request.GET.get('name'))
        if dnd_class:
            ### Если известен только класс, а сабкласс не указан
            filters = Q(classes=dnd_class)
            class_instance = DndClass.objects.get(id=dnd_class)
            form.fields['subclass'].queryset = class_instance.subclasses.all()
            source_class = class_instance.name

            if subclass:
                ### Если известен ещё и сабкласс
                source_subclass = SubClass.objects.get(id=subclass).name
                filters = filters | Q(subclasses=subclass)

                form.fields['subclass'].initial = subclass
            cards = cards.filter(filters).distinct()

            style = class_instance.style

        if circle_from >=0 and circle_to >= 0:
            cards = cards.filter(circle__gte=circle_from, circle__lte=circle_to)

        if schools:
            cards = cards.filter(school__in=schools)

        if cast_times:
            cards = cards.filter(cast_time__in=cast_times)

        for card in cards:
            card.source = (
                source_subclass
                if subclass and int(subclass) in card.subclasses.values_list('id', flat=True)
                else source_class
            )

    else:
        ### Блок обработки всего вместе
        cards = Card.objects.filter(is_face_side=True, name__icontains=request.GET.get('name'))

    if books:
        cards = cards.filter(book__in=books)

    context = {
        'cards': cards,
        'form': form,
        'style': style,
    }

    return render(request, 'cards.html', context)


def load_subclasses(request):
    class_id = request.GET.get('class')
    if class_id:
        dnd_subclasses = DndClass.objects.get(id=class_id).subclasses.all()
    else:
        dnd_subclasses = SubClass.objects.none()
    return render(request, 'tentaculus/subclasses.html', {'subclasses': dnd_subclasses})


def test(request):
    form = SearchForm(request.GET)

    cards = Card.objects.filter(is_face_side=True)
    context = {
        'cards': [card for card in cards],
        'form': form,
    }

    return render(request, 'cards.html', context)
