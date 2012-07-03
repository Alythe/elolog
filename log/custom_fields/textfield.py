from django import forms
from log.custom_fields.customfield import CustomField
from django.forms import ValidationError
from django.utils.html import escape

class TextField(forms.CharField, CustomField):
  def __init__(self, *args, **kwargs):
    super(TextField, self).__init__(widget=forms.Textarea, *args, **kwargs)

  def render(self, data):
    return escape(data)

class ShortTextField(forms.CharField, CustomField):
  def __init__(self, *args, **kwargs):
    super(ShortTextField, self).__init__(*args, **kwargs)

  def render(self, data):
    return escape(data)

class KDAField(ShortTextField):
  def __init__(self, *args, **kwargs):
    super(KDAField, self).__init__(*args, **kwargs)

  def clean(self, value):
    #super(KDAField, self).validate(value)

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

  def render(self, value):
    return "%s" % (value)
