# taken from http://copiesofcopies.org/webl/2010/04/26/a-better-datetime-widget-for-django/

from time import strptime, strftime, mktime
from datetime import datetime
from django import forms
from django.db import models
from django.forms import fields
from django.conf import settings

class IgnoreField(fields.BooleanField):
  def __init__(self, *args, **kwargs):
    super(IgnoreField, self).__init__(*args, **kwargs)
    self.hidden = True

  def is_hidden(self):
    return True
