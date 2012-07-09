from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.contrib.sites.models import Site
from django.core.validators import MaxLengthValidator
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.utils import timezone
import custom_fields.types

import hashlib
import unicodedata
import datetime
import pytz

# Create your models here.

REGION_CHOICES = (
  ('NA', 'North America'),
  ('EUW', 'EU West'),
  ('EUNE', 'EU North & East'),
  ('CH', 'China'),
  ('KO', 'Korea'),
  ('SEA', 'Southeast Asia'),
)

DATE_TIME_FORMAT = "%d.%m.%Y %H:%M"
DATE_FORMAT = "%d.%m.%Y"
TIME_FORMAT = "%H:%M"
DATEPICKER_FORMAT = "dd.mm.yyyy" # this has to be the same as DATE_FORMAT but with different syntax (fuck js)


DATE_FORMAT_CHOICES = (
  ('%d.%m.%Y', 'dd.mm.yyyy'),
  ('%m-%d-%Y', 'mm-dd-yyyy'),
  ('%m/%d/%Y', 'mm/dd/yyyy'),
)

TIME_FORMAT_CHOICES = (
  ('%H:%M', '24 hours'),
  ('%I:%M %p', '12 hours (am/pm)'),
)

TIME_ZONE_CHOICES = ()

for tz in pytz.common_timezones:
  TIME_ZONE_CHOICES += ((tz, tz),)

class OUTCOME:
  WIN = 0
  LOSS = 1
  LEAVE = 2

GAME_OUTCOME_CHOICES = (
  (OUTCOME.WIN, 'Win'),
  (OUTCOME.LOSS, 'Loss'),
  (OUTCOME.LEAVE, 'Leave/Dodge'),
)

class LockSite(models.Model):
  active = models.BooleanField(default=False)
  text = models.TextField()

class Champion(models.Model):
  name = models.CharField(max_length = 100)
  image = models.CharField(max_length = 100)

  def __unicode__(self):
    return self.name

  class Meta:
    ordering = ['name']

class UserProfile(models.Model):
  user = models.OneToOneField(User)
  last_activity = models.DateTimeField(default=timezone.now())
  date_format = models.CharField(max_length=256, choices=DATE_FORMAT_CHOICES, default='%d.%m.%Y')
  time_format = models.CharField(max_length=256, choices=TIME_FORMAT_CHOICES, default='%H:%M')
  time_zone = models.CharField(max_length=256, choices=TIME_ZONE_CHOICES, default=settings.TIME_ZONE)

  def update_activity(self):
    self.last_activity = timezone.now()
    self.save()

  def get_time_zone(self):
    return pytz.timezone(self.time_zone)

  def __unicode__(self):
    return "%s's profile" % self.user

def create_user_profile(sender, instance, created, **kwargs):
  if created:
    profile, created = UserProfile.objects.get_or_create(user=instance)

post_save.connect(create_user_profile, sender=User)

class Log(models.Model):
  user = models.ForeignKey(User)
  summoner_name = models.CharField(max_length = 48)
  region = models.CharField(max_length=4, choices=REGION_CHOICES)
  initial_elo = models.PositiveIntegerField(default=0)
  initial_games_won = models.PositiveIntegerField(default=0)
  initial_games_lost = models.PositiveIntegerField(default=0)
  initial_games_left = models.PositiveIntegerField(default=0)
  public = models.BooleanField(default=False)
  public_hash = models.CharField(max_length = 10, default = "", blank=True)
  show_on_public_list = models.BooleanField(default=False)
  last_update = models.DateTimeField('date updated', default=datetime.datetime(1970,1,1, tzinfo=pytz.utc), blank=True)

  class Meta:
    ordering = ['-last_update']

  def update_last_update(self):
    try:
      self.last_update = self.logitem_set.latest().date
      self.save()
    except ObjectDoesNotExist:
      pass

  def total_games(self):
    return self.games_won() + self.games_lost() + self.games_left()

  def games_won(self):
    count = self.initial_games_won
    return self.logitem_set.filter(outcome=OUTCOME.WIN).count() + count

  def games_lost(self):
    count = self.initial_games_lost
    return self.logitem_set.filter(outcome=OUTCOME.LOSS).count() + count

  def games_left(self):
    count = self.initial_games_left
    return self.logitem_set.filter(outcome=OUTCOME.LEAVE).count() + count

  def win_loss_ratio(self):
    if self.games_won() > 0 and self.games_lost() > 0:
      return '%.3f' % (float(self.games_won()) / float(self.games_lost()),)
    else:
      return 0

  def public_url(self):
    if len(self.public_hash) == 0 and self.public:
      name = unicodedata.normalize("NFKD", self.summoner_name).encode('ascii', 'ignore')
      self.public_hash = hashlib.md5(str(self.id) + name).hexdigest()[:10]
      self.save()
    
    if self.public:
      domain = Site.objects.get_current().domain
      return "http://%s/public/%s" % (domain, self.public_hash)
    else:
      return ""

  def current_elo(self):
    if self.logitem_set.count() == 0:
      return self.initial_elo
    else:
      from custom_fields.types import FieldTypes
      elo_field_queryset = self.logcustomfield_set.filter(type=FieldTypes.ELO)
      
      # log has an elo field
      if elo_field_queryset.count() > 0:
        elo_queryset = self.logitem_set.latest().logcustomfieldvalue_set.filter(custom_field=elo_field_queryset[0])

        if elo_queryset.count() == 1:
          return elo_queryset[0].get_value()
      
      return 0

  def __unicode__(self):
    return self.summoner_name

