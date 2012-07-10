from django.template import Library
from django.conf import settings
from django.utils import timezone
import datetime
import time

register = Library()

@register.filter
def pretty_format_date( date, user ):
  if date > datetime.datetime.fromtimestamp(0, timezone.utc):
    date_format = settings.DATE_FORMAT
    time_format = settings.TIME_FORMAT

    date = date.astimezone(timezone.get_current_timezone())

    if user.is_authenticated():
      date_format = user.get_profile().date_format
      time_format = user.get_profile().time_format

    return date.strftime("%s %s" % (date_format, time_format))
  else:
    return 'Never'
