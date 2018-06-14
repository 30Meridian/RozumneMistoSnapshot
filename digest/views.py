import json
import hashlib

from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render

from weunion.models import User
from weunion.settings import CRON_SECRET

from .helpers import DigestMail
from .models import UserSubscriptions


def send_digest(request, secret):
    if secret == CRON_SECRET:
        instance = DigestMail()
        instance.send()
    return HttpResponseRedirect('/')


def unsubscribe(request, user_id):
    user = get_object_or_404(User, id=user_id)
    response = HttpResponse(status=403)

    if 'token' in request.GET:
        if hashlib.md5(user.email.encode()).hexdigest() == request.GET['token']:
            try:
                subscribe_instance = UserSubscriptions.objects.get(user=user)
                subscribe_instance.subscription = json.dumps([])
                subscribe_instance.save()
            except UserSubscriptions.DoesNotExist:
                UserSubscriptions.objects.create(user=user, subscription=json.dumps([]))

            response = render(request, 'success_unsubscribe.html')

    return response
