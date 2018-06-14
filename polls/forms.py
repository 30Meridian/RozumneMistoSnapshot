from django import forms
from django.forms.models import inlineformset_factory
from django.forms.extras.widgets import SelectDateWidget
from datetime import datetime, timedelta
from django.forms.widgets import ClearableFileInput
from django.core.exceptions import ValidationError

from .models import Poll, Choice


class PollForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PollForm, self).__init__(*args, **kwargs)
        self.fields['date_start'].initial = datetime.now()
        self.fields['date_end'].initial = datetime.now() + timedelta(days=30)

    class Meta:
        model = Poll
        fields = ('question', 'description', 'date_start', 'date_end', 'active', 'archive')
        widgets = {
            'question': forms.TextInput(attrs={
                'placeholder': 'Введіть питання. Не більше 255 символів',
                'class': 'form-control input-lg',}
            ),
            'description': forms.Textarea(attrs={
                'placeholder': 'Текст, що передає зміст питання.',
                'class': 'form-control input-lg',
                'rows': 10, 'style': 'resize: none;'}),
            'date_start': SelectDateWidget(),
            'date_end': SelectDateWidget(),

        }


class CustomClearableFileInput(ClearableFileInput):
    template_with_initial = (
        '%(initial_text)s: <a href="%(initial_url)s">%(initial)s</a> '
        '%(clear_template)s %(input)s'
    )


class ChoiceInline(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ChoiceInline, self).__init__(*args, **kwargs)
        self.image_list = []
        self.choice_list = []

    class Meta:
        model = Choice
        fields = ('choice', 'image')
        widgets = {
            'choice': forms.TextInput(attrs={
                'placeholder': 'Введіть варіант вибору.',
                'class': 'form-control input-md'}, ),
            'image': CustomClearableFileInput(
                attrs={
                    # 'class': "filestyle",
                    'data-buttonText': "Виберіть зображення",
                    'data-badge': "false",
                    'data-buttonBefore': "true"}),
        }



ChoiceFormSet = inlineformset_factory(Poll, Choice, form=ChoiceInline, extra=1, min_num=1)