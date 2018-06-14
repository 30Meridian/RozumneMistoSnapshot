import nested_admin
from django.contrib import admin
from weunion.settings import GOOGLE_API_KEY
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site

from allauth.account.models import EmailAddress

from .forms import UserAdminForm, TownAdminForm,\
    TownAdditionsInlineForm, TownBudgetForm
from .models import User, Town, Regions, TownBanners, \
    TownEdrpou, TownsAdditions, TownGromada, \
    TownsGromadasVillages, TownBudgets, TownAllowedModules
from .admin_help import modules_values, allowed_defects, allowed_petitions, moders_content


class UserAdmin(admin.ModelAdmin):
    form = UserAdminForm
    list_display = ('id', 'get_full_name_atall', 'email', 'get_towns')
    exclude = ('password',)
    search_fields = ('last_name', 'email', 'id')
    filter_horizontal = ('groups', 'towns', 'work_for', 'user_permissions')
    fields = ('first_name', 'last_name', 'middle_name', 'username',
              'email', 'phone', 'last_login', 'date_joined', 'verified_email',
              'is_active', 'is_staff', 'is_superuser',
              'groups', 'towns', 'work_for', 'user_permissions')
    list_display_links = ('id', 'get_full_name_atall', 'email')

    def get_form(self, request, obj=None, **kwargs):
        form = super(UserAdmin, self).get_form(request, obj, **kwargs)
        try:
            account_email = EmailAddress.objects.get(user=obj.id)
            if account_email.verified:
                form.verified = True
            else:
                form.verified = False
        except:
            form.verified = False
        return form

    def get_towns(self, obj):
        towns = obj.towns.all().values_list('name', flat=True)
        return ', '.join(towns)

    get_towns.short_description = 'Міста'
    get_towns.admin_order_field = 'towns'

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        try:
            EmailAddress.objects.filter(user=obj.id).exclude(email=form.cleaned_data['email']).delete()
            account_email = EmailAddress.objects.get(user=obj.id, email=form.cleaned_data['email'])
        except:
            account_email = False

        if form.cleaned_data['verified_email']:
            if account_email:
                account_email.verified = True
                account_email.save()
            else:
                EmailAddress.objects.create(user=obj, email=form.cleaned_data['email'], verified=1, primary=1)
        else:
            if account_email:
                account_email.verified = False
                account_email.save()

        obj.save()


class RegionsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False


class TownBannerInline(admin.TabularInline):
    model = TownBanners
    max_num = 1


# class TownEdrpouInline(admin.TabularInline):
#     model = TownEdrpou
#     min_num = 0
#     extra = 0


class TownsGromadasVillagesInline(nested_admin.NestedTabularInline):
    model = TownsGromadasVillages
    fk_name = 'gromada_ref'
    min_num = 1
    extra = 0


class TownsGromadaInline(nested_admin.NestedStackedInline):
    inlines = [TownsGromadasVillagesInline]
    model = TownGromada
    fk_name = 'main_town_ref'
    min_num = 0
    extra = 0
    max_num = 1


class TownBudgetInline(admin.TabularInline):
    form = TownBudgetForm
    model = TownBudgets
    min_num = 0
    max_num = 1

    exclude = ('year',)

    def has_delete_permission(self, request, obj=None):
        return False

class TonwAdditionsFormset(BaseInlineFormSet):
    def clean(self):
        super(TonwAdditionsFormset, self).clean()
        for field in self.forms:
            if field.cleaned_data:
                if ((field.cleaned_data['type'] in ['igov', 'donor']) and
                        not field.cleaned_data['body']):
                    raise ValidationError("Обов'язково заповнити \"Донорство крові\" та \"Електронні послуги\" ")


class TonwAdditionsInline(admin.TabularInline):
    model = TownsAdditions
    formset = TonwAdditionsFormset
    form = TownAdditionsInlineForm
    fields = ('title', 'type', 'body', 'description')
    min_num = 6
    extra = 7
    # max_num = 14

    # def has_delete_permission(self, request, obj=None):
    #     return False


class TownAllowedModulesFormset(BaseInlineFormSet):
    def clean(self):
        super(TownAllowedModulesFormset, self).clean()
        list_of_modules = []
        for field in self.forms:
            if field.cleaned_data:
                if field.cleaned_data['module'] in list_of_modules:
                    raise ValidationError('Було обрано два однакових модулі. Залиште лише один з них.')
                list_of_modules.append(field.cleaned_data['module'])


class TownAllowedModulesInline(admin.TabularInline):
    model = Town.modules.through
    formset = TownAllowedModulesFormset
    min_num = 0
    extra = 13
    max_num = 13


