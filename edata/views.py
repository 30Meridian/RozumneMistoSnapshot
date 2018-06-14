from django.shortcuts import render, redirect, HttpResponse, render_to_response, get_object_or_404,get_list_or_404
from django.template import RequestContext
import json, requests
from weunion.models import Town, TownEdrpou
from .models import Edata
from .forms import SubscriptionAdd
from weunion.models import Subscriptions, SubscriptionsTypes, User
from weunion.settings import EDATA_URL
from django.db.models import Sum
from random import randrange
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
import datetime, iso8601
from weunion.settings import CRON_SECRET


def _seveToDB(data, town, rand_ind):
    '''Поцедурка сохраняет данные с e-data В базу данных'''
    try:
        for transaction in data['response']['transactions']:
            try:
                edata = Edata()
                edata.rand_ind = rand_ind
                edata.town_ref = town
                edata.trans_id = transaction['id']
                edata.trans_date = iso8601.parse_date(transaction['trans_date']).date()
                if ('recipt_bank' in transaction):
                    edata.recipt_bank = transaction['recipt_bank']
                else:
                    edata.recipt_bank = "Інформація про банк відсутня на E-Data"
                edata.recipt_name = transaction['recipt_name'].replace("'", "’")
                edata.payment_details = transaction['payment_details']
                if ('payer_bank' in transaction):
                    edata.payer_bank = transaction['payer_bank']
                else:
                    edata.payer_bank = "Інформація про банк відсутня на E-Data"
                edata.payer_edrpou = transaction['payer_edrpou']
                edata.recipt_edrpou = transaction['recipt_edrpou']
                edata.payer_name = transaction['payer_name'].replace("'", "’")
                if ('recipt_mfo' in transaction):
                    edata.recipt_mfo = transaction['recipt_mfo']
                else:
                    edata.recipt_mfo = "Дані про МФО відсутні на E-Data"
                if ('payer_mfo' in transaction):
                    edata.payer_mfo = transaction['payer_mfo']
                else:
                    edata.recipt_mfo = "Дані про МФО відсутні на E-Data"
                edata.amount = float(transaction['amount'])
                edata.save()
            except KeyError as name:
                raise KeyError("Не можливо вивантажити цілісну БД з Є-Дата!")

        return True
    except:
        return False

