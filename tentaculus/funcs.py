from django.db.models import Q

from tentaculus.forms import SearchForm
from tentaculus.models import Card, SubClass, DndClass, Spell


def get_cards_info(request):
    """
    Получение контекста по данным из реквеста
    """
    if request.method == 'GET':
        data = request.GET
    else:
        data = request.POST

    form = SearchForm(data)
    dnd_class = data.get('dnd_class')
    subclass = data.get('subclass')
    circle_from = int(data.get('circle_from'))
    circle_to = int(data.get('circle_to'))
    style = ''
    source_class = ''
    source_subclass = ''
    schools = data.getlist('schools')
    books = data.getlist('books')
    cast_times = data.getlist('cast_times')
    is_ritual = data.get('is_ritual')

    if dnd_class or (circle_from >= 0 and circle_to >= 0) or schools or cast_times or is_ritual:
        ### Блок обработки заклинаний
        cards = Spell.objects.filter(is_face_side=True, name__icontains=data.get('name'))
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

        if circle_from >= 0 and circle_to >= 0:
            cards = cards.filter(circle__gte=circle_from, circle__lte=circle_to)

        if schools:
            cards = cards.filter(school__in=schools)

        if cast_times:
            cards = cards.filter(cast_time__in=cast_times)

        if is_ritual:
            cards = cards.filter(is_ritual=True)

        for card in cards:
            card.source = (
                source_subclass
                if subclass and int(subclass) in card.subclasses.values_list('id', flat=True)
                else source_class
            )

    else:
        ### Блок обработки всего вместе
        cards = Card.objects.filter(is_face_side=True, name__icontains=data.get('name'))

    if books:
        cards = cards.filter(book__in=books)

    cards, pdf_orientation = sort_cards(cards)

    context = {
        'cards': cards,
        'form': form,
        'style': style,
        'pdf_orientation': pdf_orientation,
    }

    return context


def sort_cards(cards):
    """
    Сортировка карт для pdf.
    Если двойных карт больше, чем одинарных - альбомная сортировка, иначе - портретная
    :param cards: Query карт для сортировки
    """
    ones = [card for card in cards if len(card) == 1]
    twos = [card for card in cards if len(card) == 2]

    if len(twos) > len(ones):
        # Горизонтальная ориентация
        landscape_orientation = True
        cards = twos + ones
    else:
        # Вертикальная ориентация

        landscape_orientation = False

        result_cards = []
        for row in zip(ones, twos):
            result_cards.extend(row)
        result_cards.extend(ones[len(twos):])

    return cards, landscape_orientation
