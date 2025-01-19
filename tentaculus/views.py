import os

from asgiref.sync import async_to_sync
from django.http import HttpResponse
from django.http.response import JsonResponse
from django.shortcuts import render

from tentaculus.forms import SearchForm, ConvertFileForm
from tentaculus.funcs import get_cards_info, convert
from tentaculus.models import Item, Spell, Card, DndClass, SubClass, Circle, Race, SubRace, Book

from pyppeteer import launch


# Create your views here.


def all_cards(request):
    """
    Вообще все карты
    """

    form = SearchForm(request.GET)

    spells = Spell.objects.filter(is_face_side=True).prefetch_related('school').order_by('circle', 'name')
    for spell in spells:
        spell.get_school = spell.school.order_by('priority')[0]

    cards = list(spells) + list(Item.objects.filter(is_face_side=True).order_by('name'))

    context = {
        'cards': cards,
        'form': form,
        'convert_form': ConvertFileForm(),
    }
    return render(request, 'tentaculus/main.html', context)


def cards_block(request):
    context = get_cards_info(request)
    if request.GET.get('locked_to_print'):
        template_name = 'tentaculus/locked_cards.html'
    else:
        template_name = 'tentaculus/cards.html'

    return render(request, template_name, context)


def all_spells(request):
    """
    Все заклинания
    """

    form = SearchForm(request.GET, initial={'circle_to': Circle.NINTH})

    spells = Spell.objects.filter(is_face_side=True).prefetch_related('school').order_by('circle', 'name')
    for spell in spells:
        spell.get_school = spell.school.order_by('priority')[0]
    context = {
        'cards': spells,
        'form': form,
        'convert_form': ConvertFileForm(),
    }
    return render(request, 'tentaculus/main.html', context)


def all_items(request):
    """
    Все предметы
    """

    form = SearchForm(request.GET)

    items = Item.objects.filter(is_face_side=True).order_by('name')
    context = {
        'cards': items,
        'form': form,
        'convert_form': ConvertFileForm(),
    }
    return render(request, 'tentaculus/main.html', context)


def search(request):
    """
    Поиск
    """
    context = get_cards_info(request)
    return render(request, 'tentaculus/cards.html', context)


def update_locked_block(request):
    """
    Апдейт залоченных карт
    """
    context = get_cards_info(request)
    return render(request, 'tentaculus/locked_cards.html', context)


def print_pdf(request):
    """
    Печать pdf по кнопке
    """
    context = get_cards_info(request, True)
    return async_to_sync(get_pdf)(request, context.get('pdf_orientation'))


def load_subclasses(request):
    """
    AJAX подгрузка карт по фильтру подкласса
    """
    class_id = request.GET.get('class')
    if class_id:
        dnd_subclasses = DndClass.objects.get(id=class_id).subclasses.all()
    else:
        dnd_subclasses = SubClass.objects.none()
    return render(request, 'tentaculus/suboptions.html', {'suboptions': dnd_subclasses})


def load_subraces(request):
    """
    AJAX подгрузка карт по фильтру подрасы
    """
    race_id = request.GET.get('race')
    if race_id:
        subraces = Race.objects.get(id=race_id).subraces.all()
    else:
        subraces = SubRace.objects.none()
    return render(request, 'tentaculus/suboptions.html', {'suboptions': subraces})


async def get_pdf(request, pdf_orientation):
    """
    Генерация pdf
    """
    url = (
        f'http://127.0.0.1:8000/cards_block?'
        f'name={request.GET.get("name")}'
        f'&dnd_class={request.GET.get("dnd_class")}'
        f'&subclass={request.GET.get("subclass")}'
        f'&race={request.GET.get("race")}'
        f'&subrace={request.GET.get("subrace")}'
        f'&circle_from={request.GET.get("circle_from")}'
        f'&circle_to={request.GET.get("circle_to")}'
        f'{("&schools=" + str(request.GET.getlist("schools"))) if request.GET.getlist("schools") else ""}'
        f'{("&books=" + str(request.GET.getlist("books"))) if request.GET.getlist("books") else ""}'
        f'{("&cast_times=" + str(request.GET.getlist("cast_times"))) if request.GET.getlist("cast_times") else ""}'
        f'&is_ritual={request.GET.get("is_ritual")}'
        f'&locked_to_print={request.GET.get("locked_to_print")}'
    )
    pdf_path = 'example.pdf'

    browser = await launch(headless=True, options={'handleSIGINT': False, 'handleSIGTERM': False})
    page = await browser.newPage()
    await page.goto(url)
    await page.emulateMedia('screen')
    await page.pdf({'path': pdf_path, 'format': 'Letter' if pdf_orientation else 'A4', 'printBackground': True,
                    'landscape': pdf_orientation})

    try:
        with open(pdf_path, 'rb') as content:
            response = HttpResponse(content, content_type='application/pdf')
            response['Content-Length'] = os.path.getsize(pdf_path)
            response['Content-Disposition'] = f'attachment; filename={pdf_path}'

            return response
    except:
        return all_cards(request())


def convert_file(request):
    """
    Создание сущности в БД из файла obsidian.md
    """

    if request.method == "POST":
        form = ConvertFileForm(request.POST)
        if form.is_valid():
            message = convert(request)
        else:
            message = 'Невалидная форма'
    else:
        message = ''

    return JsonResponse({'success': True, 'message': message})


def test(request):
    books = Book.objects.all()
    return JsonResponse({'books': str(list(books))})
