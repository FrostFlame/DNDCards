import re
from abc import ABC, abstractmethod

from tentaculus.models import Spell, Book, Component, DndClass, SubClass, Race, SubRace, School, CastTime, Distance, \
    Duration


class FileConverter(ABC):
    def __init__(self, path):
        self.path = path

        with open(self.path, 'r+', encoding='utf-8') as file:
            text = file.read()
            self.text = text.replace(u'\xa0', ' ')
        self.text = text

        with open(self.path, 'w', encoding='utf-8') as file:
            file.write(text)

    @abstractmethod
    def convert(self):
        """
        Фабричный метод
        """
        pass


class SpellConverter(FileConverter):
    def __init__(self, path):
        super().__init__(path)
        self.text = self.text.replace(
            'Длительность: **Мгновенная**', 'Длительность: **Мгновенно**'
        )

        self.title_eng = None
        self.name = None
        self.circle = None
        self.schools = []
        self.description = None
        self.book = None
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

        self.set_name()
        self.set_title_eng()
        self.set_circle()
        self.set_schools()

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
        self.set_subclasses()
        self.set_races()
        self.set_subraces()

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

        if not Spell.objects.filter(title_eng=self.title_eng, name=self.name, second_side__isnull=False).exists():
            defaults['description'] = self.description

        spell, created = Spell.objects.update_or_create(
            title_eng=self.title_eng,
            name=self.name,
            defaults=defaults
        )

        spell.school.add(*self.schools)
        spell.classes.add(*self.classes)
        spell.subclasses.add(*self.subclasses)
        spell.race.add(*self.races)
        spell.subrace.add(*self.subraces)

        return ''

    def set_title_eng(self):
        try:
            self.title_eng = re.findall(r'#.+\[(.+)]', self.text)[0]
        except Exception:
            raise ValueError('Не обнаружено название на английском')

    def set_name(self):
        try:
            self.name = re.findall(r'# (.+) \[', self.text)[0]
        except Exception:
            raise ValueError('Не обнаружено название')

    def set_circle(self):
        try:
            circle = (re.findall(r'.*?, .*]]', self.text)[0].split(', ')[0])
        except Exception:
            raise ValueError('Не обнаружен круг')
        self.circle = 0 if circle == 'Заговор' else int(circle.split(' ')[0])

    def set_schools(self):
        try:
            schools_str = (re.findall(r'.*?, .*]]', self.text)[0].split(', ')[1:])
        except Exception:
            raise ValueError('Не обнаружены школы')

        for school in schools_str:
            school = school.strip('[[').strip(']]')
            try:
                school = School.objects.get(name=school)
                self.schools.append(school)
            except School.DoesNotExist as e:  # noqa
                raise ValueError(f'Обнаружена новая несуществующая школа: {school}\n')

    def clear_text(self):
        text_split = re.split('\[\[|]]', self.text)
        text = ''
        is_inside = False
        for string in text_split:
            if is_inside and '|' in string:
                string = re.findall(r'.*?\|(.*)', string)[0]

            text += string
            is_inside = not is_inside

        text = ''.join(text)

        self.text = text

    def set_description(self):
        # fonts_config = ((11.25, 17, 33),)
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
            book = re.findall(r'Источник.*?: «(.*)»', self.text)[0]
        except Exception:
            raise ValueError('Не обнаружена книга')
        try:
            self.book = Book.objects.get(title_eng=book)
        except Book.DoesNotExist as e:  # noqa
            raise ValueError(f'Обнаружена новая несуществующая книга: {book}\n')

    def set_is_ritual(self):
        self.is_ritual = True if re.findall(r'# Ритуал', self.text) else False

    def set_cast_time(self):
        try:
            cast_time = re.findall(r'Время накладывания: (.+)', self.text)[0]
            cast_time = cast_time.replace('*', '')
        except Exception:
            raise ValueError('Не обнаружено время накладывания')
        try:
            self.cast_time = CastTime.objects.get(name=cast_time)
        except CastTime.DoesNotExist as e:  # noqa
            raise ValueError(f'Обнаружено новое время накладывания: {cast_time}\n')

    def set_distance(self):
        try:
            distance = re.findall(r'Дистанция: \*\*(.+)\*\*', self.text)[0]
        except Exception:
            raise ValueError('Не обнаружена дистанция')
        try:
            self.distance = Distance.objects.get(name=distance)
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

    def set_material_components(self):
        material_components = re.findall(r'Компоненты: .+\((.*)\)', self.text)
        if material_components:
            self.material_components = material_components[0]

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
            self.duration = Duration.objects.get(name=duration)
        except Duration.DoesNotExist as e:  # noqa
            raise ValueError(f'Обнаружена новая длительность: {duration}\n')

    def set_classes(self):
        classes_str = re.findall(r'Классы: (.*)', self.text)
        if classes_str:
            classes_str = classes_str[0].split(', ')
            for dnd_class in classes_str:
                try:
                    dnd_class = DndClass.objects.get(name=dnd_class)
                    self.classes.append(dnd_class)
                except DndClass.DoesNotExist as e:
                    raise ValueError(f'Обнаружен новый класс: {dnd_class}\n')

    def set_subclasses(self):
        subclasses = re.findall(r'Архетипы: .*\n', self.text)
        if subclasses:
            subclasses_str = re.findall(r'.*?#(.*?)\|.*?', subclasses[0])
            for subclass in subclasses_str:
                try:
                    subclass = SubClass.objects.get(name=subclass)
                    self.subclasses.append(subclass)
                except SubClass.DoesNotExist as e:
                    raise ValueError(f'Обнаружен новый сабкласс: {subclass}\n')

    def set_races(self):
        races_str = re.findall(r'Расы: (.*)', self.text)
        if races_str:
            races_str = races_str[0].split(', ')
            for race in races_str:
                race = race.strip('[[').strip(']]')
                try:
                    race = Race.objects.get(name=race)
                    self.races.append(race)
                except Race.DoesNotExist as e:
                    raise ValueError(f'Обнаружена новая раса: {race}\n')

    def set_subraces(self):
        subraces = re.findall(r'Подрасы: .*\n', self.text)
        if subraces:
            subraces_str = re.findall(r'.*?#(.*?)\|.*?', subraces[0])
            for subrace in subraces_str:
                try:
                    subrace = SubRace.objects.get(name=subrace)
                    self.subraces.append(subrace)
                except SubRace.DoesNotExist as e:
                    raise ValueError(f'Обнаружена новая подраса: {subrace}\n')

