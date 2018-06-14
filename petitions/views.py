from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .forms import *
from .models import PetitionsStatuses,Petitions, PetitionsVoices
from defects.models import Town, User
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from .helper import Activity, ActivityMail, get_recipient_of_petition
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
import datetime
import time
from ipware.ip import get_ip
from weunion.settings import CRON_SECRET, KARMA
from allauth.account.decorators import verified_email_required
from weunion.helper import Karma

#если админ или модер - показываем на главной петиции на модерации

def index(request, townslug):
    if(request.user.is_authenticated() and request.user.is_active):
        if request.user.isAllowedToModerate(request.session["town"], 'Petitions'):
            return redirect('../petitions/moderate')
        else:
            return redirect('../petitions/status/2')
    return redirect('../petitions/status/2')

#добавляем петицию (показываем форму)
@verified_email_required
def add(request, townslug):
    petition_to = get_recipient_of_petition(Town.objects.get(id=request.user.towns.all()[0].id))
    if(request.user.is_authenticated() and request.user.is_active):
        if request.method == 'POST':
            form = PetitionAdd(request.POST, request.FILES)
            #fill a model from a POST
            if form.is_valid():
                user = request.user
                instance = form.save(commit=False)
                instance.owner_user = user
                instance.town = Town.objects.get(id=request.user.towns.all()[0].id)
                instance.status = PetitionsStatuses.objects.get(pk=1)
                instance.image = form.cleaned_data['image']
                instance.save()
                Activity().add_robot(request, instance.id, 'Петиція створена')
                ActivityMail.sendToModers(request,'Нова петиція на модерацію', 'petition_new.email', instance.town.id, {'petition_id':instance.id, 'title': instance.title,'townslug':townslug})
                ActivityMail.sendToModers(request,'Ваша петиція направлена на модерацію', 'petition_change_status.email', instance.town.id, {'petition_id':instance.id, 'title': instance.title, 'status':'На модерації','townslug':townslug}, [instance.owner_user.email] )
                return render(request,'thank_you.html')
            else:
                return render(request, 'add_petition.html', {'form': form, 'petition_to': petition_to})
        else:
            form = PetitionAdd()
            return render(request, 'add_petition.html', {'form': form, 'petition_to': petition_to})
    else:
        redirect('accounts/signup')


#проверяем кроном просроченые петиции и переносим в архивные
def checktimeout(request, secret, townslug):
    if(secret == CRON_SECRET):
       petitions = Petitions.objects.filter(status=2)
       count = 0
       status = PetitionsStatuses.objects.get(pk=5)
       for petition in petitions:
           need_votes =  petition.town.votes
           pet_days = petition.town.pet_days
           date_start = petition.when_approve
           days_end = date_start + datetime.timedelta(days=pet_days)
           day_now = datetime.datetime.now()
           days_left = days_end - day_now

           if(days_left.days < 0):
               petition.status= status # делаем архивной если у петиции кончилось время сбора подписей и она не набрала нужного количества голосов
               petition.save()
               Activity().add(request, petition.id, 'Автоматична зміна статусу на "Архівна"')
               ActivityMail.sendToModers(request,'Петиція НЕ набрала необхідну кількість голосів і переміщена в архів.', 'petition_change_status.email', petition.town.id, {'petition_id':petition.id, 'title': petition.title, 'status':'Архівна','townslug':townslug})
               ActivityMail.sendToModers(request,'Ваша петиція НЕ набрала необхідну кількість голосів і переміщена в архів', 'petition_change_status.email', petition.town.id, {'petition_id':petition.id, 'title': petition.title, 'status':'Архівна','townslug':townslug}, [petition.owner_user.email])
               count +=1

       if(count):
           return HttpResponse('Done! Find: '+str(count)+' petition(-s)')
       else:
           return HttpResponse("Not found any petitions that mutch enddate!")
    else:
        raise PermissionDenied('Досуп заборонено.')

