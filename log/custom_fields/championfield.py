from django.forms import ModelChoiceField
from log.custom_fields.customfield import CustomField
import log.models
from django.conf import settings

class ChampionField(ModelChoiceField, CustomField):
  def __init__(self, *args, **kwargs):
    super(ChampionField, self).__init__(queryset=log.models.Champion.objects.all(), empty_label=None, *args, **kwargs)

  def render(self, data):
    champ = log.models.Champion.objects.get(pk=int(data))
    
    return "<img src=\"%simg/champions/%s\"></img>" % (settings.STATIC_URL, champ.image)

  def clean(self, data):
    # TODO safety checks
    return data

class SmallChampionField(ChampionField):
  def __init__(self, *args, **kwargs):
    super(ChampionField, self).__init__(queryset=log.models.Champion.objects.all(), empty_label=None, *args, **kwargs)

  def render(self, data):
    champ = log.models.Champion.objects.get(pk=int(data))
    
    return "<img src=\"%simg/champions/%s\" width=\"30px\" height=\"30px\"></img>" % (settings.STATIC_URL, champ.image)
