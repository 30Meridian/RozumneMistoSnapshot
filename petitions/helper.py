from .models import *
from django.shortcuts import get_object_or_404, redirect
from ipware.ip import get_ip
from defects.models import Town
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.db.models import Q
from weunion.settings import DEFAULT_FROM_EMAIL
from email.header import Header


class Activity:
    '''Клас реализует запись всех процессов происходящих над петицией'''

    def add(self,request, petition_id, act_text):

            activity = PetitionsActivity()
            user = get_object_or_404(User, id =request.user.id)
            petition = get_object_or_404(Petitions, id = petition_id)
            try:
                activity.user = user
                activity.petition = petition
                activity.activity = act_text
                activity.ip = self._ip(request)
                activity.save()

                return redirect('petitions:petition', arg=(petition_id))
            except:
                return False

    def add_robot(self,request, petition_id, act_text):

            activity = PetitionsActivity()
            user = get_object_or_404(User, id =request.user.id)
            petition = get_object_or_404(Petitions, id = petition_id)
            try:
                activity.user = user
                activity.petition = petition
                activity.activity = act_text
                activity.ip = self._ip(request)
                activity.save()

                return True
            except:
                return False



    def _ip(self,request):
        '''Получаем IP клиента с request'''
        ip = get_ip(request)
        if ip is not None:
            return ip
        else:
            return 'local'

class ActivityMail:
    '''Отправляем почту на основе темплейтов'''
    def sendToModers(request, subject, template_name, town, context,email=None, module='Petitions'):
        recipients = []
        if(email == None):
            recipients = []
            users = Town.objects.get(pk=int(town)).user_set.filter(Q(groups__name='Moderator_%s' % module ) | Q(groups__name='Moderator'))
            for user in users:
                recipients.append(user.email)
        else:
            recipients = email

        template_html = render_to_string('emails/'+template_name, context)
        template_plain = render_to_string('emails/'+template_name, context)

        send_mail(
            subject,
            template_plain,
            DEFAULT_FROM_EMAIL,
            recipients,
            html_message=template_html,
        )


def get_town_type(town):
    text = ''
    type = str(town.town_type)
    if type == 'місто':
        text = 'міської ради м. {}'.format(town)
    elif type == 'смт.':
        text = 'селищної  ради смт. {}'.format(town)
    elif type == 'село':
        text = 'сільської ради с. {}'.format(town)
    elif type == 'район':
        text = 'районної ради р. "{}"'.format(town)
    return text

def get_recipient_of_petition(town):
    petition_to = ''
    try:
        petition_to = town.additions.get(type='petition_to').body
        if not petition_to:
            petition_to = get_town_type(town)
    except:
        petition_to = get_town_type(town)
    return petition_to


