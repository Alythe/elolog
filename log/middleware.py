from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import SiteProfileNotAvailable
from log.models import UserProfile, LockSite
from django.shortcuts import render_to_response, get_object_or_404
from django.template import Context, loader, RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.conf import settings
import pytz

class MaintenanceMiddleware():
  def process_request(self, request):
    if request.user.is_authenticated():
      try:
        profile = request.user.get_profile()
        profile.update_activity()
        timezone.activate(profile.get_time_zone())
      except SiteProfileNotAvailable:
        timezone.activate(pytz.timezone(settings.TIME_ZONE))
        return None

    return None

  def process_view(self, request, view_func, view_args, view_kwargs):
    try:
      lock = LockSite.objects.get()
      str_path = request.get_full_path()
      if lock and not str_path.startswith('/admin/'):
        if lock.active:
          return render_to_response('lock_site.html', RequestContext(request, {'text': lock.text}))
    except ObjectDoesNotExist:
      return None

    return None
