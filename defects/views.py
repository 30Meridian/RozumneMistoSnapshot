from django.forms import modelformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from weunion.models import Town, User
from defects.models import Issues, Subcontractors, Documents, Files, IssueFiles, Comments, CommentAttachements
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
import weunion.settings
import base64
import uuid
import sys
import traceback
from PIL import Image, ExifTags
from allauth.account.decorators import verified_email_required
from .helper import ActivityMail
from django.core.exceptions import PermissionDenied
from weunion.helper import Karma
from weunion.settings import KARMA


'''
Please use a  --- request.user.isAllowedToModerate(request.session["town"], 'Defects')---
instead request.user.isModer or isAdmin to check a permission to moderate

Статусы:
0 - На модерації
1 - Відкрита (назначен исполнитель)
2 - Виконана (проставляется исполителем или модератором)
3 - Відбракована (модератором)
4 - Прийнята до виконання (виконавцем)
5 - Запланована (запланирована исполнителем или модератором)
6 - Арбітраж (пользователь не согласен с решением модератора и требует вмешательства третьих лиц)
'''


def index(request, townslug):
    '''list of defects'''
    if(request.user.is_authenticated() and request.user.is_active):
        if request.user.isAllowedToModerate(request.session["town"], 'Defects'):
            return redirect('../defects/moderate')

    if('town' in request.session):
        return redirect('../defects/list')
    else:
        return redirect(reverse('regions'))


def list(request, townslug):
    if('town' in request.session):
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1

        statuses = []
        #Инициалицируем список статусов
        if not('statuses' in request.session):
            statuses = [2,1,4,5]

        #Сбиваем сессию, показываем все статусы кроме не разрешенных или выставляем фильтр
        if('status' in request.GET):
            if(request.GET['status'] == '9'):
                try:
                    del request.session['statuses']
                    statuses = [2,1,4,5]
                except:
                    pass
            else:
                request.session['statuses'] = [int(request.GET['status'])]

        if('statuses' in request.session):
            statuses = request.session['statuses']

        #Тоже самое с подрядными организациями, сбиваем сессию если хотим показать заяваки всег орг. или выставляем фильтр
        if('subcontractor' in request.GET):
            if(request.GET['subcontractor'] == '0'):
               try:
                    del request.session['subcontractor']
               except:
                   pass
            else:
                request.session['subcontractor'] = int(request.GET['subcontractor'])

        town = get_object_or_404(Town, pk = request.session['town'])
        if('subcontractor' in request.session):
            t = Paginator([i for i in Issues.objects.filter(parent_task_ref = None, town_ref = request.session["town"]).order_by('-id') if i.last_issue().status in statuses and i.last_issue().assigned_to.id == request.session['subcontractor'] ], 10, request=request)
            tasks =t.page(page)
            defects_done = len([i for i in Issues.objects.filter(parent_task_ref=None, town_ref=request.session["town"]).order_by('id') if i.last_issue().status ==2 and i.last_issue().assigned_to.id == request.session['subcontractor']])
            defects_open = len([i for i in Issues.objects.filter(parent_task_ref=None, town_ref=request.session["town"]).order_by('id') if i.last_issue().status ==1 and i.last_issue().assigned_to.id == request.session['subcontractor']])
            defects_planning = len([i for i in Issues.objects.filter(parent_task_ref=None, town_ref=request.session["town"]).order_by('id') if i.last_issue().status ==5 and i.last_issue().assigned_to.id == request.session['subcontractor']])
            defects_get = len([i for i in Issues.objects.filter(parent_task_ref=None, town_ref=request.session["town"]).order_by('id') if i.last_issue().status ==4 and i.last_issue().assigned_to.id == request.session['subcontractor']])

        else:
            t = Paginator([i for i in Issues.objects.filter(parent_task_ref = None, town_ref = request.session["town"]).order_by('-id') if i.last_issue().status in statuses ], 10, request=request)
            tasks =t.page(page)
            defects_done = len([i for i in Issues.objects.filter(parent_task_ref=None, town_ref=request.session["town"]).order_by('id') if i.last_issue().status ==2])
            defects_open = len([i for i in Issues.objects.filter(parent_task_ref=None, town_ref=request.session["town"]).order_by('id') if i.last_issue().status ==1])
            defects_planning = len([i for i in Issues.objects.filter(parent_task_ref=None, town_ref=request.session["town"]).order_by('id') if i.last_issue().status ==5])
            defects_get = len([i for i in Issues.objects.filter(parent_task_ref=None, town_ref=request.session["town"]).order_by('id') if i.last_issue().status ==4])

        api_key=weunion.settings.GOOGLE_API_KEY
        subcontractor_list = Subcontractors.objects.filter(town_ref=request.session['town'])

        return render(request, 'index.html',{"issues":tasks,'town': town, 'api_key': api_key,'defects_done': defects_done,'defects_open': defects_open,'defects_planning': defects_planning,'defects_get': defects_get,'subcontractor_list':subcontractor_list })
    else:
        return redirect(reverse('regions'))


