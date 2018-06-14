from .models import Town
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, HttpResponseRedirect


def towntemp(request):
    town = None
    if("town" in request.session and "town_name" in request.session):
        town = request.session["town"]

    if town and Town.objects.filter(pk=town).count() != 0:
        menu = Town.objects.get(pk=town).menu
        slug = Town.objects.get(pk=town).slug
        return {'town': True, 'menu':menu, 'townslugheader': slug}
    else:
        return{'town':False}


class TownSessionMiddleware(object):
    def process_view(self, request, view_func, view_args, view_kwargs):
        self.set_session_town(request, view_kwargs.get('townslug'))

    def set_session_town(self, request, slug):
        if slug:
            try:
                town = Town.objects.get(slug=slug)
                request.session["town"] = town.id
                request.session["town_name"]= town.name
            except:
                 return redirect('/regions/')