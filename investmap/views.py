import json
import urllib.parse as urllib_parse

from django.views.generic import CreateView, DetailView, DeleteView, UpdateView, FormView
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.core.mail import EmailMessage

from ipware.ip import get_ip

from weunion.models import Town
from weunion.settings import GOOGLE_API_KEY, DEFAULT_FROM_EMAIL

from .forms import InvestMapInitForm, StatsAdd, DescriptionEdit, SuggestProject
from .models import InvestMapLog, InvestMapPoint, InvestMapObject, InvestMapStats, InvestMapDescriptionTabs
from .exel_utils import generate_investmap_objects_xlsx


def index(request, townslug):
    return HttpResponseRedirect(reverse('investmap:list', args=[townslug]))


def get_list_context(request, townslug):
    town = get_object_or_404(Town, slug=townslug)
    api_key = GOOGLE_API_KEY
    gmap = {'lon': town.map_lon, 'lat': town.map_lat, 'zoom': town.zoom}
    allow = False
    stats = InvestMapStats.objects.filter(town=town).all()
    tabs_list = [{tab.slug: tab} for tab in InvestMapDescriptionTabs.objects.filter(town=town).all()]
    tabs = {}
    for tab in tabs_list:
        tabs.update(tab)

    if request.user.is_authenticated():
        allow = request.user.isAllowedToModerate(Town.objects.get(slug=townslug).id)
    return {'api_key': api_key, 'gmap': gmap, 'town': town, 'allow': allow, 'add_form': StatsAdd(), 'stats_list': stats,
            'tabs': tabs}


class PermissionRequiredMixin(object):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(status=403)
        if request.user.is_authenticated() and request.user.is_active:
            if request.user.isAllowedToModerate(Town.objects.get(slug=kwargs.get('townslug')).id):
                response = super(PermissionRequiredMixin, self).get(self, request, *args, **kwargs)
        return response

    def post(self, request, *args, **kwargs):
        response = HttpResponseRedirect(self.get_success_url())
        if request.user.is_authenticated() and request.user.is_active:
            if request.user.isAllowedToModerate(Town.objects.get(slug=kwargs.get('townslug')).id):
                response = super(PermissionRequiredMixin, self).post(self, request, *args, **kwargs)
        return response


class CreateInvestMapObject(PermissionRequiredMixin, CreateView):
    form_class = InvestMapInitForm
    template_name = 'investmap/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateInvestMapObject, self).get_context_data(**kwargs)
        context['api_key'] = GOOGLE_API_KEY
        town = Town.objects.get(slug=self.kwargs.get('townslug'))
        gmap = {'lon': town.map_lon, 'lat': town.map_lat, 'zoom': town.zoom}
        context['gmap'] = gmap
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.town = Town.objects.get(slug=self.kwargs.get('townslug'))
        self.object.object_type = form.cleaned_data['object_type']
        self.object.save()

        InvestMapLog.objects.create(operation='create', investmap_object=self.object, user=self.request.user,
                                    ip_address=get_ip(self.request))

        object_map = json.loads(form.cleaned_data['object_map'])
        for coordinate_pair in object_map:
            InvestMapPoint.objects.create(investmap_object=self.object,
                                          map_lon=coordinate_pair['lng'], map_lat=coordinate_pair['lat'])

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('investmap:list', args=[self.kwargs.get('townslug')])


create = CreateInvestMapObject.as_view()


class EditInvestMapObject(PermissionRequiredMixin, UpdateView):
    form_class = InvestMapInitForm
    model = InvestMapObject
    template_name = 'investmap/edit.html'
    pk_url_kwarg = 'investmap_pk'

    def get_initial(self):
        response = super(EditInvestMapObject, self).get_initial()
        response['object_map'] = json.dumps(self.object.lat_lng)
        return response

    def get_context_data(self, **kwargs):
        context = super(EditInvestMapObject, self).get_context_data(**kwargs)
        context['api_key'] = GOOGLE_API_KEY
        town = Town.objects.get(slug=self.kwargs.get('townslug'))
        gmap = {'lon': town.map_lon, 'lat': town.map_lat, 'zoom': town.zoom}
        context['gmap'] = gmap
        return context

    def get_success_url(self):
        return reverse('investmap:detail', args=[self.kwargs.get('townslug'), self.kwargs.get(self.pk_url_kwarg)])

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.object_type = form.cleaned_data['object_type']
        self.object.save()

        InvestMapLog.objects.create(operation='edit', investmap_object=self.object, user=self.request.user,
                                    ip_address=get_ip(self.request))

        object_map = json.loads(form.cleaned_data['object_map'])
        InvestMapPoint.objects.filter(investmap_object=self.object).delete()

        for coordinate_pair in object_map:
            InvestMapPoint.objects.create(investmap_object=self.object,
                                          map_lon=coordinate_pair['lng'], map_lat=coordinate_pair['lat'])

        return HttpResponseRedirect(self.get_success_url())


edit = EditInvestMapObject.as_view()


