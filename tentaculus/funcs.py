from django.db.models import Q
from pathlib import Path

from tentaculus.converter import SpellConverter
from tentaculus.forms import SearchForm, ConvertFileForm
from tentaculus.models import Card, SubClass, DndClass, Spell, Source, Race, SubRace, Item


def get_cards_info(request, is_print=False):
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
    race = data.get('race')
    subrace = data.get('subrace')
    circle_from = int(data.get('circle_from'))
    circle_to = int(data.get('circle_to'))
    style = ''
    schools = data.getlist('schools')
    books = data.getlist('books')
    cast_times = data.getlist('cast_times')
    is_ritual = data.get('is_ritual') == 'true'

    if is_spell(data):
        ### Блок обработки заклинаний
        cards = Spell.objects.filter(is_face_side=True).select_related('second_side_spell').order_by('circle', 'name').distinct()

        source_class = None
        source_subclass = None
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
            cards = cards.filter(filters)

            style = class_instance.style

        source_race = None
        source_subrace = None
        if race:
            ### Если известна только раса, а подраса не указана
            filters = Q(race=race)
            race_instance = Race.objects.get(id=race)
            form.fields['subrace'].queryset = race_instance.subraces.all()
            source_race = race_instance.name

            if subrace:
                ### Если известна ещё и подраса
                source_subrace = SubRace.objects.get(id=subrace).name
                filters = filters | Q(subclasses=subrace)

                form.fields['subrace'].initial = subrace
            cards = cards.filter(filters)

            style = race_instance.style

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

        if books:
            cards = cards.filter(book__in=books)

        if name:
            name = name.strip().split(',')
            filters = Q()
            for separate_name in name:
                if separate_name:
                    filters = filters | Q(name__icontains=separate_name.strip())
            cards = cards.filter(filters)

    else:
        ### Блок обработки всего вместе
        filters = Q()
        if name:
            name = name.strip().split(',')
            for separate_name in name:
                if separate_name:
                    filters = filters | Q(name__icontains=separate_name.strip())

        if books:
            filters = filters | Q(book__in=books)

        cards = (
            list(Spell.objects.filter(is_face_side=True).filter(filters).select_related('second_side_spell').order_by('circle', 'name').distinct())
            + list(Item.objects.filter(is_face_side=True).filter(filters).select_related('second_side_spell').distinct())
        )

    pdf_orientation = None
    if is_print:
        cards, pdf_orientation = sort_cards(cards)

    cards_full = []
    for card in cards:
        cards_full.append(card)

        if card.second_side:
            cards_full.append(card.second_side)

    for card in cards_full:
        if card.style == 'Default':
            card.style = style

        if is_spell(data):
            if schools:
                card.get_school = card.school.filter(id__in=schools).order_by('priority')[0]
            else:
                card.get_school = card.school.order_by('priority')[0]

            if source_class:  # noqa
                card.source = (
                    source_subclass  # noqa
                    if subclass and int(subclass) in card.subclasses.values_list('id', flat=True)
                    else source_class  # noqa
                )
            elif source_race:  # noqa
                card.source = (
                    source_subrace  # noqa
                    if subrace and int(subrace) in card.subrace.values_list('id', flat=True)
                    else source_race  # noqa
                )

    context = {
        'cards': cards_full,
        'form': form,
        'convert_form': ConvertFileForm(),
        'pdf_orientation': pdf_orientation,
    }

    return context


def is_spell(data):
    dnd_class = data.get('dnd_class')
    race = data.get('race')
    circle_from = int(data.get('circle_from'))
    circle_to = int(data.get('circle_to'))
    schools = data.getlist('schools')
    cast_times = data.getlist('cast_times')
    is_ritual = data.get('is_ritual') == 'true'

    return dnd_class or race or circle_from >= 0 or circle_to >= 0 or schools or cast_times or is_ritual


def get_locked_cards_info(cards_names):
    """
    Получение контекста блока залоченных карт

    :param cards_names: Строка, объединённых через запятую имён залоченных карт
    """
    cards = []
    if cards_names == 'empty':
        cards_names = ''
    cards_names = (card_name.strip() for card_name in cards_names.split(', ') if card_name)
    for card_name in cards_names:
        card_name, style = card_name.split('|')
        if card_name[0].isdigit():
            card_name = ''.join(card_name.split('. ')[1:])
        card = (
            Spell.objects.filter(name__iexact=card_name).first()
            or Item.objects.filter(name__iexact=card_name).first()
        )

        if card.style == 'Default' and style:
            style = Source.objects.get(name=style)
            card.style = style.style
            card.source = style.name
        cards.append(card)

    # cards, pdf_orientation = sort_cards(cards)

    context = {
        'locked_cards': cards,
        # 'pdf_orientation': pdf_orientation,
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


def convert(request):
    """
    Конвертирование загруженного файла в сущность БД
    """
    obsidian_root = 'D:\Dnd\Obsidian\Kirania'
    search_word = request.POST.get('file_name')

    if not search_word:
        return 'Не указан файл'

    message = ''
    at_least_one = False
    for path in Path(obsidian_root).glob(f'**/*.md'):
        if search_word.lower() in str(path).lower():
            at_least_one = True
            if '\\заклинания\\' in str(path).lower():
                try:
                     message += SpellConverter(path).convert()
                except Exception as e:
                    message += f'{str(path)}: {e.args[0]}'

    if not message and at_least_one:
        message = 'Выполнено'

    return message or 'Не найдено такого файла'
