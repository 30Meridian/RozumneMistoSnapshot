import base64
from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.views.generic.edit import FormView
from django.db.models import Q
from django.core.mail import send_mail, EmailMessage

from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from allauth.account.decorators import verified_email_required

from weunion.settings import DEFAULT_FROM_EMAIL
from weunion.models import Town

from .models import News
from .forms import NewsAdd, SuggestNews


# Добавить новость
@verified_email_required
def add(request, townslug):
    if (request.user.is_authenticated() and request.user.is_active):
        if request.user.isAllowedToModerate(request.session["town"], 'News'):
            if request.method == 'POST':
                town = Town.objects.get(pk=request.session["town"])
                form = NewsAdd(request.POST or None, request.FILES)
                # fill a model from a POST
                if form.is_valid():
                    instance = form.save(commit=False)
                    instance.town = town
                    instance.mainimg = form.cleaned_data['mainimg']
                    instance.author = request.user
                    instance.publish = 0
                    instance.save()
                    return redirect('../news/%s' % instance.id)
                else:
                    return render(request, 'add_news.html', {'form': form})
            else:
                form = NewsAdd()
                return render(request, 'add_news.html', {'form': form})
        else:
            raise PermissionDenied("Доступ заборонено")
    else:
        raise PermissionDenied("Доступ заборонено")


# Отобразить список новостей
def list(request, townslug):
    try:
        page = request.GET.get('page', 1)
    except PageNotAnInteger:
        page = 1

    if 'town' in request.session:
        if request.user.is_authenticated() and request.user.is_active and request.user.isAllowedToModerate(
                request.session["town"], 'News'):
            allowed = True
            news_list = News.objects.filter(town=request.session["town"]).all().order_by('-datetime_publish', 'publish')
        else:
            allowed = False
            news_list = News.objects.filter(town=request.session["town"], publish=1).all().order_by('-datetime_publish')

        p = Paginator(news_list, 10, request=request)
        articles = p.page(page)
        return render(request, 'articles_list.html', {'articles': articles, 'allowed': allowed, 'townslug': townslug})
    else:
        return redirect(reverse('regions'))


# Отобразить новость
def article(request, id, townslug):
    article = get_object_or_404(News, id=id)

    if not (request.session.has_key('town')):
        request.session['town'] = article.town.id
        request.session['town_name'] = article.town.name

    allowed = False
    if request.user.is_authenticated() and request.user.is_active:
        allowed = request.user.isAllowedToModerate(article.town.id, 'News')

    if (article.publish == False and allowed == False):
        raise PermissionDenied("Доступ заборонено")

    return render(request, 'article.html', {'article': article, 'allowed': allowed, })


# Удалить новость
def delete(request, id, townslug):
    if request.user.is_authenticated() and request.user.is_active and request.user.isAllowedToModerate(
            request.session["town"], 'News'):
        news = get_object_or_404(News, pk=id)
        news.delete()
        return redirect('../../news')


# Выставить статус опубликована
def publish(request, id, townslug):
    if request.user.is_authenticated() and request.user.is_active and request.user.isAllowedToModerate(
            request.session["town"], 'News'):
        news = get_object_or_404(News, pk=id)
        news.publish = 1
        if not (news.datetime_publish):
            news.datetime_publish = datetime.now()
        news.save()
        return redirect('../../news/' + id)


# Выставить статус снята с опубликации
def unpublish(request, id, townslug):
    if request.user.is_authenticated() and request.user.is_active and request.user.isAllowedToModerate(
            request.session["town"], 'News'):
        news = get_object_or_404(News, pk=id)
        news.publish = 0
        news.save()
        return redirect('../../news/' + id)


# Редактировать новость
def edit(request, id, townslug):
    if (request.user.is_authenticated() and request.user.is_active):
        if request.user.isAllowedToModerate(request.session["town"], 'News'):
            news = get_object_or_404(News, pk=id)
            form = NewsAdd(instance=news)
            if request.method == 'POST':
                form = NewsAdd(request.POST, request.FILES, instance=news)
                if form.is_valid():
                    instance = form.save(commit=False)
                    instance.mainimg = form.cleaned_data['mainimg']
                    instance.author = request.user
                    instance.publish = 0
                    instance.save()
                    return redirect('../../news/%s' % instance.id)
                else:
                    return render(request, 'edit_news.html', {'form': form, 'id': id})
            else:
                return render(request, 'edit_news.html', {'form': form, 'id': id})
        else:
            raise PermissionDenied("Доступ заборонено")
    else:
        raise PermissionDenied("Доступ заборонено")


class SuggestNewsView(FormView):
    form_class = SuggestNews
    template_name = 'suggest_news.html'

    def get_success_url(self):
        reverse('news:list', kwargs={'townslug': self.kwargs.get('townslug')})

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist('file_field')
        if form.is_valid():
            recipients = []
            town = Town.objects.filter(slug=self.kwargs.get('townslug')).first()
            users = town.user_set.filter(
                Q(groups__name='Moderator_news') | Q(groups__name='Moderator') | Q(groups__name='Control_news'))
            for user in users:
                recipients.append(user.email)

            subject = 'Запропонована новина від {0} {1}'.format(request.user.first_name, request.user.last_name)
            text = form.cleaned_data['text'] + '\nEmail: ' + str(request.user.email)
            mail = EmailMessage(subject, text, DEFAULT_FROM_EMAIL, recipients)
            for file in files:
                mail.attach(file.name, file.read(), file.content_type)

            mail.send()

            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        return render(self.request, 'success_suggestion.html', {'townslug': self.kwargs.get('townslug')})


suggest_news = SuggestNewsView.as_view()
