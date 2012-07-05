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
