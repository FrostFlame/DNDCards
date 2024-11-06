from django import forms

from tentaculus.models import DndClass


class SearchForm(forms.Form):
    name = forms.CharField(label='Название', max_length=100, required=False)
    dnd_class = forms.ModelChoiceField(
        label='Класс',
        empty_label='Все',
        queryset=DndClass.objects.order_by('name'),
        widget=forms.Select(attrs={'class':'customSelect'}),
        required=False
    )
    subclass = forms.ModelChoiceField(
        label='Подкласс',
        empty_label='Все',
        queryset=DndClass.objects.none(),
        widget=forms.Select(attrs={'class':'customSelect'}),
        required=False
    )