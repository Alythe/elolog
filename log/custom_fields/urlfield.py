from django import forms
from log.custom_fields.textfield import ShortTextField
from django.forms import ValidationError
from django.utils.html import escape
from django.core.validators import URLValidator

class URLField(ShortTextField):
  def __init__(self, *args, **kwargs):
    super(URLField, self).__init__(*args, **kwargs)

  def clean(self, data):
    # URLFields can be empty
    if data == "":
      return data

    validate = URLValidator(verify_exists=False)

    try:
      validate(data)
    except ValidationError, e:
      raise ValidationError("This is not a valid URL!")

    return data

  def convert_value(self, value):
    try:
      self.clean(value)
    except ValidationError:
      return ""

    return value

  def render(self, data):
    if data != "":
      return '<a href="%s"><i class="icon-globe"></i></a>' % (data)
    else:
      return ""
