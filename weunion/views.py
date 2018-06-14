import datetime
import urllib.request
import json
import requests
import re

from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, request
from django.template import RequestContext
from django.shortcuts import render, render_to_response, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_exempt

import weunion
from weunion.settings import DEFAULT_TO_EMAIL
from .helper import SendMail
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from digest.forms import DigestSubscribeForm

from edata.forms import SubscriptionAdd

from .forms import ProfileChangeForm, CustomResetPasswordForm, ContactForm
from .models import Regions, User, Town, TownEdrpou, Subscriptions

# cache_page(60 * 200)
def index(request, townslug=None):
    # if ("town" in request.session and "town_name" in request.session):
    #     slug = get_object_or_404(Town, pk=request.session["town"]).slug
    #     return redirect('/%s' % slug)

    # if ("town" in request.session and "town_name" in request.session):
    if (request.user.is_authenticated()):
        if ("town" not in request.session and "town_name" not in request.session):
            request.session["town"] = request.user.towns.all()[0].id
            request.session["town_name"] = request.user.towns.all()[0].name
        return redirect('/%s' % request.user.towns.all()[0].slug)

    return redirect(reverse('first_page:index'))


def redirectToSummary(request, townslug):
    return redirect('../%s/home' % townslug)


def errorPage(request, townslug, brockenlink):
    return redirect(request, 'error.html',
                    {'desc': "Неправильно вказане посилання на модуль, або такого модуля не існує"})


def index_town(request, townslug):
    if ("town" in request.session and "town_name" in request.session):
        issues = None
        petitions = None
        news = None
        polls = None
        allowed = None
        town = get_object_or_404(Town, pk=request.session["town"])
        town_banners = town.townbanners_set.all()
        modules = [m.module.id for m in Town.objects.get(pk=request.session["town"]).townallowedmodules_set.filter(active=1)]
        if (1 in modules):  # Дефекты ЖКХ
            from defects.models import Issues
            issues = [i for i in
                      Issues.objects.filter(parent_task_ref=None, town_ref=request.session["town"]).order_by('-id') if
                      i.last_issue().status != 0 and i.last_issue().status != 3]

        if (2 in modules):  # Петиции
            from petitions.models import Petitions
            petitions = Petitions.objects.filter(town=request.session["town"], status=2).order_by('-id')[:3]

        if (3 in modules):  # Новости
            from news.models import News
            news = News.objects.filter(town=request.session["town"], publish=1).order_by('-datetime_publish')[:3]

        if (13 in modules):  # Голосование
            from polls.models import Poll
            polls = Poll.objects.filter(active=1, archive=0, town=request.session['town']).order_by('id')[:3]

        return render(request, 'summarypage.html',
                      {'issues': issues, 'petitions': petitions, 'news': news, 'town': town,
                       'town_banners': town_banners, 'polls': polls})
    else:
        return HttpResponseRedirect('/regions/')


def test(request):
    return render(request, 'test.html')


# вывести список городов согласно области
def towns(request, region_ref):
    region = get_object_or_404(Regions, id=region_ref)
    tws = Town.objects.filter(region_ref=region, is_active=1)
    return render(request, 'towns.html', {'towns': tws})


# the ABOUT page
def about(request):
    return render(request, 'about.html')


# the CONTACTS page
def contacts(request):
    return render(request, 'contacts.html')


# the HELP page
def help(request):
    return render(request, 'help.html')


# the JOIN page
def join(request):
    return render(request, 'join.html')


# the MAP pageap
def map(request):
    return render(request, 'map_of_the_ukraine.html')


# про децентрализацию
def decentralization(request):
    return render(request, 'decentralization.html')


# партнеры
def partners(request):
    return render(request, 'partners.html')


# правила
def rules(request):
    return render(request, 'rules_common.html')


def useragreement(request):
    return render(request, 'user_agreement.html')

def first_page(request):
    api_key = weunion.settings.GOOGLE_API_KEY
    town = Town.objects.filter(is_active=1)
    return render(request, 'first_page.html', {'api_key': api_key, 'town': town})

# def profilechange(request):
#    return render(request, 'profile_change.html')