class LogItem(models.Model):
  log = models.ForeignKey(Log)
  #champion = models.ForeignKey(Champion)
  #elo = models.IntegerField()
  #text = models.TextField()
  outcome = models.IntegerField(default=0, choices=GAME_OUTCOME_CHOICES)
  date = models.DateTimeField('date created', auto_now_add=True, blank=True)

  def __unicode__(self):
    return "Entry #%d, Log %s" % (self.id, self.log.summoner_name)

  def save(self, **kwargs):
    super(LogItem, self).save(**kwargs)
    self.log.update_last_update()

  def delete(self):
    super(LogItem, self).delete()
    self.log.update_last_update()

  def is_win(self):
    return self.outcome==OUTCOME.WIN
  
  def is_loss(self):
    return self.outcome==OUTCOME.LOSS

  def is_leave(self):
    return self.outcome==OUTCOME.LEAVE

  def get_elo(self):
    from custom_fields.types import FieldTypes
    elo_field_queryset = self.log.logcustomfield_set.filter(type=FieldTypes.ELO)

    if elo_field_queryset.count() > 0:
      elo_queryset = self.logcustomfieldvalue_set.filter(custom_field=elo_field_queryset[0])
      if elo_queryset.count() == 1:
        return int(elo_queryset[0].get_value())
    
    return 0

  class Meta:
    ordering = ['date']
    get_latest_by = 'date'

class LogCustomField(models.Model):
  from custom_fields.types import FIELD_TYPE_CHOICES, FieldTypes, FIELD_TYPES
  log = models.ForeignKey(Log)
  type = models.IntegerField(choices=FIELD_TYPE_CHOICES)
  name = models.CharField(max_length=255, default="")
  display_on_overview = models.BooleanField(default=True)
  order = models.IntegerField(default=0)
  
  class Meta:
    ordering = ['order']
    get_latest_by = 'order'

  def get_form_field(self, user, *args, **kwargs):
    from custom_fields.types import FIELD_TYPES
    return FIELD_TYPES[self.type](user, *args, **kwargs)

  def __unicode__(self):
    return "#%d '%s' (%s)" % (self.id, self.name, self.get_type_display())

class LogCustomFieldValue(models.Model):
  custom_field = models.ForeignKey(LogCustomField)
  log_item = models.ForeignKey(LogItem)
  _value = models.TextField(db_column='value', blank=True)

  def set_value(self, value):
    self._value = str(value)

  def get_value(self):
    return self._value or ""

  def get_custom_field(self):
    return self.custom_field

  data = property(get_value, set_value)

class News(models.Model):
  date = models.DateTimeField()
  title = models.CharField(max_length = 200)
  text = models.TextField()
  user = models.ForeignKey(User)
  comments_allowed = models.BooleanField(default=True)

  def __unicode__(self):
    return self.title

  class Meta:
    ordering = ['-date']
    get_latest_by = 'date'

class Comment(models.Model):
  date = models.DateTimeField()
  user = models.ForeignKey(User)
  news = models.ForeignKey(News)
  text = models.CharField(max_length=1000)

  def __unicode__(self):
    return "%s - %s" % (self.user.username, self.text)

  class Meta:
    ordering = ['-date']

class StatisticEntry(models.Model):
  date = models.DateTimeField()
  user_count = models.IntegerField()
  log_count = models.IntegerField()
  game_count = models.IntegerField()
  game_win_count = models.IntegerField()
  game_loss_count = models.IntegerField()
  game_leave_count = models.IntegerField()
  wl_ratio = models.FloatField()
  users_online = models.IntegerField(default=0)
  active_users = models.IntegerField(default=0)

  class Meta:
    ordering = ['-date']
