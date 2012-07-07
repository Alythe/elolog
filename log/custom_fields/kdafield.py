from django import forms
from log.custom_fields.customfield import CustomField
from log.fields import KDAField
from log.widgets import KDAWidget
from django.forms import ValidationError

class KDAField(KDAField, CustomField):
  def __init__(self, *args, **kwargs):
    super(KDAField, self).__init__(widget=KDAWidget(attrs={'class': 'kda_field'}), *args, **kwargs)

  def clean(self, value):
    return self.compress(value)

  def convert_value(self, value):
    try:
      self.clean(value)
    except ValidationError:
      return "0/0/0"

    return value

  def render(self, value):
    return "%s" % (value)
