from django.forms import ModelForm, CharField, Textarea, Form, EmailField, ValidationError, ChoiceField, Select
from django.forms.util import ErrorList
from log.models import Log, LogItem, Comment, LogCustomFieldValue, LogCustomField, UserProfile, LOGITEMS_PER_PAGE_CHOICES
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render_to_response, get_object_or_404

from log.fields import IgnoreField
from log.custom_fields import presets

class AlertDivErrorList(ErrorList):
  def __unicode__(self):    
    return self.view_as_div()
  
  def view_as_div(self):
    if not self: 
      return u'' 
    
    return u'<div class="alert alert-error">%s</div>' % '<br/>'.join([u'<span>%s</span>' % e for e in self])

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
        value_obj = None
        if self.instance.id:
          try:
            value_obj = self.instance.logcustomfieldvalue_set.get(log_item=self.instance, custom_field=field)
            value = value_obj.get_value()
          except ObjectDoesNotExist:
            pass
      
        field_name = str(field.id)
        ignore_field_name = "%s_ignore" % field_name
        
        self.fields[field_name] = field.get_form_field(user, required=False, initial=value)
        
        ignore_field_value = False
        if self.data and ignore_field_name in self.data:
          ignore_field_value = True

        self.fields[ignore_field_name] = IgnoreField(required=False)
        self.fields[field_name].ignore_field = self[ignore_field_name]

        self.fields[field_name].label = field.name
        self.custom_fields[field_name] = field

  def clean(self):
    super(LogItemForm, self).clean()
    for field in self.custom_fields:
      ignore_field_name = "%s_ignore" % field
      if ignore_field_name in self.cleaned_data and self.cleaned_data[ignore_field_name] and field in self._errors:
        del self._errors[field]

    return self.cleaned_data   

  def save(self, force_insert=False, force_update=False, commit=True):
    o = super(LogItemForm, self).save(commit=False)

    if commit:
      o.save()
 
    for field in self.custom_fields:
      ignore_field_name = "%s_ignore" % field        

      # insert
      try:
        value = self.instance.logcustomfieldvalue_set.get(log_item=self.instance, custom_field=self.custom_fields[field])
      except ObjectDoesNotExist:
        value = LogCustomFieldValue(log_item=self.instance, custom_field = self.custom_fields[field])

      if self.cleaned_data[ignore_field_name]:
        if value.id:
          value.delete()
        continue
        
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
  logitems_per_page = ChoiceField(label="Log items per page", choices=LOGITEMS_PER_PAGE_CHOICES)

  class Meta:
    model = UserProfile
    fields = ('date_format', 'time_format', 'time_zone', 'logitems_per_page')
