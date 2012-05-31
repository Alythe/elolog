# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect
from log.models import Log, LogItem, News, Comment
from log.forms import LogForm, LogItemForm, CommentForm
from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import csv
import unicodedata
import datetime

### LOG Viewing ###
def index(request):
  c = RequestContext(request, {'user': request.user})
  news = News.objects.latest()
  logs = Log.objects.all()
  users = User.objects.all()
  logitems_won = LogItem.objects.filter(win__exact=True)
  logitems_lost = LogItem.objects.filter(win__exact=False)
  logitems_count = logitems_won.count() + logitems_lost.count()
  wl_ratio = "%.3f" % (float(logitems_won.count())/float(logitems_lost.count()))
  public_logs = Log.objects.filter(public__exact=True)
  public_logs_on_list = Log.objects.filter(public__exact=True, show_on_public_list__exact=True)

  c['news_item'] = news
  c['logs'] = logs
  c['public_logs'] = public_logs
  c['public_logs_on_list'] = public_logs_on_list
  c['users'] = users
  c['logitems_won'] = logitems_won
  c['logitems_lost'] = logitems_lost
  c['logitems_count'] = logitems_count
  c['wl_ratio'] = wl_ratio

  return render_to_response('home.html', c)

def logs(request, public=False, page=0):
  if not request.user.is_authenticated() and not public:
    return HttpResponseRedirect(reverse(index))
    
  if not public:
    log_list_all = Log.objects.filter(user__id__exact=request.user.id)
  else:
    log_list_all = Log.objects.filter(public__exact=True, show_on_public_list__exact=True).order_by('summoner_name')

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

  log_item_list = log.logitem_set.all()

  start_elo = log.initial_elo
  nr = 1
  elo_gain = []
  for item in log_item_list:
    item.nr = nr
    elo_gain.append(item.elo - start_elo)
    start_elo = item.elo
    nr += 1

  index = 0
  log_item_list_r = log_item_list.reverse()
  size = log_item_list_r.count()
  for item in log_item_list_r:
    item.elo_gain = elo_gain[size - 1 - index]
    index += 1

  c = RequestContext(request, {
    'log': log,
    'log_item_list': log_item_list_r,
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

  log_item_list = log.logitem_set.all()
  log_empty = len(log_item_list) == 0

  if not log_empty:
    data = "[ [0, %d], " % log.initial_elo

    index = 1
    for item in log.logitem_set.all():
      data += "[%d, %d]," % (index, item.elo)
      index += 1

    data += "]"
  else:
    data = ""

  return render_to_response('graph.html', RequestContext(request, {'log': log, 'js_data': data, 'log_empty': log_empty, 'log_id': log_id, 'is_public': public}))

def export_log(request, log_id):
  if not request.user.is_authenticated():
    return HttpResponseRedirect(reverse('log.views.index'))

  log = get_object_or_404(Log, pk=log_id)
  
  if not request.user.id == log.user.id:
    return HttpResponseRedirect(reverse('log.views.index'))

  response = HttpResponse(mimetype="text/csv")

  # do this to remove non ascii-printable characters
  name = unicodedata.normalize("NFKD", log.summoner_name).encode('ascii', 'ignore')
  response['Content-Disposition'] = 'attachment; filename=export_%s.csv' % name

  writer = csv.writer(response)
  writer.writerow(['Champion', 'Elo after', 'Remarks'])

  for item in log.logitem_set.all():
    writer.writerow([item.champion.name, item.elo, item.text])

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

  item = log.logitem_set.get(id=item_id)
  item.delete()

  return HttpResponseRedirect(reverse('log.views.index') + str(log_id))


def delete_log(request, log_id):
  if not request.user.is_authenticated():
    return HttpResponseRedirect(reverse('log.views.index'))
  
  log = get_object_or_404(Log, pk=log_id)
  
  if not request.user.id == log.user.id:
    return HttpResponseRedirect(reverse('log.views.index'))

  log.delete()

  return HttpResponseRedirect(reverse('log.views.index'))

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
    form = LogItemForm(request.POST, instance=item)

    if form.is_valid():
      form.save()

      return HttpResponseRedirect(reverse('log.views.view', args=[log_id]))
  else:
    form = LogItemForm(instance=item)

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
        return HttpResponseRedirect(reverse('log.views.logs'))

  else:
    form = LogForm(instance=log)

  return render_to_response('edit_log.html', RequestContext(request, {'form': form, 'log': log}))

### MISC News
def news(request):
  news = News.objects.all()
  return render_to_response('news/news_list.html', RequestContext(request, {'news': news}))

def news_comments(request, news_id):
  news = get_object_or_404(News, pk=news_id)
  
  if request.method == 'POST':
    if not request.user.is_authenticated() or not news.comments_allowed:
      return HttpResponseRedirect(reverse('log.views.news_comments', args=[news_id]))

    comment = Comment(user=request.user, news=news, date=datetime.datetime.today())
    form = CommentForm(request.POST, instance=comment)

    if form.is_valid():
      form.save()
    
  else:
    form = CommentForm()

  return render_to_response('news/news_detail.html', RequestContext(request, {'news_item': news, 'form': form}))
