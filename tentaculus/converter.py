import re
from abc import ABC, abstractmethod
from PIL import ImageFont

from tentaculus.models import Spell, Book, Component, DndClass, SubClass, Race, SubRace, School, CastTime, Distance, \
    Duration, Item, Attunement, ItemType, Rarity, ItemRequirements


class FileConverter(ABC):
    def __init__(self, path):
        self.path = path

        self.title_eng = None
        self.name = None
        self.description_1 = None
        self.description_2 = None
        self.description_font_size = None
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

        self.description_1 = description

    def split_text_for_cards(self, is_item=False):
        font_size = 12
        line_height_multiplier = 1.08333333333
        font_path_normal = 'arial.ttf'
        font_path_bold = 'arialbd.ttf'
        remaining_lines = 'filled'
        max_width_px = 215
        max_height_px = 200
        max_height_px_second_card = 290

        max_lines_fit_mapper = {
            12: 16,
            11: 18,
            10: 20,
        }

        wrapped_lines = []
        current_line = ""
        current_width = 0

        extra_lines = 0

        if hasattr(self, 'material_components') and self.material_components:
            font_materials = ImageFont.truetype(font_path_normal, 10)
            words = self.material_components.split(' ')
            for j, word in enumerate(words):
                if j > 0:
                    word = " " + word
                word_width = font_materials.getlength(word)

                if current_width + word_width <= max_width_px:
                    current_line += word
                    current_width += word_width
                else:
                    wrapped_lines.append(current_line)
                    current_line = word.strip()
                    current_width = font_materials.getlength(current_line.strip('<b>').strip('</b>'))

            if current_line:
                wrapped_lines.append(current_line)

            extra_lines = len(wrapped_lines)

        while remaining_lines:
            if font_size < 9:
                raise ValueError(f"Слишком много текста, шрифт уже меньше 9")

            try:
                font_normal = ImageFont.truetype(font_path_normal, font_size)
                font_bold = ImageFont.truetype(font_path_bold, font_size)
            except IOError as e:
                raise ValueError(f"Ошибка: файл шрифта не найден: {e}")

            segments = re.split(r'(<b>.*?</b>)', self.description_1)
            calculated_line_height = font_size * line_height_multiplier

            max_lines_fit = max_lines_fit_mapper.get(font_size) - extra_lines
            if is_item:
                max_lines_fit += 2
            max_lines_fit_second_card = int(max_height_px_second_card / calculated_line_height)

            wrapped_lines = []
            current_line = ""
            current_width = 0

            for segment in segments:
                is_bold = segment.startswith('<b>') and segment.endswith('</b>')
                text_content = segment
                sub_segments = text_content.split('<br><br>')

                for i, sub_seg in enumerate(sub_segments):
                    if i > 0:
                        wrapped_lines.append(current_line)
                        wrapped_lines.append("<br><br>")
                        current_line = ""
                        current_width = 0

                    words = sub_seg.split(' ')
                    for j, word in enumerate(words):
                        if j > 0:
                            word = " " + word
                        font_to_use = font_bold if is_bold else font_normal
                        word_width = font_to_use.getlength(word.strip('<b>').strip('</b>'))

                        if current_width + word_width <= max_width_px:
                            current_line += word
                            current_width += word_width
                        else:
                            wrapped_lines.append(current_line)
                            current_line = word.strip()
                            current_width = font_to_use.getlength(current_line.strip('<b>').strip('</b>'))

            if current_line:
                wrapped_lines.append(current_line)

            if wrapped_lines and wrapped_lines[-1] == "":
                wrapped_lines.pop()

            first_card_lines = wrapped_lines[:max_lines_fit]
            second_card_lines = wrapped_lines[max_lines_fit:max_lines_fit + max_lines_fit_second_card]
            remaining_lines = wrapped_lines[max_lines_fit + max_lines_fit_second_card:]

            if first_card_lines[-1] == '<br><br>':
                first_card_lines.pop(-1)

            if second_card_lines and second_card_lines[0] == '<br><br>':
                second_card_lines.pop(0)

            if second_card_lines and len(second_card_lines) <= 3:
                remaining_lines = 'filled'

            if remaining_lines:
                font_size -= 1

        if re.findall(r'<b>(?!.*?</b>).*$', first_card_lines[-1]):
            first_card_lines[-1] += '</b>'
            second_card_lines[0] = '<b>' + second_card_lines[0]

        # Чтобы получить плоский текст для последующего расчета:
        part1 = " ".join(first_card_lines)
        part2 = " ".join(second_card_lines)

        self.description_1 = part1
        self.description_2 = part2
        self.description_font_size = font_size

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

        self.set_material_components()
        self.set_description()
        self.split_text_for_cards()
        self.set_book()
        self.set_is_ritual()
        self.set_cast_time()
        self.set_distance()
        self.set_components()
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
            'description': self.description_1,
            'font_size': self.description_font_size,
            'is_face_side': True,
        }

        # if not Spell.objects.filter(is_ability=False, title_eng=self.title_eng, name=self.name, second_side_spell__isnull=False).exists():  # noqa
        #     defaults['description'] = self.description


        spell, _ = Spell.objects.update_or_create(  # noqa
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

        if self.description_2:
            defaults['name'] = self.name + '*'
            defaults['description'] = self.description_2
            defaults['is_face_side'] = False
            second_side, _ = Spell.objects.update_or_create(  # noqa
                title_eng=self.title_eng,
                name=self.name + '*',
                defaults=defaults
            )

            second_side.school.clear()
            second_side.school.add(*self.schools)
            second_side.classes.clear()
            second_side.classes.add(*self.classes)
            second_side.subclasses.clear()
            second_side.subclasses.add(*self.subclasses)
            second_side.race.clear()
            second_side.race.add(*self.races)
            second_side.subrace.clear()
            second_side.subrace.add(*self.subraces)

            spell.second_side_spell = second_side
            spell.save()

        if not self.description_2 and spell.second_side:
            second_side = spell.second_side
            second_side.delete()

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
        all_subclasses = re.findall(r'<td>Архетипы.*</td>', self.text, re.DOTALL)
        if not all_subclasses:
            return
        all_subclasses = all_subclasses[0].replace('<td>', '').replace('</td>', '').split('\n')[1:]
        classes = re.findall(r'<th>Классы.*</th>', self.text, re.DOTALL)[0].replace('<th>', '').replace('</th>', '').split('\n')[1:]
        if all_subclasses:
            for dnd_class, class_subclasses in zip(classes, all_subclasses):
                for subclass in class_subclasses.split('<br>'):
                    try:
                        subclass = SubClass.objects.get(name__iexact=subclass)  # noqa
                        self.subclasses.append(subclass)
                    except SubClass.DoesNotExist as e:  # noqa
                        raise ValueError(f'Обнаружен новый сабкласс: {dnd_class}|{subclass}\n')

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

        self.attunement = None
        self.item_type = None
        self.rarity = None
        self.requirements = None

    def convert(self):
        """
        Конвертация файла предмета
        """

        super().convert()
        self.clear_text()

        self.set_attunement()
        self.set_description()
        self.split_text_for_cards(is_item=True)
        self.set_book()
        self.set_item_type()
        self.set_rarity()
        self.set_requirements()

        defaults = {
            'title_eng': self.title_eng,
            'name': self.name,
            'attunement': self.attunement,
            'book': self.book,
            'item_type': self.item_type,
            'rarity': self.rarity,
            'requirements': self.requirements,
            'description': self.description_1,
            'font_size': self.description_font_size,
            'is_face_side': True,
        }

        # if not Item.objects.filter(title_eng=self.title_eng, name=self.name, second_side_spell__isnull=False).exists():  # noqa
        #     defaults['description'] = self.description_1

        item, created = Item.objects.update_or_create(  # noqa
            name=self.name,
            defaults=defaults
        )

        if self.description_2:
            defaults['name'] = self.name + '*'
            defaults['description'] = self.description_2
            defaults['is_face_side'] = False
            second_side, _ = Item.objects.update_or_create(  # noqa
                title_eng=self.title_eng,
                name=self.name + '*',
                defaults=defaults
            )

            item.second_side_item = second_side
            item.save()

        if not self.description_2 and item.second_side_item:
            second_side = item.second_side
            second_side.delete()

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
            item_type = re.findall(r'(.*),', self.text)[0].strip('<b>').strip('</b>')
        except Exception:
            raise ValueError('Не обнаружен тип предмета')
        try:
            self.item_type = ItemType.objects.get(name=item_type)  # noqa
        except ItemType.DoesNotExist as e:  # noqa
            raise ValueError(f'Обнаружен новый тип предмета: {item_type}\n')

    def set_rarity(self):
        try:
            rarity = re.findall(r', \*\*.*?\*\*', self.text)[0].strip(', ').strip('**')
        except:
            raise ValueError('Не обнаружена редкость')

        for r in Rarity:
            if r.lower() == rarity.lower():
                self.rarity = r
                return

        raise ValueError(f'Обнаружена некорректная редкость {rarity}\n')

    def set_requirements(self):
        try:
            requirements = re.findall(r'Требования\*\*: (.*)', self.text)
            if not requirements:
               return
            requirements = requirements[0].replace('<b>', '').replace('</b>', '')
        except:
            raise ValueError('Не обнаружены требования')

        try:
            self.requirements = ItemRequirements.objects.get(name=requirements)  # noqa
        except ItemRequirements.DoesNotExist as e:  # noqa
            raise ValueError(f'Обнаружены новые требования: {requirements}\n')

