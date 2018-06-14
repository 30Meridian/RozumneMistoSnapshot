from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from .models import *
import weunion.settings
from weunion.models import Town
from django.core.exceptions import PermissionDenied
from .forms import Add as SmartroadsForm
from django.core.urlresolvers import reverse
#Ключ для АПИ
API_KEY = weunion.settings.GOOGLE_API_KEY

def index(request, townslug):
    is_allowed = False #модераторы или админы?

    #модераторы или админы?
    if (request.user.is_authenticated() and request.user.is_active):
        if request.user.isAllowedToModerate(request.session["town"], 'Smartroads'):
            is_allowed =True #дать возможность на манипулирование данными

    issues_list = SmartroadsIssues.objects.filter(town_ref=request.session['town'])
    town = get_object_or_404(Town, pk = request.session['town'])
    return render(request,'smartroads/index.html',{'list': issues_list,'api_key': API_KEY,'town': town,'is_allowed': is_allowed})

def add(request, townslug):
    if(request.user.is_authenticated() and request.user.is_active):
        if request.user.isAllowedToModerate(request.session["town"], 'Smartroads'):
            town = Town.objects.get(pk=request.session["town"])
            if request.method == 'POST':
                form = SmartroadsForm(request.POST or None)
                #fill a model from a POST
                if form.is_valid():
                    instance = form.save(commit=False)
                    instance.town_ref = town
                    instance.user_ref= request.user
                    instance.status_ref = SmartroadsStatuses.objects.get(pk = request.POST.get('status'))
                    instance.isblock = 0
                    instance.save()
                    return redirect(reverse('smartroads:card', args=(instance.id,)))
                else:
                    return render(request, 'smartroads/add.html', {'form': form, 'api_key':API_KEY,'lat': town.map_lat, 'lon': town.map_lon,'zoom': town.zoom})
            else:
                form = SmartroadsForm()
                return render(request, 'smartroads/add.html', {'form': form, 'api_key':API_KEY,'lat': town.map_lat, 'lon': town.map_lon,'zoom': town.zoom})
        else:
            raise PermissionDenied("Доступ заборонено")
    else:
        raise PermissionDenied("Доступ заборонено")

def card(request,issue_id, townslug):
    issue = get_object_or_404(SmartroadsIssues,pk=issue_id)
    is_allowed = False

    if (request.user.is_authenticated() and request.user.is_active):
        if request.user.isAllowedToModerate(request.session["town"], 'Smartroads'):
            is_allowed = True
    return render(request,'smartroads/card.html',{'api_key': API_KEY,'issue': issue,'is_allowed':is_allowed})

def edit(request, issue_id, townslug):
    if (request.user.is_authenticated() and request.user.is_active):
        if request.user.isAllowedToModerate(request.session["town"], 'SmartRoads'):
            town = Town.objects.get(pk=request.session["town"])
            issue = get_object_or_404(SmartroadsIssues, pk=issue_id)
            form = SmartroadsForm(instance=issue)
            if request.method == 'POST':
                form = SmartroadsForm(request.POST or None, instance=issue)
                # fill a model from a POST
                if form.is_valid():
                    instance = form.save(commit=False)
                    instance.status_ref = SmartroadsStatuses.objects.get(pk=request.POST.get('status'))
                    instance.save()
                    return redirect('../../smartroads/%s' % instance.id)
                else:
                    return render(request, '../smartroads/edit.html',
                                  {'form': form, 'api_key': API_KEY, 'lat': town.map_lat, 'lon': town.map_lon,
                                   'zoom': town.zoom,'id': issue_id,'lon_issue':issue.lon,'lat_issue':issue.lat})
            else:

                return render(request, 'smartroads/edit.html',
                              {'form': form, 'api_key': API_KEY, 'lat': town.map_lat, 'lon': town.map_lon,
                               'zoom': town.zoom,'status': issue.status_ref.id,'id': issue_id,'lon_issue':issue.lon,'lat_issue':issue.lat})
        else:
            raise PermissionDenied("Доступ заборонено")
    else:
        raise PermissionDenied("Доступ заборонено")

def delete_issue(request,issue_id, townslug):
    if (request.user.is_authenticated() and request.user.is_active):
        if request.user.isAllowedToModerate(request.session["town"], 'SmartRoads'):
            issue = get_object_or_404(SmartroadsIssues, pk=issue_id)
            issue.delete()
            return redirect('../../smartroads/')

        else:
            raise PermissionDenied("Доступ заборонено")
    else:
        raise PermissionDenied("Доступ заборонено")