# Выбор города с помещением в сессию
def choosetown(request, townid):
    town_name = get_object_or_404(Town, id=townid).name
    slug = get_object_or_404(Town, id=townid).slug
    response = redirect('/%s' % slug)
    request.session["town"] = townid
    request.session["town_name"] = town_name
    return response

#get out from the town
def getoutfromtown(request):
    if 'town' in request.session:
        del request.session["town"]
    if 'town_name' in request.session:
        del request.session["town_name"]

    return redirect("/")

#a livestream for registered user
def livestream(request):
    from petitions.models import Petitions, PetitionsVoices
    from news.models import News
    from defects.models import Issues
    from polls.models import Poll, Vote
    from weunion.models import Modules

    statistic = {}
    statistic['petitions'] = Petitions.objects.all().count()
    statistic['petitions_voices'] = PetitionsVoices.objects.all().count()
    statistic['issues'] = len([i for i in Issues.objects.filter(parent_task_ref=None).order_by('-id')])
    statistic['news'] = News.objects.all().count()
    statistic['polls'] = Poll.objects.all().count()
    statistic['polls_votes'] = Vote.objects.all().count()
    statistic['towns'] = Town.objects.all().count()
    statistic['users'] = User.objects.all().count()
    statistic['modules'] = Modules.objects.all().count()

    return render(request, 'livestream.html',{'statistic': statistic})

#Формируем название города в хэддере
def gettown(request):
    if ("town" in request.session and "town_name" in request.session):
        return HttpResponse(request.session["town_name"])
    elif (request.user.is_authenticated()):
        town_name = request.user.towns.all()[0].name
        townid = request.user.towns.all()[0].id
        response = HttpResponse(town_name)
        request.session["town"] = townid
        request.session["town_name"] = town_name
        return response
    else:
        return HttpResponse(False)


def _get_town_name(town_id):
    '''Возвращаем Имя города'''
    if (town_id):
        town_name = Town.objects.get(id=town_id).name
        return town_name
    else:
        return 'Вкажіть ID міста'


# страница регионов
def regions(request):
    return render(request, 'regions.html')


# сраничка IGOV
def igov(request, townslug):
    if ("town" in request.session and "town_name" in request.session):
        if (request.is_ajax()):
            req = urllib.request.Request(
                "https://igov.org.ua/api/catalog?%s" % Town.objects.get(pk=request.session["town"]).additions.get(
                    type='igov').body)
            res = urllib.request.urlopen(req)
            data = res.read().decode("UTF-8")
            data = json.loads(data)
            return render_to_response('_igov-ajax.html', {"sData": data})
        else:
            return render(request, 'igov.html')
    else:
        return redirect('regions')


# страничка Open Budget
def budget(request, townslug):
    if ("town" in request.session):
        try:
            openbudget = Town.objects.get(pk=request.session['town']).openbudget.all()[0].body
        except:
            return render(request, '404.html')
        return render(request, 'budget.html', {"openbudget": openbudget})
    else:
        redirect('regions')


# for <iframe>
@xframe_options_exempt
def budget_api(request, townslug):
    try:
        openbudget = Town.objects.get(slug=townslug).openbudget.all()[0].body
    except:
        return render(request, '404.html')
    return render(request, 'budget_api.html', {"openbudget": openbudget})


