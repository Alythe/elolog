# taken from http://copiesofcopies.org/webl/2010/04/26/a-better-datetime-widget-for-django/

from time import strptime, strftime, mktime
from datetime import datetime
from django import forms
from django.db import models
from django.forms import fields
from django.conf import settings
from log.widgets import LogSplitDateTimeWidget, KDAWidget

class KDAField(fields.MultiValueField):
  widget = KDAWidget

  def __init__(self, *args, **kwargs):
    all_fields = (
        fields.IntegerField(),
        fields.IntegerField(),
        fields.IntegerField(),
        )

    super(KDAField, self).__init__(all_fields, *args, **kwargs)

  def compress(self, data_list):
    if data_list:
      if not (data_list[0] and data_list[1] and data_list[2]):
        raise forms.ValidationError("Field is imssing data.")

      try:
        data_list[0] = int(data_list[0])
        data_list[1] = int(data_list[1])
        data_list[2] = int(data_list[2])

        if data_list[0] < 0 or data_list[1] < 0 or data_list[2] < 0:
          raise ValueError()

      except ValueError:
        raise forms.ValidationError("Please only specify whole, positive numbers!")

      return "%s/%s/%s" % (data_list[0], data_list[1], data_list[2])

    return None
