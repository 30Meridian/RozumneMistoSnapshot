from django.core.mail import send_mail
from django.db.models import Q
from django.template.loader import render_to_string
from defects.models import *
from django.db.models import Sum
from django.shortcuts import get_object_or_404, get_list_or_404
from django.http import response

from datetime import datetime

from .models import AuthUserKarma, Modules
from .settings import DEFAULT_FROM_EMAIL

class Karma:
    '''Клас используется для работы с кармой пользователя'''

    def add(user, points, action, module):
        """Добавим пользователю в карму балов или отнимем(отрицательное значение)"""
        if (user and action and module):
            karma = AuthUserKarma()
            karma.forwhat = action
            karma.user_ref = user
            karma.points = points
            karma.module_ref = get_object_or_404(Modules, title=module)
            karma.save()

    def list(user):
        """Вернем список кармической активности для пользователя"""
        return AuthUserKarma.objects.filter(user_ref=user)


class Towns:
    '''Используется в списке городов по регионах'''

    def get_town(request, town_id):

        town_id = town_id
        town_name = ''
        set_cookie = None

        if (town_id == None) and (request.session.has_key('town')):
            town = request.session["town"]
            if (town):
                town_id = town
                town_name = self._get_town_name(town_id)
            else:
                return 'Місто не знайдено ні в куках, ні в url'
        elif (town_id) and not (request.session.has_key('town')):
            town_name = self._get_town_name(town_id)
            set_cookie = True
        elif not (town_id) and not (request.session.has_key('town')):
            if (request.user.is_authenticated()):
                town = User.objects.get(id=request.user.id).towns.all()[0]
                town_id = town.id
                set_cookie = True
                town_name = self._get_town_name(town_id)
        else:
            return None

        return {'town_id': town_id, 'town_name': town_name, 'set_cookie': set_cookie}

    def _get_town_name(town_id):

        if (town_id):
            town_name = Town.objects.get(id=town_id).name
            return town_name
        else:
            return 'Вкажіть ID міста'


class SendMail:
    #Send email only to official "rozumne misto"s email
    def sendToModers(request, subject, template_name, context, email):

        template_html = render_to_string('emails/' + template_name, context)
        template_plain = render_to_string('emails/' + template_name, context)

        send_mail(
            subject,
            template_plain,
            DEFAULT_FROM_EMAIL,
            [email],
            html_message=template_html,
        )