class DeleteInvestMapObject(PermissionRequiredMixin, DeleteView):
    template_name = 'investmap/delete.html'
    model = InvestMapObject
    pk_url_kwarg = 'investmap_pk'

    def get_success_url(self):
        return reverse('investmap:list', args=[self.kwargs.get('townslug')])

    def delete(self, request, *args, **kwargs):
        InvestMapLog.objects.create(operation='delete', investmap_object=self.get_object(), user=self.request.user,
                                    ip_address=get_ip(self.request))

        return super(DeleteInvestMapObject, self).delete(request, *args, **kwargs)


delete = DeleteInvestMapObject.as_view()


class DetailInvestMapObject(DetailView):
    template_name = 'investmap/detail.html'
    model = InvestMapObject
    pk_url_kwarg = 'investmap_pk'

    def get_context_data(self, **kwargs):
        context = super(DetailInvestMapObject, self).get_context_data(**kwargs)
        context['allow'] = False
        obj = kwargs.get('object')
        context['townslug'] = obj.town.slug
        if self.request.user.is_authenticated():
            if self.request.user.isAllowedToModerate(Town.objects.get(slug=context['townslug']).id):
                context['allow'] = True
        return context


detail = DetailInvestMapObject.as_view()


@csrf_exempt
def ajax(request, townslug):
    value = None
    if request.POST:
        value = json.loads(urllib_parse.unquote(request.POST['filter']))

    query = InvestMapObject.objects.filter(town__slug=townslug)

    if value is not None and len(value) > 0:
        query = query.filter(project_type__in=value)
    else:
        query = []

    result = []
    for investmap_object in query:
        result.append({
            'name': investmap_object.name,
            # 'image': investmap_object.image.url,
            'category': investmap_object.get_project_type_display(),
            # 'metrics': investmap_object.metrics,
            'address': investmap_object.address,
            'price': investmap_object.price,
            # 'contacts': investmap_object.contacts,
            # 'additional': investmap_object.document.url,
            'type': investmap_object.object_type,
            'path': investmap_object.lat_lng,
            'href': reverse('investmap:detail', args=[townslug, investmap_object.id])
        })
    return JsonResponse(result, safe=False)


def add_stats(request, townslug):
    form = StatsAdd(request.POST)

    if form.is_valid():
        instance = form.save(commit=False)
        instance.town = Town.objects.get(slug=townslug)
        instance.save()

    return redirect('/{0}/investmap/list/#tab_2'.format(townslug))


class DeleteInvestMapStats(PermissionRequiredMixin, DeleteView):
    template_name = 'investmap/delete_stats.html'
    model = InvestMapStats
    pk_url_kwarg = 'investstat_pk'

    def get_success_url(self):
        return '/{0}/investmap/list/#tab_2'.format(self.kwargs.get('townslug'))


delete_stats = DeleteInvestMapStats.as_view()


class EditInvestMapDescriptions(PermissionRequiredMixin, UpdateView):
    form_class = DescriptionEdit
    model = InvestMapDescriptionTabs
    template_name = 'investmap/edit_description.html'
    slug_field = 'slug'

    def get_success_url(self):
        return reverse('investmap:list', args=[self.kwargs.get('townslug')])

    def get_object(self, queryset=None):
        slug = self.kwargs.get(self.slug_url_kwarg, None)
        townslug = self.kwargs.get('townslug', None)
        town = Town.objects.get(slug=townslug)
        instance, created = InvestMapDescriptionTabs.objects.get_or_create(slug=slug, town=town)
        return instance


edit_description = EditInvestMapDescriptions.as_view()


class ListBaseView(FormView):
    form_class = SuggestProject
    template_name = 'investmap/list.html'

    def get_success_url(self):
        reverse('investmap:list', kwargs={'townslug': self.kwargs.get('townslug')})

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist('file_field')
        if form.is_valid():
            recipients = []
            town = Town.objects.filter(slug=self.kwargs.get('townslug')).first()
            users = town.user_set.filter(
                Q(groups__name='Moderator_investmap') |
                Q(groups__name='Moderator') |
                Q(groups__name='Control_investmap'))
            for user in users:
                recipients.append(user.email)

            subject = 'Запропонований проект від {0} {1}'.format(request.user.first_name, request.user.last_name)
            text = form.cleaned_data['text'] + '\nEmail: ' + str(request.user.email) + '\nPhone: ' + \
                   form.cleaned_data['phone']
            mail = EmailMessage(subject, text, DEFAULT_FROM_EMAIL, recipients)
            for file in files:
                mail.attach(file.name, file.read(), file.content_type)
            mail.send()

            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        return render(self.request, 'investmap/suggestion_success.html', {'townslug': self.kwargs.get('townslug')})

    def get_context_data(self, **kwargs):
        context = super(ListBaseView, self).get_context_data(**kwargs)
        context.update(get_list_context(self.request, self.kwargs.get('townslug')))
        return context


list_base = ListBaseView.as_view()


class ListBaseIFraneView(ListBaseView):
    template_name = 'investmap/iframe_list.html'


iframe_list_base = ListBaseIFraneView.as_view()


def export_to_exel(request, townslug):
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=investmap_{}_(www.rozumnemisto.org).xlsx'.format(townslug)
    xlsx_data = generate_investmap_objects_xlsx()
    response.write(xlsx_data)
    return response