def moderate(request, townslug):
    '''Moderator's page'''
    if 'town' in request.session:
        if(request.user.is_authenticated() and request.user.is_active):
            if request.user.isAllowedToModerate(request.session["town"], 'Defects'):
                try:
                    page = request.GET.get('page', 1)
                except PageNotAnInteger:
                    page = 1

                defects_moderate = [i for i in Issues.objects.filter(parent_task_ref=None, town_ref=request.session["town"]).order_by('id') if i.last_issue().status ==0]
                defects_arbitrage = [i for i in Issues.objects.filter(parent_task_ref=None, town_ref=request.session["town"]).order_by('id') if i.last_issue().status ==6]
                defects_disaprove = [i for i in Issues.objects.filter(parent_task_ref=None, town_ref=request.session["town"]).order_by('id') if i.last_issue().status ==3]

                ts = Town.objects.all()
                return render(request, 'moderate_def.html',{"defects_moderate":defects_moderate,"defects_arbitrage":defects_arbitrage,"defects_disaprove":defects_disaprove, "towns": ts})
            else:
                raise PermissionDenied("Доступ заборонено")
        else:
            raise PermissionDenied("Доступ заборонено")
    else:
        return redirect(reverse('regions'))

def mydefects(request, townslug):
    '''list of defects'''
    if(request.user.is_authenticated() and request.user.is_active):

        if 'town' in request.session:
            try:
                page = request.GET.get('page', 1)
            except PageNotAnInteger:
                page = 1
            #TODO: показывать только с особым статусом
            t = Paginator([i for i in Issues.objects.filter(parent_task_ref=None, town_ref=request.session["town"], owner_ref = request.user).order_by('id') if i.last_issue().status !=0 and i.last_issue().status !=3], 10, request=request)
            tasks =t.page(page)
            ts = Town.objects.all()
            return render(request, 'mydefects.html',{"issues":tasks, "towns": ts})
        else:
            return redirect(reverse('regions'))
    else:
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(
            request.get_full_path(),
            reverse('account_login')
        )


