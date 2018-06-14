import re
from django.contrib.auth.models import AbstractUser
from django.db import models
import hashlib

from django.http import HttpResponseRedirect
from stdimage.models import StdImageField
import uuid

#генерируем псевдоуникальный файлнейм для загружаемых изображений
def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return 'citybanners/%s' % filename


class AttrLookup(object):#http://www.stavros.io/posts/function-calls-in-django-templates/
    def __init__(self, func, instance=None):
        self._func = func
        self._instance = instance

    def __get__(self, instance, owner):
        # Return a new instance of the decorator with the class embedded, rather than
        # store instance here, to avoid race conditions in multithreaded scenarios.
        return AttrLookup(self._func, instance)

    def __getitem__(self, argument):
        return self._func(self._instance, argument)

    def __call__(self, argument=None):
        # When resolving something like {{ user.can.change_number }}, Django will call
        # each element in the dot sequence in order (or otherwise try to access it).
        # When trying to call can(), that will fail, because it expects an extra
        # argument, so Django will fail and leave it at that.
        # If there's no argument passed, we return itself, so Django can continue with
        # the attribute lookup down the chain.
        if argument is None:
            return self
        else:
            return self._func(self._instance, argument)

class User(AbstractUser):
    work_for = models.ManyToManyField("Subcontractors", blank=True, verbose_name='Огранізацiя',related_name="user_set", related_query_name="user")
    towns = models.ManyToManyField("Town", verbose_name='Населений пункт проживання або центр громади',related_name="user_set", related_query_name="user")
    phone = models.CharField(max_length=50, verbose_name='Номер телефону', unique=True)
    middle_name = models.CharField(max_length=50,verbose_name='По батькові')
    is_checked = models.BooleanField(default=False, verbose_name="Перевірений")
    #this stuff is needed to use this model with django auth as a custom user class
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'phone']

    #Возвращаем хэш имейла для чата поддержки
    def chathash(self):
        return hashlib.sha224(self.email.encode('UTF-8')+self.middle_name.encode('UTF-8')).hexdigest()

    def __str__(self):
        if(len(self.first_name)<0 and len(self.last_name)<0):
           return self.username
        else:
           return self.get_full_name()

    def get_full_name_atall(self):
        """
        Returns the first_name plus the last_name, with a space in between without initials
        """
        full_name = '%s %s %s' % (self.last_name, self.first_name, self.middle_name )
        return full_name.strip()
    get_full_name_atall.short_description = "Повне ім'я"

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        firstname = '.'.join(name[0].upper() for name in self.first_name.split())
        midlename = '.'.join(name[0].upper() for name in self.middle_name.split())
        full_name = '%s %s. %s.' % (self.last_name, firstname, midlename )
        return full_name.strip()

    def get_initials(self):
        """
        Показываем полные инициалы: П.В.С
        """
        last_name = '.'.join(name[0].upper() for name in self.last_name.split())
        firstname = '.'.join(name[0].upper() for name in self.first_name.split())
        midlename = '.'.join(name[0].upper() for name in self.middle_name.split())
        full_name = '%s.%s.%s.' % (last_name, firstname, midlename )
        return full_name.strip()


#Общая функция для проверки прав на модерацию. Как город можно кидать ID
    def isAllowedToModerate(self, town, module=None):
        if self.is_authenticated():
            if self.isAdmin() or self.isModerator(town, module):
                return True
            else:
                return False
        else:
            return False

