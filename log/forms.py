from django.forms import ModelForm
from log.models import Log, LogItem
from django.contrib.auth.models import User

class LogForm(ModelForm):
  class Meta:
    model = Log
    fields = ('summoner_name', 'region', 'initial_elo', 'games_won', 'games_lost')

class LogItemForm(ModelForm):
  class Meta:
    model = LogItem
    fields = ('champion', 'elo', 'text', 'win')

class SignupForm(ModelForm):
  class Meta:
    model = User
    fields = ('username', 'password', 'email')