@verified_email_required
def add(request, townslug):
    if(request.user.is_authenticated() and request.user.is_active):
        if(request.method=="POST"):
            data=request.POST
            if(len(data["title"])>1 and len(data["description"])>1 and len(data['address'])>1):
                form = Issues()
                user=request.user
                form.owner_ref=user
                town=request.user.towns.first()
                form.town_ref=town
                form.title=data["title"]
                form.description=data["description"]
                form.address=data["address"]
                form.map_lat=data["map_lat"]
                form.map_lon=data["map_lon"]
                #form.parent_task_ref=Issues(id=1)
                form.status=0
                form.assigned_to=Subcontractors.objects.get(pk=2)#TODO:ВАЖНО! Здесь нужно выбрать именно админ группу из нужного города!!!
                #TODO:write valiadation
                #if form.is_valid():
                form.save()
                if("files[]" in data):
                    for filename in data.getlist("files[]"):
                        body64=data["attachements[%s]" % filename]
                        body=""
                        body=base64.b64decode(body64[body64.index(",")+1:])
                        ext = filename.split('.')[-1]
                        sys_filename="%s.%s" % (uuid.uuid4(), ext)
                        path=weunion.settings.MEDIA_ROOT+"/defects/"
                        f=open(path+sys_filename,"wb")
                        file_size=f.write(body)
                        f.close()
                        img=Image.open(path+sys_filename)
                        if(getattr(img,"_getexif",None) is not None and img._getexif()):
                            exif=dict((ExifTags.TAGS[k], v) for k, v in img._getexif().items() if k in ExifTags.TAGS)
                            if('Orientation' in exif):
                                if(exif['Orientation'] == 3):
                                    img=img.rotate(180, expand=True)

                                elif(exif['Orientation'] == 6):
                                    img=img.rotate(270, expand=True)

                                elif(exif['Orientation'] == 8):
                                    img=img.rotate(90, expand=True)

                        img.save(path+sys_filename)
                        img.thumbnail((350,350),Image.ANTIALIAS)
                        img.save(path+"medium."+sys_filename)
                        img.thumbnail((150,150),Image.ANTIALIAS)
                        img.save(path+"thumbnail."+sys_filename)
                        doc = Documents()
                        doc.owner_ref=user
                        #doc.file_ref=filedata
                        doc.name=filename
                        doc.type_name="image"
                        doc.file_name=sys_filename
                        doc.size=file_size
                        doc.save()
                        issuefile=IssueFiles()
                        issuefile.issue_ref=form
                        issuefile.document_ref=doc
                        issuefile.save()
                ActivityMail.sendToModers(request, 'Було додано нову заявку #' + str(
                    form.getFirst().id),
                                          'defect_new.email', form.town_ref.id,
                                          {'title': form.getFirst().title,'townslug':townslug,'defect_id': form.getFirst().id })

                return redirect('../defects/ok')
            else:
                issue = Issues()
                api_key = weunion.settings.GOOGLE_API_KEY
                userTown = request.user.towns.first()
                gmap = {}
                gmap["lon"] = userTown.map_lon
                gmap["lat"] = userTown.map_lat
                gmap["zoom"] = userTown.zoom
                title = request.POST["title"],
                description = request.POST["description"],
                address = request.POST["address"],
                print(request.POST)
                return render(request, 'add.html',
                       {"issue": issue,
                        "townz": Town.objects.all(),
                        "api_key": api_key,
                        "gmap": gmap,
                        "title": title[0],
                        "description": description[0],
                        "address": address[0],
                        "error": "Заповніть назву, опис та адресу дефекту!"
                        },)
        else:
            pass
            #TODO: Print error, saving already inputed data

        issue = Issues()
        api_key=weunion.settings.GOOGLE_API_KEY
        userTown=request.user.towns.first()
        gmap={}
        gmap["lon"]=userTown.map_lon
        gmap["lat"]=userTown.map_lat
        gmap["zoom"]=userTown.zoom
        return render(request, 'add.html',{"issue":issue,"townz":Town.objects.all(),"api_key":api_key,"gmap":gmap})
    else:
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(
            request.get_full_path(),
            reverse('account_signup')
)


def card(request, issue_id, townslug):
    issue = get_object_or_404(Issues, pk=issue_id)

    if(not(request.session.has_key('town'))):
           request.session['town'] = issue.town_ref.id
           request.session['town_name'] = issue.town_ref.name

    allowed = False
    if(request.user.is_authenticated() and request.user.is_active):
        allowed = request.user.isAllowedToModerate(issue.town_ref_id, 'Defects')
    images = []
    api_key = weunion.settings.GOOGLE_API_KEY

    if((issue.last_issue().status == 0 or issue.last_issue().status == 3) and allowed == False ):
        raise PermissionDenied("Доступ заборонено!")
    else:
        return render(request, 'card.html', {"issue": issue,"defect_id": issue_id, "api_key": api_key, "images": images, "allowed": allowed})


