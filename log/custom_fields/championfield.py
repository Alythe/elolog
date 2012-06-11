from django.forms import ModelChoiceField
from log.custom_fields.customfield import CustomField
from log.models import Champion
from django.conf import settings

class ChampionField(ModelChoiceField, CustomField):
  def __init__(self, *args, **kwargs):
    super(ChampionField, self).__init__(queryset=Champion.objects.all(), empty_label=None, *args, **kwargs)

  def render(self, data):
    champ = Champion.objects.get(pk=int(data))
    return "<img src=\"%simg/champions/%s\"></img>" % (settings.STATIC_URL, champ.image)

  def clean(self, data):
    # TODO safety checks
    return data
