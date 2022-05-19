from django.contrib import admin

from .models import Gridiron


class GridironAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'date_created', 'date_updated',)
    list_display = (
        'id', 'team_name', 'team_mem1', 'team_mem2', 'team_mem3',
        'team_event', 'date_created', 'date_updated',
    )
    list_editable = (
        'team_name', 'team_mem1', 'team_mem2', 'team_mem3', 'team_event'
    )


admin.site.register(Gridiron, GridironAdmin)