def printIssue(request, issue_id, townslug):
    issue = get_object_or_404(Issues, pk=issue_id)
    api_key = weunion.settings.GOOGLE_API_KEY
    return render(request, 'print.html', {"issue": issue, "api_key": api_key})


@verified_email_required
def addComment(request,issue_id, townslug):
    if(request.method=="POST"):
        if(request.user.is_authenticated() and request.user.is_active):
            data=request.POST
            try:
                issue=Issues.objects.get(pk=issue_id)
                last_issue=issue.last_issue()

                if("body" not in data):#return some error
                    pass

                if(issue.town_ref in request.user.towns.all()):#если юзер относится к городу дефекта, может комментировать
                    comment=Comments()
                    comment.owner_ref=request.user
                    comment.issue_ref=last_issue
                    comment.body=data["body"]
                    if("files[]" in data):
                        comment.attachements=True
                    else:
                        comment.attachements=False
                    comment.save()
                    Karma.add(request.user,KARMA['DEFECT_COMMENT'],"Коментар до дефекту", "Дефекти ЖКГ")
                    #TODO: Сделать разссылку по модерам и ответсвенным организациям
                    try:
                        if("files[]" in data):
                            for filename in data.getlist("files[]"):
                                #filedata=Files(body=data["attachements[%s]" % filename])
                                #filedata.save()
                                try:
                                    body64=data["attachements[%s]" % filename]
                                    body=""
                                    body=base64.b64decode(body64[body64.index(",")+1:])
                                    ext = filename.split('.')[-1]
                                    sys_filename="%s.%s" % (uuid.uuid4(), ext)
                                    path=weunion.settings.MEDIA_ROOT+"/defects/comments/"
                                    f=open(path+sys_filename,"wb")
                                    file_size=f.write(body)
                                    f.close()
                                    img=Image.open(path+sys_filename)
                                    img.thumbnail((350,350),Image.ANTIALIAS)
                                    img.save(path+"medium."+sys_filename)
                                    img.thumbnail((150,150),Image.ANTIALIAS)
                                    img.save(path+"thumbnail."+sys_filename)
                                except:
                                    print(str(sys.exc_info()[0])+str(sys.exc_info()[1]))
                                    traceback.print_exc(file=sys.stdout)
                                    return
                                doc = Documents()
                                doc.owner_ref=request.user
                                #doc.file_ref=filedata
                                doc.name=filename
                                doc.type_name="image"
                                doc.file_name=sys_filename
                                doc.size=file_size
                                doc.save()
                                commentfile=CommentAttachements()
                                commentfile.comment_ref=comment
                                commentfile.document_ref=doc
                                commentfile.save()
                                Karma.add(request.user,KARMA['DEFECT_COMMENT'],"Коментар до дефекту", "Дефекти ЖКГ")
                    except:
                        print(str(sys.exc_info()[0])+str(sys.exc_info()[1]))
                        traceback.print_exc(file=sys.stdout)
            except Issues.DoesNotExist:
                #print some error page or send back to index
                return HttpResponseRedirect('../defects')
        else:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(
                request.get_full_path(),
                reverse('account_signup')
            )
    return HttpResponseRedirect('../../defects/%s' % issue_id)