def prozorro(request, townslug):
    """Вытягиваем данные из системы Прозоро"""
    if ("town" in request.session):
        try:
            url = "https://bid.e-tender.biz/api/services/etender/tender/GetTenders"
            town = Town.objects.get(id=request.session['town'])
            edrpous = TownEdrpou.objects.filter(koatuu=town.koatuu)[:500]
            codes = [str(edrpou.code) for edrpou in edrpous]
            if not codes:
                return render(request, 'prozorro.html',
                          {"error": "На жаль, для вашого міста ще не вказані коди ЄДРПОУ!"})
            data = {'Page':1,
                    'PageSize':500,
                    'OrderColumn':'tenderStartDate',
                    'OrderDirection':'desc',
                    'SearchFilter':{
                        'Cpvs': [],
                        'CustomerRegion': None,
                        'Description': None,
                        'Dkpp': None,
                        'IsStasusesDefaulted': True,
                        'OrganizationName': None,
                        'PriceFrom': None,
                        'PriceTo': None,
                        'ProcurementMethod': "open",
                        'Statuses':[
                            'active.enquiries',
                            'active.tendering',
                            'active.auction',
                            'active.qualification',
                            'active.awarded',
                            'unsuccessful',
                            'complete',
                            'cancelled'],
                        'Title':None,
                        'isProductionMode':True,
                        'codeEDRPOUs':codes,
                        'isShowOnlyTendersCreatedOnOurSite': False,
                        'parentCodesEDRPOU': [],
                        'procurementMethodTypes': [],
                        'regions': [],
                        'tenderPeriodEndFrom': None,
                        'tenderPeriodEndTo': None,
                        'tenderPeriodStartFrom': None,
                        'tenderPeriodStartTo': None
                    }
                    }
            headers = {'content-type': 'application/json'}
            r = requests.post(url, data=json.dumps(data), headers=headers)
            data = r.content.decode("UTF-8")
            data = json.loads(data)
        except:
            return render(request, 'prozorro.html',
                          {"error": "Нечуване нахабство! Ми не можемо отримати доступ до сервера 'Prozorro'!"})

        return render(request, 'prozorro.html', {"data": data})
    else:
        return redirect('regions')


def profile(request, user_id):
    """
    показываем профиль пользователя
    :param request: HTTP request object
    :param user_id: User.id
    :return: Profile page for user with id=user_id
    """
    if request.user.is_authenticated() and request.user.is_active:
        town = Town.objects.get(pk=request.session['town'])

        payers_dict = TownEdrpou.objects.filter(koatuu=town.koatuu)[:500]
            # town.townedrpou_set.all()
        ss_list = Subscriptions.objects.filter(town_ref=request.session['town'], type_ref=1, user_ref=request.user)
        ssAddForm = SubscriptionAdd()  # Форма добавления подписки

        user = get_object_or_404(User, pk=user_id)
        moder = request.user.isAllowedToModerate(request.session["town"], 'Profile')

        allowed = (user.towns.all()[0] in [t for t in request.user.towns.all()] and moder)
        if request.method == 'POST':
            subscribe_form = DigestSubscribeForm(request.user, 'POST', request.POST)
            if subscribe_form.is_valid():
                subscribe_form.save()
        else:
            subscribe_form = DigestSubscribeForm(request.user, 'GET')
        return render(request,'profile.html', {
            'allowed': allowed,
            'user': user,
            'subscribe_form': subscribe_form,
            'payers_dict': payers_dict,
            'ss_list': ss_list,
            'ssAddForm': ssAddForm,
        })
    else:
        return redirect('/accounts/login')


def karma(request, user_id):
    """Листинг кармы пользователя"""
    from .helper import Karma
    if (request.user.is_authenticated() and request.user.is_active):
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        p = Paginator(Karma.list(get_object_or_404(User, pk=user_id)), 10, request=request)
        points = p.page(page)
        return render(request, 'karma_list.html', {'points': points})
    else:
        return redirect('/accounts/login')


def userban(request, user_id, status):
    if (request.user.is_authenticated() and request.user.is_active):
        user = get_object_or_404(User, pk=user_id)
        moder = request.user.isAllowedToModerate(request.session["town"], 'Profile')
        allowed = (user.towns.all()[0] in [t for t in request.user.towns.all()] and moder)
        if (allowed):
            user.is_active = int(status)
            user.save()
            return redirect('/profile/' + user_id)
        else:
            raise PermissionDenied("Доступ заборонено")
    else:
        raise PermissionDenied("Доступ заборонено")


# показываем пользовател
# ю после регистрации
def confirmyouremail(request):
    return render(request, 'please_confirm_your_email.html')


# контакты модераторов
def moderators(request, townslug):
    if ('town' in request.session):
        try:
            moders = Town.objects.get(pk=request.session["town"]).additions.filter(type='moderators')[0].body
            if not moders:
                moders = 'В процесі наповнення.'
        except:
            moders = 'В процесі наповнення.'
        return render(request, 'moderators_info_page.html', {'moders': moders})
    else:
        return redirect('regions')