@csrf_exempt
def index(request, townslug):
    if("town" in request.session):
        error = None
        town = Town.objects.get(pk=request.session['town'])
        payers_dict = TownEdrpou.objects.filter(koatuu=town.koatuu)[:500]
        summa = ''

        if not('norefresh' in request.GET):
            if ('payer' in request.session):
                del request.session['payer']
            if ('date_from' in request.session):
                del request.session['date_from']
            if ('date_to' in request.session):
                del request.session['date_to']
            if ('receiver' in request.session):
                del request.session['receiver']

        if(request.is_ajax()):
            ###Формируем поисковый запрос
            #Плательщики/плательщик
            payers = []

            if('payer' in request.POST):
                if(request.POST['payer'] != '0'):
                    payers = [request.POST['payer']]
                    request.session['payer'] = request.POST['payer']
                else:
                    request.session['payer'] = request.POST['payer']
                    for payer in payers_dict:
                        payer = payer.code.strip()
                        payers.append(payer)
                    if not(payers):
                        raise ObjectDoesNotExist("Не знайдені коди ЕДРПОУ для вибраного міста")
            else:
                request.session['payer'] = '0'
                for payer in payers_dict:
                    payer = payer.code.strip()
                    payers.append(payer)
                if not(payers):
                    raise ObjectDoesNotExist("Не знайдені коди ЕДРПОУ для вибраного міста")

            data = {"payers_edrpous":payers}
            rand_ind = randrange(100000000)
            search_from_db = {"rand_ind": rand_ind}

            #Получатель
            #TODO: нужно разделять получателя с кодом ЄРДПОУ и по имени
            if('receiver' in request.POST):
                if(request.POST['receiver'].isdigit()):
                    data.update({"recipt_edrpous":request.POST['receiver']})
                else:
                    search_from_db.update({"recipt_name__icontains": request.POST['receiver']})

                request.session['receiver'] = request.POST['receiver']

            if(('date_from' in request.POST and 'date_to' in request.POST) and not(request.POST['date_from']=='' and request.POST['date_to']=='')):
                data.update({"startdate": request.POST['date_from']})
                request.session['date_from'] = request.POST['date_from']

                data.update({"enddate": request.POST['date_to']})
                request.session['date_to'] = request.POST['date_to']
                daterange = 'Показано платежі з '+request.POST['date_from']+' по '+request.POST['date_to']

            else:
                enddate_obj = datetime.datetime.now()
                town_edata_addition = Town.objects.get(slug=townslug).additions_queryset.filter(type='edata').first()
                startdate_obj = enddate_obj - datetime.timedelta(days=int(town_edata_addition.body)
                if town_edata_addition else 7)
                startdate = startdate_obj.strftime('%d-%m-%Y')
                enddate = enddate_obj.strftime('%d-%m-%Y')
                data.update({"startdate": startdate })
                data.update({"enddate": enddate})
                daterange = 'Показано платежі з '+startdate+' по '+enddate

            headers = {'content-type': 'application/json'}
            r = requests.post(EDATA_URL, data=json.dumps(data), headers=headers)
            data = r.content.decode("UTF-8")
            data = json.loads(data)

             #Сохраняем данные в нашу БД

            _seveToDB(data, town, rand_ind)
            fop_rating = Edata.objects.values('recipt_name').filter(recipt_edrpou__contains='x',rand_ind=rand_ind).annotate(total=Sum('amount')).order_by('-total')[:10]
            uric_rating = Edata.objects.values('recipt_name','recipt_edrpou').filter(rand_ind=rand_ind).exclude(recipt_edrpou__contains='x').annotate(total=Sum('amount')).order_by('-total')[:10]
            data = Edata.objects.filter(**search_from_db)
            if(data):
                try:
                    summa = '{:2,.2f}'.format(round(Edata.objects.filter(**search_from_db).aggregate(summ = Sum('amount'))['summ'],2))
                except:
                    summa = None
            rnd = render_to_response('edata/_index-ajax.html',{"data":data,'fop_rating':fop_rating,'uric_rating':uric_rating,'daterange': daterange,'summa':summa,'townslug':townslug},context_instance=RequestContext(request))
            rows = Edata.objects.filter(rand_ind=rand_ind).delete()  # видаляємо усі записи по ідентифікатору
            return rnd
        else:
            ss_list = '' #подписки пользователя
            if (request.user.is_authenticated() and request.user.is_active):
                ss_list = Subscriptions.objects.filter(town_ref=request.session['town'],type_ref=1,user_ref=request.user)
            else:
                ss_list = None

            ssAddForm = SubscriptionAdd() #Форма добавления подписки

            return render(request,'edata/index.html',{'payers_dict': payers_dict,'ss_list': ss_list,'ssAddForm':ssAddForm})
    else:
        redirect('regions')

def clearFilter(request,type, code, townslug):
    if('payer' in request.session):
        del request.session['payer']
    if('date_from' in request.session):
        del request.session['date_from']
    if('date_to' in request.session):
        del request.session['date_to']
    if('receiver' in request.session):
        del request.session['receiver']
    if(type == 'index'):
        return redirect('/../%s/edata' % townslug)
    elif(type =='payer'):
        return redirect('/../%s/edata/payer/%s' % (townslug, code))
    elif(type == 'reciever'):
        return redirect('/../%s/edata/recipient/%s' % (townslug, code))
    else:
        raise PermissionDenied('Доступ заборонено')


