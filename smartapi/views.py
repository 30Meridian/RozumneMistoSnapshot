import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, get_list_or_404, render
from weunion.models import User,Town,Regions
from .models import AuthUserApiKeys
from django.core.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt


#@csrf_exempt - привинтивный декоратор для подавления проверки csrf-подписи

@csrf_exempt
def router(request):
    if(request.method == "POST"):
        if request.POST:
            try:
                allowed = get_object_or_404(AuthUserApiKeys, apikey=request.POST['apikey'])
            except:
                return JsonResponse({'error': 'Вкажіть, будь ласка, вірний ключ API'})

            if('command' in request.POST):
                data = '' #сущности, которые мы должны веруть клиенту
                command = request.POST['command']
                if(command == 'gettowns'):
                    data = _getLocation()

                elif(command == 'gettownsbyreg'):
                    try:
                        regid=request.POST['regid']
                    except:
                        return JsonResponse({'error': "Акажіть ID регіону (regid)"})
                    data = _getTownsByReg(regid)

                elif(command == 'gettownbyid'):
                    try:
                        townid=request.POST['townid']
                    except:
                        return JsonResponse({'error': "Акажіть ID міста (townid)"})
                    data = _getTownById(request.POST['townid'])

                elif(command == 'getuserbyid'):
                    try:
                        townid=request.POST['uid']
                    except:
                        return JsonResponse({'error': "Акажіть ID користувача (uid)"})
                    data = _getUserById(request.POST['uid'])
                elif(command == 'getuserbyemail'):
                    try:
                        townid=request.POST['email']
                    except:
                        return JsonResponse({'error': "Акажіть email користувача (email)"})
                    data = _getUserByEmail(request.POST['email'])

                elif(command == 'getlastpetitions'):
                    try:
                        count = request.POST['count']
                        statusid = request.POST['statusid']
                    except:
                        count = None
                        statusid = None
                    data = _getLastPetitions(request.POST['townid'], count, statusid)


                elif(command == 'getlastdefects'):
                    try:
                        count = request.POST['count']
                    except:
                        count = None
                    data = _getLastDefects(request.POST['townid'], count)
                elif(command == 'getlastnews'):
                    try:
                        count = request.POST['count']
                    except:
                        count = None
                    data = _getLastNews(request.POST['townid'], count)
                elif(command == 'getlastpolls'):
                    try:
                        count = request.POST['count']
                    except:
                        count = None
                    data = _getLastPolls(request.POST['townid'], count)
                else:
                    return JsonResponse({'error': "Команда не розпізнана"})
                return  JsonResponse(data)#возвращаем конечному пользователю данные
            else:
                return JsonResponse({'error': 'Виберіть, будь ласка, комaнду для API'})
        else:
            clients_post = json.loads(request.body.decode("UTF-8"))
            try:
                allowed = get_object_or_404(AuthUserApiKeys, apikey=clients_post['apikey'])
            except:
                return JsonResponse({'error': 'Вкажіть, будь ласка, вірний ключ API'})

            if ('command' in clients_post):
                data = ''  # сущности, которые мы должны веруть клиенту
                command = clients_post['command']
                if (command == 'gettowns'):
                    data = _getLocation()

                elif (command == 'gettownsbyreg'):
                    try:
                        regid = clients_post['regid']
                    except:
                        return JsonResponse({'error': "Акажіть ID регіону (regid)"})
                    data = _getTownsByReg(regid)

                elif (command == 'gettownbyid'):
                    try:
                        townid = clients_post['townid']
                    except:
                        return JsonResponse({'error': "Акажіть ID міста (townid)"})
                    data = _getTownById(clients_post['townid'])

                elif (command == 'getuserbyid'):
                    try:
                        townid = clients_post['uid']
                    except:
                        return JsonResponse({'error': "Акажіть ID користувача (uid)"})
                    data = _getUserById(clients_post['uid'])
                elif (command == 'getuserbyemail'):
                    try:
                        townid = clients_post['email']
                    except:
                        return JsonResponse({'error': "Акажіть email користувача (email)"})
                    data = _getUserByEmail(clients_post['email'])

                elif (command == 'getlastpetitions'):
                    try:
                        count = clients_post['count']
                        statusid = clients_post['statusid']
                    except:
                        count = None
                        statusid = None
                    data = _getLastPetitions(clients_post['townid'], count, statusid)

                elif (command == 'getlastdefects'):
                    try:
                        count = clients_post['count']
                    except:
                        count = None
                    data = _getLastDefects(clients_post['townid'], count)
                elif (command == 'getlastnews'):
                    try:
                        count = clients_post['count']
                    except:
                        count = None
                    data = _getLastNews(clients_post['townid'], count)
                elif (command == 'getlastpolls'):
                    try:
                        count = clients_post['count']
                    except:
                        count = None
                    data = _getLastPolls(clients_post['townid'], count)
                else:
                    return JsonResponse({'error': "Команда не розпізнана"})
                return JsonResponse(data)  # возвращаем конечному пользователю данные
            else:
                return JsonResponse({'error': 'Виберіть, будь ласка, комaнду для API'})

    else:

        return render(request,'smartapi/api.html',_page(request))



#Возвращеет JSON опитування
def _getLastPolls(townid, count=5):
    if(townid):
        if(count):
            count = int(count)

        from polls.models import Poll
        polls = {'polls':[]}

        for poll in Poll.objects.filter(active=1,archive=0, town=townid).order_by('id')[:count]:
            poll = {'id': poll.id, 'question': poll.question,'description': poll.description, 'date_end': poll.date_end}
            polls['polls'].append(poll)

        return polls



