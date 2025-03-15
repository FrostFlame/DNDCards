import re
from abc import ABC, abstractmethod

from tentaculus.models import Spell, Book, Component, DndClass, SubClass, Race, SubRace, School, CastTime, Distance, \
    Duration, Item, Attunement, ItemType, Rarity


class FileConverter(ABC):
    def __init__(self, path):
        self.path = path

        self.title_eng = None
        self.name = None
        self.description = None
        self.book = None

        with open(self.path, 'r+', encoding='utf-8') as file:
            text = file.read()
            text = ''.join(re.split('lastSync.*\n', text))
            text = text.replace('---\n---\n', '').replace('---\n\n---\n', '')
            self.text = text.replace(u'\xa0', ' ').replace(' ', ' ')

        with open(self.path, 'w', encoding='utf-8') as file:
            file.write(self.text)

    @abstractmethod
    def convert(self):
        """
        Фабричный метод
        """
        self.set_name()
        self.set_title_eng()

    def clear_text(self):
        text_split = re.split('\[\[|]]', self.text)
        text = ''
        is_inside = False
        for string in text_split:
            if is_inside:
                if '|' in string:
                    string = re.findall(r'.*?\|(.*)', string)[0]
                string = f'<b>{string}</b>'

            text += string
            is_inside = not is_inside

        text = ''.join(text)

        text = ''.join(re.split('\(https.*?\)', text))
        text = text.replace('[', '<b>').replace(']', '</b>')

        self.text = text

    def set_name(self):
        try:
            self.name = re.findall(r'# (.+) \[', self.text)[0]
        except Exception:
            raise ValueError('Не обнаружено название')

    def set_title_eng(self):
        try:
            self.title_eng = re.findall(r'#.+\[(.+)]', self.text)[0]
        except Exception:
            raise ValueError('Не обнаружено название на английском')

    def set_description(self):
        try:
            description_split = (
                re.findall(re.compile(r'Источник.+?\n\n(.*)', re.S), self.text)[0]
                .replace('\n', '<br>')
                .replace('d', 'к')
                .replace('<br>- ', '<br>• ')
                .replace('На больших уровнях', '<i>НБУ</i>')
                .replace('_', '')
                .split('**')
            )
            description = ''
            for i, string in enumerate(description_split):
                description += string
                if i % 2 == 0:
                    if i != len(description_split) - 1:
                        description += '<b>'
                else:
                    description += '</b>'
        except Exception:
            raise ValueError('Ошибка в описании')

        self.description = description

    def set_book(self):
        try:
            book = re.findall(r'Источник.*?:\s«(.*)»', self.text)[0]
        except Exception:
            raise ValueError('Не обнаружена книга')
        try:
            self.book = Book.objects.get(title_eng=book)  # noqa
        except Book.DoesNotExist as e:  # noqa
            raise ValueError(f'Обнаружена новая несуществующая книга: {book}\n')


