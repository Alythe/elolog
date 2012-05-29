from log.models import UserProfile
from log.models import Log
from log.models import LogItem
from log.models import Champion
from django.contrib import admin

admin.site.register(Champion)
admin.site.register(UserProfile)

class LogItemAdmin(admin.TabularInline):
  model = LogItem

class LogAdmin(admin.ModelAdmin):
  inlines = [ LogItemAdmin, ]

admin.site.register(Log, LogAdmin)
