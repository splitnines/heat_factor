from django.contrib import admin

from .models import Uspsa


class UspsaAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'date_created', 'date_updated',)
    list_display = (
        'id', 'uspsa_num', 'division', 'date_created', 'date_updated',
    )


admin.site.register(Uspsa, UspsaAdmin)
