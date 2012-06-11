from django.forms import IntegerField
from log.custom_fields.customfield import CustomField

class NumberField(IntegerField, CustomField):
  def __init__(self, *args, **kwargs):
    super(NumberField, self).__init__(*args, **kwargs)

# rendering of this is done in views.py
class EloField(NumberField):
  def __init__(self, *args, **kwargs):
    super(EloField, self).__init__(*args, **kwargs)

  def render(self, elo_gain, elo):
    return "%d (%s)" % (elo_gain, elo)