class SpellConverter(FileConverter):
    def __init__(self, path):
        super().__init__(path)
        self.text = self.text.replace(
            'Длительность: **Мгновенная**', 'Длительность: **Мгновенно**'
        )

        self.circle = None
        self.schools = []
        self.is_ritual = False
        self.cast_time = None
        self.distance = None
        self.components = None
        self.material_components = None
        self.duration = None
        self.classes = []
        self.subclasses = []
        self.races = []
        self.subraces = []

    def convert(self):
        """
        Конвертация файла заклинания
        """

        super().convert()

        self.set_circle()
        self.set_schools()
        self.set_subclasses()
        self.set_subraces()

        self.clear_text()

        self.set_description()
        self.set_book()
        self.set_is_ritual()
        self.set_cast_time()
        self.set_distance()
        self.set_components()
        self.set_material_components()
        self.set_duration()
        self.set_classes()
        self.set_races()

        defaults = {
            'title_eng': self.title_eng,
            'name': self.name,
            'book': self.book,
            'circle': self.circle,
            'is_ritual': self.is_ritual,
            'cast_time': self.cast_time,
            'distance': self.distance,
            'components': self.components,
            'material_component': self.material_components,
            'duration': self.duration,
        }

        if not Spell.objects.filter(title_eng=self.title_eng, name=self.name, second_side_spell__isnull=False).exists():  # noqa
            defaults['description'] = self.description

        spell, created = Spell.objects.update_or_create(  # noqa
            title_eng=self.title_eng,
            name=self.name,
            defaults=defaults
        )

        spell.school.clear()
        spell.school.add(*self.schools)
        spell.classes.clear()
        spell.classes.add(*self.classes)
        spell.subclasses.clear()
        spell.subclasses.add(*self.subclasses)
        spell.race.clear()
        spell.race.add(*self.races)
        spell.subrace.clear()
        spell.subrace.add(*self.subraces)

        return ''

    def set_circle(self):
        try:
            circle = (re.findall(r'.*?, .*]]', self.text)[0].split(', ')[0])
            self.circle = 0 if circle == 'Заговор' else int(circle.split(' ')[0])
        except Exception:
            raise ValueError('Не обнаружен круг')

    def set_schools(self):
        try:
            schools_str = (re.findall(r'.*?, .*]]', self.text)[0].split(', ')[1:])
        except Exception:
            raise ValueError('Не обнаружены школы')

        for school in schools_str:
            school = school.strip('[[').strip(']]')
            try:
                school = School.objects.get(name=school)  # noqa
                self.schools.append(school)
            except School.DoesNotExist as e:  # noqa
                raise ValueError(f'Обнаружена новая несуществующая школа: {school}\n')

    def set_is_ritual(self):
        self.is_ritual = True if re.findall(r'# Ритуал', self.text) else False

    def set_cast_time(self):
        try:
            cast_time = re.findall(r'Время накладывания: (.+)', self.text)[0]
            cast_time = cast_time.replace('*', '')
        except Exception:
            raise ValueError('Не обнаружено время накладывания')
        try:
            self.cast_time = CastTime.objects.get(name=cast_time)  # noqa
        except CastTime.DoesNotExist as e:  # noqa
            raise ValueError(f'Обнаружено новое время накладывания: {cast_time}\n')

    def set_distance(self):
        try:
            distance = re.findall(r'Дистанция: \*\*(.+)\*\*', self.text)[0]
        except Exception:
            raise ValueError('Не обнаружена дистанция')
        try:
            self.distance = Distance.objects.get(name=distance)  # noqa
        except Distance.DoesNotExist as e:  # noqa
            raise ValueError(f'Обнаружена новая дистанция: {distance}\n')

    def set_components(self):
        try:
            components = [
                component.strip('**')[0] for component in re.findall(
                    r'Компоненты: (.*)\*\*', self.text
                )[0].split(', ')
            ]
        except Exception:
            raise ValueError('Не обнаружены компоненты')
        for comp in Component:
            if all([letter in comp for letter in components]):
                self.components = comp
                return

    def set_material_components(self):
        material_components = re.findall(r'Компоненты: .+\((.*)\)', self.text)
        if material_components:
            self.material_components = material_components[0].replace('<b>', '').replace('</b>', '')

    def set_duration(self):
        try:
            duration = re.findall(r'Длительность: \*\*(.*)\*\*', self.text)[0]
        except Exception:
            raise ValueError('Не обнаружена длительность')
        try:
            duration = (
                duration.replace('**', '')
                .replace('Концентрация, вплоть до', 'Конц. до')
                .replace('Концентрация', 'Конц.')
                .replace('Вплоть до', 'До')
            )
            self.duration = Duration.objects.get(name=duration)  # noqa
        except Duration.DoesNotExist as e:  # noqa
            raise ValueError(f'Обнаружена новая длительность: {duration}\n')

    def set_classes(self):
        classes_str = re.findall(r'Классы: (.*)', self.text.replace('<b>', '').replace('</b>', ''))
        if classes_str:
            classes_str = classes_str[0].split(', ')
            for dnd_class in classes_str:
                try:
                    dnd_class = DndClass.objects.get(name=dnd_class)  # noqa
                    self.classes.append(dnd_class)
                except DndClass.DoesNotExist as e:  # noqa
                    raise ValueError(f'Обнаружен новый класс: {dnd_class}\n')

    def set_subclasses(self):
        subclasses = re.findall(r'Архетипы: .*\n', self.text.replace('<b>', '').replace('</b>', ''))
        if subclasses:
            subclasses_str = re.findall(r'.*?#.*?\|(.*?) \(', subclasses[0])
            for subclass in subclasses_str:
                try:
                    subclass = SubClass.objects.get(name__iexact=subclass)  # noqa
                    self.subclasses.append(subclass)
                except SubClass.DoesNotExist as e:  # noqa
                    raise ValueError(f'Обнаружен новый сабкласс: {subclass}\n')

    def set_races(self):
        races_str = re.findall(r'Расы: (.*)', self.text.replace('<b>', '').replace('</b>', ''))
        if races_str:
            races_str = races_str[0].split(', ')
            for race in races_str:
                race = race.strip('[[').strip(']]')
                try:
                    race = Race.objects.get(name=race)  # noqa
                    self.races.append(race)
                except Race.DoesNotExist as e:  # noqa
                    raise ValueError(f'Обнаружена новая раса: {race}\n')

    def set_subraces(self):
        subraces = re.findall(r'Подрасы: .*\n', self.text.replace('<b>', '').replace('</b>', ''))
        if subraces:
            subraces_str = re.findall(r'.*?#(.*?)\|.*?', subraces[0])
            for subrace in subraces_str:
                try:
                    subrace = SubRace.objects.get(name=subrace)  # noqa
                    self.subraces.append(subrace)
                except SubRace.DoesNotExist as e:  # noqa
                    raise ValueError(f'Обнаружена новая подраса: {subrace}\n')