# панель модераторов
def moderator(request):
    if (request.user.is_authenticated() and request.user.is_active):
        town = request.user.towns.all()[0]
        if request.user.isAllowedToModerate(town.id):
            from defects.models import Issues
            users = town.user_set.all()
            petitions = town.petitions_set.all()
            issues = len([i for i in Issues.objects.filter(parent_task_ref=None, town_ref=town).order_by('-id')])
            news = town.news_set.all()
            return render(request, 'moderators.html',
                          {'users': users, 'petitions': petitions, 'issues': issues, 'news': news,})
        else:
            raise PermissionDenied
    else:
        raise PermissionDenied

@csrf_exempt
def check_user(request):
    user = User.objects.get(id=request.POST.get('user_id'))
    user.is_checked = False
    if request.POST.get('checked') == 'true':
        user.is_checked = True
    user.save()
    return HttpResponse('OK')

# Звіт для модератора за період
def moderatorsZvit(request):
    from defects.models import Issues

    if (request.user.is_authenticated() and request.user.is_active):
        town = request.user.towns.all()[0]
        modules = [m.module.id for m in town.townallowedmodules_set.all()]
        if request.user.isAllowedToModerate(town.id):
            stat = {}

            if not (request.is_ajax()):
                return render(request, 'moder_zvit.html')

            start = request.POST.get('start')
            end = request.POST.get('end')

            # Вытаскиваем число зарегистрированых пользователей
            stat['users'] = len(town.user_set.filter(date_joined__range=[start, end]))

            if (1 in modules):
                # Дефекты на сегодняшний день
                stat['defects'] = {}
                stat['defects']['add'] = len([i for i in Issues.objects.filter(parent_task_ref=None, town_ref=town,
                                                                               created__range=[start, end]).order_by(
                    'id') if i.last_issue()])
                stat['defects']['defects_done'] = len([i for i in
                                                       Issues.objects.filter(parent_task_ref=None, town_ref=town,
                                                                             created__range=[start, end]).order_by('id')
                                                       if i.last_issue().status == 2])
                stat['defects']['defects_open'] = len([i for i in
                                                       Issues.objects.filter(parent_task_ref=None, town_ref=town,
                                                                             created__range=[start, end]).order_by('id')
                                                       if i.last_issue().status == 1])
                stat['defects']['defects_planning'] = len([i for i in
                                                           Issues.objects.filter(parent_task_ref=None, town_ref=town,
                                                                                 created__range=[start, end]).order_by(
                                                               'id') if i.last_issue().status == 5])
                stat['defects']['defects_get'] = len([i for i in
                                                      Issues.objects.filter(parent_task_ref=None, town_ref=town,
                                                                            created__range=[start, end]).order_by('id')
                                                      if i.last_issue().status == 4])

            if (2 in modules):
                # Петиции на сегодняшний день
                stat['petitions'] = {}
                # Число добавленых петиций
                stat['petitions']['add'] = len(town.petitions_set.filter(create_date__range=[start, end]))
                stat['petitions']['1'] = len(town.petitions_set.filter(status=1))  # Модерация
                stat['petitions']['2'] = len(town.petitions_set.filter(status=2))  # Сбор подписей
                stat['petitions']['4'] = len(town.petitions_set.filter(status=4))  # Розглянута
                stat['petitions']['5'] = len(town.petitions_set.filter(status=5))  # Архівна
                stat['petitions']['6'] = len(town.petitions_set.filter(status=6))  # Розглядається
                stat['petitions']['8'] = len(town.petitions_set.filter(status=8))  # На перевірці голосів

            if (3 in modules):
                # Число опубликованых новостей
                stat['news'] = len(town.news_set.filter(datetime_publish__range=[start, end]))

            return render_to_response('_moder_zvit_ajax.html', {"stat": stat, 'start': start, 'end': end})

        else:
            raise PermissionDenied
    else:
        raise PermissionDenied


# Интеграция с DONOR.UA
# https://donor.ua/api/cities
def donor(request, townslug):
    if ("town" in request.session and "town_name" in request.session):
        data = []
        try:
            req = urllib.request.Request('https://donor.ua/api/cities(%s)/Recipients' % (
            Town.objects.get(pk=request.session["town"]).additions.filter(type='donor')[0].body))
            res = urllib.request.urlopen(req)
            data = res.read().decode("UTF-8")
            data = json.loads(data)
        except:
            print('Помилка завантаження данних')

        return render(request, 'donor.html', {'data': data})
    else:
        return redirect('regions')