#=================== ПОДПИСКИ НА ПЛАТЕЖИ ======================#
#Деактивируем подписку на платежь
def ssdeactivate(request, ss_id, townslug):
    if("town" in request.session):
        if(request.user):
            ss = get_object_or_404(Subscriptions, pk=ss_id, user_ref=request.user)
            ss.is_active = 0
            ss.save()
            if request.GET.get('profile'):
                # for change from porfile
                return redirect('/profile/{}/#tab_1-2'.format(request.user.id))
            else:
                return redirect('/%s/edata/#tab_1-2' % townslug)
        else:
            return redirect('/accounts/login/')
    else:
        return redirect('/regions')

#Активируем подписку на платежь
def ssactivate(request, ss_id, townslug):
    if("town" in request.session):
        if(request.user):
            ss = get_object_or_404(Subscriptions, pk=ss_id, user_ref=request.user)
            ss.is_active = 1
            ss.save()
            if request.GET.get('profile'):
                # for change from porfile
                return redirect('/profile/{}/#tab_1-2'.format(request.user.id))
            else:
                return redirect('/%s/edata/#tab_1-2' % townslug)
        else:
            return redirect('/accounts/login/')
    else:
        return redirect('/regions')

#Удаляем подписку на платежь
def ssdelete(request, ss_id, townslug):
    if("town" in request.session):
        if(request.user):
            ss = get_object_or_404(Subscriptions, pk=ss_id, user_ref=request.user)
            ss.delete()
            if request.GET.get('profile'):
                # for change from porfile
                return redirect('/profile/{}/#tab_1-2'.format(request.user.id))
            else:
                return redirect('/%s/edata/#tab_1-2' % townslug)
        else:
            return redirect('/accounts/login/')
    else:
        return redirect('/regions')


def ssadd(request, townslug):
    if(request.user.is_authenticated() and request.user.is_active):
        if request.method == 'POST':
            #вместо модели используем класс формы (а он уже сам работает с моделью+валидирует поля)
            form = SubscriptionAdd(request.POST)
            #fill a model from a POST
            if form.is_valid():
                 #!!!! Меняем инстранс, а не форму!!!
                instance = form.save(commit=False)
                instance.town_ref = Town.objects.get(id=request.session["town"])
                instance.user_ref = request.user
                instance.type_ref = SubscriptionsTypes.objects.get(pk=1)
                instance.is_active = 1
                instance.gencode = randrange(100000000000000000000000000000)
                instance.save()
                if request.POST.get('profile'):
                    # for add from porfile
                    return redirect('/profile/{}/#tab_1-2'.format(request.user.id))
                else:
                    return redirect('/%s/edata/#tab_1-2' % townslug)
            else:
                raise ConnectionError
        else:
            raise PermissionDenied("Доступ заборонено")
    else:
        redirect('accounts/signup')

#отписатся от подписки прямо из письма по коду
def ssunsubscription(request, code, townslug):
    if(code):
        ss = get_object_or_404(Subscriptions, gencode=code)
        ss.delete()
        return render(request,'ok_unsubscribe.html',)
    else:
        return redirect('/accounts/login/')


#=======================СТРАНИЦА ПЛАТЕЛЬШИКА (Гос. организации)===============================#

