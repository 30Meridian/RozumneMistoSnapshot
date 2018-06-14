import datetime

from django.contrib.admin import AdminSite

from . import statistics


class CustomAdminSite(AdminSite):
    def index(self, request, extra_context=None):
        def period(end_date, step):
            curr_date = end_date - 12*step
            for i in range(12):
                curr_date += step
                yield curr_date

        extra_context = extra_context or {}

        values = {}
        now_date = datetime.datetime.now()
        delta = datetime.timedelta(days=30)
        values['period'] = [date.date() for date in period(now_date, delta)]

        stats = []
        functions_list = [
            ('Кількість користувачів в системі', statistics.users_registered),
            ('Кількість новин, опублікованих в системі', statistics.news_published),
            ('Кількість петицій, створених в системі', statistics.petitions_created),
            ('Кількість стоворених дефектів ЖКГ', statistics.defects_created),
            ('Кількість створених опитувань', statistics.polls_created)
        ]
        for f in functions_list:
            stats.append({
                'title': f[0],
                'values': [f[1](date) for date in period(now_date, delta)]
            })

        values['stats'] = stats

        extra_context['statistics'] = values
        extra_context['users'] = statistics.city_stats()

        extra_context.update()
        return super(CustomAdminSite, self).index(request, extra_context)