#Отображаем петицию
def petition(request, petition_id, townslug):
    petition = get_object_or_404(Petitions,id=petition_id)
    town = Town.objects.get(id=petition.town.id)
    petition_to = get_recipient_of_petition(town)
    need_votes =  town.votes
    pet_days = town.pet_days
    petition_number = town.pet_number_templ % (petition_id)
    allowed = False
    activities = None
    if not(request.session.has_key('town')):
        request.session['town'] = petition.town.id
        request.session['town_name'] = petition.town.name

    if request.user.is_authenticated():
        allowed = request.user.isAllowedToModerate(petition.town.id, 'Petitions')
    else:
        allowed = False

    if(petition.status.id == 1 and not allowed):
        raise PermissionDenied("Перегляд петицій, що знаходяться на модерації не дозволено!")

    if(allowed):
        activities = petition.petitionsactivity_set.all().order_by("-id")

    form_chagestatus = PetitionChangeStatus()

    try:
        page = request.GET.get('page', 1)
    except PageNotAnInteger:
        vpage = 1

    p = Paginator(PetitionsVoices.objects.filter(petition=petition_id).exclude(block=1).all(),9, request=request)
    votes = p.page(page)
    votes_count =  PetitionsVoices.objects.filter(petition=petition_id).exclude(block=1).all().count()
    fullname =  get_object_or_404(User,id = petition.owner_user.id).get_full_name_atall()
    end_date = False

    if(petition.status.id == 5):
        date_start = petition.when_approve
        end_date = date_start + datetime.timedelta(days=pet_days)

    if(petition.status.id == 2):
        can_vote = False
        if (request.user.is_authenticated() and request.user.is_active) and \
            petition.town in request.user.towns.all():
                can_vote = True
        date_start = petition.when_approve
        days_end = date_start + datetime.timedelta(days=pet_days+1)
        day_now = datetime.datetime.now()
        days_left = days_end - day_now
        return render(request, 'petition.html',{
            'petition': petition,
            'days_left': days_left.days,
            'pet_days':pet_days,
            'needvotes':need_votes,
            'petition_number': petition_number,
            'fullname': fullname,
            'votes': votes,
            'votes_count': votes_count,
            'allowed': allowed,
            'form_chagestatus': form_chagestatus,
            'getusersign': _getusersign(request, petition_id),
            'activities': activities,
            'end_date': end_date,
            'can_vote': can_vote,
            'petition_to': petition_to,
            })
    else:
        return render(request, 'petition.html',{
            'petition': petition,
            'pet_days':pet_days,
            'needvotes':need_votes,
            'fullname': fullname,
            'petition_number': petition_number,
            'allowed': allowed,
            'form_chagestatus': form_chagestatus,
            'votes': votes,
            'votes_count': votes_count,
            'getusersign': _getusersign(request,petition_id),
            'activities':activities,
            'end_date':end_date,
            'petition_to': petition_to,
        })


# Показываем список петиций
def list(request, status, townslug):

    try:
        page = request.GET.get('page', 1)
    except PageNotAnInteger:
        page = 1

    if 'town' in request.session:

        p = Paginator(Petitions.objects.filter(town = request.session["town"], status = status).order_by("-id"), 25, request=request)
        petitions = p.page(page)

        if status == '2':
            return render(request, 'petitions_list_2.html',{'petitions': petitions})
        elif status == '3':
            return render(request, 'petitions_list_3.html',{'petitions': petitions})
        elif status == '4':
            return render(request, 'petitions_list_4.html',{'petitions': petitions})
        elif status == '5':
            return render(request, 'petitions_list_5.html',{'petitions': petitions})
        elif status == '6':
            return render(request, 'petitions_list_6.html',{'petitions': petitions})
        elif status == '8':
            return render(request, 'petitions_list_8.html',{'petitions': petitions})
    else:
        return redirect(reverse('regions'))


# Показываем список петиций
def moderate(request, townslug):

    try:
        page = request.GET.get('page', 1)
    except PageNotAnInteger:
        page = 1

    if 'town' in request.session:

        petitions_moder = Petitions.objects.filter(town = request.session["town"]).exclude(status__in=[2, 3, 4, 5, 6, 7]).all().order_by('status')
        petitions_hidden = Petitions.objects.filter(town = request.session["town"]).exclude(status__in=[1, 2, 3, 4, 5, 6, 8]).all().order_by('status')


        if(request.user.is_authenticated() and request.user.is_active):
            if request.user.isAllowedToModerate(request.session["town"], 'Petitions'):
                    return render(request, 'moderate.html',{'petitions_moder': petitions_moder, 'petitions_hidden': petitions_hidden})
            else:
                raise PermissionDenied('Доступ заборонено')
        else:
            raise PermissionDenied('Доступ заборонено')
    else:
        return redirect(reverse('regions'))