@csrf_exempt
def payer(request, townslug, payer_id=None):
    #Показать платежи по плательшику - гос.структуре
    if("town" in request.session):
        #Если не ввели код ЄДРПОУ
        if(payer_id == None):
            raise ObjectDoesNotExist("Невказано коду ЄРДПОУ")

        error = None
        town = Town.objects.get(pk=request.session['town'])
        payers_name = TownEdrpou.objects.get(code=payer_id).title
            # town.townedrpou_set.get(code=payer_id).title

        if(request.is_ajax()):
            ###Формируем поисковый запрос
            #Плательщики/плательщик
            if(payer_id): #если передали айдишку плательщика через URL
                payers = [payer_id]
                request.session['payer'] = payer_id
            else:
                payers = []

            data = {"payers_edrpous":payers}
            rand_ind = randrange(100000000)
            search_from_db = {"rand_ind": rand_ind}
            search_from_db_i = False

            #Получатель
            #TODO: нужно разделять получателя с кодом ЄРДПОУ и по имени
            if('receiver' in request.POST):
                if(request.POST['receiver'].isdigit()):
                    data.update({"recipt_edrpous":request.POST['receiver']})
                else:
                    search_from_db_i = search_from_db
                    str_original = request.POST['receiver']
                    str_i = str_original.replace('і', 'i')

                    search_from_db.update({"recipt_name__icontains": str_original})
                    search_from_db_i.update({"recipt_name__icontains": str_i})

                request.session['receiver'] = request.POST['receiver']

            if(('date_from' in request.POST and 'date_to' in request.POST) and not(request.POST['date_from']=='' and request.POST['date_to']=='')):
                data.update({"startdate": request.POST['date_from']})
                request.session['date_from'] = request.POST['date_from']

                data.update({"enddate": request.POST['date_to']})
                request.session['date_to'] = request.POST['date_to']
                daterange = 'Показано платежі з '+request.POST['date_from']+' по '+request.POST['date_to']

            else:
                enddate_obj = datetime.datetime.now()
                town_edata_addition = Town.objects.get(slug=townslug).additions_queryset.filter(type='edata').first()
                startdate_obj = enddate_obj - datetime.timedelta(days=int(town_edata_addition.body)
                if town_edata_addition else 7)
                startdate = startdate_obj.strftime('%d-%m-%Y')
                enddate = enddate_obj.strftime('%d-%m-%Y')
                data.update({"startdate": startdate })
                data.update({"enddate": enddate})
                daterange = 'Показано платежі з '+startdate+' по '+enddate

            headers = {'content-type': 'application/json'}
            r = requests.post(EDATA_URL, data=json.dumps(data), headers=headers)
            data = r.content.decode("UTF-8")
            data = json.loads(data)

            #Сохраняем данные в нашу БД
            _seveToDB(data, town, rand_ind)

            fop_rating = Edata.objects.values('recipt_name').filter(recipt_edrpou__contains='x',rand_ind=rand_ind).annotate(total=Sum('amount')).order_by('-total')[:10]
            uric_rating = Edata.objects.values('recipt_name', 'recipt_edrpou').filter(rand_ind=rand_ind).exclude(recipt_edrpou__contains='x').annotate(total=Sum('amount')).order_by('-total')[:10]
            data = Edata.objects.filter(**search_from_db)
            if(search_from_db_i):
                from itertools import chain
                data_i = Edata.objects.filter(**search_from_db_i)
                result_list = list(chain(data_i, data))
            try:
                summa = '{:2,.2f}'.format(
                    round(Edata.objects.filter(**search_from_db).aggregate(summ=Sum('amount'))['summ'], 2))
            except:
                summa = None
            rnd = render_to_response('edata/payer/_payer-ajax.html',{"data":data,'fop_rating':fop_rating,'uric_rating':uric_rating,'daterange': daterange,'payers_name': payers_name,'summa':summa,'townslug':townslug},context_instance=RequestContext(request))
            rows = Edata.objects.filter(rand_ind=rand_ind).delete()  # видаляємо усі записи по ідентифікатору
            return rnd
        else:
            return render(request,'edata/payer/payer.html',{'payers_name': payers_name,'payer_id': payer_id})
    else:
        redirect('regions')

#========================СТРАНИЦА ПОЛУЧАТЕЛЯ ПЛАТЕЖЕЙ (БИЗНЕС-СТРУКТУРА)===================================#

def test(request, receiver, townslug):
    print("It's working:%s" % receiver)

