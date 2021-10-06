from django.contrib import admin
from .models import *

class LogAdmin(admin.ModelAdmin):
    list_display = (
        'plot', 'share_delta_percent', 'share_delta_money',
        'balance_delta_percent', 'balance_delta_money', 'share',
        'strategy', 'time_interval_start', 'time_interval_end',
    )


admin.site.register(Log, LogAdmin)
admin.site.register(Strategy)