# Рейтинг пользователей
def rating(request, townslug):
    list = []
    if ("town" in request.session and "town_name" in request.session):
        from django.db.models import Sum
        list = []
        for user in get_object_or_404(Town, pk=request.session['town']).user_set.all().annotate(
                points_sum=Sum('karma__points')).order_by('-points_sum'):
            if not user.isAllowedToModerate(request.session['town']):
                u = user
                list.append(u)

        if (request.POST):
            list = list[:3]
            return render_to_response('_rating-ajax.html', {"list": list})
        else:
            return render(request, 'user_rating.html', {'list': list})
    else:
        return redirect('regions')


# выловить динамический url и показать документ
def getDocums(request, url_param, townslug):
    if ('town' in request.session):
        try:
            doc = get_object_or_404(Town, pk=request.session['town']).additions.get(type=url_param)
        except:
            raise ObjectDoesNotExist("Такого об'єкта не існує")
        ###############

        return render(request, 'docs.html', {'doc': doc})
    else:
        return redirect('regions')
    return render(request, 'docs.html', {'doc': doc})


def gromadasVillages(request, gromada_id):
    from .models import TownGromada

    gromada = get_object_or_404(TownGromada, pk=gromada_id, main_town_ref__is_active=1 )

    return render(request, 'gromadas_villages.html', {'gromada': gromada})


def handler404(request):
    response = render_to_response('404.html', {}, context_instance=RequestContext(request))
    response.status_code = 404
    return response


def handler500(request):
    response = render_to_response('500.html', {}, context_instance=RequestContext(request))
    response.status_code = 500
    return response


@csrf_exempt
def townLiveSearch(request):
    from .models import TownsGromadasVillages
    result = []
    for t in Town.objects.filter(is_active=1):
        town = {}
        town['id'] = t.id
        town['name'] = t.name
        town['type'] = t.town_type.title
        town['region'] = t.region_ref.name
        town['gromada'] = "%s. " % t.towngromada_set.first().title if t.towngromada_set.first() else ''
        # town['slug'] = t.slug
        result.append(town)
    for v in TownsGromadasVillages.objects.filter(gromada_ref__main_town_ref__is_active=1):
        village = {}
        village['id'] = v.gromada_ref.main_town_ref_id
        village['type'] = v.type_ref.title
        village['name'] = v.title
        village['region'] = v.gromada_ref.main_town_ref.region_ref.name
        village['gromada'] = "%s. " % v.gromada_ref.title
        result.append(village)
    return JsonResponse(result, safe=False)


def townRedirect(request, townredirect):
    return redirect('/%s' % townredirect)


def get_news(date, days_count):
    from news.models import News
    query = News.objects.filter(publish=True, datetime_publish__lt=date).order_by('-datetime_publish')
    if days_count is not None:
        end_date = date - datetime.timedelta(days=days_count)
        query = query.filter(datetime_publish__gt=end_date)

    result = []
    for news in query[0:10]:
        try:
            image_url = news.mainimg.url
        except ValueError:
            image_url = ''

        result.append({
            'type': 2,
            'id': news.id,
            'datetime': news.datetime_publish,
            'time': news.datetime_publish.time(),
            'class': 'fa fa-newspaper-o bg-green',
            'town_name': news.town.name,
            'town_slug': news.town.slug,
            'module_name': 'Новини',
            'module_link': 'news/',
            'image': image_url,
            'header': news.title,
            'content': news.shortdesc or ''
        })

    return result


def get_petitions(date, days_count):
    from petitions.models import Petitions
    query = Petitions.objects.filter(status__in=[2, 4, 6], when_approve__lt=date).order_by('-when_approve')
    if days_count is not None:
        end_date = date - datetime.timedelta(days=days_count)
        query = query.filter(when_approve__gt=end_date)


    result = []
    for petition in query[0:10]:
        try:
            image_url = petition.image.url
        except ValueError:
            image_url = ''

        result.append({
            'type': 2,
            'id': petition.id,
            'datetime': petition.when_approve,
            'time': petition.when_approve.time(),
            'class': 'fa fa-commenting-o bg-blue',
            'town_name': petition.town.name,
            'town_slug': petition.town.slug,
            'module_name': 'Петиції',
            'module_link': 'petitions/',
            'image': image_url,
            'status': str(petition.status),
            'header': petition.title,
            'content': petition.text or ''
        })

    return result