def recipient(request, townslug, receiver):
    '''Показать все входящие платежи по получателю платежей с гос. органов'''
    #Показать платежи по плательшику - гос.структуре
    if("town" in request.session):


        town = Town.objects.get(pk=request.session['town'])
        request.session['town_type'] = town.town_type.title[0]+"."
        payers_dict = TownEdrpou.objects.filter(koatuu=town.koatuu)[:500]
        error = ''

        if(request.is_ajax()):

            ###Формируем поисковый запрос
            # Плательщики/плательщик
            payers = []

            if ('payer' in request.POST):
                if (request.POST['payer'] != '0'):
                    payers = [request.POST['payer']]
                    request.session['payer'] = request.POST['payer']
                else:
                    request.session['payer'] = request.POST['payer']
                    for payer in payers_dict:
                        payer = payer.code.strip()
                        payers.append(payer)
                    if not (payers):
                        raise ObjectDoesNotExist("Не знайдені коди ЕДРПОУ для вибраного міста")
            else:
                request.session['payer'] = '0'
                for payer in payers_dict:
                    payer = payer.code.strip()
                    payers.append(payer)
                if not (payers):
                    raise ObjectDoesNotExist("Не знайдені коди ЕДРПОУ для вибраного міста")

            rand_ind = randrange(100000000)
            search_from_db = {"rand_ind": rand_ind}
            search_from_db_i = search_from_db.copy()
            receiver_name = ''
            data = {"payers_edrpous": payers}


            # TODO: Сделать проверку на буквенное или цифровое значение получателя платежа

            if (receiver == None):
                raise ObjectDoesNotExist("Невказано коду ЄРДПОУ отримувача або назва")
            elif (receiver.isdigit()):
                print(receiver)
                data.update({"recipt_edrpous": receiver})
            else:
                str_original = str(receiver)
                receiver_name = str(receiver)
                str_i = str_original.replace('і', 'i')
                search_from_db.update({"recipt_name__icontains": str_original})
                search_from_db_i.update({"recipt_name__icontains": str_i})


            if(('date_from' in request.POST and 'date_to' in request.POST) and not(request.POST['date_from']=='' and request.POST['date_to']=='')):
                data.update({"startdate": request.POST['date_from']})
                request.session['date_from'] = request.POST['date_from']

                data.update({"enddate": request.POST['date_to']})
                request.session['date_to'] = request.POST['date_to']
                daterange = 'Показано платежі з '+request.POST['date_from']+' по '+request.POST['date_to']

            else:
                enddate_obj = datetime.datetime.now()
                town_edata_addition = Town.objects.get(slug=townslug).additions_queryset.filter(type='edata').first()
                startdate_obj = enddate_obj - datetime.timedelta(days=int(town_edata_addition.body)
                if town_edata_addition else 7)
                startdate = startdate_obj.strftime('%d-%m-%Y')
                enddate = enddate_obj.strftime('%d-%m-%Y')
                data.update({"startdate": startdate })
                data.update({"enddate": enddate})
                daterange = 'Показано платежі з '+startdate+' по '+enddate

            headers = {'content-type': 'application/json'}
            r = requests.post(EDATA_URL, data=json.dumps(data), headers=headers)
            data = r.content.decode("UTF-8")
            data = json.loads(data)

            #Сохраняем данные в нашу БД
            _seveToDB(data, town, rand_ind)


            #Выбираем данные для формирования графика
            if not(receiver.isdigit()):
                rating = Edata.objects.values('trans_date').filter(**search_from_db).annotate(total=Sum('amount')).order_by('-trans_date')
                if (search_from_db_i):
                    from itertools import chain
                    rating_i = Edata.objects.values('trans_date').filter(**search_from_db_i).annotate(total=Sum('amount')).order_by('-trans_date')
                    result_rating = list(chain(rating_i, rating))


            else:
                rating = Edata.objects.values('trans_date').filter(rand_ind=rand_ind, recipt_edrpou=receiver).annotate(total=Sum('amount')).order_by('-trans_date')

            data = Edata.objects.filter(**search_from_db)
            if(data):
                receiver_name = data[0].recipt_name
            else:
                error = "Не знайдено отримувача платежу"

            if(search_from_db_i):
                from itertools import chain
                data_i = Edata.objects.filter(**search_from_db_i)
                result_list = list(chain(data_i, data))
            try:
                summa = '{:2,.2f}'.format(
                    round(Edata.objects.filter(**search_from_db).aggregate(summ=Sum('amount'))['summ'], 2))
            except:
                summa = None
            if not(error):
                rnd = render_to_response('edata/receiver/_receiver-ajax.html',{"data":data,'rating':rating,'daterange': daterange,'receiver_name': receiver_name ,'summa':summa})
            else:
                rnd = render_to_response('edata/receiver/_receiver-ajax.html', {"error": error})

            rows = Edata.objects.filter(rand_ind=rand_ind).delete()  # видаляємо усі записи по ідентифікатору
            return rnd
        else:
            return render(request,'edata/receiver/receiver.html',{'payers_name': None,'receiver': receiver, 'payers_dict': payers_dict})
    else:
        redirect('regions')


