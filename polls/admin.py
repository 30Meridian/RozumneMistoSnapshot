from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError

from weunion.models import Town
from polls.models import Poll, Choice, Vote


class ChoiseInlineFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super(ChoiseInlineFormSet, self).clean()
        image_list = []
        choice_list = []
        for form in self.forms:
            if form.cleaned_data:
                if form.cleaned_data['image']:
                    image_list.append(form.cleaned_data['image'])
                if form.cleaned_data['choice']:
                    choice_list.append(form.cleaned_data['choice'])

        if not (choice_list or image_list):
            raise ValidationError('Please add some choices or images')
        if choice_list and image_list:
            raise ValidationError('Please add pictures or choices, but not both!')


class ChoiceInline(admin.TabularInline):
    formset = ChoiseInlineFormSet
    verbose_name_plural = "Choices of poll (Please add only pictures or only text)."
    model = Choice
    min_num = 1
    extra = 0
    max_num = 25


class PollAdminForm(forms.ModelForm):
    description = forms.CharField(max_length=2000,
                          widget=forms.Textarea(attrs={'rows': 15, 'style': 'resize: none; width: 90%'}), label = 'description')


class PollAdmin(admin.ModelAdmin):
    model = Poll
    form = PollAdminForm
    inlines = (ChoiceInline,)
    list_display = ('town','question', 'count_choices', 'count_total_votes','date_start','date_end','archive','active')
    exclude = ('town',)

    def save_model(self, request, obj, form, change):
        # obj.author = request.user
        obj.town = Town.objects.get(id=request.session['town'])
        obj.save()

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super(PollAdmin, self).get_queryset(request)
        else:
            qs = super(PollAdmin, self).get_queryset(request)
            return qs.filter(town=request.session['town'])


class VoteAdmin(admin.ModelAdmin):
    model = Vote
    list_display = ('choice', 'user', 'poll')

admin.site.register(Poll, PollAdmin)
admin.site.register(Vote, VoteAdmin)
