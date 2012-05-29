from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import hashlib

# Create your models here.

REGION_CHOICES = (
  ('NA', 'North America'),
  ('EUW', 'EU West'),
  ('EUNE', 'EU North & East'),
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
  current_elo = models.PositiveIntegerField(default=0)
  games_won = models.PositiveIntegerField(default=0)
  games_lost = models.PositiveIntegerField(default=0)
  public = models.BooleanField(default=False)
  public_hash = models.CharField(max_length = 10, default = "", blank=True)

  def total_games(self):
    return self.games_won + self.games_lost

  def win_loss_ratio(self):
    if self.games_won > 0 and self.games_lost > 0:
      return '%.3f' % (float(self.games_won) / float(self.games_lost),)
    else:
      return 0

  def public_url(self):
    if len(self.public_hash) == 0 and self.public:
      self.public_hash = hashlib.md5(str(self.id) + self.summoner_name).hexdigest()[:10]
      self.save()
    
    if self.public:
      return "http://elolog.com/public/%s" % self.public_hash
    else:
      return ""

  def __unicode__(self):
    return self.summoner_name

class LogItem(models.Model):
  log = models.ForeignKey(Log)
  champion = models.ForeignKey(Champion)
  elo = models.IntegerField()
  text = models.TextField()
  win = models.BooleanField()
  date = models.DateTimeField('date created', auto_now_add=True, blank=True)

  def __unicode__(self):
    return self.text

  class Meta:
    ordering = ['date']
    get_latest_by = 'date'

