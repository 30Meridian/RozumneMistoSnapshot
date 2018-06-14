from django import forms

from ckeditor_uploader.widgets import CKEditorUploadingWidget

from .models import InvestMapObject, InvestMapStats, InvestMapDescriptionTabs
from .validators import validate_file_extension


class InvestMapInitForm(forms.ModelForm):
    object_map = forms.CharField(widget=forms.HiddenInput(), label='')

    def __init__(self, *args, **kwargs):
        super(InvestMapInitForm, self).__init__(*args, **kwargs)
        self.fields['image'].label = 'Зображення'
        self.fields['document'].label = 'Додаткові матеріали'
        self.fields['object_type'].label = ''

    class Meta:
        model = InvestMapObject
        fields = ['project_type', 'name', 'price', 'address', 'metrics', 'contacts', 'image', 'document',
                  'object_type', 'object_map', 'description',]
        widgets = {
            'project_type': forms.Select(attrs={
                'class': 'form-control',
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Назва проекту',
            }),
            'price': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Вартість з указанням валюти',
            }),
            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Юридична адреса',
            }),
            'metrics': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Площа проекту'
            }),
            'contacts': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Контакти для купівлі',
            }),
            'image': forms.FileInput(),
            'document': forms.FileInput(),
            'description': CKEditorUploadingWidget(),
            'object_type': forms.HiddenInput(),
        }


class StatsAdd(forms.ModelForm):
    class Meta:
        model = InvestMapStats
        fields = ('title', 'param')


class DescriptionEdit(forms.ModelForm):
    class Meta:
        model = InvestMapDescriptionTabs
        fields = ('description',)
        widgets = {
            'description': CKEditorUploadingWidget(),
        }


class SuggestProject(forms.Form):
    text = forms.Field(label='Коротко опишіть ваш проект',
                       widget=forms.Textarea(attrs={
                           'rows': 8,
                           'maxlength': 500,
                           'placeholder': 'Опишіть ваш проект.',
                           'style': 'width: 100%;'}))
    phone = forms.CharField(label='Телефон для зворотнього зв\'язку',
                            widget=forms.TextInput(attrs={
                                'maxlength': 20,
                            }))
    file_field = forms.FileField(label='Матеріали',
                                 widget=forms.ClearableFileInput(attrs={'multiple': True}),
                                 validators=[validate_file_extension])