class TownAdmin(nested_admin.NestedModelAdmin):
    form = TownAdminForm
    list_display = ('name', 'koatuu', 'town_type')
    search_fields = ('name', 'koatuu', 'slug', 'id')
    inlines = [TownBannerInline, TownAllowedModulesInline, TownBudgetInline, TonwAdditionsInline, TownsGromadaInline]
    add_fields = ('name', 'slug', 'region_ref', 'koatuu', 'is_active', 'town_type', 'votes', 'pet_days', 'pet_number_templ', ('map_lon', 'map_lat', 'zoom'), )
    change_fields = ('name', 'slug', 'region_ref', 'koatuu', 'is_active', 'town_type', 'votes', 'pet_days', 'pet_number_templ', ('map_lon', 'map_lat', 'zoom'), 'menu')

    def __init__(self, *args, **kwargs):
        super(TownAdmin, self).__init__(*args, **kwargs)
        self.town_slug = ''
        self.menu_html = render_to_string('menu_for_town.html')

    def add_view(self, request, form_url='', extra_context=None):
        self.fields = getattr(self, 'add_fields', ())
        extra_context = extra_context or {}
        extra_context['api_key'] = GOOGLE_API_KEY
        gmap = {'lon': 50.27, 'lat': 30.31, 'zoom': 6}
        extra_context['gmap'] = gmap
        return super(TownAdmin, self).add_view(
            request, form_url=form_url, extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        self.fields = getattr(self, 'change_fields', ())
        extra_context = extra_context or {}
        extra_context['api_key'] = GOOGLE_API_KEY
        town = Town.objects.get(id=object_id)
        gmap = {'lon': town.map_lon, 'lat': town.map_lat, 'zoom': town.zoom}
        extra_context['gmap'] = gmap
        return super(TownAdmin, self).change_view(
            request, object_id=object_id, form_url=form_url, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        self.town_slug = obj.slug
        obj.slug = str(obj.slug).lower()
        modules_list= '''{edata} {igov} {prozorro} {donor} {news}
                       {defects} {petitions} {polls} {openbudget}
                       {medicine} {flats} {smartroads} {mvs_wanted}'''
        obj.menu = self.menu_html.format(town_slug=obj.slug, town_name=obj.name,
                                         additional_items='{additional_items}',
                                         moders='{moders}',
                                         modules = modules_list
                                         )

        obj.save()

    def save_formset(self, request, form, formset, change):
        super(TownAdmin, self).save_formset(request, form, formset, change)
        town = Town.objects.get(slug=self.town_slug)

        if formset.model == TownAllowedModules:

            dict_of_modules = {
                'edata':['/{town_slug}/edata'.format(town_slug=town.slug), '/{town_slug}/edata'.format(town_slug=town.slug), 'Відкриті фінанси'],
                'igov':['/{town_slug}/igov'.format(town_slug=town.slug), '/{town_slug}/igov'.format(town_slug=town.slug), 'Електронні послуги'],
                'prozorro':['/{town_slug}/prozorro'.format(town_slug=town.slug), '/{town_slug}/prozorro'.format(town_slug=town.slug), 'Електронні закупівлі'],
                'donor':['/{town_slug}/donor'.format(town_slug=town.slug), '/{town_slug}/donor'.format(town_slug=town.slug), 'Донорство крові'],
                'polls':['/{town_slug}/polls'.format(town_slug=town.slug), '/polls', 'Опитування'],
                'defects':['/{town_slug}/defects'.format(town_slug=town.slug), '/defects/', 'Дефекти ЖКГ'],
                'petitions':['/{town_slug}/petitions'.format(town_slug=town.slug), '/petitions/', 'Петиції'],
                'news':['/{town_slug}/news'.format(town_slug=town.slug), '/news/', 'Новини міста'],
                'openbudget':['{openbudget_url}', '/openbudget/', 'Відкритий бюджет'],
                'medicine':['{medicine_url}', '/medicines/', 'Реєстр ліків'],
                'flats':['{flats_url}', '/flats/', 'Черги на житло'],
                'mvs_wanted':['/{town_slug}/mvs_wanted/'.format(town_slug=town.slug), '/mvs_wanted/', 'Розшук поліції'],
                'smartroads':['/{town_slug}/smartroads'.format(town_slug=town.slug), '/smartroads/', 'Розумні дороги'],
            }
            list_of_modules = [module[2] for module in dict_of_modules.values()]
            dict_of_values = {}
            for fields in formset:
                if fields.cleaned_data:
                    module = str(fields.cleaned_data['module'])
                    to_delete = fields.cleaned_data['DELETE']
            #
                    if module in list_of_modules and not to_delete:
                        title = [str(title) for title, value in dict_of_modules.items() if value[2] == module][0]
                        if fields.cleaned_data['active']:
                            dict_of_values[title] =  modules_values[title].format(url=dict_of_modules[title][0] ,
                                                                                  allowed_petitions=allowed_petitions.format(town_slug=town.slug),
                                                                                  allowed_defects=allowed_defects.format(town_slug=town.slug))

                        else:
                            dict_of_values[title] = modules_values[title].format(url=dict_of_modules[title][1],
                                                                                 allowed_petitions='</a>',
                                                                                 allowed_defects='</a>')
                    elif module in list_of_modules and to_delete:
                        title = [str(title) for title, value in dict_of_modules.items() if value[2] == module][0]
                        dict_of_values[title] = ''

            for name in dict_of_modules.keys():
                if name not in dict_of_values.keys():
                    dict_of_values[name] = ''

            town.menu = town.menu.format(
                edata=dict_of_values['edata'],
                igov=dict_of_values['igov'],
                prozorro=dict_of_values['prozorro'],
                donor=dict_of_values['donor'],
                news=dict_of_values['news'],
                defects=dict_of_values['defects'],
                petitions=dict_of_values['petitions'],
                polls=dict_of_values['polls'],
                openbudget=dict_of_values['openbudget'],
                medicine=dict_of_values['medicine'],
                flats=dict_of_values['flats'],
                smartroads=dict_of_values['smartroads'],
                mvs_wanted=dict_of_values['mvs_wanted'],

                additional_items = '{additional_items}',
                moders='{moders}'
            )
            town.save()

        if formset.model == TownBudgets:
            budget = ''
            for fields in formset:
                if fields.cleaned_data:
                    if fields.cleaned_data['body']:
                        budget = '/{town_slug}/budget'.format(town_slug=town.slug)
                    else:
                        budget = '/openbudget/'
                else:
                    budget = '/openbudget/'

            town.menu = town.menu.format(
                openbudget_url=budget,
                medicine_url='{medicine_url}',
                flats_url='{flats_url}',
                additional_items='{additional_items}',
                moders = '{moders}',

            )
            town.save()
        #
        if formset.model == TownsAdditions:
            list_of_names = ['moders', 'flats', 'medicines', 'additional_items']
            dict_of_values = {}
            additional_items =''
            for fields in formset:
                if fields.cleaned_data:
                    if fields.cleaned_data['type'] == 'additional_items':
                        dict_of_values['additional_items'] = fields.cleaned_data['body']
                    elif fields.cleaned_data['type'] == 'moderators':
                        if fields.cleaned_data['body']:
                            dict_of_values['moders'] = moders_content.format(town_slug=town.slug)
                        else:
                            dict_of_values['moders'] = ''
                    elif fields.cleaned_data['type'] == 'flats':
                        if fields.cleaned_data['body']:
                            dict_of_values['flats'] = '/{town_slug}/info/flats'.format(town_slug=town.slug)
                        else:
                            dict_of_values['flats'] = '/flats/'
                    elif fields.cleaned_data['type'] == 'medicines':
                        if fields.cleaned_data['body']:
                            dict_of_values['medicines'] = '/{town_slug}/info/medicines'.format(town_slug=town.slug)
                        else:
                            dict_of_values['medicines'] = '/medicines/'
                    elif fields.cleaned_data['type'] == 'edata' and not fields.cleaned_data['body']:
                        edata = fields.save(commit=False)
                        edata.body = 7
                        edata.save()
            town.menu = town.menu.format(
                medicine_url=dict_of_values['medicines'],
                flats_url=dict_of_values['flats'],
                additional_items= dict_of_values['additional_items'],
                moders=dict_of_values['moders']
            )
            town.save()

    def get_form(self, request, obj=None, **kwargs):
        form = super(TownAdmin, self).get_form(request, obj, **kwargs)
        if obj is None:
            form.add_obj = True
        else:
            form.add_obj = False
        return form


class TownEdrpouAdmin(admin.ModelAdmin):
    # def has_change_permission(self, request, obj=None):
    #     return False
    fields = ('code', 'title', 'koatuu')
    search_fields = ('koatuu', 'title', 'code')
    list_display = ('code', 'title', 'koatuu')
    list_display_links = ('code', 'name')

admin.site.register(Town, TownAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Regions, RegionsAdmin)
admin.site.register(TownEdrpou, TownEdrpouAdmin)

admin.site.unregister(Group)
admin.site.unregister(Site)