# Назначаем подрядную организацию
def setSubcontractor(request,issue_id, townslug):
    if(request.method=="POST"):
        try:
            issue=Issues.objects.get(pk=issue_id)
            last_issue=issue.last_issue()
            if(request.user.isAllowedToModerate(request.session["town"], 'Defects') and issue.town_ref in request.user.towns.all()):
                subc = Subcontractors.objects.get(pk=request.POST["subc"])
                form = Issues()
                form.owner_ref=request.user
                form.town_ref=issue.town_ref
                form.title="Змiна статусу"
                form.description="Вiдправлено на виконання до "+subc.name
                form.parent_task_ref=last_issue
                form.status=1
                form.assigned_to=subc
                form.save()
                Karma.add(form.getFirst().owner_ref,KARMA['DEFECT_WAS_APPROVE'],"Додано дефект який погодив модератор", "Дефекти ЖКГ")
                ActivityMail.sendToSubcontractors(request,'Заявка #'+str(form.getFirst().id)+' назначена на Вашу організацію', 'defect_subcontractor.email', form.assigned_to.id, {'defect_id':form.getFirst().id, 'title': form.getFirst().title, 'status':'Назначена на Вашу організацію','townslug':townslug})
                ActivityMail.sendToModers(request,'Заявка #'+str(form.getFirst().id)+' пройшла модерацію і було назначено відповідальну підрядну організацію.', 'defect_change_status.email', form.town_ref.id, {'defect_id':form.getFirst().id, 'title': form.getFirst().title, 'status':'Відкрита. Відповідальна організація - '+subc.name,'townslug':townslug})
                ActivityMail.sendToModers(request,'Ваша заявка #'+str(form.getFirst().id)+' пройшла модерацію і було назначено відповідальну підрядну організацію.', 'defect_change_status.email', form.town_ref.id, {'defect_id':form.getFirst().id, 'title': form.getFirst().title, 'status':'Відкрита.  Відповідальна організація - '+subc.name,'townslug':townslug}, [form.owner_ref.email])

        except Issues.DoesNotExist:
            return HttpResponseRedirect('../defects')
    return HttpResponseRedirect('../../defects/%s' % issue_id)


#Ставим статус "Принято к исполнению"
def padding(request,issue_id, townslug):
        try:
            issue=Issues.objects.get(pk=issue_id)
            last_issue=issue.last_issue()
            if((issue.last_issue().assigned_to in request.user.work_for.all()) and issue.town_ref in request.user.towns.all()):
                form = Issues()
                form.owner_ref=request.user
                form.town_ref=issue.town_ref
                form.title="Змiна статусу"
                form.description="Дякуємо! Ваша заявка прийнята у роботу."
                form.parent_task_ref=last_issue
                form.assigned_to=last_issue.assigned_to
                form.status=4
                form.save()
                ActivityMail.sendToModers(request,'Заявка #'+str(form.getFirst().id)+' ПРИЙНЯТА відповідальною організацією.', 'defect_change_status.email', form.town_ref.id, {'defect_id':form.getFirst().id, 'title': form.getFirst().title, 'status':'Прийнята до виконання','townslug':townslug})
                ActivityMail.sendToModers(request,'Ваша заявка #'+str(form.getFirst().id)+' ПРИЙНЯТА відповідальною організацією.', 'defect_change_status.email', form.town_ref.id, {'defect_id':form.getFirst().id, 'title': form.getFirst().title, 'status':'Прийнята до виконання','townslug':townslug}, [form.owner_ref.email])
                return redirect("../../defects/"+issue_id)
            else:
                raise PermissionDenied("Доступ заборонено")

        except Issues.DoesNotExist:
           return HttpResponseRedirect('../../defects')


#Ставим статус "Запланована"
def hold(request,issue_id, townslug):
    if(request.user.is_authenticated() and request.user.is_active):
            try:
                issue=Issues.objects.get(pk=issue_id)
                last_issue=issue.last_issue()
                if(request.user.isAllowedToModerate(request.session["town"], 'Defects') or issue.last_issue().assigned_to in request.user.work_for.all()) and issue.town_ref in request.user.towns.all():
                    form = Issues()
                    form.owner_ref=request.user
                    form.town_ref=issue.town_ref
                    form.title="Змiна статусу"
                    form.description= request.POST['description']
                    form.parent_task_ref=last_issue
                    form.assigned_to=last_issue.assigned_to
                    form.status=5
                    form.save()
                    ActivityMail.sendToModers(request,'Заявка #'+str(form.getFirst().id)+' "ЗАПЛАНОВАНА" відповідальною організацією.', 'defect_change_status.email', form.town_ref.id, {'defect_id':form.getFirst().id, 'title': form.getFirst().title, 'status':'Запланована','resolution':form.description,'townslug':townslug})
                    ActivityMail.sendToModers(request,'Ваша заявка #'+str(form.getFirst().id)+' "ЗАПЛАНОВАНА" відповідальною організацією.', 'defect_change_status.email', form.town_ref.id, {'defect_id':form.getFirst().id, 'title': form.getFirst().title, 'status':'Запланована','resolution':form.description,'townslug':townslug}, [form.owner_ref.email])
                    return redirect("../../defects/"+issue_id)
                else:
                    raise PermissionDenied("Доступ заборонено")
            except Issues.DoesNotExist:
                return HttpResponseRedirect('../defects')
    else:
        raise PermissionDenied("Доступ заборонено")