#Правила петиций
def rules(request, townslug):
    return render(request, 'rules.html')


#Помощь
def help(request, townslug):
    return render(request, 'help_pet.html')

#отдать cвой голос
@verified_email_required
def vote(request, petition_id, townslug):
    if(request.user.is_authenticated() and request.user.is_active):
        petition = get_object_or_404(Petitions, id=petition_id)
        if petition.town in request.user.towns.all():
            vote = PetitionsVoices()
            vote.petition_id = petition_id
            vote.user = request.user
            vote.ip = get_ip(request)
            vote.save()
            Karma.add(request.user,KARMA['PETITION_VOTE'],"Голосування за петицію", "Петиції")
            votes_count =  PetitionsVoices.objects.filter(petition=petition_id).exclude(block=1).all().count()
            if (votes_count >=  petition.town.votes):
                status = PetitionsStatuses.objects.get(pk=8)
                petition.status = status
                petition.save()

                Activity().add(request, petition_id, 'Автоматична зміна статусу на "На перевірці голосів"')
                ActivityMail.sendToModers(request,'Петиція набрала необхідну кількість голосів. Перевірте підписи.', 'petition_change_status.email', petition.town.id, {'petition_id':petition.id, 'title': petition.title, 'status':'На перевірці голосів','townslug':townslug})
                ActivityMail.sendToModers(request,'Ваша петиція набрала необхідну кількість голосів і знаходиться на перевірці підписів', 'petition_change_status.email', petition.town.id, {'petition_id':petition.id, 'title': petition.title, 'status':'На перевірці голосів','townslug':townslug}, [petition.owner_user.email])
            return redirect('../../petitions/%s' % petition_id)
        else:
            # raise PermissionDenied('Доступ заборонено')
            return render(request, '403.html', {'exception': "Ви намагаєтесь підписати петицію іншого населеного пункту, у якому Ви не зареєстровані."})
    else:
        raise PermissionDenied('Доступ заборонено')


#отдать/забрать свой голос
@verified_email_required
def disvote(request, petition_id, townslug):
    if(request.user.is_authenticated() and request.user.is_active):
        petition = get_object_or_404(Petitions, id=petition_id)
        if petition.town in request.user.towns.all():
            vote = get_object_or_404(PetitionsVoices,petition=petition_id, user= request.user.id)
            vote.delete()
            Karma.add(request.user,KARMA['PETITION_DISVOTE'],"Забрано голос з петиції", "Петиції")
            return redirect('../../petitions/%s' % petition_id)
        else:
            raise PermissionDenied('Доступ заборонено')
    else:
        raise PermissionDenied('Доступ заборонено')

#проверяем голосовал ли пользователь за петицию
def _getusersign(request, petition_id):

    if(request.user in [ p.user for p in PetitionsVoices.objects.filter(petition = petition_id)]):
        return True
    else:
        return False


#Изменение статусов
def approve(request,petition_id, townslug):
    """Апруваем петицию"""
    petition = get_object_or_404(Petitions,id=petition_id)
    if request.user.isAllowedToModerate(petition.town.id, 'Petitions'):
           petition = get_object_or_404(Petitions,id=petition_id)
           status = get_object_or_404(PetitionsStatuses,id=2)
           try:
                petition.status = status
                petition.when_approve = time.strftime('%Y-%m-%d %H:%M:%S')
                petition.save()
                Karma.add(petition.owner_user,KARMA['PETITION_WAS_APPROVE'],"Створення власної петиції, що пройшла модерацію", "Петиції")
                Activity().add(request, petition_id, 'Зміна статусу на Опублікована')
                ActivityMail.sendToModers(request,'Петиція пройшла модерацію і опублікована', 'petition_change_status.email', petition.town.id, {'petition_id':petition.id, 'title': petition.title, 'status':'Триває збір підписів','townslug':townslug})
                ActivityMail.sendToModers(request,'Ваша петиція пройшла модерацію і опублікована', 'petition_change_status.email', petition.town.id, {'petition_id':petition.id, 'title': petition.title, 'status':'Триває збір підписів','townslug':townslug}, [petition.owner_user.email])

                return redirect('../../petitions/%s' % petition_id)
           except:
                pass
    else:
       raise PermissionDenied('Доступ заборонено')


