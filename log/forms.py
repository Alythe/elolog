from django.forms import ModelForm, CharField, Textarea, Form, EmailField, ValidationError, ChoiceField, Select
from log.models import Log, LogItem, Comment, LogCustomFieldValue, LogCustomField, UserProfile
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render_to_response, get_object_or_404

from log.custom_fields import presets

class LogForm(ModelForm):
  def __init__(self, *args, **kwargs):
    super(LogForm, self).__init__(*args, **kwargs)
    self.presets = presets.get_preset_data()
    
    preset_list = ()
    for name in self.presets:
      preset_list += ((name, name),)


    logs = self.instance.user.log_set.all()
    log_list = ()
    for log in logs:
      log_list += ((str(log.id), log.summoner_name),)

    choices = (
        ('Presets', (
          preset_list
        )),
        ('Copy fields from ...', (
          log_list
        )),
      )
    
    if not self.instance.id:
      self.fields_preset_field = ChoiceField(required=True, choices=choices)
      self.fields["preset"] = self.fields_preset_field

  def save(self, force_insert=False, force_update=False, commit=True):
    o = super(LogForm, self).save(commit=False)

    is_new = not self.instance.id

    if commit:
      o.save()

    if is_new:
      if self.cleaned_data['preset'] in self.presets:
        preset = self.presets[self.cleaned_data['preset']]
        presets.initialize_preset(self.instance, preset)
      else:
        try:
          log_id = long(self.cleaned_data['preset'])
        except ValueError:
          # silently catching this casting exception
          # as this will only happen when a user fiddles with POST data
          return

        log = get_object_or_404(Log, pk=log_id)

        for field in log.logcustomfield_set.all():
          new_field = LogCustomField(log=self.instance, type=field.type, name=field.name, order=field.order)
          new_field.save()

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
  def __init__(self, data=None, user=None, *args, **kwargs):
    from log.custom_fields.types import FieldTypes
    super(LogItemForm, self).__init__(data, *args, **kwargs)
    self.custom_fields = {}

    if self.instance:
      for field in self.instance.log.logcustomfield_set.all():
        value = None
        if self.instance.id:
          value = self.instance.logcustomfieldvalue_set.get_or_create(log_item=self.instance, custom_field=field)[0].get_value()
        
        self.fields[field.name] = field.get_form_field(user, initial=value)
        
        self.fields[field.name].label = field.name
        self.custom_fields[field.name] = field

  def save(self, force_insert=False, force_update=False, commit=True):
    o = super(LogItemForm, self).save(commit=False)

    if commit:
      o.save()
 
    for field in self.custom_fields:
      # insert
      value = self.instance.logcustomfieldvalue_set.get_or_create(log_item=self.instance, custom_field=self.custom_fields[field])[0]
        
      value.set_value(self.cleaned_data[field])
      value.save()

  class Meta:
    model = LogItem
    fields = ('outcome',)

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

class CustomFieldForm(ModelForm):
  class Meta:
    model = LogCustomField
    fields = ('name', 'type', 'display_on_overview')

class ResendActivationForm(Form):
  email = EmailField(required=True)

class UserSettingsForm(ModelForm):
  class Meta:
    model = UserProfile
    fields = ('date_format', 'time_format', 'time_zone')
