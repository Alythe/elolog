from django.forms import ModelForm, CharField, Textarea
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
  text = CharField(
      max_length = 1000,
      widget = Textarea,
      error_messages={'max_length': u'Please write no more than 1000 characters!'}
  )

  class Meta:
    model = Comment
    fields = ('text',)