def onconsideration(request,petition_id, townslug):
    """Перемещаем петицию в статус 'Расматривается' """
    petition = get_object_or_404(Petitions,id=petition_id)
    if request.user.isAllowedToModerate(petition.town.id, 'Petitions'):
           petition = get_object_or_404(Petitions,id=petition_id)
           status = get_object_or_404(PetitionsStatuses,id=6)
           try:
                petition.status = status
                petition.when_approve = time.strftime('%Y-%m-%d %H:%M:%S')
                petition.save()
                Karma.add(petition.owner_user,KARMA['PETITION_ONCONSIDERATION'],"Ваша петиція набрала необхідну кількість голосів і пройшла їх перевірку", "Петиції")
                Activity().add(request, petition_id, 'Зміна статусу на "Розглядається"')
                ActivityMail.sendToModers(request,'Петиція пройшла перевірку голосів і тепер знаходиться на розгляді', 'petition_change_status.email', petition.town.id, {'petition_id':petition.id, 'title': petition.title, 'status':'Розглядається','townslug':townslug})
                ActivityMail.sendToModers(request,'Ваша петиція пройшла перевірку голосів і тепер знаходиться на розгляді', 'petition_change_status.email', petition.town.id, {'petition_id':petition.id, 'title': petition.title, 'status':'Розглядається','townslug':townslug}, [petition.owner_user.email])
                return redirect('../../petitions/%s' % petition_id)
           except:
                pass
    else:
       raise PermissionDenied('Доступ заборонено')


def tomoderate(request, petition_id, townslug):
    """Возвращеем петициию на модерацию"""
    petition = get_object_or_404(Petitions,id=petition_id)
    if request.user.isAllowedToModerate(petition.town.id, 'Petitions'):
           petition = get_object_or_404(Petitions,id=petition_id)
           status = get_object_or_404(PetitionsStatuses,id=1)
           try:
                petition.status = status
                petition.when_approve = time.strftime('%Y-%m-%d %H:%M:%S')
                petition.save()
                Activity().add(request, petition_id, 'Зміна статусу на "Повернуто на домодерацію"')
                ActivityMail.sendToModers(request,'Петиція повернута на домодерацію', 'petition_change_status.email', petition.town.id, {'petition_id':petition.id, 'title': petition.title, 'status':'Повернуто на домодерацію','townslug':townslug})
                ActivityMail.sendToModers(request,'Ваша петиція повернута на домодерацію', 'petition_change_status.email', petition.town.id, {'petition_id':petition.id, 'title': petition.title, 'status':'Повернуто на домодерацію','townslug':townslug}, [petition.owner_user.email])
                return redirect('../../petitions/%s' % petition_id)
           except:
                pass
    else:
       raise PermissionDenied('Доступ заборонено')


def returntoactive(request, townslug):
    """возвращаем петицию на сбор подписей"""
    if request.POST:
        petition_id = request.POST['petition_id']
        form = PetitionChangeStatus(request.POST)
        petition = get_object_or_404(Petitions,id=petition_id)
        if request.user.isAllowedToModerate(petition.town.id, 'Petitions'):
            town_slug = Town.objects.get(id=request.session['town']).slug
            status = get_object_or_404(PetitionsStatuses,id=2) #Статус: Активна
            if form.is_valid():
                petition.status = status
                petition.resolution = form.cleaned_data['resolution']
                petition.save()
                Activity().add(request, petition_id, 'Зміна статусу на "Повернута на збір підписів. Причина: '+petition.resolution+'"')
                ActivityMail.sendToModers(request,'Петиція повернута на добір підписів зі статусу "На розгляді"', 'petition_change_status.email', petition.town.id, {'petition_id':petition.id, 'title': petition.title, 'status': 'Розглядається', 'resolution': 'Причина: '+petition.resolution})
                ActivityMail.sendToModers(request,'Ваша петиція повернута модератором на добір підписів', 'petition_change_status.email', petition.town.id, {'petition_id':petition.id, 'title': petition.title, 'status': 'Повернено на збір підписів', 'resolution': 'Причина: '+petition.resolution}, [petition.owner_user.email])
                return redirect(reverse('petitions:petition', args=(town_slug, petition_id,)))
            else:
                return HttpResponse("Помилка. Зверніть увагу на поле резолюція, воно має бути заповнене")
        else:
           raise PermissionDenied('Досуп заборонено')
    else:
        raise PermissionDenied('Досуп заборонено. POST')


