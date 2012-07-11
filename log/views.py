# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect
from log.models import Log, LogItem, News, Comment, OUTCOME, UserProfile, StatisticEntry, LogCustomField
from log.forms import LogForm, LogItemForm, CommentForm, ResendActivationForm, CustomFieldForm, UserSettingsForm
from log.custom_fields.types import FieldTypes
from django.core.exceptions import ObjectDoesNotExist
from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.hashcompat import sha_constructor
from registration.models import RegistrationProfile
from django.contrib.sites.models import Site
from django.conf import settings
from django.utils import timezone

from random import random
import csv
import unicodedata
import datetime
import time
import re

### LOG Viewing ###
def index(request):
  c = RequestContext(request, {'user': request.user})
  news = News.objects.latest()
  logs = Log.objects.all()
  users = User.objects.all()
  logitems_won = LogItem.objects.filter(outcome=OUTCOME.WIN)
  logitems_lost = LogItem.objects.filter(outcome=OUTCOME.LOSS)
  logitems_left = LogItem.objects.filter(outcome=OUTCOME.LEAVE)
  logitems_count = logitems_won.count() + logitems_lost.count()
  wl_ratio = "%.3f" % (float(logitems_won.count())/float(logitems_lost.count()))
  
  # do this after wl_ratio calculation
  logitems_count += logitems_left.count()

  public_logs = Log.objects.filter(public__exact=True)
  public_logs_on_list = Log.objects.filter(public__exact=True, show_on_public_list__exact=True)

  logged_in_threshold = timezone.now() - datetime.timedelta(minutes=10)
  logged_in_profiles = UserProfile.objects.filter(last_activity__gte=logged_in_threshold)

  c['news_item'] = news
  c['logs'] = logs
  c['public_logs'] = public_logs
  c['public_logs_on_list'] = public_logs_on_list
  c['users'] = users
  c['logitems_won'] = logitems_won
  c['logitems_lost'] = logitems_lost
  c['logitems_left'] = logitems_left
  c['logitems_count'] = logitems_count
  c['wl_ratio'] = wl_ratio
  c['logged_in_profiles'] = logged_in_profiles

  if request.user.is_authenticated():
    c['last_login_str'] = time.strftime("%s %s" % (request.user.get_profile().date_format,
                                                 request.user.get_profile().time_format), 
                                                 request.user.last_login.timetuple())

  return render_to_response('home.html', c)

def logs(request, public=False, page=0):
  if not request.user.is_authenticated() and not public:
    return HttpResponseRedirect(reverse(index))
    
  if not public:
    log_list_all = Log.objects.filter(user__id__exact=request.user.id)
  else:
    log_list_all = Log.objects.filter(public__exact=True, show_on_public_list__exact=True)#.order_by('-last_update')

  paginator = Paginator(log_list_all, 25)
  page = request.GET.get('p')

  try:
    log_list = paginator.page(page)
  except PageNotAnInteger:
    log_list = paginator.page(1)
  except EmptyPage:
    log_list = paginator.page(paginator.num_pages)

  return render_to_response('logs.html', RequestContext(request, {'log_list': log_list, 'is_public': public}))

