from django.contrib import admin
from .models import *

class LogAdmin(admin.ModelAdmin):
    list_display = ('plot', 'share_delta', 'balance_delta')


admin.site.register(Log, LogAdmin)
admin.site.register(Strategy)