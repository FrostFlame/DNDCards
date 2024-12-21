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

    locked_to_print = request.GET.get('locked_to_print')

    if locked_to_print:
        return get_locked_cards_info(locked_to_print)

    form = SearchForm(data)
    name = data.get('name')
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
    is_ritual = data.get('is_ritual') == 'true'

    if dnd_class or circle_from >= 0 or circle_to >= 0 or schools or cast_times or is_ritual:
        ### Блок обработки заклинаний
        cards = Spell.objects.all()
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

        if circle_from >= 0:
            cards = cards.filter(circle__gte=circle_from)

        if circle_to >= 0:
            cards = cards.filter(circle__lte=circle_to)

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
        cards = Card.objects.all()

    if name:
        name = name.strip().split(',')
        filters = Q()
        for separate_name in name:
            if separate_name:
                filters = filters | Q(name__icontains=separate_name.strip())
        cards = cards.filter(filters)

    if books:
        cards = cards.filter(book__in=books)

    cards, pdf_orientation = sort_cards(cards)

    for card in cards:
        if card.style == 'Default':
            card.style = style

    context = {
        'cards': cards,
        'form': form,
        'pdf_orientation': pdf_orientation,
    }

    return context


def get_locked_cards_info(cards_names):
    """
    Получение контекста блока залоченных карт

    :param cards_names: Строка, объединённых через запятую имён залоченных карт
    """
    cards = []
    cards_names = (card_name.strip() for card_name in cards_names.split(', ') if card_name)
    for card_name in cards_names:
        card_name, style = card_name.split('|')
        if card_name[0].isdigit():
            card_name = ''.join(card_name.split('. ')[1:])
        card = Card.objects.get(name__iexact=card_name)

        if card.style == 'Default':
            card.style = style
        cards.append(card)

    cards, pdf_orientation = sort_cards(cards)

    context = {
        'locked_cards': cards,
        'pdf_orientation': pdf_orientation,
    }
    return context


def sort_cards(cards):
    """
    Сортировка карт для pdf
    Если двойных карт больше, чем одинарных - альбомная сортировка, иначе - портретная
    :param cards: Query карт для сортировки
    """
    ones = [card for card in cards if len(card) == 1]
    twos = [card for card in cards if len(card) == 2]

    if len(twos) > len(ones):
        # Горизонтальная ориентация
        landscape_orientation = True
        result_cards = twos + ones
    else:
        # Вертикальная ориентация

        landscape_orientation = False

        result_cards = []
        for row in zip(ones, twos):
            result_cards.extend(row)
        result_cards.extend(ones[len(twos):])

    return result_cards, landscape_orientation
