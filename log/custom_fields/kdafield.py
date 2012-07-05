from django import forms
from log.custom_fields.textfield import ShortTextField
from django.forms import ValidationError

class KDAField(ShortTextField):
  def __init__(self, *args, **kwargs):
    super(KDAField, self).__init__(*args, **kwargs)

  def clean(self, value):
    if '/' not in value and '-' not in value and ' ' not in value:
      raise ValidationError("Please enter your K/D/A in one of the following forms: K/D/A, K-D-A or K D A")

    data = []
    if '/' in value:
      data = value.split('/')
    elif ' ' in value:
      data = value.split(' ')
    elif '-' in value:
      data = value.split('-')

    if len(data) != 3:
      raise ValidationError("Please specify kills, deaths and assists!")

    for num in data:
      try:
        n = int(num)
        if n < 0:
          raise ValueError
      except ValueError:
        raise ValidationError("Please specify kills, deaths, assists as positive numbers!")

    return '/'.join(data)

  def convert_value(self, value):
    try:
      self.clean(value)
    except ValidationError:
      return "0/0/0"

    return value

  def render(self, value):
    return "%s" % (value)
