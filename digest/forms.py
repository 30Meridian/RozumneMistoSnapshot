import json

from django import forms

from .models import UserSubscriptions


class DigestSubscribeForm(forms.Form):
    choices = forms.MultipleChoiceField(
        choices=[('News', 'Новини'), ('Petitions', 'Петиції'), ('Polls', 'Опитування'), ('Defects', 'Дефекти')],
        widget=forms.CheckboxSelectMultiple, required=False
    )

    def __init__(self, user=None, method='GET', *args, **kwargs):
        initial = {'choices': ['News', 'Petitions', 'Polls', 'Defects']}
        self.user = user
        if method == 'GET':
            try:
                subscribe_instance = UserSubscriptions.objects.get(user=self.user)
                initial['choices'] = subscribe_instance.filter_list
            except UserSubscriptions.DoesNotExist:
                pass
        super(DigestSubscribeForm, self).__init__(initial=initial, *args, **kwargs)

    def save(self):
        try:
            subscribe_instance = UserSubscriptions.objects.get(user=self.user)
            subscribe_instance.subscription = json.dumps(self.cleaned_data['choices'], )
            subscribe_instance.save()
        except UserSubscriptions.DoesNotExist:
            UserSubscriptions.objects.create(user=self.user, subscription=json.dumps(self.cleaned_data['choices']))
