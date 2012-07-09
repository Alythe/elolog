from django.template import Library
import datetime
import time
import pytz

register = Library()

@register.filter
def date_or_never( date ):
  if date > datetime.datetime.fromtimestamp(0, pytz.utc):
    return date
  else:
    return None
