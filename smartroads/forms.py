from .models import SmartroadsIssues,SmartroadsStatuses
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget

class Add(forms.ModelForm):
    class Meta:
        model = SmartroadsIssues
        fields = ['title','description','resolution', 'what_to_do', 'cost', 'done_date','lon','lat']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Введіть назву зони. Не більше 150 символів. Напр. "Зона 51. Вул. Сагайдачного - набережна Челночна"', 'class': 'form-control input-lg'}, ),
            'text': CKEditorUploadingWidget(),
            'lon': forms.HiddenInput(),
            'lat': forms.HiddenInput()
        }

