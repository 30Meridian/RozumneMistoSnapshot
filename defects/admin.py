from django.contrib import admin
from .models import Issues, Subcontractors


class SubcontractorsAdmin(admin.ModelAdmin):
    list_display = ("name", "town_ref")


class DefectsAdmin(admin.ModelAdmin):
    list_display = ('title', 'short_desc', 'address')
    exclude = ('parent_task_ref',)
    readonly_fields = ('owner_ref','status','assigned_to','town_ref','title','description','address','map_lon','map_lat')
    def short_desc(self, obj):
        if len(obj.description) > 80:
            return obj.description[:80] + '...'
        else:
            return obj.description

    def get_queryset(self, request):
        queryset = super(DefectsAdmin, self).get_queryset(request)
        return queryset.filter(parent_task_ref=None)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    short_desc.short_description = 'Опис'
    short_desc.admin_order_field = 'description'


admin.site.register(Subcontractors, SubcontractorsAdmin)
admin.site.register(Issues, DefectsAdmin)
