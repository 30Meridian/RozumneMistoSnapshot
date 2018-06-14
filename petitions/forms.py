from petitions.models import Petitions
from django import forms


class PetitionAdd(forms.ModelForm):
    class Meta:
        model = Petitions
        fields = ['title', 'claim','image', 'text', 'anonymous']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Опишіть петицію одним реченням (максимально 255 символів)', 'class': 'form-control input-lg'}, ),
            'text': forms.Textarea(attrs={'placeholder': 'Розгорнуто опишіть підняте питання, приведіть аргументи, '
                                                         'чому саме ця петиція має бути задоволена (максимально 1000 '
                                                         'символів)', 'class': 'form-control input-lg',}),
            'claim': forms.Textarea(attrs={'placeholder': 'Опишіть вимогу до цієї петиції: Прошу встановити/розглянути/надати і т.д. Вкажіть адресата петиції: міська рада, міський голова, тощо. Максимально 1000 символів', 'class': 'form-control input-lg'}),
            'image': forms.FileInput(attrs={'class':"filestyle",'data-buttonText': "Виберіть зображення", 'data-badge':"false",'data-buttonBefore':"true"}),
        }

class PetitionChangeStatus(forms.ModelForm):
     def __init__(self, *args, **kwargs):
        super(PetitionChangeStatus, self).__init__(*args, **kwargs)
        self.fields['resolution'].required = True
        self.fields['resolution'].label = False

     class Meta:
        model = Petitions
        fields = ['resolution']
        widgets = {
                'resolution': forms.Textarea(attrs={'placeholder': 'Опишіть причину зміни статусу: порушення, виконання робіт, тощо... ', 'class': 'form-control input-lg',}),
        }