def view(request, log_id, public=False):

  if not public:
    if not request.user.is_authenticated():
      return HttpResponseRedirect(reverse('log.views.index'))
    
    log = get_object_or_404(Log, pk=log_id)

    if not request.user.id == log.user.id:
      return HttpResponseRedirect(reverse('log.views.index'))
  else:
    log = get_object_or_404(Log, public_hash__exact=log_id)
   
    if not log.public:
      return HttpResponseRedirect(reverse('log.views.index'))
  
  # next up: a piece of shitty code
  # this is so ugly, I wanna puke.
  # What it does:
  # It calculates the elo gain of ever log item
  # I store elo_gain in the log_item_list itself
  # But when I reverse it, the information is gone
  # So I store it in a temporary list first, reverse
  # and write everything back. That's O(n^2) and pretty fucked up
  # but it works for now(tm)

  field_list = log.logcustomfield_set.filter(display_on_overview=True)
  has_elo_field = field_list.filter(type=FieldTypes.ELO).count() > 0

  log_item_list = log.logitem_set.all()
  log_item_list_r = []

  if has_elo_field:
    start_elo = log.initial_elo
    elo_gain = []
    for item in log_item_list:
      elo_gain.append(item.get_elo() - start_elo)
      start_elo = item.get_elo()

  index = 0
  log_item_list_r = log_item_list.reverse()
  size = log_item_list_r.count()
  for item in log_item_list_r:
    item.nr = size - index
    if has_elo_field:
      item.elo_gain = elo_gain[size - 1 - index]
    index += 1

  paginator = Paginator(log_item_list_r, 25)
  page = request.GET.get('p')

  try:
    log_item_list = paginator.page(page)
  except PageNotAnInteger:
    log_item_list = paginator.page(1)
  except EmptyPage:
    log_item_list = paginator.page(paginator.num_pages)

  for item in log_item_list:
    item.field_values = []
    for field in field_list:
      field_queryset = item.logcustomfieldvalue_set.filter(custom_field=field)
      
      if field_queryset.count() == 0:
        item.field_values.append("")
      else:
        form_user = request.user
        if not request.user.is_authenticated():
          form_user = log.user

        field_value = field_queryset[0]
        if field_value.custom_field.type == FieldTypes.ELO:
          item.field_values.append(field.get_form_field(form_user).render(item.elo_gain, field_value.get_value()))
        else:
          item.field_values.append(field.get_form_field(form_user).render(field_value.get_value()))

  c = RequestContext(request, {
    'log': log,
    'log_item_list': log_item_list,
    'field_list': field_list,
    'user': request.user.id,
    'is_public': public
  })

  return render_to_response('view.html', c) 

### LOG Functions ###
def graph_log(request, log_id, public=False):

  if not public:
    if not request.user.is_authenticated():
      return HttpResponseRedirect(reverse('log.views.index'))

    log = get_object_or_404(Log, pk=log_id)
  
    if not request.user.id == log.user.id:
      return HttpResponseRedirect(reverse('log.views.index'))
  else:
    log = get_object_or_404(Log, public_hash__exact=log_id)

    if not log.public:
      return HttpResponseRedirect(reverse('log.views.index'))

  has_elo_field = log.logcustomfield_set.filter(type=FieldTypes.ELO).count() > 0

  data = ""
  log_empty = False
  if has_elo_field:

    log_item_list = log.logitem_set.all()
    log_empty = len(log_item_list) == 0

    if not log_empty:
      data = "[ [0, %d], " % log.initial_elo

      index = 1
      for item in log.logitem_set.all():
        data += "[%d, %d]," % (index, item.get_elo())
        index += 1

      data += "]"
    else:
      data = ""

  return render_to_response('graph.html', RequestContext(request, {'log': log, 'js_data': data, 'log_empty': log_empty, 'log_id': log_id, 'is_public': public, 'has_graph': has_elo_field}))

def export_log(request, log_id):
  if not request.user.is_authenticated():
    return HttpResponseRedirect(reverse('log.views.index'))

  log = get_object_or_404(Log, pk=log_id)
  
  if not request.user.id == log.user.id:
    return HttpResponseRedirect(reverse('log.views.index'))

  if not log.logitem_set.all().count():
    return HttpResponseRedirect(reverse('log.views.view', args=[log_id]))

  response = HttpResponse(mimetype="text/csv")

  # do this to remove non ascii-printable characters
  name = unicodedata.normalize("NFKD", log.summoner_name).encode('ascii', 'ignore')
  name = unicode(re.sub('[^\w\s-]', '', name).strip().lower())
  name = re.sub('[-\s]+', '-', name)

  response['Content-Disposition'] = 'attachment; filename=ex%d_%s.csv' % (log.id, name)

  writer = csv.writer(response)
  field_list = log.logcustomfield_set.all()
  head_row = [f.name for f in field_list]
  head_row.append("Outcome")

  writer.writerow(head_row)

  for item in log.logitem_set.all():
    row = []
    for field in field_list:
      field_value = item.logcustomfieldvalue_set.filter(custom_field=field)

      if field_value.count() == 0:
        row.append("")
      else:
        row.append(field_value[0].get_custom_field().get_form_field(request.user).format_value(field_value[0].get_value()))
    row.append(item.get_outcome_display())
    writer.writerow([s.encode("utf-8") for s in row])

  return response

def publish(request, log_id):
  log = get_object_or_404(Log, pk=log_id)

  if not request.user.is_authenticated():
    return HttpResponseRedirect(reverse('log.views.index'))

  if not request.user.id == log.user.id:
    return HttpResponseRedirect(reverse('log.views.index'))

  log.public = True
  log.save()
  return HttpResponseRedirect(reverse('log.views.view', args=[log_id]))

