from log.models import UserProfile
from log.models import Log
from log.models import LogItem
from log.models import Champion, News, Comment
from django.contrib import admin

admin.site.register(Champion)
admin.site.register(UserProfile)

class LogItemAdmin(admin.TabularInline):
  model = LogItem

class LogAdmin(admin.ModelAdmin):
  inlines = [ LogItemAdmin, ]

class CommentAdmin(admin.TabularInline):
  model = Comment

class NewsAdmin(admin.ModelAdmin):
  inlines = [ CommentAdmin, ]

admin.site.register(Log, LogAdmin)
admin.site.register(News, NewsAdmin)
