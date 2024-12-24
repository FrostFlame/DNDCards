import re

from django.db.models import Q
from pathlib import Path

from tentaculus.forms import SearchForm, ConvertFileForm
from tentaculus.models import Card, SubClass, DndClass, Spell, Book, CastTime, Distance, Component, Duration, Source, \
    Race, SubRace


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
    race = data.get('race')
    subrace = data.get('subrace')
    circle_from = int(data.get('circle_from'))
    circle_to = int(data.get('circle_to'))
    style = ''
    source = ''
    schools = data.getlist('schools')
    books = data.getlist('books')
    cast_times = data.getlist('cast_times')
    is_ritual = data.get('is_ritual') == 'true'

    if dnd_class or race or circle_from >= 0 or circle_to >= 0 or schools or cast_times or is_ritual:
        ### Блок обработки заклинаний
        cards = Spell.objects.all()
        if dnd_class:
            ### Если известен только класс, а сабкласс не указан
            filters = Q(classes=dnd_class)
            class_instance = DndClass.objects.get(id=dnd_class)
            form.fields['subclass'].queryset = class_instance.subclasses.all()
            source = class_instance.name

            if subclass:
                ### Если известен ещё и сабкласс
                source = SubClass.objects.get(id=subclass).name
                filters = filters | Q(subclasses=subclass)

                form.fields['subclass'].initial = subclass
            cards = cards.filter(filters).distinct()

            style = class_instance.style

        if race:
            ### Если известна только раса, а сабраса не указана
            filters = Q(race=race)
            race_instance = Race.objects.get(id=race)
            form.fields['subrace'].queryset = race_instance.subraces.all()
            source = race_instance.name

            if subrace:
                ### Если известна ещё и сабраса
                source = SubRace.objects.get(id=subrace).name
                filters = filters | Q(subclasses=subrace)

                form.fields['subrace'].initial = subrace
            cards = cards.filter(filters).distinct()

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

        card.source = source

    context = {
        'cards': cards,
        'form': form,
        'convert_form': ConvertFileForm(),
        'pdf_orientation': pdf_orientation,
    }

    return context


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
        card = Card.objects.get(name__iexact=card_name)

        if card.style == 'Default' and style:
            style = Source.objects.get(name=style)
            card.style = style.style
            card.source = style.name
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


def convert(request):
    """
    Конвертирование загруженного файла в сущность БД
    """
    obsidian_root = 'D:\Dnd\Obsidian\Кирания'
    search_word = request.POST.get('file_name')

    message = ''
    for path in Path(obsidian_root).glob(f'**/*.md'):
        if search_word.lower() in str(path).lower():
            if '\\заклинания\\' in str(path).lower():
                message += convert_spell(path)

    return message or 'Не найдено такого файла'


def convert_spell(path):
    """
    Конвертация файла заклинания
    """
    with open(path, 'r+', encoding='utf-8') as file:
        text = file.read()
        text = text.replace(u'\xa0', ' ').replace('Длительность: **Мгновенная**', 'Длительность: **Мгновенно**')
        file.seek(0)
        file.write(text)

    with open(path, 'r', encoding='utf-8') as file:
        file.seek(0)
        file_lines = list(file)
        title_eng = re.findall(r'#.+\[(.+)]', text)[0]
        name = re.findall(r'# (.+) \[', text)[0]
        description = None
        book = re.findall(r'Источник: «(.*)»', text)[0]
        try:
            book = Book.objects.get(title_eng=book)  # noqa
        except Book.DoesNotExist as e:  # noqa
            return f'{name}: Обнаружена новая несуществующая книга: {book}'
        circle = re.findall(r'\n(.+), \[\[', text)[0]
        circle = 0 if circle == 'Заговор' else int(circle.split(' ')[0])
        is_ritual = True if re.findall(r'# Ритуал', text) else False
        cast_time = re.findall(r'Время накладывания: \*\*(.+)\*\*', text)[0]
        try:
            cast_time = CastTime.objects.get(name=cast_time)  # noqa
        except CastTime.DoesNotExist as e:  # noqa
            return f'{name}: Обнаружено новое время накладывания: {cast_time}'
        distance = re.findall(r'Дистанция: \*\*(.+)\*\*', text)[0]
        try:
            distance = Distance.objects.get(name=distance)  # noqa
        except Distance.DoesNotExist as e:  # noqa
            return f'{name}: Обнаружена новая дистанция: {distance}'
        components = [
            component.strip('**')[0] for component in re.findall(r'Компоненты: \*\*(.*)\*\*', text)[0].split(', ')
        ]
        for comp in Component:
            if all([letter in comp for letter in components]):
                components = comp
                break
        material_component = re.findall(r'Компоненты: .+\((.*)\)', text)
        duration = re.findall(r'Длительность: \*\*(.+)\*\*', text)[0]
        try:
            duration = Duration.objects.get(name=duration)  # noqa
        except Duration.DoesNotExist as e:  # noqa
            return f'{name}: Обнаружена новая длительность: {duration}'
        classes_str = re.findall(r'Классы: (.*)', text)[0].split(', ')
        classes_obj = []
        for dnd_class in classes_str:
            dnd_class = dnd_class.strip('[[').strip(']]')
            try:
                dnd_class = DndClass.objects.get(name=dnd_class)  # noqa
                classes_obj.append(dnd_class)
            except DndClass.DoesNotExist as e:  # noqa
                return f'{name}: Обнаружен новый класс: {dnd_class}'
        subclasses_str = re.findall(r'.*?\#(.*?)\|.*?', re.findall(r'Архетипы: .*\n', text)[0])
        subclasses_obj = []
        for subclass in subclasses_str:
            try:
                subclass = SubClass.objects.get(name=subclass)
                subclasses_obj.append(subclass)
            except SubClass.DoesNotExist as e:
                    return f'{name}: Обнаружен новый сабкласс: {subclass}'
        races = []
        subraces = []
        schools = []

    return 'Файлы конвертированы'
