from django import forms
from log.custom_fields.customfield import CustomField
from django.forms import ValidationError
from django.utils.html import escape
from django.core.validators import URLValidator
from django.conf import settings
from log.fields import LogSplitDateTimeField
from log.widgets import LogSplitDateTimeWidget
import datetime
import time

class DateField(LogSplitDateTimeField, CustomField):
  def __init__(self, initial=None, *args, **kwargs):
   
    initial_date = datetime.datetime.now()
    if initial != None:
      try:
        initial_date = datetime.datetime.fromtimestamp(time.mktime(time.strptime(initial, settings.DATE_TIME_FORMAT)))
      except ValueError:
        initial_date = datetime.datetime.now()
    
    super(DateField, self).__init__(widget=LogSplitDateTimeWidget(attrs={'date_class':'datepicker','time_class':'timepicker'}, initial=initial_date), *args, **kwargs)

  def clean(self, data):
    return self.compress(data)

  def render(self, data):
    return "%s" % (data)
