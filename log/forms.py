from django.forms import ModelForm
from log.models import Log, LogItem, Comment
from django.contrib.auth.models import User

class LogForm(ModelForm):
  class Meta:
    model = Log
    fields = ('summoner_name', 'region', 'initial_elo', 'initial_games_won', 'initial_games_lost')

class LogItemForm(ModelForm):
  class Meta:
    model = LogItem
    fields = ('champion', 'elo', 'text', 'win')

class SignupForm(ModelForm):
  class Meta:
    model = User
    fields = ('username', 'password', 'email')

class CommentForm(ModelForm):
  class Meta:
    model = Comment
    fields = ('text',)