def get_defects(date, days_count=None):
    from defects.models import Issues

    query = Issues.objects.filter(parent_task_ref=None, created__lt=date).order_by('-created')
    if days_count is not None:
        end_date = date - datetime.timedelta(days=days_count)
        query = query.filter(created__gt=end_date)

    issues = []
    counter = 0
    for i in query.all():
        last_issue = i.last_issue()
        last_issue_status = last_issue.status
        if last_issue_status in [2, 4]:
            issues.append(i)
            counter += 1
        if counter >= 10:
            break

    result = []
    for defect in issues:
        last_defect = defect.last_issue()
        result.append({
            'type': 2,
            'id': defect.id,
            'datetime': defect.created,
            'time': defect.created.time(),
            'class': 'fa fa-search bg-red',
            'town_name': defect.town_ref.name,
            'town_slug': defect.town_ref.slug,
            'module_name': 'Дефекти ЖКГ',
            'module_link': 'defects/',
            'status': 'Виконана' if last_defect.status == 2 else 'Прийнята до виконання' if last_defect.status == 4
            else '',
            'header': defect.title,
            'content': defect.description or ''
        })
    return result


def get_polls(date, days_count=None):
    from polls.models import Poll

    query = Poll.objects.filter(date_start__lt=date).order_by('-date_start')
    if days_count is not None:
        end_date = date - datetime.timedelta(days=days_count)
        query = query.filter(date_start__gt=end_date)

    result = []
    for poll in query[0:10]:
        result.append({
            'type': 2,
            'id': poll.id,
            'datetime': datetime.datetime.combine(poll.date_start, datetime.datetime.min.time()),
            'time': '',
            'class': 'fa  fa-check bg-orange',
            'town_name': poll.town.name,
            'town_slug': poll.town.slug,
            'module_name': 'Опитування',
            'module_link': 'polls/',
            'header': poll.question,
            'content': poll.description or ''
        })

    return result


def get_new_day(date):
    return {
        'type': 1,
        'date': date.date()
    }


def live_stream_list(date, filter_list=None, days_count=None):
    related_func = {
        'News': get_news,
        'Petitions': get_petitions,
        'Polls': get_polls,
        'Defects': get_defects
    }

    object_list = []
    for tag in filter_list:
        objects = related_func[tag](date, days_count)
        if len(objects):
            object_list.append(objects)

    last_datetime = date
    result = []
    for post in range(4):
        if len(object_list) == 0:
            result.append({'type': 3})
            break
        else:
            max_val = object_list[0][0]['datetime']
            max_index = 0
            if len(object_list) > 1:
                for i in range(1, len(object_list)):
                    if object_list[i][0]['datetime'] > max_val:
                        max_val = object_list[i][0]['datetime']
                        max_index = i

        present_datetime = object_list[max_index][0]['datetime']
        if present_datetime.date() < last_datetime.date():
            result.append(get_new_day(present_datetime))
        last_datetime = present_datetime

        result.append(object_list[max_index].pop(0))
        if len(object_list[max_index]) == 0:
            object_list.pop(max_index)

    return {'value': result, 'end_date': last_datetime.isoformat()}


@csrf_exempt
def last_news(request):
    date = datetime.datetime.strptime(request.GET['date'], '%Y-%m-%dT%H:%M:%S.%fZ')
    filter_list = ['News', 'Petitions', 'Polls', 'Defects']  # it will be sent from user later

    return JsonResponse(live_stream_list(date, filter_list), safe=False)


def profile_change(request):
    if request.method == 'POST':
        form = ProfileChangeForm(request.POST, request.FILES)
        if form.is_valid():
            SendMail.sendToModers(request, 'Зміна даних профіля', 'profile_change.email',
                                         {'name': request.user.id, 'text': form.cleaned_data['text'],
                                          'reason': form.cleaned_data['reason']}, DEFAULT_TO_EMAIL)
            return redirect('../../profile/%s' % request.user.id)
        else:
            form = ProfileChangeForm(request.GET, request.FILES)
    else:
        form = ProfileChangeForm()
    return render(request, 'profile_change.html', {'form': form})

