# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect
from log.models import Log, LogItem, News
from log.forms import LogForm, LogItemForm
from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth import logout, authenticate, login
from django.core.context_processors import csrf
import csv
import unicodedata

### LOG Viewing ###
def home(request):
  c = RequestContext(request, {'user': request.user})
  if not request.user.is_authenticated():
    return HttpResponseRedirect('/accounts/login')
  else:
    log_list = Log.objects.filter(user__id__exact=request.user.id)
    c['log_list'] = log_list
    return render_to_response('home.html', c)

def view(request, log_id, public=False):

  if not public:
    if not request.user.is_authenticated():
      return HttpResponseRedirect('/')
    
    log = get_object_or_404(Log, pk=log_id)

    if not request.user.id == log.user.id:
      return HttpResponseRedirect('/')
  else:
    log = get_object_or_404(Log, public_hash__exact=log_id)
   
    if not log.public:
      return HttpResponseRedirect('/')
    
  log_item_list = log.logitem_set.all()

  start_elo = log.initial_elo
  nr = 1
  for item in log_item_list:
    item.nr = nr
    item.elo_gain = item.elo - start_elo
    start_elo = item.elo
    nr += 1

  c = RequestContext(request, {
    'log': log,
    'log_item_list': log_item_list,
    'user': request.user.id,
    'is_public': public
  })

  return render_to_response('view.html', c) 

### LOG Functions ###
def graph_log(request, log_id, public=False):

  if not public:
    if not request.user.is_authenticated():
      return HttpResponseRedirect('/')

    log = get_object_or_404(Log, pk=log_id)
  
    if not request.user.id == log.user.id:
      return HttpResponseRedirect('/')
  else:
    log = get_object_or_404(Log, public_hash__exact=log_id)

    if not log.public:
      return HttpResponseRedirect('/')

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
    return HttpResponseRedirect('/')

  log = get_object_or_404(Log, pk=log_id)
  
  if not request.user.id == log.user.id:
    return HttpResponseRedirect('/')

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
    return HttpResponseRedirect('/')

  if not request.user.id == log.user.id:
    return HttpResponseRedirect('/')

  log.public = True
  log.save()
  return HttpResponseRedirect('/' + log_id)

def unpublish(request, log_id):
  log = get_object_or_404(Log, pk=log_id)

  if not request.user.is_authenticated():
    return HttpResponseRedirect('/')

  if not request.user.id == log.user.id:
    return HttpResponseRedirect('/')

  log.public = False
  log.save()
  return HttpResponseRedirect('/' + log_id)

### LOG Management
def delete_item(request, log_id, item_id):
  if not request.user.is_authenticated():
    return HttpResponseRedirect('/')

  log = get_object_or_404(Log, pk=log_id)
  
  if not request.user.id == log.user.id:
    return HttpResponseRedirect('/')

  item = log.logitem_set.get(id=item_id)
  item.delete()

  return HttpResponseRedirect('/' + str(log_id))


def delete_log(request, log_id):
  if not request.user.is_authenticated():
    return HttpResponseRedirect('/')
  
  log = get_object_or_404(Log, pk=log_id)
  
  if not request.user.id == log.user.id:
    return HttpResponseRedirect('/')

  log.delete()

  return HttpResponseRedirect('/')

def edit_item(request, log_id, item_id=None):
  if not request.user.is_authenticated():
    return HttpResponseRedirect('/')
  
  log = get_object_or_404(Log, pk=log_id)

  if not request.user.id == log.user.id:
    return HttpResponseRedirect('/')

  if item_id:
    item = log.logitem_set.get(id=item_id)
  else:
    item = LogItem(log=log)

  if request.method == 'POST':
    form = LogItemForm(request.POST, instance=item)

    if form.is_valid():
      form.save()

      return HttpResponseRedirect('/' + str(log_id))
  else:
    form = LogItemForm(instance=item)

  return render_to_response('edit_item.html', RequestContext(request, {'form': form, 'item': item, 'log': log}))

def edit_log(request, log_id=None):
  if not request.user.is_authenticated():
    return HttpResponseRedirect('/')
  
  if log_id:
    log = get_object_or_404(Log, pk=log_id)
  else:
    log = Log(user=request.user)
  
  if not request.user.id == log.user.id:
    return HttpResponseRedirect('/')

  if request.method == 'POST':
    form = LogForm(request.POST, instance=log)

    if form.is_valid():

      form.save()
      if log_id:
        return HttpResponseRedirect('/' + str(log_id))
      else:
        return HttpResponseRedirect('/')

  else:
    form = LogForm(instance=log)

  return render_to_response('edit_log.html', RequestContext(request, {'form': form, 'log': log}))

### MISC News
def news(request):
  news = News.objects.all()
  return render_to_response('news.html', RequestContext(request, {'news': news}))
