from django.shortcuts import render

# Create your views here.


def all_cards(request):
    return render(request, 'cards.html')


def test(request):
    context = {
        'cards': [{
            'title': 'test_title',
            'name': 'Тестовая карта',
            'circle': '0',
            'cast_time': 'Тестовое действие',
            'distance': 'Тестовая дистанция',
            'components': 'Тестовые компоненты',
            'duration': 'Тестовая длительность',
            'material_components': 'Тестовые материальные компоненты',
            'font_size': '10.25',
            'description': 'Вы касаетесь 1 предмета, длина которого ни по одному из измерений не превышает <b>10 футов</b>. Пока заклинание активно, предмет испускает яркий свет в радиусе <b>20 футов</b>&nbsp;и тусклый свет в пределах ещё <b>20 футов</b>. Свет может быть любого выбранного вами цвета. Полное покрытие предмета чем-то непрозрачным блокирует свет. Заклинание оканчивается, если вы наложите его ещё раз или окончите <b>действием</b><br><br>Если вы нацелились на предмет, несомый или носимый враждебным существом, это существо должно преуспеть в <b>спасброске Ловкости</b>, чтобы увернуться от заклинания',
            'source': 'Тестовый источник',
            'source_class': 'Bard',
            'source_font_size': '10',
            'school_font_size': '10',
            'school': 'Тест',
            'book': 'Тестовая книга',
            'book_short': 'TST',
        }]
    }
    return render(request, 'cards.html', context)