def budgetuchastiya(request):
    return render(request, 'static_pages/about_modules/budgetuchastiya.html')

def defects(request):
    cities_allowed = Town.objects.filter(modules=1, townallowedmodules__active=1).count()
    return render(request, 'static_pages/about_modules/defects.html', {'cities_allowed': cities_allowed})

def donors(request):
    cities_allowed = Town.objects.filter(modules=15, townallowedmodules__active=1).count()
    return render(request, 'static_pages/about_modules/donors.html', {'cities_allowed': cities_allowed})

def edata(request):
    cities_allowed = Town.objects.filter(modules=14, townallowedmodules__active=1).count()
    return render(request, 'static_pages/about_modules/edata.html', {'cities_allowed': cities_allowed})

def flats(request):
    return render(request, 'static_pages/about_modules/flats.html')

def igov_2(request):
    cities_allowed = Town.objects.filter(modules=4, townallowedmodules__active=1).count()
    return render(request, 'static_pages/about_modules/igov.html', {'cities_allowed': cities_allowed})

def medicines(request):
    cities_allowed = Town.objects.filter(modules=7, townallowedmodules__active=1).count()
    return render(request, 'static_pages/about_modules/medicines.html', {'cities_allowed': cities_allowed})

def news(request):
    cities_allowed = Town.objects.filter(modules=3, townallowedmodules__active=1).count()
    return render(request, 'static_pages/about_modules/news.html', {'cities_allowed': cities_allowed})

def openbudget(request):
    cities_allowed = Town.objects.filter(modules=5, townallowedmodules__active=1).count()
    return render(request, 'static_pages/about_modules/openbudget.html', {'cities_allowed': cities_allowed})

def petitions(request):
    cities_allowed = Town.objects.filter(modules=2, townallowedmodules__active=1).count()
    return render(request, 'static_pages/about_modules/petitions.html', {'cities_allowed': cities_allowed})

def polls(request):
    cities_allowed = Town.objects.filter(modules=13, townallowedmodules__active=1).count()
    return render(request, 'static_pages/about_modules/polls.html', {'cities_allowed': cities_allowed})

def prozorro_2(request):
    cities_allowed = Town.objects.filter(modules=6, townallowedmodules__active=1).count()
    return render(request, 'static_pages/about_modules/prozorro.html', {'cities_allowed': cities_allowed})

def smartroads(request):
    return render(request, 'static_pages/about_modules/smartroads.html')

def mvs_wanted(request):
    return render(request, 'static_pages/about_modules/mvs_wanted.html')

def eng_index(request):
    return render(request, 'static_pages/eng_index.html')


def projects_about(request):
    defects = Town.objects.filter(modules=1, townallowedmodules__active=1).count()
    igov = Town.objects.filter(modules=4, townallowedmodules__active=1).count()
    edata = Town.objects.filter(modules=14, townallowedmodules__active=1).count()
    open_budget = Town.objects.filter(modules=5, townallowedmodules__active=1).count()
    prozorro = Town.objects.filter(modules=6, townallowedmodules__active=1).count()
    donor = Town.objects.filter(modules=15, townallowedmodules__active=1).count()
    news = Town.objects.filter(modules=3, townallowedmodules__active=1).count()
    polls = Town.objects.filter(modules=13, townallowedmodules__active=1).count()
    medicines = Town.objects.filter(modules=7, townallowedmodules__active=1).count()
    petitions = Town.objects.filter(modules=2, townallowedmodules__active=1).count()
    cities_allowed = {
        'defects': defects,
        'petitions': petitions,
        'igov': igov,
        'edata': edata,
        'open_budget': open_budget,
        'prozorro': prozorro,
        'donor': donor,
        'news': news,
        'polls': polls,
        'medicines': medicines,
    }
    return render(request, "static_pages/projects_about.html",{'cities_allowed':cities_allowed})

