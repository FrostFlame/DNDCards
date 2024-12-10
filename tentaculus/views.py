import os

from asgiref.sync import async_to_sync
from django.http import HttpResponse
from django.shortcuts import render

from tentaculus.forms import SearchForm
from tentaculus.funcs import get_cards_info
from tentaculus.models import Item, Spell, Card, DndClass, SubClass, Circle

from pyppeteer import launch


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
    return render(request, 'main.html', context)


def cards_block(request):
    context = get_cards_info(request)

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
    return render(request, 'main.html', context)


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
    return render(request, 'main.html', context)


def search(request):
    """
    Поиск
    """
    if not all((request.POST.get('circle_from'), request.POST.get('circle_to'))):
        return all_cards(request)

    context = get_cards_info(request)

    if 'print' in request.POST:
        return async_to_sync(get_pdf)(request, context.get('pdf_orientation'))
    else:
        return render(request, 'main.html', context)


def load_subclasses(request):
    """
    AJAX подгрузка карт по фильтру подкласса
    """
    class_id = request.GET.get('class')
    if class_id:
        dnd_subclasses = DndClass.objects.get(id=class_id).subclasses.all()
    else:
        dnd_subclasses = SubClass.objects.none()
    return render(request, 'tentaculus/subclasses.html', {'subclasses': dnd_subclasses})


async def get_pdf(request, pdf_orientation):
    """
    Генерация pdf
    """
    url = (
        f'http://127.0.0.1:8000/cards_block?'
        f'name={request.POST.get("name")}'
        f'&dnd_class={request.POST.get("dnd_class")}'
        f'&subclass={request.POST.get("subclass")}'
        f'&circle_from={request.POST.get("circle_from")}'
        f'&circle_to={request.POST.get("circle_to")}'
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


def test(request):
    form = SearchForm(request.GET)

    cards = Card.objects.filter(is_face_side=True)
    context = {
        'cards': [card for card in cards],
        'form': form,
    }

    return render(request, 'main.html', context)