#Проверяем на админа. Админы это работники City of the Future. Полные привелегии
    def isAdmin(self):
        if self.is_authenticated():
            try:
                self.groups.get(name="Admin")
                return True
            except:
                return False
        else:
            return False


    #Проверяем на модератора. Модераторы - это представители в городах. Привязаны к городу и модулям, которые они обслуживают
    def isModerator(self, town, module=None):
        moder = False
        if self.is_authenticated():
            try:
                self.groups.get(name="Moderator")
                moder = True
            except:
                moder = False

            if (moder == False and module != None):
                try:
                    self.groups.get(name="Moderator_%s" % module)
                    moder = True
                except:
                    moder = False

            if moder:
                if town in [t.id for t in self.towns.all()]:
                    return True
                else:
                    return False

            return False
        else:
            return False


    #Проверяем на контролера. Котроллеры- это представители ОО в городах. Привязаны к городу и модулям, которые они контролируют
    def isController(self, town, module=None):
        moder = False
        if self.is_authenticated():
            if module == None:
                try:
                    self.groups.get(name="Controller")
                    moder = True
                except:
                    moder = False
            else:
                try:
                    self.groups.get(name="Controller_%s" % module)
                    moder = True
                except:
                    moder = False

            if moder:
                if town in self.towns.all():
                    return True
                else:
                    return False

            return False
        else:
            return False


    #до рефакторинга, пусай болтается
    def isModer(self):
        try:
            self.groups.get(name="Moderator")
            return True
        except:
            return False


    #test mixin that enables single parram to be passed from template like {{user.test.zzz}}
    @AttrLookup
    def test(self,param):
        return "Param is:%s" % param

    class Meta:
        managed = False
        db_table = 'auth_user'
        verbose_name = 'користувач'
        verbose_name_plural = 'Користувачі'


    #Возвращаем очки кармы для пользователя
    def points(self):
        from django.db.models import Sum
        return self.karma.aggregate(Sum('points'))['points__sum'] or '0'