#Возвращеет JSON новостей
def _getLastNews(townid, count=5):
    if(townid):
        if(count):
            count = int(count)

        from news.models import News
        news = {'news':[]}

        for n in News.objects.filter(town=townid, publish=1).order_by('-datetime_publish')[:count]:
            n = {'id':n.id,'title':n.title,'date_publish':n.datetime_publish,'description': n.shortdesc,'image':'http://rozumnemisto.org/medial/'+n.mainimg.name}
            news['news'].append(n)

        return news




#Возвращеет JSON дефектов
def _getLastDefects(townid, count=5):
    if(townid):
        if(count):
            count = int(count)

        from defects.models import Issues
        defects = {'defects':[]}

        for defect in [i for i in Issues.objects.filter(parent_task_ref=None, town_ref=townid).order_by('-id') if i.last_issue().status !=0 and i.last_issue().status !=3][:count]:
            defect = {'id':defect.id,'title':defect.title,'description': defect.description,'address': defect.address, 'status':defect.last_issue().status}
            defects['defects'].append(defect)

        return defects




#Возвращеет JSON петиций
def _getLastPetitions(townid, count=5, statusid=2):
    from petitions.models import Petitions
    if(townid):
        if(count):
            count = int(count)
        if (statusid):
            statusid = int(statusid)
        if statusid == 1 or statusid == 3 or statusid == 7:
            petitions = {'petitions': []}

            for petition in Petitions.objects.filter():
                petition = {'Error your statusid is inadmissible': statusid}
                petitions['petitions'].append(petition)
            return petitions
        else:
            petitions = {'petitions':[]}

            for petition in Petitions.objects.filter(town=townid, status=statusid).order_by('-id')[:count]:
                    petition = {'id':petition.id, 'votes': petition.vote_count(), 'votes_needs': petition.town.votes,'title':petition.title,'status': statusid ,'text':petition.text,'claim':petition.claim,\
                                'date':petition.when_approve,'image': 'http://rozumnemisto.org/media/%s' % petition.image,\
                                'url':'http://rozumnemisto.org/%s/petitions/%s' % (petition.town.slug, petition.id)}
                    petitions['petitions'].append(petition)

            return petitions


#Возвращает JSON локации в ассортименте
def _getLocation():
    towns = {'towns':[]} #инициализируем словарик городов
    for town in get_list_or_404(Town, is_active=1):
        town = {'id':town.id,'name':town.name,'type': town.town_type.title,'region': town.region_ref.name }
        towns['towns'].append(town)
    return towns



def _getTownById(townid):
    if(townid):
        try:
            town = get_object_or_404(Town,pk=townid, is_active=1)
            town_dict = {'name': town.name, 'type': town.town_type.title, 'region': town.region_ref.name,
                         'url':'http://rozumnemisto.org/town/%s' % town.slug}
            return town_dict
        except:
            return _sendError("Місто з ID: %s не знайдене!" % townid)

def _getTownsByReg(regid):
    if(regid):
        try:
            towns_objects = Regions.objects.get(pk=regid).town_set.filter(is_active=1)
        except:
            return _sendError("Регіон з ID: %s не знайдений!" % regid)

        towns = {'towns':[]} #инициализируем словарик городов
        for town in towns_objects:
            town = {'id':town.id,'name':town.name,'type': town.town_type.title,'url':'http://rozumnemisto.org/town/%s' % town.slug}
            towns['towns'].append(town)
        return towns

#возвращаем JSON с юзером в ассортименте
def _getUserById(uid):
    if(uid):
        try:
            user = get_object_or_404(User, pk=uid)
            user_dict = {'first_name': user.first_name, 'middle_name': user.middle_name, 'last_name': user.last_name,
                         'phone': user.phone,'email': user.email,'town': user.towns.all()[0].name}
            return user_dict
        except:
            return _sendError("Користувач не знайдений")
    else:
        return _sendError("Вкажіть коректний user ID")

#возвращаем JSON с юзером в ассортименте
def _getUserByEmail(email):
    if(email):
        try:
            user = get_object_or_404(User, email=email)
            user_dict = {'first_name': user.first_name, 'middle_name': user.middle_name, 'last_name': user.last_name,
                         'phone': user.phone,'email': user.email,'town': user.towns.all()[0].name}
            return user_dict
        except:
            return _sendError("Користувач не знайдений")
    else:
        return _sendError("Вкажіть коректний Email")

#Аутендифицируем пользователя
def _loginUser(request, email, password):
    pass


#Возвращалочка ошибки когда пользователь не задал команду для интерфейса
def _sendError(message):
    return {'error':message}

@csrf_exempt
def apitest(request, message):
    return JsonResponse({'error':message},safe=False)

#Генерируем ключик API
def _generateApiKey(request):
    import random
    import string
    from .models import AuthUserApiKeys
    if(request.user.is_authenticated() and request.user.is_active):
        key = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(30))
        userapikey = AuthUserApiKeys()
        userapikey.user_ref = request.user
        userapikey.apikey = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(30))
        userapikey.isblock = 0
        userapikey.save()
        return userapikey.apikey
    else:
        return None

#Страничка API для пользователя
def _page(request):
    if(request.user.is_authenticated() and request.user.is_active):
        try:
            userkey = request.user.authuserapikeys_set.all()[0]
        except:
            userkey = None

        if(userkey):
            apikey = userkey.apikey
        else:
            apikey = _generateApiKey(request)
    else:
        apikey = None

    regions = Regions.objects.all()
    towns = Town.objects.all()

    return {'apikey': apikey,'regions': regions, 'towns': towns}