def sendSub(request, code, townslug):
    '''Разсылка платежей'''
    from weunion.models import Subscriptions
    import datetime

    if str(code) != CRON_SECRET:
        return ''

    payer_edrpou_title = 'Платежі по платинку-державній організації'
    recipt_edrpou_title = 'Пошук по отримувачу платежів'
    recipt_name_title = 'Пошук за отримувачем платежів по масці його назви'
    amount_title = 'Пошук за сумою'

    #1. Выбрать все подписки подписки с типом "edata"
    subscriptions = Subscriptions.objects.filter(type_ref__name='edata')

    #2. Отобрать в dictr все города и их пользователей подписок по distinct. Формат {город: юзеры}. towns_and_they_users = {1:[1,12,54],12;[34,14,123]}
    towns_and_they_users = {}
    for town in subscriptions.values_list('town_ref', flat=True).distinct():
        towns_and_they_users.update({town: subscriptions.filter(town_ref=town).values_list('user_ref', flat=True).distinct()})

    #3. Цикл по городам. Выбрать город.
    for town in towns_and_they_users:
        # 4. Выкачать платежи с е-дата за продыдущий день
        town_obj = Town.objects.get(pk=town)
        payers_dict = TownEdrpou.objects.filter(koatuu=town_obj.koatuu)[:500]
            # town_obj.townedrpou_set.all()
        payers = []
        for payer in payers_dict:
            payer = payer.code.strip()
            payers.append(payer)
        if not (payers):
            continue

        from_date = datetime.date.fromordinal(datetime.date.today().toordinal()-1).strftime("%d-%m-%Y")
        to_date = datetime.date.fromordinal(datetime.date.today().toordinal()).strftime("%d-%m-%Y")
        data = {"startdate": from_date, "enddate": to_date, "payers_edrpous": payers}
        rand_ind = randrange(100000000) #временный идентификатор что бы потом удалить
        headers = {'content-type': 'application/json'}
        r = requests.post(EDATA_URL, data=json.dumps(data), headers=headers)
        data = r.content.decode("UTF-8")
        data = json.loads(data)

        #Сохраняем данные в нашу БД
        _seveToDB(data, town_obj, rand_ind)

        # 5. Сделать цикл по юзерам города.Выбрать подписки пользователя.
        for user_id in towns_and_they_users[town]:
            # 6. Сделать цикл по подпискам
            user = User.objects.get(id=user_id)
            payments = {}
            for user_subscription in subscriptions.filter(town_ref=town, user_ref=user, is_active=1):
                #7. Поиск  платежей с сохраненных данных
                subscription_title = ''
                if user_subscription.parameter=='payer_edrpou':
                    subscription_title = payer_edrpou_title
                elif user_subscription.parameter=='recipt_edrpou':
                    subscription_title = recipt_edrpou_title
                elif user_subscription.parameter=='recipt_name':
                    subscription_title = recipt_name_title
                elif user_subscription.parameter=='amount':
                    subscription_title = amount_title

                kwargs = {}

                options = {
                    '==': '',
                    '!=': '',
                    '>': '__gt',
                    '<': '__lt',
                }
                kwargs.update({user_subscription.parameter+options[user_subscription.comparison]: user_subscription.value})
                if user_subscription.comparison != '!=':
                    users_payments = Edata.objects.filter(**kwargs).values()
                else:
                    users_payments = Edata.objects.exclude(**kwargs).values()

                payments.update({subscription_title: users_payments})

            #8. Оправить письмо пользователю
            if len(payments):
                _sendMail(town_obj, payments, user.email)

        Edata.objects.filter(rand_ind=rand_ind).delete()  # видаляємо усі записи по ідентифікатору

    return HttpResponse('Finished')

