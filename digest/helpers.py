import hashlib

from datetime import datetime

from django.core.mail import send_mail
from django.template.loader import render_to_string

from weunion.settings import DEFAULT_FROM_EMAIL
from weunion.views import live_stream_list
from weunion.models import User

from .models import UserSubscriptions


class DigestMail(object):
    local_life_stream_cache = {}

    def send(self, recipients=None):
        """
        Sending letters to all in dispatch list
        :param recipients: queryset of users for whom will be sent a letter
        :return: None
        """
        if recipients is None:
            recipients = User.objects

        day = datetime.now().date()

        for user in recipients.all():
            try:
                user_subscription = UserSubscriptions.objects.get(user=user)
                filter_list = user_subscription.filter_list
            except UserSubscriptions.DoesNotExist:
                filter_list = {'News', 'Petitions', 'Polls', 'Defects'}

            if len(filter_list) == 0:
                continue

            context = self.get_context(filter_list)
            context['unsubscribe'] = str(user.id) + '?token=' + hashlib.md5(user.email.encode()).hexdigest()

            if len(context['value']) > 1:
                send_mail(
                    'Дайджест подій на ' + str(day),
                    render_to_string('emails/digest.email', context),
                    DEFAULT_FROM_EMAIL,
                    [user.email],
                    html_message=render_to_string('emails/digest.email', context),
                )

        self.local_life_stream_cache.clear()

    def get_context(self, filter_list):
        filter_list_like_string = str(set(filter_list))
        if filter_list_like_string in self.local_life_stream_cache:
            return self.local_life_stream_cache[filter_list_like_string]
        else:
            context = live_stream_list(datetime.now(), filter_list, 7)
            self.local_life_stream_cache[filter_list_like_string] = context
            return context