def disapprove(request, townslug):
    """Отклоняем петицию"""
    if request.POST:
        petition_id = request.POST['petition_id']
        form = PetitionChangeStatus(request.POST)
        petition = get_object_or_404(Petitions,id=petition_id)
        if request.user.isAllowedToModerate(petition.town.id, 'Petitions'):
            status = get_object_or_404(PetitionsStatuses,id=3) #Статус: Відхилена модератором
            if form.is_valid():
                petition.status = status
                petition.resolution = form.cleaned_data['resolution']
                petition.save()
                Activity().add(request, petition_id, 'Зміна статусу на "Відхилена модератором Причина: '+petition.resolution+'"')
                ActivityMail.sendToModers(request,'Петиція відхилена модератором', 'petition_change_status.email', petition.town.id, {'petition_id':petition.id, 'title': petition.title, 'status': 'Відхилена модератором', 'resolution': 'Причина: '+petition.resolution,'townslug':townslug})
                ActivityMail.sendToModers(request,'Ваша петиція відхилена модератором', 'petition_change_status.email', petition.town.id, {'petition_id':petition.id, 'title': petition.title, 'status': 'Відхилена модератором', 'resolution': 'Причина: '+petition.resolution,'townslug':townslug}, [petition.owner_user.email])
                return redirect('../../petitions/%s' % petition_id)
            else:
                return HttpResponse("Помилка. Зверніть увагу на поле резолюція, воно має бути заповнене")
        else:
           raise PermissionDenied('Досуп заборонено')
    else:
        raise PermissionDenied('Досуп заборонено. POST')


def hidepetition(request, townslug):
    """Прячим петицию петицию"""
    if request.POST:
        petition_id = request.POST['petition_id']
        form = PetitionChangeStatus(request.POST)#
        petition = get_object_or_404(Petitions,id=petition_id)
        if request.user.isAllowedToModerate(petition.town.id, 'Petitions'):
            status = get_object_or_404(PetitionsStatuses,id=7) #Статус: Схована модератором
            if form.is_valid():
                petition.status = status
                petition.resolution = form.cleaned_data['resolution']
                petition.save()
                Activity().add(request, petition_id, 'Зміна статусу на "Модератором відхилив і приховав петицію Причина: '+petition.resolution+'"')
                ActivityMail.sendToModers(request,'Петиція відхилена модератором і їй надано спец.статус "Прихована"', 'petition_change_status.email', petition.town.id, {'petition_id':petition.id, 'title': petition.title, 'status': 'Відхилена модератором і прихована', 'resolution': 'Причина: '+petition.resolution,'townslug':townslug})
                ActivityMail.sendToModers(request,'Ваша петиція відхилена модератором і їй надано спец.статус "Прихована"', 'petition_change_status.email', petition.town.id, {'petition_id':petition.id, 'title': petition.title, 'status': 'Відхилена модератором і прихована', 'resolution': 'Причина: '+petition.resolution,'townslug':townslug}, [petition.owner_user.email])
                return redirect('../../petitions/%s' % petition_id)
            else:
                return HttpResponse("Помилка. Зверніть увагу на поле резолюція, воно має бути заповнене")
        else:
           raise PermissionDenied('Досуп заборонено')
    else:
        raise PermissionDenied('Досуп заборонено. POST')

