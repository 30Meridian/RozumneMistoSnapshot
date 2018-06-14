from django import forms

from ckeditor_uploader.widgets import CKEditorUploadingWidget

from .models import News
from .validators import validate_file_extension


class NewsAdd(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'shortdesc', 'text', 'mainimg', 'publish']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Уведіть заголовок новини. Не більше 150 символів',
                                            'class': 'form-control input-lg'}, ),
            'shortdesc': forms.Textarea(
                attrs={'placeholder': 'Короткий текст, що передає контекст новини. Не більше 300 символів.',
                       'class': 'form-control input-lg', }),
            'text': CKEditorUploadingWidget(),
            'mainimg': forms.FileInput(
                attrs={'class': "filestyle", 'data-buttonText': "Виберіть зображення", 'data-badge': "false",
                       'data-buttonBefore': "true"}),

        }


class SuggestNews(forms.Form):
    text = forms.Field(label='Текст новини',
                       widget=forms.Textarea(attrs={
                           'rows': 8,
                           'placeholder': 'Опишіть вашу новину.',
                           'style': 'width: 100%;'}))
    file_field = forms.FileField(label='Матеріали',
                                 widget=forms.ClearableFileInput(attrs={'multiple': True}),
                                 validators=[validate_file_extension])
