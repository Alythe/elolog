from django.forms import ModelForm, CharField, Textarea, Form, EmailField, ValidationError
from log.models import Log, LogItem, Comment
from django.contrib.auth.models import User

class LogForm(ModelForm):

  def clean_initial_elo(self):
    data = self.cleaned_data['initial_elo']
    if data > 5000 or data < 0:
      raise ValidationError("Please enter a reasonable Elo value")
    return data

  def clean_initial_games_won(self):
    data = self.cleaned_data['initial_games_won']
    if data > 50000 or data < 0:
      raise ValidationError("Please enter a reasonable number of games")
    return data

  def clean_initial_games_lost(self):
    data = self.cleaned_data['initial_games_lost']
    if data > 50000 or data < 0:
      raise ValidationError("Please enter a reasonable number of games")
    return data

  def clean_initial_games_left(self):
    data = self.cleaned_data['initial_games_left']
    if data > 50000 or data < 0:
      raise ValidationError("Please enter a reasonable number of games")
    return data

  class Meta:
    model = Log
    fields = ('summoner_name', 'region', 'initial_elo', 'initial_games_won', 'initial_games_lost', 'initial_games_left', 'show_on_public_list')

class LogItemForm(ModelForm):

  def clean_elo(self):
    data = self.cleaned_data['elo']
    if data > 5000 or data < 0:
      raise ValidationError("Please enter a reasonable Elo value")
    return data

  class Meta:
    model = LogItem
    fields = ('champion', 'elo', 'text', 'outcome')

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

class ResendActivationForm(Form):
  email = EmailField(required=True)