def done(request, townslug):
    """Петицию рассмотрено"""
    if request.POST:
        petition_id = request.POST['petition_id']
        form = PetitionChangeStatus(request.POST)
        petition = get_object_or_404(Petitions,id=petition_id)
        if request.user.isAllowedToModerate(petition.town.id, 'Petitions'):
            status = get_object_or_404(PetitionsStatuses,id=4) #Статус: Розглянута
            if form.is_valid():
                petition.status = status
                petition.resolution = form.cleaned_data['resolution']
                petition.save()
                Activity().add(request, petition_id, 'Зміна статусу на "Петиція розглянута Резолюція: '+petition.resolution+'"')
                ActivityMail.sendToModers(request,'Петиція розглянута', 'petition_change_status.email', petition.town.id, {'petition_id':petition.id, 'title': petition.title, 'status': 'Розглянута', 'resolution': 'Причина: '+petition.resolution,'townslug':townslug})
                ActivityMail.sendToModers(request,'Ваша петиція розглянута', 'petition_change_status.email', petition.town.id, {'petition_id':petition.id, 'title': petition.title, 'status': 'Розглянута', 'resolution': 'Причина: '+petition.resolution,'townslug':townslug}, [petition.owner_user.email])
                return redirect('../../petitions/%s' % petition_id)
            else:
                return HttpResponse("Помилка. Зверніть увагу на поле резолюція, воно має бути заповнене.")
        else:
           raise PermissionDenied('Досуп заборонено.')
    else:
        raise PermissionDenied('Досуп заборонено.')

#бан модератором пользователя и его голоса согласно регламенту
def ban(request,user_id, petition_id, vote_id, townslug):
    '''забанить подпись пользователя и его самого. Если пользователь уже забанен
    забанить только подпись'''
    from django.db.models import Q
    if(request.user.is_authenticated() and request.user.is_active):
        petition = get_object_or_404(Petitions,id=petition_id)
        if request.user.isAllowedToModerate(petition.town.id, 'Petitions'):
            if user_id and petition_id and vote_id:
                votes = [p.petitionsvoices_set.filter(user=user_id) for p in Petitions.objects.filter(Q(status=2) | Q(status=8)).all()]
                block_voices_number = 0
                for vote in votes:
                        for v in vote:
                            v.block = 1
                            v.save()
                            block_voices_number += 1

                user = get_object_or_404(User, id=user_id)
                if user.is_active == 0:
                    return redirect('../../../../petitions/%s' % petition_id)
                else:
                    user.is_active = 0
                    user.save()
                    Activity().add(request, petition_id, 'Заблокований користувач '+user_id)
                    return redirect('../../../../petitions/%s' % petition_id)
            else:
                raise PermissionDenied('Досуп заборонено.')
        else:
            raise PermissionDenied('Досуп заборонено.')
    else:
        raise PermissionDenied('Досуп заборонено.')


#распечатать петицию
def print(request, petition_id, townslug):
       petition = get_object_or_404(Petitions,id=petition_id)
       town = Town.objects.get(id=request.session["town"])
       petition_to = get_recipient_of_petition(town)
       petition_number = town.pet_number_templ % (petition_id)
       town = Town.objects.get(id=request.session["town"])
       need_votes =  town.votes
       pet_days = town.pet_days
       if request.user.is_authenticated():
          allowed = request.user.isAllowedToModerate(petition.town.id, 'Petitions')
       else:
          allowed = False

       days_end = False
       if (petition.status.id == 5):
           date_start = petition.when_approve
           days_end = date_start + datetime.timedelta(days=pet_days)
           day_now = datetime.datetime.now()

       if allowed:
           votes = PetitionsVoices.objects.filter(petition=petition_id).exclude(block=1).all()
           owner = get_object_or_404(User,id = petition.owner_user.id)
           return render(request, 'petition_print.html',{'petition': petition,'needvotes': need_votes, 'owner': owner,'petition_number': petition_number,'allowed': allowed, 'votes': votes, 'end_date':days_end, 'petition_to': petition_to})
       else:
           raise PermissionDenied('Досуп заборонено.')

def test(request, townslug):
    ActivityMail.sendToModers(request,'Тестовый имейл', 'new_petition.email', 1, {'url':'www.google.com','title': 'Сайт гугла'})
    return HttpResponse("Done!")