#Ставим статус "Відхилена"
def disapprove(request,issue_id, townslug):
    if(request.method=="POST"):
        try:
            issue=Issues.objects.get(pk=issue_id)
            last_issue=issue.last_issue()
            if(request.user.isAllowedToModerate(request.session["town"], 'Defects') and issue.town_ref in request.user.towns.all()):
                form = Issues()
                form.owner_ref=request.user
                form.town_ref=issue.town_ref
                form.title="Змiна статусу"
                form.description="Вiдхилено по причині: " + request.POST['description']
                form.parent_task_ref=last_issue
                form.assigned_to=last_issue.assigned_to
                form.status=3
                form.save()
                ActivityMail.sendToModers(request,'Заявка #'+str(form.getFirst().id)+' відхилена модератором.', 'defect_change_status.email', form.town_ref.id, {'defect_id':form.getFirst().id, 'title': form.getFirst().title, 'status':'Відхилена','resolution':form.description,'townslug':townslug})
                ActivityMail.sendToModers(request,'Ваша заявка #'+str(form.getFirst().id)+' відхилена модератором', 'defect_change_status.email', form.town_ref.id, {'defect_id':form.getFirst().id, 'title': form.getFirst().title, 'status':'Відхилена','resolution':form.description,'townslug':townslug}, [form.owner_ref.email])
        except Issues.DoesNotExist:
            return HttpResponseRedirect('../defects')
    return HttpResponseRedirect('../../defects/%s' % issue_id)


#Исполнитель отказался от назначения. Ставим статус "На модерации"
def unsubscribe(request,issue_id, townslug):
    if(request.method=="POST"):
        try:
            issue=Issues.objects.get(pk=issue_id)
            last_issue=issue.last_issue()
            if((issue.last_issue().assigned_to in request.user.work_for.all()) and issue.town_ref in request.user.towns.all()):
                form = Issues()
                form.owner_ref=request.user
                form.town_ref=issue.town_ref
                form.title="Змiна статусу"
                form.description="Виконавець відхилив призначення по причині: " + request.POST['description']
                form.parent_task_ref=last_issue
                form.assigned_to=last_issue.assigned_to
                form.status=0
                form.save()
                ActivityMail.sendToSubcontractors(request,'Заявка #'+str(form.getFirst().id)+' відхилена представником виконавця ', 'defect_change_status.email', form.assigned_to.id, {'defect_id':form.getFirst().id, 'title': form.getFirst().title, 'status':'Відмова. Повернута на модерацію','resolution':form.description,'townslug':townslug})
                ActivityMail.sendToModers(request,'Виконавець відхилив призначення по заявці #'+str(form.getFirst().id)+'.', 'defect_change_status.email', form.town_ref.id, {'defect_id':form.getFirst().id, 'title': form.getFirst().title, 'status':'Повернуто на модерацію','resolution':form.description,'townslug':townslug})
                #ActivityMail.sendToModers(request,'Ваша заявка #'+str(form.getFirst().id)+' відхилена модератором', 'defect_change_status.email', form.town_ref.id, {'defect_id':form.getFirst().id, 'title': form.getFirst().title, 'status':'Відхилена'}, [form.owner_ref.email])
        except Issues.DoesNotExist:
            return HttpResponseRedirect('../defects/list')
    return HttpResponseRedirect('../defects/list')


