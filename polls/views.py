import datetime

from django.views.generic import DetailView, ListView, RedirectView, CreateView, DeleteView, UpdateView
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ValidationError

from weunion.settings import CRON_SECRET
from weunion.models import Town

from polls.models import Choice, Poll, Vote
from .forms import PollForm, ChoiceFormSet


class PollListView(ListView):

    def get_queryset(self):
        if 'town' in self.request.session:
            return Poll.objects.filter(active=1, town=self.request.session['town']).order_by('id','archive')
        else:
            #return reverse_lazy('regions')
            return Poll.objects.filter(active=3)

    def get_context_data(self, **kwargs):
        context = super(PollListView, self).get_context_data(**kwargs)
        context['slug'] = get_object_or_404(Town, id=self.request.session['town']).slug
        if self.request.user.is_authenticated() and self.request.user.is_active \
            and self.request.user.isAllowedToModerate(self.request.session["town"]):
            context['allowed'] = True
        else:
            context['allowed'] = False
        return context


class PollDetailView(DetailView):
    model = Poll

    def get_context_data(self, **kwargs):
        context = super(PollDetailView, self).get_context_data(**kwargs)

        if not(self.request.session.has_key('town')):
            self.request.session['town'] = self.object.town.id
            self.request.session['town_name'] = self.object.town.name

        if(self.request.user.is_authenticated() and self.request.user.is_active):
            context['poll'].votable = self.object.can_vote(self.request.user)
            if self.request.user.isAllowedToModerate(self.request.session["town"]):
                context['allowed'] = True
            else:
                context['allowed'] = False
        else:
            context['poll'].votable = False
        return context


class PollVoteView(RedirectView):
    def post(self, request, *args, **kwargs):
        poll = Poll.objects.get(id=kwargs['pk'])
        user = request.user
        choice = Choice.objects.get(id=request.POST['choice_pk'])
        Vote.objects.create(poll=poll, user=user, choice=choice)
        messages.success(request,"Дякуємо за Ваш голос")
        return redirect('../../', args=kwargs['pk'])
        #return super(PollVoteView, self).post(request, *args, **kwargs)

    def get_redirect_url(self, **kwargs):
        return redirect('../polls', args=[kwargs['pk']])


class PollCreateView(CreateView):
    model = Poll
    form_class = PollForm

    def get(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        choice_form = ChoiceFormSet()
        if self.request.user.is_authenticated() and self.request.user.is_active \
                and self.request.user.isAllowedToModerate(self.request.session["town"]):
            return self.render_to_response(self.get_context_data(form=form,
                                      choice_form=choice_form,))
        else:
            raise PermissionDenied('Доступ заборнено!')

    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        choice_form = ChoiceFormSet(request.POST, request.FILES)

        if (form.is_valid() and choice_form.is_valid()):
            image_list = []
            choice_list = []
            for field in choice_form:
                if field.cleaned_data:
                    if field.cleaned_data['image']:
                        image_list.append(field.cleaned_data['image'])
                    if field.cleaned_data['choice']:
                        choice_list.append(field.cleaned_data['choice'])

            if not (choice_list or image_list):
                return self.form_invalid(form, choice_form, 'Додайте зображення або текстовий варіант відповіді.')
            if choice_list and image_list:
                return self.form_invalid(form, choice_form, 'Додайте лише або зображення , або текстовий варіант відповіді!')
            return self.form_valid(form, choice_form)
        else:
            return self.form_invalid(form, choice_form, 'Дані не коректні, або не заповлені поля!')

    def form_valid(self, form, choice_form):
        town = Town.objects.get(pk=self.request.session["town"])

        self.object = form.save(commit=False)
        self.object.town = town
        self.object.save()
        choice_form.instance = self.object
        choice_form.save()
        messages.success(self.request, "Опитування успішно додано.")
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, choice_form, message):
        messages.warning(self.request, message)
        return self.render_to_response(
            self.get_context_data(form=form, choice_form=choice_form,))

    def get_success_url(self):
        slug = get_object_or_404(Town, id=self.request.session['town']).slug
        return reverse_lazy('polls:list', kwargs={'townslug': slug},)


class PollDeleteView(DeleteView):
    model = Poll

    def get_success_url(self):
        slug = get_object_or_404(Town, id=self.request.session['town']).slug
        messages.success(self.request, "Опитування успішно видалене")
        return reverse_lazy('polls:list', kwargs={'townslug': slug},)

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated() and self.request.user.is_active \
                and self.request.user.isAllowedToModerate(self.request.session["town"]):
            return super(PollDeleteView, self).get(request, *args, **kwargs)
        else:
            raise PermissionDenied('Доступ заборнено!')


class PollUpdateView(UpdateView):
    model = Poll
    form_class = PollForm

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated() and self.request.user.is_active \
                and self.request.user.isAllowedToModerate(self.request.session["town"]):
            return super(PollUpdateView, self).get(request, *args, **kwargs)
        else:
            raise PermissionDenied('Доступ заборнено!')
    def get_context_data(self, **kwargs):
        context = super(PollUpdateView, self).get_context_data(**kwargs)
        if self.request.POST:
            context['form'] = PollForm(self.request.POST, instance=self.object)
            context['choice_form'] = ChoiceFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            context['form'] = PollForm(instance=self.object)
            context['choice_form'] = ChoiceFormSet(instance=self.object)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        choice_form = ChoiceFormSet(request.POST, request.FILES, instance=self.object)

        if (form.is_valid() and choice_form.is_valid()):
            image_list = []
            choice_list = []
            for field in choice_form:
                if field.cleaned_data:
                    if field.cleaned_data['image']:
                        image_list.append(field.cleaned_data['image'])
                    if field.cleaned_data['choice']:
                        choice_list.append(field.cleaned_data['choice'])

            if not (choice_list or image_list):
                return self.form_invalid(form, choice_form, 'Додайте зображення або текстовий варіант відповіді.')
            if choice_list and image_list:
                return self.form_invalid(form, choice_form, 'Додайте лише або зображення , або текстовий варіант відповіді!')
            return self.form_valid(form, choice_form)
        else:
            return self.form_invalid(form, choice_form, 'Дані не коректні, або не заповлені поля!')

    def form_valid(self, form, choice_form):
        town = Town.objects.get(pk=self.request.session["town"])

        self.object = form.save(commit=False)
        self.object.town = town
        self.object.save()
        choice_form.instance = self.object
        choice_form.save()
        messages.success(self.request, "Опитування успішно змінено.")
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, choice_form, message):
        messages.warning(self.request, message)
        return self.render_to_response(
            self.get_context_data(form=form, choice_form=choice_form,))

    def get_success_url(self):
        slug = get_object_or_404(Town, id=self.request.session['town']).slug
        return reverse_lazy('polls:detail', kwargs={'townslug': slug,'pk': self.object.pk },)


#проверяем кроном просроченые голосования и переносим в архивные\
def checktimeout(request, secret, townslug):
    if(secret == CRON_SECRET):
       polls = Poll.objects.filter(active=1, archive=0)
       count = 0
       for poll in polls:
           if(poll.date_end <= datetime.date.today() ):
               poll.archive= 1 # делаем архивной если у петиции кончилось время сбора подписей и она не набрала нужного количества голосов
               poll.save()
               count +=1
       if(count):
           return HttpResponse('Done! Find: '+str(count)+' poll(-s)')
       else:
           return HttpResponse("Not found any polls that mutch enddate!")
    else:
        raise PermissionDenied('Досуп заборонено.')