def _sendMail(town_obj, context, email_address):
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    from weunion.settings import DEFAULT_FROM_EMAIL

    template_html = render_to_string('emails/edata_subscriptions.email', context={'subjects': context})
    template_plain = render_to_string('emails/edata_subscriptions.email', context={'subjects': context})
    subject = 'Дайджест платежів по %s' % town_obj.name

    send_mail(
        subject,
        template_plain,
        DEFAULT_FROM_EMAIL,
        [email_address],
        html_message=template_html,
    )

def exportToExcel(request, townslug):
    from .exportExcelUtils import WriteToExcel
    if("town" in request.session):
        error = None
        town = Town.objects.get(pk=request.session['town'])
        payers_dict = TownEdrpou.objects.filter(koatuu=town.koatuu)[:500]
            # town.townedrpou_set.all()

        ###Формируем поисковый запрос
        #Плательщики/плательщик
        payers = []

        if ('payer' in request.session):
            if (request.session['payer'] != '0'):
                payers = [request.session['payer']]
            else:
                for payer in payers_dict:
                    payer = payer.code.strip()
                    payers.append(payer)
                if not (payers):
                    raise ObjectDoesNotExist("Не знайдені коди ЕДРПОУ для вибраного міста")
        else:
            request.session['payer'] = '0'
            for payer in payers_dict:
                payer = payer.code.strip()
                payers.append(payer)
            if not (payers):
                raise ObjectDoesNotExist("Не знайдені коди ЕДРПОУ для вибраного міста")

        data = {"payers_edrpous":payers}
        rand_ind = randrange(100000000)
        search_from_db = {"rand_ind": rand_ind}

        #Получатель
        #TODO: нужно разделять получателя с кодом ЄРДПОУ и по имени
        if('receiver' in request.session):
            if(request.session['receiver'].isdigit()):
                data.update({"recipt_edrpous":request.session['receiver']}) #ищеим на E-data
            else:
                search_from_db.update({"recipt_name__icontains": request.session['receiver']}) # ищем у себя локально

        if(('date_from' in request.session and 'date_to' in request.session) and not(request.session['date_from']=='' and request.session['date_to']=='')):
            data.update({"startdate": request.session['date_from']})
            data.update({"enddate": request.session['date_to']})
            daterange = 'з '+request.session['date_from']+' по '+request.session['date_to']

        else:
            enddate_obj = datetime.datetime.now()
            startdate_obj = enddate_obj - datetime.timedelta(days=7)
            startdate = startdate_obj.strftime('%d-%m-%Y')
            enddate = enddate_obj.strftime('%d-%m-%Y')
            data.update({"startdate": startdate })
            data.update({"enddate": enddate})
            daterange = 'з '+startdate+' по '+enddate

        headers = {'content-type': 'application/json'}
        r = requests.post(EDATA_URL, data=json.dumps(data), headers=headers)
        data = r.content.decode("UTF-8")
        data = json.loads(data)

        #Сохраняем данные в нашу БД
        _seveToDB(data, town, rand_ind)

        fop_rating = Edata.objects.values('recipt_name').filter(recipt_edrpou__contains='x',rand_ind=rand_ind).annotate(total=Sum('amount')).order_by('-total')[:10]
        uric_rating = Edata.objects.values('recipt_name').filter(rand_ind=rand_ind).exclude(recipt_edrpou__contains='x').annotate(total=Sum('amount')).order_by('-total')[:10]
        transactions = Edata.objects.filter(**search_from_db)
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=transactions_report_(www.rozumnemisto.org).xlsx'
        xlsx_data = WriteToExcel(transactions, request.session['town_name'], townslug, daterange, fop_rating, uric_rating)
        Edata.objects.filter(rand_ind=rand_ind).delete()  # видаляємо усі записи по ідентифікатору
        response.write(xlsx_data)
        return response