class ItemConverter(FileConverter):
    def __init__(self, path):
        super().__init__(path)
        self.text = self.text.replace(
            'Длительность: **Мгновенная**', 'Длительность: **Мгновенно**'
        )

        self.attunement = None
        self.item_type = None
        self.rarity = None

    def convert(self):
        """
        Конвертация файла предмета
        """

        super().convert()
        self.clear_text()

        self.set_attunement()
        self.set_description()
        self.set_book()
        self.set_item_type()
        self.set_rarity()

        defaults = {
            'title_eng': self.title_eng,
            'name': self.name,
            'attunement': self.attunement,
            'book': self.book,
            'item_type': self.item_type,
            'rarity': self.rarity,
        }

        if not Item.objects.filter(title_eng=self.title_eng, name=self.name, second_side_spell__isnull=False).exists():  # noqa
            defaults['description'] = self.description

        item, created = Item.objects.update_or_create(  # noqa
            title_eng=self.title_eng,
            name=self.name,
            defaults=defaults
        )

        return ''

    def set_attunement(self):
        try:
            attunement = re.findall(r'\(требуется \*\*настройка\*\*.*\)', self.text)
            if not attunement:
                attunement = 'Нет'
            else:
                attunement = attunement[0].strip('(').strip(')').split('**настройка**')
                if not attunement[1]:
                    attunement = 'Да'
                else:
                    attunement = attunement[1].replace('<b>', '').replace('</b>', '').strip(')').strip(' ').capitalize()
        except Exception:
            raise ValueError('Что-то не так с настройкой')
        try:
            self.attunement = Attunement.objects.get(name=attunement)  # noqa
        except Attunement.DoesNotExist as e:  # noqa
            raise ValueError(f'Обнаружена новая настройка: {attunement}\n')

    def set_item_type(self):
        try:
            item_type = re.findall(r'(.*),', self.text)[0]
        except Exception:
            raise ValueError('Не обнаружен тип предмета')
        try:
            self.item_type = ItemType.objects.get(name=item_type)  # noqa
        except ItemType.DoesNotExist as e:  # noqa
            raise ValueError(f'Обнаружен новый тип предмета: {item_type}\n')

    def set_rarity(self):
        try:
            rarity = re.findall(r', .*', self.text)[0]
        except:
            raise ValueError('Не обнаружена редкость')

        for r in Rarity:
            if r in rarity:
                self.rarity = r
                return

        raise ValueError(f'Обнаружена некорректная редкость\n')

