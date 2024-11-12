from audioop import reverse

from django import forms

from tentaculus.models import DndClass, Circle, School


class SearchForm(forms.Form):
    name = forms.CharField(label='Название', max_length=100, required=False)
    dnd_class = forms.ModelChoiceField(
        label='Класс',
        empty_label='Все',
        queryset=DndClass.objects.order_by('name'),
        widget=forms.Select(attrs={'class':'customSelect', 'style': 'padding: .5em .2em'}),
        required=False
    )
    subclass = forms.ModelChoiceField(
        label='Подкласс',
        empty_label='Все',
        queryset=DndClass.objects.none(),
        widget=forms.Select(attrs={'class':'customSelect', 'style': 'padding: .5em .2em'}),
        required=False
    )
    circle_from = forms.ChoiceField(
        choices=Circle.choices,
        widget=forms.Select(attrs={'class': 'customSelect', 'style': 'padding: .5em .2em'})
    )
    circle_to = forms.ChoiceField(
        choices=Circle.choices,
        initial=[Circle.NINTH],
        widget=forms.Select(attrs={'class': 'customSelect', 'style': 'padding: .5em .2em'})
    )
    schools = forms.ModelMultipleChoiceField(
        label='Школы',
        required=False,
        widget=forms.CheckboxSelectMultiple,
        queryset=School.objects.order_by('name'),
    )