#Экспортируем в эксель-файл платежи получателя
def exportToExcelRecipient(request, townslug, receiver):
    from .exportExcelUtilsRecipient import WriteToExcel
    if ("town" in request.session):
        town = Town.objects.get(pk=request.session['town'])
        payers_dict = TownEdrpou.objects.filter(koatuu=town.koatuu)[:500]
            # town.townedrpou_set.all()
        ###Формируем поисковый запрос
        # Плательщики/плательщик
        payers = []

        if ('payer' in request.session):
            if (request.session['payer'] != '0'):
                payers = [request.session['payer']]
            else:
                for payer in payers_dict:
                    payer = payer.code.strip()
                    payers.append(payer)
                if not (payers):
                    raise ObjectDoesNotExist("Не знайдені коди ЕДРПОУ для вибраного міста")
        else:
            request.session['payer'] = '0'
            for payer in payers_dict:
                payer = payer.code.strip()
                payers.append(payer)
            if not (payers):
                raise ObjectDoesNotExist("Не знайдені коди ЕДРПОУ для вибраного міста")

        rand_ind = randrange(100000000)
        search_from_db = {"rand_ind": rand_ind}
        search_from_db_i = search_from_db.copy()
        receiver_name = ''
        data = {"payers_edrpous": payers}

        # TODO: Сделать проверку на буквенное или цифровое значение получателя платежа

        if (receiver == None):
            raise ObjectDoesNotExist("Невказано коду ЄРДПОУ отримувача або назва")
        elif (receiver.isdigit()):
            data.update({"recipt_edrpous": receiver})
        else:
            str_original = receiver
            receiver_name = receiver
            str_i = str_original.replace('і', 'i')
            search_from_db.update({"recipt_name__icontains": str_original})
            search_from_db_i.update({"recipt_name__icontains": str_i})


        if (('date_from' in request.session and 'date_to' in request.session) and not (request.session['date_from'] == '' and request.session['date_to'] == '')):
            data.update({"startdate": request.session['date_from']})
            data.update({"enddate": request.session['date_to']})
            daterange = 'Показано платежі з ' + request.session['date_from'] + ' по ' + request.session['date_to']

        else:
            enddate_obj = datetime.datetime.now()
            startdate_obj = enddate_obj - datetime.timedelta(days=7)
            startdate = startdate_obj.strftime('%d-%m-%Y')
            enddate = enddate_obj.strftime('%d-%m-%Y')
            data.update({"startdate": startdate})
            data.update({"enddate": enddate})
            daterange = 'Показано платежі з ' + startdate + ' по ' + enddate

        headers = {'content-type': 'application/json'}
        r = requests.post(EDATA_URL, data=json.dumps(data), headers=headers)
        data = r.content.decode("UTF-8")
        data = json.loads(data)

        # Сохраняем данные в нашу БД
        _seveToDB(data, town, rand_ind)

        data = Edata.objects.filter(**search_from_db)
        if data:
            receiver_name = data[0].recipt_name
        if (search_from_db_i):
            from itertools import chain
            data_i = Edata.objects.filter(**search_from_db_i)
            result_list = list(chain(data_i, data))
        transactions = Edata.objects.filter(**search_from_db)
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=transactions_report_recipient(www.rozumnemisto.org).xlsx'

        xlsx_data = WriteToExcel(transactions, request.session['town_name'], townslug, daterange, receiver_name )

        Edata.objects.filter(rand_ind=rand_ind).delete()  # видаляємо усі записи по ідентифікатору
        response.write(xlsx_data)
        return response