# Статус "Виконана"
def setFix(request,issue_id, townslug):
    if(request.method=="POST"):
        #here we must find bottom issue
        try:
            issue=Issues.objects.get(pk=issue_id)
            last_issue=issue.last_issue()
            if((issue.last_issue().assigned_to in request.user.work_for.all()) or (request.user.isAllowedToModerate(request.session["town"], 'Defects') and issue.town_ref in request.user.towns.all()) and last_issue.status==1):
                data=request.POST
                form = Issues()
                user=request.user
                form.owner_ref=user
                form.town_ref=issue.town_ref
                form.title="Змiна статусу"
                form.assigned_to=last_issue.assigned_to
                if("description" in data):
                    form.description=data["description"]
                    form.parent_task_ref=last_issue
                    form.status=2

                try:
                    form.save()
                    ActivityMail.sendToSubcontractors(request,'Заявка #'+str(form.getFirst().id)+' виконана', 'defect_change_status.email', form.assigned_to.id, {'defect_id':form.getFirst().id, 'title': form.getFirst().title, 'status':'Виконана','resolution':form.description,'townslug':townslug})
                    ActivityMail.sendToModers(request,'Заявка #'+str(form.getFirst().id)+' виконана підрядною організацією', 'defect_change_status.email', form.town_ref.id, {'defect_id':form.getFirst().id, 'title': form.getFirst().title, 'status':'Виконана','resolution':form.description,'townslug':townslug})
                    ActivityMail.sendToModers(request,'Ваша заявка #'+str(form.getFirst().id)+' виконана підрядною організацією', 'defect_change_status.email', form.town_ref.id, {'defect_id':form.getFirst().id, 'title': form.getFirst().title, 'status':'Виконана','resolution':form.description,'townslug':townslug}, [form.owner_ref.email])
                except:
                    pass
            return HttpResponseRedirect('../../defects/%s' % issue_id)
        except Issues.DoesNotExist:
            #print some error page or send back to index
            return HttpResponseRedirect('../defects')


# Статус "Виконана"
def setFixModer(request,issue_id, townslug):
    if(request.method=="POST"):
        try:
            issue=Issues.objects.get(pk=issue_id)
            last_issue=issue.last_issue()
            if(request.user.isAllowedToModerate(request.session["town"], 'Defects') and issue.town_ref in request.user.towns.all()):
                data=request.POST
                form = Issues()
                user=request.user
                form.owner_ref=user
                form.town_ref=issue.town_ref
                form.title="Змiна статусу"
                form.assigned_to=last_issue.assigned_to
                if("description" in data):
                    form.description=data["description"]
                    form.parent_task_ref=last_issue
                    form.status=2
                try:
                    form.save()
                    ActivityMail.sendToModers(request,'Заявка #'+str(form.getFirst().id)+' "ВИКОНАНА" підрядною організацією', 'defect_change_status.email', form.town_ref.id, {'defect_id':form.getFirst().id, 'title': form.getFirst().title, 'status':'Виконана','resolution':form.description,'townslug':townslug})
                    ActivityMail.sendToModers(request,'Ваша заявка #'+str(form.getFirst().id)+' "ВИКОНАНА" підрядною організацією', 'defect_change_status.email', form.town_ref.id, {'defect_id':form.getFirst().id, 'title': form.getFirst().title, 'status':'Виконана','resolution':form.description,'townslug':townslug}, [form.owner_ref.email])
                except:
                    pass
            return redirect('../../defects/%s' % issue_id)
        except Issues.DoesNotExist:
            #print some error page or send back to index
            return HttpResponseRedirect('../defects')

