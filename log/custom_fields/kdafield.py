from django import forms
from log.custom_fields.customfield import CustomField
from log.widgets import KDAWidget
from django.forms import ValidationError, MultiValueField, IntegerField

class KDAField(MultiValueField, CustomField):
  widget = KDAWidget

  def __init__(self, *args, **kwargs):

    all_fields = (
        IntegerField(),
        IntegerField(),
        IntegerField(),
        )
    
    if "required" in kwargs:
      self.required = kwargs['required']
      kwargs.pop("required")

    super(KDAField, self).__init__(all_fields, widget=KDAWidget(attrs={'class': 'kda_field'}), *args, **kwargs)

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

  def clean(self, value):
    try:
      if len(value) != 3:
        raise ValidationError("Please enter positive, reasonable numbers.")

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
