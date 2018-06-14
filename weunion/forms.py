import string
from django.contrib.auth import get_user_model
from django import forms
from functools import reduce

from .models import Town, User


class SignupForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['towns'].queryset = Town.objects.filter(is_active=1)

    error_css_class = 'myerror'
    required_css_class = 'myrequired'

    class Meta:
        model = get_user_model()
        fields = ('towns', 'last_name', 'first_name', 'middle_name', 'phone', 'email')
        widgets = {
            'towns': forms.SelectMultiple(attrs={
                'class': 'selectpicker form-control dropdown',
                'title': 'Почніть вводит назву Вашого населеного пункту',
                'data-live-search': 'true',
                'data-size': 10,
                'data-container': 'body'
            }),
            'first_name': forms.TextInput(
                attrs={'placeholder': "Ведіть ваше ім'я, напр. Євген", 'class': 'form-control input-lg'}),
            'last_name': forms.TextInput(
                attrs={'placeholder': "Введіть ваше прізвище, напр. Поремчук", 'class': 'form-control input-lg'}),
            'middle_name': forms.TextInput(attrs={
                'placeholder': "Введіть ім'я по батькові, напр. Володимирович. Вимагається деякими модулями, напр. 'Петиції'",
                'class': 'form-control input-lg'}),
            'phone': forms.TextInput(attrs={'placeholder': "Вкажіть Ваш номер телефону, напр. 097 111 22 33",
                                            'class': 'form-control input-lg'}),

        }

    def phone_split(x, format=[4, 3, 2, 2]):
        parts = []
        reduce(lambda x, y: parts.append(x[:y]) or x[y:], format, x)
        return ' '.join(parts)

    def signup(self, request, user):
        try:
            user.first_name = string.capwords(self.cleaned_data['first_name'].lower())
            user.middle_name = string.capwords(self.cleaned_data['middle_name'].lower())
            user.last_name = string.capwords(self.cleaned_data['last_name'].lower())
            user.phone = self.cleaned_data['phone']
            user.save()
            town = Town.objects.get(pk=self.cleaned_data['towns'][0].id)
            user.towns.add(town)
            user.save()
        except Exception as e:
            raise e

class TownAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TownAdminForm, self).__init__(*args, **kwargs)
        if not self.add_obj:
            self.fields['menu'].widget = forms.widgets.Textarea(attrs={'rows': 15, 'style': 'resize: none; width: 90%', })
        self.fields['pet_number_templ'].initial = '10/00%s-ЕП'
        self.fields['pet_days'].initial = 90

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        townname = self.cleaned_data.get('name')
        if slug and Town.objects.filter(slug=slug).exclude(name=townname).count():
            raise forms.ValidationError('Така системна назва вже існує!')
        return slug

class TownAdditionsInlineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TownAdditionsInlineForm, self).__init__(*args, **kwargs)
        self.fields['body'].widget = forms.widgets.Textarea(attrs={'rows': 5, 'style': 'resize: vertical; width: 95%', })
        self.fields['description'].widget = forms.widgets.Textarea(attrs={'rows': 5, 'style': 'resize: vertical; width: 95%', })


class ProfileChangeForm(forms.Form):
    text = forms.CharField(label='text', max_length=2000, required=True,
                           widget=forms.Textarea(attrs={'cols': 139, 'placeholder': "Наприклад: example@mail.ru на example@gmail.com", 'style': "resize: none;", 'class': 'form-control input-lg'}))
    reason = forms.CharField(label='reason', max_length=2000, required=True,
                             widget=forms.Textarea(attrs={'cols': 139, 'placeholder':"Чому?", 'style': "resize: none;", 'class': 'form-control input-lg'}))


class UserAdminForm(forms.ModelForm):
    verified_email = forms.BooleanField(help_text= 'Визначає чи підтверджена електронна адреса. ',
                                      label='Підтвердити email-адресу')
    def __init__(self, *args, **kwargs):
        super(UserAdminForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['verified_email'].required = False
        self.fields['email']._unique = True
        self.fields['middle_name'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True


        self.fields['verified_email'].initial = False
        if self.verified:
            self.fields['verified_email'].initial = True

    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.cleaned_data.get('username')
        if email and User.objects.filter(email=email).exclude(username=username).count():
            raise forms.ValidationError('Така електронна адреса вже існує!')
        return email


class TownBudgetForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TownBudgetForm, self).__init__(*args, **kwargs)
        self.fields['body'].widget = forms.widgets.Textarea(attrs={'rows': 5, 'style': 'resize: vertical; width: 95%', })


from allauth.account.forms import ResetPasswordForm
from allauth.account.adapter import get_adapter
from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse
from allauth.account.utils import user_pk_to_url_str, user_username
from allauth.utils import get_current_site, build_absolute_uri
from allauth.account import app_settings


class CustomResetPasswordForm(ResetPasswordForm):
    def save(self, request, **kwargs):
        # context = super(CustomResetPasswordForm, self).save(request, **kwargs)
        # print(context, '------------')

        email = self.cleaned_data["email"]
        token_generator = kwargs.get("token_generator",
                                     default_token_generator)

        for user in self.users:

            temp_key = token_generator.make_token(user)

            # save it to the password reset model
            # password_reset = PasswordReset(user=user, temp_key=temp_key)
            # password_reset.save()

            current_site = get_current_site(request)

            # send the password reset email
            path = reverse("first_page:reset_password_from_key",
                           kwargs=dict(uidb36=user_pk_to_url_str(user),
                                       key=temp_key))
            url = build_absolute_uri(
                request, path,
                protocol=app_settings.DEFAULT_HTTP_PROTOCOL)
            context = {"site": current_site,
                       "user": user,
                       "password_reset_url": url,
                       "request": request}
            if app_settings.AUTHENTICATION_METHOD \
                    != app_settings.AuthenticationMethod.EMAIL:
                context['username'] = user_username(user)
            get_adapter().send_mail('account/email/password_reset_key',
                                    email,
                                    context)
        return self.cleaned_data["email"]

class ContactForm(forms.Form):
    name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={
                           'placeholder': "Ваше ім'я",
                           'class': 'form-control input-lg'
                        }))
    email = forms.CharField(max_length=50, widget=forms.EmailInput(attrs={
                           'placeholder': "E-mail адреса",
                           'class': 'form-control input-lg'
                        }))
    phone = forms.CharField(max_length=50, widget=forms.TextInput(attrs={
                           'placeholder': "Ваш телефон",
                           'class': 'form-control input-lg'
                        }))
    text = forms.CharField(max_length=2000, widget=forms.Textarea(attrs={
                            'rows': 10,
                            'cols': 30,
                        }))

     # <input class="form-control input-lg" type="text" placeholder="Ваше ім'я">#}
     # <input class="form-control input-lg" type="email" placeholder="E-mail адреса">#}
     # <input class="form-control input-lg" type="text" placeholder="Ваш телефон">#}
     # <textarea name="" id="" cols="30" rows="10"></textarea>#}
