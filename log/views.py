# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect
from log.models import Log, LogItem
from log.forms import LogForm, LogItemForm
from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth import logout, authenticate, login
from django.core.context_processors import csrf
import csv

def home(request):
  c = RequestContext(request, {'user': request.user})
  if not request.user.is_authenticated():
    return HttpResponseRedirect('/accounts/login')
  else:
    log_list = Log.objects.filter(user__id__exact=request.user.id)
    c['log_list'] = log_list
    return render_to_response('home.html', c)

def graph_log(request, log_id):
  if not request.user.is_authenticated():
    return HttpResponseRedirect('/')

  log = get_object_or_404(Log, pk=log_id)
  
  if not request.user.id == log.user.id:
    return HttpResponseRedirect('/')

  log_item_list = log.logitem_set.all()
  log_empty = len(log_item_list) == 0

  if not log_empty:
    data = "["

    index = 0
    for item in log.logitem_set.all():
      data += "[%d, %d]," % (index, item.elo)
      index += 1

    data += "]"
  else:
    data = ""


def public_graph_log(request, log_hash):
  log = get_object_or_404(Log, public_hash__exact=log_hash)

  if not log.public:
    return HttpResponseRedirect('/')
  
  log_item_list = log.logitem_set.all()
  log_empty = len(log_item_list) == 0

  if not log_empty:
    data = "["

    index = 0
    for item in log.logitem_set.all():
      data += "[%d, %d]," % (index, item.elo)
      index += 1

    data += "]"
  else:
    data = ""

  return render_to_response('graph.html', RequestContext(request, {'log': log, 'js_data': data, 'log_empty': log_empty}))


def export_log(request, log_id):
  if not request.user.is_authenticated():
    return HttpResponseRedirect('/')

  log = get_object_or_404(Log, pk=log_id)
  
  if not request.user.id == log.user.id:
    return HttpResponseRedirect('/')

  response = HttpResponse(mimetype="text/csv")
  response['Content-Disposition'] = 'attachment; filename=%s.csv' % log.summoner_name

  writer = csv.writer(response)
  writer.writerow(['Champion', 'ELO after', 'Remarks'])

  for item in log.logitem_set.all():
    writer.writerow([item.champion.name, item.elo, item.text])

  return response

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

      # update won/lost games in log
      won = 0
      lost = 0
      for item in log.logitem_set.all():
        if item.win:
          won += 1
        else:
          lost += 1

      log.games_won = won
      log.games_lost = lost
      log.current_elo = log.logitem_set.latest().elo
      log.save()

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

def view(request, log_id):
  log = get_object_or_404(Log, pk=log_id)

  if not request.user.is_authenticated():
    return HttpResponseRedirect('/')

  if not request.user.id == log.user.id:
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
    'user': request.user.id
  })

  return render_to_response('view.html', c) 

def public_view(request, log_hash):
  log = get_object_or_404(Log, public_hash__exact=log_hash)

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
    'user': request.user,
    'is_public': True
  })

  return render_to_response('view.html', c) 


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


def logout_user(request):
  if not request.user.is_authenticated():
    return HttpResponseRedirect('/')
  else:
    logout(request)
    return HttpResponseRedirect('/')