def unpublish(request, log_id):
  log = get_object_or_404(Log, pk=log_id)

  if not request.user.is_authenticated():
    return HttpResponseRedirect(reverse('log.views.index'))

  if not request.user.id == log.user.id:
    return HttpResponseRedirect(reverse('log.views.index'))

  log.public = False
  log.save()
  return HttpResponseRedirect(reverse('log.views.view', args=[log_id]))

### LOG Management
def delete_item(request, log_id, item_id):
  if not request.user.is_authenticated():
    return HttpResponseRedirect(reverse('log.views.index'))

  log = get_object_or_404(Log, pk=log_id)
  
  if not request.user.id == log.user.id:
    return HttpResponseRedirect(reverse('log.views.index'))

  # FIXME Do something instead of just failing silently
  try:
    item = log.logitem_set.get(id=item_id)
    item.delete()
  except ObjectDoesNotExist:
    pass

  return HttpResponseRedirect(reverse('log.views.view', args=[log_id]))


def delete_log(request, log_id):
  if not request.user.is_authenticated():
    return HttpResponseRedirect(reverse('log.views.index'))
  
  log = get_object_or_404(Log, pk=log_id)
  
  if not request.user.id == log.user.id:
    return HttpResponseRedirect(reverse('log.views.index'))

  log.delete()

  return HttpResponseRedirect(reverse('my_logs'))

def edit_item(request, log_id, item_id=None):
  if not request.user.is_authenticated():
    return HttpResponseRedirect(reverse('log.views.index'))
  
  log = get_object_or_404(Log, pk=log_id)

  if not request.user.id == log.user.id:
    return HttpResponseRedirect(reverse('log.views.index'))

  if item_id:
    item = log.logitem_set.get(id=item_id)
  else:
    item = LogItem(log=log)

  if request.method == 'POST':
    form = LogItemForm(request.POST, user=request.user, instance=item)

    if form.is_valid():
      form.save()

      return HttpResponseRedirect(reverse('log.views.view', args=[log_id]))
  else:
    form = LogItemForm(user=request.user, instance=item)

  return render_to_response('edit_item.html', RequestContext(request, {'form': form, 'item': item, 'log': log}))

def edit_log(request, log_id=None):
  if not request.user.is_authenticated():
    return HttpResponseRedirect(reverse('log.views.index'))
  
  if log_id:
    log = get_object_or_404(Log, pk=log_id)
  else:
    log = Log(user=request.user)
  
  if not request.user.id == log.user.id:
    return HttpResponseRedirect(reverse('log.views.index'))

  if request.method == 'POST':
    form = LogForm(request.POST, instance=log)

    if form.is_valid():

      form.save()
      if log_id:
        return HttpResponseRedirect(reverse('log.views.view', args=[log_id]))
      else:
        return HttpResponseRedirect(reverse('my_logs'))

  else:
    form = LogForm(instance=log)

  return render_to_response('edit_log.html', RequestContext(request, {'form': form, 'log': log}))

def view_fields(request, log_id):
  if not request.user.is_authenticated():
    return HttpResponseRedirect(reverse('log.views.index'))

  log = get_object_or_404(Log, pk=log_id)

  if not request.user.id == log.user.id:
    return HttpResponseRedirect(reverse('log.views.index'))

  field_list = log.logcustomfield_set.all()
  try:
    last_field = log.logcustomfield_set.latest()
  except ObjectDoesNotExist:
    last_field = None

  add_new_allowed = field_list.count() < settings.EG_MAX_CUSTOM_FIELDS

  return render_to_response('view_fields.html', RequestContext(request, {'log': log, 'field_list': field_list, 'add_new_allowed': add_new_allowed, 'last_field': last_field }))

