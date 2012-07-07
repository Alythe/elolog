from django import forms
from log.custom_fields.customfield import CustomField
from django.forms import ValidationError
from django.forms.fields import MultiValueField, CharField
from django.utils.html import escape
from django.core.validators import URLValidator
from django.conf import settings
from log.widgets import LogSplitDateTimeWidget
import datetime
import time

class DateField(MultiValueField, CustomField):
  widget = LogSplitDateTimeWidget

  def __init__(self, user, initial=None, *args, **kwargs):
    self.user = user 

    self.date_format = self.user.get_profile().date_format
    self.time_format = self.user.get_profile().time_format

    initial_date = datetime.datetime.now()
    if initial:
      try:
        initial_date = datetime.datetime.fromtimestamp(float(initial))
      except ValueError:
        initial_date = datetime.datetime.now()
    
    all_fields = (
        CharField(max_length=10),
        CharField(max_length=2),
        CharField(max_length=2),
        )

    super(DateField, self).__init__(all_fields, widget=LogSplitDateTimeWidget(date_format=self.date_format, time_format=self.time_format, attrs={'date_class':'datepicker','time_class':'timepicker'}, initial=initial_date), *args, **kwargs)

  def compress(self, data_list):
    """
    Takes the values from the MultiWidget and passes them as a
    list to this function. This function needs to compress the
    list into a single object to save.
    """
    if data_list:
      if not (data_list[0] and data_list[1] and data_list[2]):
        raise forms.ValidationError("Field is missing data.")
      
      try:
        obj_date = time.strptime("%s %s:%s" % (data_list[0], data_list[1], data_list[2]), "%s %%H:%%M" % (self.date_format))
      except ValueError:
        raise forms.ValidationError("Date and/or time is malformed!")

      return time.mktime(obj_date)            
    return None

  def clean(self, data):
    return self.compress(data)

  def render(self, data):
    timetuple = datetime.datetime.fromtimestamp(float(data)).timetuple()
    return "%s %s" % (time.strftime(self.date_format, timetuple),
        time.strftime(self.time_format, timetuple))
