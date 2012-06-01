from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.contrib.sites.models import Site
from django.core.validators import MaxLengthValidator

import hashlib
import unicodedata

# Create your models here.

REGION_CHOICES = (
  ('NA', 'North America'),
  ('EUW', 'EU West'),
  ('EUNE', 'EU North & East'),
  ('CH', 'China'),
  ('KO', 'Korea'),
  ('SEA', 'Southeast Asia'),
)

class OUTCOME:
  WIN = 0
  LOSS = 1
  LEAVE = 2

GAME_OUTCOME_CHOICES = (
  (OUTCOME.WIN, 'Win'),
  (OUTCOME.LOSS, 'Loss'),
  (OUTCOME.LEAVE, 'Leave/Dodge'),
)

class Champion(models.Model):
  name = models.CharField(max_length = 100)
  image = models.CharField(max_length = 100)

  def __unicode__(self):
    return self.name

class UserProfile(models.Model):
  user = models.OneToOneField(User)

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
      return self.logitem_set.latest().elo

  def __unicode__(self):
    return self.summoner_name

class LogItem(models.Model):
  log = models.ForeignKey(Log)
  champion = models.ForeignKey(Champion)
  elo = models.IntegerField()
  text = models.TextField()
  outcome = models.IntegerField(default=0, choices=GAME_OUTCOME_CHOICES)
  date = models.DateTimeField('date created', auto_now_add=True, blank=True)

  def __unicode__(self):
    return self.text

  def is_win(self):
    return self.outcome==OUTCOME.WIN
  
  def is_loss(self):
    return self.outcome==OUTCOME.LOSS

  def is_leave(self):
    return self.outcome==OUTCOME.LEAVE

  class Meta:
    ordering = ['date']
    get_latest_by = 'date'

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