#Переоткрыть заявку
def reopen(request,issue_id, townslug):
    if(request.method=="POST"):
        #todo: ПРОВЕРКА: ТОЛЬКО ДЛЯ МОДЕРА, ПОДРЯДЧИКА ИЛИ ЖЕ ДЛЯ ВЛАДЕЛЬЦА ЗАЯВКИ
        try:
            issue=Issues.objects.get(pk=issue_id)
            last_issue=issue.last_issue()
            if(last_issue.status==2):
                data=request.POST
                form = Issues()
                user=request.user
                form.owner_ref=user
                form.town_ref=issue.town_ref
                form.title="Змiна статусу"
                if("description" in data):
                    form.description=data["description"]
                form.parent_task_ref=last_issue
                form.status=1
                form.assigned_to=last_issue.assigned_to
                form.save()
                ActivityMail.sendToSubcontractors(request,'Заявка #'+str(form.getFirst().id)+' перевідкрита власником', 'defect_change_status.email', form.assigned_to.id, {'defect_id':form.getFirst().id, 'title': form.getFirst().title, 'status': 'Перевідкрита власником', 'resolution':form.description,'townslug':townslug})
                ActivityMail.sendToModers(request,'Заявка #'+str(form.getFirst().id)+' перевідкрита власником', 'defect_change_status.email', form.town_ref.id, {'defect_id':form.getFirst().id, 'title': form.getFirst().title, 'status':'Відкрита', 'resolution':form.description,'townslug':townslug})
                if("files[]" in data):
                    for filename in data.getlist("files[]"):
                        try:
                            body64=data["attachements[%s]" % filename]
                            body=""
                            body=base64.b64decode(body64[body64.index(",")+1:])
                            ext = filename.split('.')[-1]
                            sys_filename="%s.%s" % (uuid.uuid4(), ext)
                            path=weunion.settings.MEDIA_ROOT+"/defects/"
                            f=open(path+sys_filename,"wb")
                            file_size=f.write(body)
                            f.close()
                            img=Image.open(path+sys_filename)
                            img.thumbnail((350,350),Image.ANTIALIAS)
                            img.save(path+"medium."+sys_filename)
                            img.thumbnail((150,150),Image.ANTIALIAS)
                            img.save(path+"thumbnail."+sys_filename)
                        except:
                            print(str(sys.exc_info()[0])+str(sys.exc_info()[1]))
                            traceback.print_exc(file=sys.stdout)
                            return
                        doc = Documents()
                        doc.owner_ref=user
                        doc.name=filename
                        doc.file_name=sys_filename
                        doc.type_name="image"
                        doc.size=file_size
                        doc.save()
                        issuefile=IssueFiles()
                        issuefile.issue_ref=form
                        issuefile.document_ref=doc
                        issuefile.save()
                return HttpResponseRedirect('../../defects/%s' % issue_id)
            else:
                raise PermissionDenied("Доступ заборонено")

        except Issues.DoesNotExist:
            #print some error page or send back to index
            return HttpResponseRedirect('../defects')


#Блокировать комментарий
def blockcomment(request, comment_id, issue_id, townslug):
    if(request.user.is_authenticated() and request.user.is_active):
        if(request.user.isAllowedToModerate(request.session["town"], 'Defects')):
            if(comment_id):
                comment = get_object_or_404(Comments, pk=comment_id)
                comment.block = 1
                comment.save()
                Karma.add(comment.owner_ref,KARMA['DEFECT_COMMENT_BLOCK'],"Блокування коментаря", "Дефекти ЖКГ")
                #TODO:оправлять письмо пользователю о заблокированом комменте
                return redirect('../../../defects/'+issue_id)
            else:
                return PermissionDenied("Доступ заборонено")
        else:
            return PermissionDenied("Доступ заборонено")
    else:
        return PermissionDenied("Доступ заборонено")


def help(request, townslug):
    return render(request,"help_def.html")


def rules(request, townslug):
    return render(request,"rules_def.html")


def ok(request, townslug):
    return render(request,"ok_def.html")



#if(request.user.isAllowedToModerate(request.session["town"], 'Defects') or issue.last_issue().assigned_to in request.user.work_for.all()) and issue.town_ref in request.user.towns.all():