from django.template import Library
import datetime
import time

register = Library()

@register.filter
def date_or_never( date ):
  if date > datetime.datetime.fromtimestamp(0):
    return date
  else:
    return None