def contacts_new(request):
    if request.method == 'POST':
        form = ContactForm(request.POST or None, request.FILES)
        if form.is_valid():
            SendMail.sendToModers(request, 'Повідомлення від користувача', 'contact.email',
                                  {'name': form.cleaned_data['name'], 'text': form.cleaned_data['text'],
                                   'phone': form.cleaned_data['phone'], 'email': form.cleaned_data['email'],}, DEFAULT_TO_EMAIL)
            return redirect('/index/contacts')
        else:
            return render(request, 'static_pages/contacts_new.html', {'form': form})
    else:
        if request.user.is_authenticated():
            form = ContactForm(initial={
                'name': request.user.first_name,
                'phone': request.user.phone,
                'email': request.user.email
            })
        else:
            form = ContactForm()
        return render(request, "static_pages/contacts_new.html", {'form': form})

def new_team(request):
    return render(request, "static_pages/new_team.html")

def for_local_goverment(request):
    return render(request, "static_pages/for_local_goverment.html")

def for_citizens(request):
    return render(request, "static_pages/for_citizens.html")

def how_to(request):
    return render(request, "static_pages/how_to.html")

def statistics(request):
    from petitions.models import Petitions, PetitionsVoices
    from news.models import News
    from defects.models import Issues
    from polls.models import Poll, Vote
    from weunion.models import Modules

    statistic = {}
    statistic['petitions'] = Petitions.objects.all().count()
    statistic['petitions_voices'] = PetitionsVoices.objects.all().count()
    statistic['issues'] = len([i for i in Issues.objects.filter(parent_task_ref=None).order_by('-id')])
    statistic['news'] = News.objects.all().count()
    statistic['polls'] = Poll.objects.all().count()
    statistic['polls_votes'] = Vote.objects.all().count()
    statistic['towns'] = Town.objects.filter(is_active=1).count()
    statistic['users'] = User.objects.all().count()
    statistic['modules'] = Modules.objects.all().count()
    return render(request, "static_pages/statistics.html",
                  context={'statistic': statistic})

def first_page_rules(request):
    return render(request, 'static_pages/rules.html')

def success_signup(request):
    return render(request, 'static_pages/allauth/success_signup.html')

from allauth.account.views import LoginView, SignupView, PasswordResetView, PasswordResetDoneView, PasswordResetFromKeyView, PasswordResetFromKeyDoneView
class LoginPage(LoginView):
    template_name = "static_pages/allauth/login.html"
login_page = LoginPage.as_view()

class SignupPage(SignupView):
    template_name = "static_pages/allauth/signup.html"
    success_url = ('/index/success_signup')
signup_page = SignupPage.as_view()

class PasswordResetPage(PasswordResetView):
    template_name = "static_pages/allauth/password_reset.html"
    form_class = CustomResetPasswordForm
    success_url = "/index/password_reset_done"
password_reset_page = PasswordResetPage.as_view()

class PasswordResetDonePage(PasswordResetDoneView):
    template_name = "static_pages/allauth/password_reset_done.html"
password_reset_done_page = PasswordResetDonePage.as_view()

class PasswordResetFromKeyPage(PasswordResetFromKeyView):
    template_name = 'static_pages/allauth/password_reset_from_key.html'
    success_url = '/index/password/reset/key/done/'
password_reset_from_key_page = PasswordResetFromKeyPage.as_view()

class PasswordResetFromKeyDonePage(PasswordResetFromKeyDoneView):
    template_name = "static_pages/allauth/password_reset_from_key_done.html"

password_reset_from_key_done_page = PasswordResetFromKeyDonePage.as_view()

def add_message_to_session(request):
    if not request.user.is_authenticated():
        if not 'message' in request.session:
            request.session['message'] = True
    return HttpResponse('OK')


@csrf_exempt
def edrpou_count(request):
    result = TownEdrpou.objects.filter(koatuu=request.POST.get('koatuu')).count()
    return JsonResponse(result, safe=False)


@csrf_exempt
def filter_cities(request):
    town_qs = Town.objects.all()
    result = []
    for i in town_qs:
        result.append({"value": i.name, "desc": i.slug, 'region': i.region_ref.name, 'type': i.town_type.title})
    return JsonResponse(result, safe=False)