def edit_field(request, log_id, field_id=None):
  if not request.user.is_authenticated():
    return HttpResponseRedirect(reverse('log.views.index'))
  
  log = get_object_or_404(Log, pk=log_id)
  
  if not request.user.id == log.user.id:
    return HttpResponseRedirect(reverse('log.views.index'))

  if field_id:
    field = get_object_or_404(LogCustomField, pk=field_id)
  else:
    if log.logcustomfield_set.count() >= settings.EG_MAX_CUSTOM_FIELDS:
      return HttpResponseRedirect(reverse('log.views.view_fields', args=[log_id]))

    field = LogCustomField(log=log)
    try:
      field.order = log.logcustomfield_set.latest().order + 1
    except ObjectDoesNotExist:
      field.order = 0

  if request.method == 'POST':
    form = CustomFieldForm(request.POST, instance=field)
    old_type = field.type

    if form.is_valid():
      form.save()
      
      for item in log.logitem_set.all():
        for custom_value in item.logcustomfieldvalue_set.filter(custom_field=field):
          custom_value.set_value(field.get_form_field(log.user).convert_value(custom_value.get_value()))
          custom_value.save()


      return HttpResponseRedirect(reverse('log.views.view_fields', args=[log_id]))
  else:
    form = CustomFieldForm(instance=field)

  return render_to_response('edit_field.html', RequestContext(request, {'form': form, 'log': log, 'field': field}))

def delete_field(request, log_id, field_id):
  if not request.user.is_authenticated():
    return HttpResponseRedirect(reverse('log.views.index'))

  log = get_object_or_404(Log, pk=log_id)
  
  if not request.user.id == log.user.id:
    return HttpResponseRedirect(reverse('log.views.index'))

  try:
    field = log.logcustomfield_set.get(id=field_id)
  except ObjectDoesNotExist:
    return HttpResponseRedirect(reverse('log.views.view', args=[log_id]))

  field.delete()

  return HttpResponseRedirect(reverse('log.views.view_fields', args=[log_id]))

def order_field_up(request, log_id, field_id):
  if not request.user.is_authenticated():
    return HttpResponseRedirect(reverse('log.views.index'))

  log = get_object_or_404(Log, pk=log_id)
  
  if not request.user.id == log.user.id:
    return HttpResponseRedirect(reverse('log.views.index'))

  try:
    field = log.logcustomfield_set.get(id=field_id)
  except ObjectDoesNotExist:
    return HttpResponseRedirect(reverse('log.views.view_fields', args=[log_id]))

  if field.order == 0:
    return HttpResponseRedirect(reverse('log.views.view_fields', args=[log_id]))

  try:
    field_swap = log.logcustomfield_set.get(order=field.order-1)
  except ObjectDoesNotExist:
    return HttpResponseRedirect(reverse('log.views.view_fields', args=[log_id]))

  new_order = field_swap.order
  field_swap.order = field.order
  field.order = new_order
  field.save()
  field_swap.save()

  return HttpResponseRedirect(reverse('log.views.view_fields', args=[log_id]))

def order_field_down(request, log_id, field_id):
  if not request.user.is_authenticated():
    return HttpResponseRedirect(reverse('log.views.index'))

  log = get_object_or_404(Log, pk=log_id)
  
  if not request.user.id == log.user.id:
    return HttpResponseRedirect(reverse('log.views.index'))

  try:
    field = log.logcustomfield_set.get(id=field_id)
  except ObjectDoesNotExist:
    return HttpResponseRedirect(reverse('log.views.view_fields', args=[log_id]))

  if field.order == log.logcustomfield_set.latest().order:
    return HttpResponseRedirect(reverse('log.views.view_fields', args=[log_id]))

  try:
    field_swap = log.logcustomfield_set.get(order=field.order+1)
  except ObjectDoesNotExist:
    return HttpResponseRedirect(reverse('log.views.view_fields', args=[log_id]))

  new_order = field_swap.order
  field_swap.order = field.order
  field.order = new_order
  field.save()
  field_swap.save()

  return HttpResponseRedirect(reverse('log.views.view_fields', args=[log_id]))

### ACCOUNT Management
def user_settings(request):
  if not request.user.is_authenticated():
    return HttpResponseRedirect(reverse('log.views.index'))

  saved = False

  if request.method == 'POST':
    form = UserSettingsForm(request.POST, instance=request.user.get_profile())

    if form.is_valid():
      form.save()
      saved = True
  else:
    form = UserSettingsForm(instance=request.user.get_profile())

  return render_to_response("user_settings.html", RequestContext(request, {'form': form, 'saved': saved}))


