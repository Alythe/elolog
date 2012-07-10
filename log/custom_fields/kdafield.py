from django import forms
from log.custom_fields.customfield import CustomField
from log.fields import KDAField
from log.widgets import KDAWidget
from django.forms import ValidationError

class KDAField(KDAField, CustomField):
  def __init__(self, *args, **kwargs):
    super(KDAField, self).__init__(widget=KDAWidget(attrs={'class': 'kda_field'}), *args, **kwargs)

  def clean(self, value):
    try:
      k = int(value[0])
      d = int(value[1])
      a = int(value[2])

      if k < 0 or k > 200 or d < 0 or d > 200 or a < 0 or a > 200:
        raise ValidationError("Please enter positive, reasonable numbers.")
    except ValueError:
      raise ValidationError("Please enter positive, reasonable numbers.")
    
    return self.compress(value)

  def convert_value(self, value):
    try:
      self.clean(value)
    except ValidationError:
      return "0/0/0"

    return value

  def render(self, value):
    return "%s" % (value)
