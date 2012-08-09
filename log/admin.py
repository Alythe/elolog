from log.models import UserProfile
from log.models import Log
from log.models import LogItem
from log.models import Champion, News, Comment, LockSite
from django.contrib import admin

admin.site.register(Champion)
admin.site.register(UserProfile)
admin.site.register(LockSite)

class LogItemAdmin(admin.TabularInline):
  model = LogItem

class LogAdmin(admin.ModelAdmin):
  inlines = [ LogItemAdmin, ]
  search_fields = [ 'summoner_name', ]

class CommentAdmin(admin.TabularInline):
  model = Comment

class NewsAdmin(admin.ModelAdmin):
  inlines = [ CommentAdmin, ]

admin.site.register(Log, LogAdmin)
admin.site.register(News, NewsAdmin)