class Subcontractors(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    town_ref = models.ForeignKey('Town', db_column='town_ref', verbose_name="Город")


    class Meta:
        managed = False
        db_table = 'subcontractors'
        verbose_name = 'підрядник'
        verbose_name_plural = 'Підрядні організації'

    def __str__(self):
        return self.name


class Regions(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'regions'
        verbose_name = 'регіон'
        verbose_name_plural = 'Регіони'


class Town(models.Model):
    name = models.CharField(max_length=45, blank=True, null=True, verbose_name="Назва")
    slug = models.CharField(max_length=50, blank=False, verbose_name="Cистемна назва")
    votes = models.IntegerField(default=0, verbose_name="Кількість необхідних голосів для петиції")
    region_ref = models.ForeignKey(Regions, db_column='region_ref', verbose_name="Регіон")
    town_type = models.ForeignKey('TownTypes', db_column='type_id', verbose_name="Тип населеного пункту")
    pet_days = models.IntegerField(verbose_name="Кількість днів на петицію")
    pet_number_templ = models.CharField(max_length=10, blank=True, null=True, verbose_name="Шаблон номеру петиції")
    map_lon=models.CharField(max_length=128, verbose_name="Широта")
    map_lat=models.CharField(max_length=128, verbose_name="Довгота")
    zoom=models.IntegerField(default=14, verbose_name="Зум на мапі")
    map_radius=models.IntegerField(verbose_name="Радіус на мапі")
    menu = models.CharField(max_length=10000, blank=True, null=True, verbose_name="Меню")
    modules = models.ManyToManyField('Modules', through='TownAllowedModules', through_fields=('town', 'module'), verbose_name='Модуль')
    is_active = models.BooleanField(verbose_name='Активне', default=False,
                                    help_text='Визначає, чи буде місто відображатись в системі.')
    additions_queryset = property(lambda self: TownsAdditions.objects.filter(town_ref=self).all())

    koatuu = models.CharField(max_length=20, unique=True, verbose_name='КОАТУУ')

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'town'
        verbose_name = 'Місто'
        verbose_name_plural = 'Міста'

class TownTypes(models.Model):
    title = models.CharField(max_length=50, verbose_name='тип')

    class Meta:
        managed = False
        db_table = 'town_types'

    def __str__(self):
        return self.title


class TownBanners(models.Model):
    imgsource = StdImageField(upload_to=get_file_path,verbose_name="Зображення")
    town = models.ForeignKey(Town, db_column='town', blank=True, null=True, verbose_name='Місто')

    class Meta:
        managed = False
        db_table = 'town_banners'
        verbose_name = 'Банер міста'
        verbose_name_plural = 'Банер міста'

    def __str__(self):
        return "Банер міста {}".format(self.town)


class Modules(models.Model):
    title = models.CharField(max_length=15, blank=True, null=True)
    slug = models.CharField(max_length=15, blank=True, null=True)
    # towns = models.ManyToManyField(Town, through='TownAllowedModules', through_fields=('module', 'town'))

    class Meta:
        managed = False
        db_table = 'modules'

    def __str__(self):
        return self.title or ""

class TownAllowedModules(models.Model):
    town = models.ForeignKey(Town, db_column='town', blank=True)
    module = models.ForeignKey(Modules, db_column='module', blank=True, null=True, verbose_name='Модулі')
    active = models.BooleanField(default=False, verbose_name='Активний',
                                 help_text='Визначає посилання усіх модулів, окрім: '
                                           '"Електронні послуги", "Відкриті фінанси", '
                                           '"Електронні закупівлі", "Донорство крові"')

    class Meta:
        managed = False
        db_table = 'town_allowed_modules'
        verbose_name = 'модуль для міста'
        verbose_name_plural = 'Дозволені модулі для міста'

    def __str__(self):
        return 'Відображати модуль: "{}"'.format(self.module)


class AuthUserKarma(models.Model):
    user_ref = models.ForeignKey(User, db_column='user_ref', blank=True, null=True,related_name="karma")
    points = models.IntegerField(blank=True, null=True)
    forwhat = models.CharField(max_length=255)
    module_ref = models.ForeignKey('Modules', db_column='module_ref')
    datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'auth_user_karma'

class TownBudgets(models.Model):
    year = models.IntegerField(blank=True, null=True, verbose_name='Рік')
    town_ref = models.ForeignKey(Town, db_column='town_ref', blank=True, null=True,related_name="openbudget", verbose_name='Місто')
    body = models.TextField(blank=True, null=True, verbose_name='Зміст')

    def __str__(self):
        return ''

    class Meta:
        managed = False
        db_table = 'town_budgets'
        verbose_name = 'Відкритий бюджет'
        verbose_name_plural = 'Відкритий бюджет'


class TownsAdditions(models.Model):
    town_ref = models.ForeignKey(Town, db_column='town_ref',related_name="additions", verbose_name='Місто')
    type = models.CharField(max_length=50, verbose_name='Тип')
    body = models.TextField(verbose_name='Зміст', blank=True)
    title = models.CharField(max_length=150, blank=True, null=True, verbose_name='Назва')
    description = models.CharField(max_length=1000, blank=True, null=True, verbose_name='Опис')

    def __str__(self):
        return self.title or ''

    class Meta:
        managed = False
        db_table = 'towns_additions'
        verbose_name = 'Додаток міста'
        verbose_name_plural = 'Додатки міста'



class TownGromada(models.Model):
    title = models.CharField(max_length=50, blank=True, null=True, verbose_name="Назва")
    main_town_ref = models.ForeignKey(Town, db_column='main_town_ref', verbose_name="Місто")

    class Meta:
        managed = False
        verbose_name = "Громада"
        verbose_name_plural = "Громади"
        db_table = 'town_gromada'


class TownEdrpou(models.Model):
    title = models.CharField(max_length=1000, verbose_name='Назва організації')
    code = models.CharField(unique=True, db_column='edrpou', max_length=100, verbose_name='Код')
    koatuu = models.CharField(max_length=20, verbose_name='КОАТУУ')

    class Meta:
        managed = False
        db_table = 'town_edrpou'
        verbose_name = 'Код ЄДРПОУ'
        verbose_name_plural ='Код ЄДРПОУ'

    def __str__(self):
        return 'Код організації "{}"'.format(self.title)

class TownsGromadasVillages(models.Model):
    title = models.CharField(max_length=100, verbose_name='Назва')
    gromada_ref = models.ForeignKey(TownGromada, db_column='gromada_ref', verbose_name='Громада')
    type_ref = models.ForeignKey(TownTypes, db_column='type_ref', verbose_name='Тип')

    class Meta:
        managed = False
        db_table = 'towns_gromadas_villages'
        verbose_name = 'Населений пункт'
        verbose_name_plural = 'Населені пункти - сателіти'


EDATA_PARAMETERS_CHOICES = (
    ('amount', 'Сума транзакції (гривень)'),
    ('recipt_edrpou', 'ЄРДПОУ-код отримувача'),
    ('recipt_name', 'Назва отримувача (по масці)'),
    ('payer_edrpou', 'ЄРДПОУ-код платника'),
)

COMPARISON_CHARACTERS = (
    ('==','Дорівнює (==)'),
    ('!=','Не дорівнює (!=)'),
    ('>','Більше (>)'),
    ('<','Менше (<)'),
)

class Subscriptions(models.Model):
    type_ref = models.ForeignKey('SubscriptionsTypes', db_column='type_ref', blank=True, null=True)
    user_ref = models.ForeignKey(User, db_column='user_ref')
    town_ref = models.ForeignKey(Town, db_column='town_ref')
    is_active = models.IntegerField()
    parameter = models.CharField(max_length=50,choices=EDATA_PARAMETERS_CHOICES)
    comparison = models.CharField(max_length=10, choices=COMPARISON_CHARACTERS)
    value = models.CharField(max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)
    gencode = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'subscriptions'


class SubscriptionsTypes(models.Model):
    name = models.CharField(max_length=50)
    is_active = models.IntegerField()
    periodic = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'subscriptions_types'

reg_b = re.compile(r"(android|bb\\d+|meego).+mobile|avantgo|bada\\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\\.(browser|link)|vodafone|wap|windows ce|xda|xiino", re.I|re.M)
reg_v = re.compile(r"1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\\-(n|u)|c55\\/|capi|ccwa|cdm\\-|cell|chtm|cldc|cmd\\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\\-s|devi|dica|dmob|do(c|p)o|ds(12|\\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\\-|_)|g1 u|g560|gene|gf\\-5|g\\-mo|go(\\.w|od)|gr(ad|un)|haie|hcit|hd\\-(m|p|t)|hei\\-|hi(pt|ta)|hp( i|ip)|hs\\-c|ht(c(\\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\\-(20|go|ma)|i230|iac( |\\-|\\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\\/)|klon|kpt |kwc\\-|kyo(c|k)|le(no|xi)|lg( g|\\/(k|l|u)|50|54|\\-[a-w])|libw|lynx|m1\\-w|m3ga|m50\\/|ma(te|ui|xo)|mc(01|21|ca)|m\\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\\-2|po(ck|rt|se)|prox|psio|pt\\-g|qa\\-a|qc(07|12|21|32|60|\\-[2-7]|i\\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\\-|oo|p\\-)|sdk\\/|se(c(\\-|0|1)|47|mc|nd|ri)|sgh\\-|shar|sie(\\-|m)|sk\\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\\-|v\\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\\-|tdg\\-|tel(i|m)|tim\\-|t\\-mo|to(pl|sh)|ts(70|m\\-|m3|m5)|tx\\-9|up(\\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\\-|your|zeto|zte\\-", re.I|re.M)

class DetectMobileBrowser():
    def process_request(self, request):
        request.mobile = False
        if request.META.has_key('HTTP_USER_AGENT'):
            user_agent = request.META['HTTP_USER_AGENT']
            b = reg_b.search(user_agent)
            v = reg_v.search(user_agent[0:4])
            if b or v:
                return HttpResponseRedirect("")