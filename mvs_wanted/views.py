from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .forms import *
from .models import MvsWantedCategories, MvsWanted
from .forms import MvsWantedAdd #используем класс формы для генерации формы добавления
from defects.models import Town, User
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

def index(request, townslug):
    return render(request, 'mvs_wanted/index.html')

def add(request, townslug):
    if(request.user.is_authenticated() and request.user.is_active):
        allowed = request.user.isAllowedToModerate(request.session["town"], 'MvsWanted')
        if allowed:
            categories = MvsWantedCategories.objects.all()
            if request.method == 'POST':
                #вместо модели используем класс формы (а он уже сам работает с моделью+валидирует поля)
                form = MvsWantedAdd(request.POST, request.FILES)
                #fill a model from a POST
                if form.is_valid():
                    user=request.user
                    instance = form.save(commit=False)
                    instance.owner_user = user
                    instance.town = Town.objects.get(id= request.session["town"])
                    instance.image = form.cleaned_data['image']
                    instance.save()
                    return render(request,'mvs_wanted/thank_you.html')
                else:
                    return render(request, 'mvs_wanted/add.html', {'form': form, 'categories': categories})
            else:
                #создаем объект формы
                form = MvsWantedAdd()
                return render(request, 'mvs_wanted/add.html', {'form': form, 'categories': categories})
        else:
            raise PermissionDenied('Досуп заборонено.')
    else:
        redirect('accounts/signup')


def mvs_wanted(request, mvs_wanted_id, townslug):
       mvs_wanted = get_object_or_404(MvsWanted,id=mvs_wanted_id)

       if not (request.session.has_key('town')):
           request.session['town'] = mvs_wanted.town.id
           request.session['town_name'] = mvs_wanted.town.name

       if request.user.is_authenticated():
           allowed = request.user.isAllowedToModerate(mvs_wanted.town.id, 'MvsWanted')
       else:
           allowed = False

       return render(request, 'mvs_wanted/get.html', {'person': mvs_wanted, 'allowed': allowed})


def list(request, category, townslug):
    try:
        page = request.GET.get('page', 1)
    except PageNotAnInteger:
        page = 1

    if 'town' in request.session:
        p = Paginator(MvsWanted.objects.filter(town = request.session["town"], category = category).order_by("-id"), 25, request=request)
        list = p.page(page)
        categoryObject = MvsWantedCategories.objects.get(id = category)
        if request.user.is_authenticated():
            allowed = request.user.isAllowedToModerate(request.session["town"], 'MvsWanted')
        else:
            allowed = False
            
        return render(request, 'mvs_wanted/list.html',{'list': list, 'category': categoryObject, 'allowed': allowed})
    else:
        return redirect(reverse('regions'))


def print(request, mvs_wanted_id, townslug):
    mvs_wanted = get_object_or_404(MvsWanted, id=mvs_wanted_id)
    name = mvs_wanted.name
    date_of_birth = mvs_wanted.birth_date
    create_date = mvs_wanted.create_date
    town = mvs_wanted.town
    text = mvs_wanted.text
    if request.user.is_authenticated():
        allowed = request.user.isAllowedToModerate(mvs_wanted.town.id, 'MvsWanted')
    else:
        allowed = False

    if allowed:
        owner = get_object_or_404(User, id=mvs_wanted.owner_user.id)
        return render(request, 'mvs_wanted/print.html', {'person': mvs_wanted, 'name': name, 'date_of_birth': date_of_birth, 'create_date': create_date, 'town': town, 'text': text, 'owner': owner})
    else:
        raise PermissionDenied('Доступ заборонено.')


def delete(request, mvs_wanted_id, townslug):
    mvs_wanted = get_object_or_404(MvsWanted, id=mvs_wanted_id)
    allowed = request.user.isAllowedToModerate(mvs_wanted.town.id, 'MvsWanted')

    if request.user.is_authenticated() and allowed:
        name = mvs_wanted.name
        mvs_wanted.delete()
        return render(request, 'mvs_wanted/deleted.html', {'person': name})
    else:
        raise PermissionDenied('Доступ заборонено.')


def edit(request, mvs_wanted_id, townslug):
    mvs_wanted = get_object_or_404(MvsWanted, id=mvs_wanted_id)
    allowed = request.user.isAllowedToModerate(mvs_wanted.town.id, 'MvsWanted')

    if allowed:
        categories = MvsWantedCategories.objects.all()
        if request.method == 'POST':
            form = MvsWantedAdd(request.POST, request.FILES)
            if form.is_valid():
                user = request.user
                instance = form.save(commit=False)
                instance.id = mvs_wanted_id
                instance.owner_user = user
                instance.town = Town.objects.get(id=request.session["town"])
                instance.image = form.cleaned_data['image']
                if not form.cleaned_data['image']:
                    instance.image = mvs_wanted.image
                instance.save()
                return redirect('../' + mvs_wanted_id)
            else:
                return render(request, 'mvs_wanted/edit.html', {'form': form, 'categories': categories, 'person': mvs_wanted})
        else:
            form = MvsWantedAdd(instance=mvs_wanted)
            return render(request, 'mvs_wanted/edit.html', {'form': form, 'categories': categories, 'person': mvs_wanted})
    else:
        raise PermissionDenied('Доступ заборонено.')
