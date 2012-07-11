from django.forms import ModelChoiceField
from log.custom_fields.customfield import CustomField
import log.models
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

class ChampionField(ModelChoiceField, CustomField):
  def __init__(self, value=None, *args, **kwargs):
    super(ChampionField, self).__init__(queryset=log.models.Champion.objects.all(), empty_label=None, *args, **kwargs)

  def render(self, data):
    try:
      champ_id = int(data)
    except ValueError:
      champ_id = 1

    try:
      champ = log.models.Champion.objects.get(pk=champ_id)
    except ObjectDoesNotExist:
      return ""
  
    if champ.image == "-":
      return ""

    return "<img src=\"%simg/champions/%s\" width=\"80px\"></img>" % (settings.STATIC_URL, champ.image)

  def format_value(self, value):
    try:
      champ = log.models.Champion.objects.get(pk=int(value))
    except (ObjectDoesNotExist, ValueError):
      return ""

    return champ.name

  def convert_value(self, value):
    try:
      id = int(value)
      champ = log.models.Champion.objects.get(pk=id)
    except (ValueError, ObjectDoesNotExist):
      return 1 # return first champion

    return value

  def clean(self, data):
    # TODO safety checks
    return data

class SmallChampionField(ChampionField):
  def __init__(self, *args, **kwargs):
    super(SmallChampionField, self).__init__(*args, **kwargs)

  def render(self, data):
    try:
      champ = log.models.Champion.objects.get(pk=int(data))
    except (ObjectDoesNotExist, ValueError):
      return ""
   
    if champ.image == "-":
      return ""

    return "<img src=\"%simg/champions/%s\" width=\"30px\" height=\"30px\"></img>" % (settings.STATIC_URL, champ.image)
