from .models import CrowdfoundingProjects
from django import forms
from ckeditor_uploader.widgets import CKEditorUploadingWidget

class ProjectAdd(forms.ModelForm):
    class Meta:
        model = CrowdfoundingProjects
        fields = ['title','description','ifnotcollect', 'image','money_goal']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Уведіть назву проекту. Не більше 100 символів', 'class': 'form-control input-lg'}, ),
            'money_goal':  forms.TextInput(attrs={'placeholder': 'Скільки плануєте зібрати для проекту?', 'class': 'form-control input-lg'}, ),
            'ifnotcollect': forms.Textarea(attrs={'placeholder': 'На що плануєте потратити гроші якщо не назбираєте необхідну суму?. Не більше 300 символів.', 'class': 'form-control input-lg',}),
            'description': CKEditorUploadingWidget(),
            'image': forms.FileInput(attrs={'class':"filestyle",'data-buttonText': "Виберіть зображення", 'data-badge':"false",'data-buttonBefore':"true"}),

        }