def resend_activation(request):
  if request.user.is_authenticated():
    return HttpResponseRedirect(reverse('log.views.index'))

  if request.method == 'POST':
    form = ResendActivationForm(request.POST)

    if form.is_valid():
      email = form.cleaned_data["email"]
      
      try:
        user = User.objects.get(email=email, is_active=0)
      except ObjectDoesNotExist:
        user = None

      if not user:
        form._errors["email"] = ("No account found for this email or already activated!",)
      else:
        profile = RegistrationProfile.objects.get(user=user)

        if profile.activation_key_expired():
          salt = sha_constructor(str(random())).hexdigest()[:5]
          profile.activation_key = sha_constructor(salt+user.username).hexdigest()
          user.date_joined = timezone.now()
          user.save()
          profile.save()
        else:
          # as long as the key is not expired, don't let them send a new one
          # this is to avoid abuse
          expiration_date = datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
          date = user.date_joined + expiration_date - timezone.now()
          if date > datetime.timedelta(days=1):
            time_to_wait = "two days"
          elif date > datetime.timedelta(hours=8):
            time_to_wait = "a day"
          elif date > datetime.timedelta(hours=3):
            time_to_wait = "a few hours"
          else:
            time_to_wait = "an hour"

          return render_to_response("registration/activation_resend_complete.html", 
              RequestContext(request, {'success': False, 'time_to_wait': time_to_wait}))

        if Site._meta.installed:
          site = Site.objects.get_current()
        else:
          site = RequestSite(request)

        profile.send_activation_email(site)

        return render_to_response("registration/activation_resend_complete.html", 
            RequestContext(request, {'success': True}))
  else:
    form = ResendActivationForm()

  return render_to_response("registration/activation_resend_form.html",
      RequestContext(request, {'form': form}))
        
### MISC News
def news(request):
  news = News.objects.all()
  return render_to_response('news/news_list.html', RequestContext(request, {'news': news}))

def news_comments(request, news_id):
  news = get_object_or_404(News, pk=news_id)
  
  if request.method == 'POST':
    if not request.user.is_authenticated() or not news.comments_allowed:
      return HttpResponseRedirect(reverse('log.views.news_comments', args=[news_id]))

    comment = Comment(user=request.user, news=news, date=timezone.now())
    form = CommentForm(request.POST, instance=comment)

    if form.is_valid():
      form.save()
      return HttpResponseRedirect(reverse('log.views.news_comments', args=[news_id]))

  else:
    form = CommentForm()

  comments_all = news.comment_set.all()
  paginator = Paginator(comments_all, 10)
  page = request.GET.get('p')

  try:
    comment_list = paginator.page(page)
  except PageNotAnInteger:
    comment_list = paginator.page(1)
  except EmptyPage:
    comment_list = paginator.page(paginator.num_pages)

  return render_to_response('news/news_detail.html', RequestContext(request, {'news_item': news, 'comment_list': comment_list, 'form': form}))

### MISC Global stats
def global_stats(request):
  if not request.user.is_authenticated() or not request.user.is_staff:
    return HttpResponseRedirect(reverse('log.views.index'))

  stats = StatisticEntry.objects.all().reverse() 
  
  data_games = []
  data_users = []
  data_wl_ratio = []
  data_users_online = []
  users_online_hourly = 24*[0]
  data_active_users = []

  tmp_count = 0

  # dirty hacks because of empty records
  start_users = False
  start_users_active = False

  for entry in stats:
    timestamp = int(time.mktime(entry.date.timetuple())*1000)
    data_games.append("[%d, %d]" % (timestamp, entry.game_count))
    data_users.append("[%d, %d]" % (timestamp, entry.user_count))
    data_wl_ratio.append("[%d, %f]" % (timestamp, entry.wl_ratio))
    if (entry.users_online > 0):
      start_users = True

    if start_users:
      data_users_online.append("[%d, %d]" % (timestamp, entry.users_online))

    if (entry.active_users > 0):
      start_users_active = True

    if start_users_active:
      data_active_users.append("[%d, %d]" % (timestamp, entry.active_users))

    users_online_hourly[entry.date.hour] += entry.users_online
    if entry.users_online > 0:
      tmp_count += 1
  
  data_users_online_hourly = 24*[""]
  for i in range(0, 24):
    data_users_online_hourly[i] = "[%d, %f]" % (i, float(users_online_hourly[i]) / float(tmp_count))

  return render_to_response('global_stats.html', RequestContext(request, {
    'data_games': ','.join(data_games),
    'data_users': ','.join(data_users),
    'data_wl_ratio': ','.join(data_wl_ratio),
    'data_users_online': ','.join(data_users_online),
    'data_users_online_hourly': ','.join(data_users_online_hourly),
    'data_active_users': ','.join(data_active_users),
     }))
