from .models import MvsWanted
from django import forms
from django.forms.extras.widgets import SelectDateWidget

class MvsWantedAdd(forms.ModelForm):
    class Meta:
        model = MvsWanted
        fields = ['category', 'name', 'birth_date','text', 'image']
        widgets = {
            'category': forms.TextInput(attrs={'placeholder': 'Категорія', 'class': 'form-control input-lg'}),
            'name': forms.TextInput(attrs={'placeholder': 'Ім\'я розшукованої особи (максимально 255 символів)',
                                           'class': 'form-control input-lg'}),
            'birth_date': forms.DateInput(
                # format=('%d-%m-%Y'),`
                                             attrs={'class':'form-control input-lg',
                                            'placeholder':'Введіть дату у форматі рррр-мм-дд'}),
            'text': forms.Textarea(attrs={'placeholder': 'Інформація про розшукувану особу (максимально 2000 символів)',
                                          'class': 'form-control input-lg'}),
            'image': forms.FileInput(attrs={'class':"filestyle",'data-buttonText': "Виберіть зображення",
                                            'data-badge':"false",'data-buttonBefore':"true"}),
        }
