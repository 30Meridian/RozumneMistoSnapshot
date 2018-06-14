from django.shortcuts import render,redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from allauth.account.decorators import verified_email_required
from weunion.models import Town
from datetime import datetime
from .forms import ProjectAdd
from  .models import CrowdfoundingStatuses


def index(request):
    '''Метод показывает список проектов'''
    return render(request,'crowdfunding/index.html')


@verified_email_required
def add(request):
    '''Показывает форму добавления нового проекта'''
    if(request.user.is_authenticated() and request.user.is_active):
            if request.method == 'POST':
                town = Town.objects.get(pk=request.session["town"])
                form = ProjectAdd(request.POST or None, request.FILES)

                #fill a model from a POST
                if form.is_valid():
                    instance = form.save(commit=False)
                    instance.town_ref = town
                    instance.image = form.cleaned_data['image']
                    instance.user_owner_ref = request.user
                    instance.status_ref.id = 0
                    instance.save()
                    return redirect(reverse('crowdfunding:card', args=(instance.id,)))
                else:
                    return render(request, 'add_project.html', {'form': form})
            else:
                form = ProjectAdd()
                return render(request, 'add_project.html', {'form': form})
    else:
        raise PermissionDenied("Доступ заборонено")


def card(request):
    '''Показываем карточку проекта'''
    pass


def approve(request):
    '''Модератор выполняет проверку проекта, пользователя и принимает решения "Разрешит публикацию проекта"'''
    pass


def disapprove(request):
    '''Модератор выполняет проверку проекта, пользователя и принимает решения "Отклонить публикацию проекта"'''
    pass


def donate(request):
    '''Обработка кнопки "Підтримати"'''
    pass


def reportByProject(request, proj_id):
    '''Отчет по проекту'''
    pass