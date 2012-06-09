from django.core.management.base import BaseCommand, CommandError
from log.models import Log, LogItem, StatisticEntry, OUTCOME, UserProfile
from django.contrib.auth.models import User
import datetime

class Command(BaseCommand):
  args = ''
  help = 'Takes a statistical snapshot and stores it into the database'

  def handle(self, *args, **options):
    log_count = Log.objects.all().count()
    game_count = LogItem.objects.all().count()
    user_count = User.objects.all().count()
    logitems_won = LogItem.objects.filter(outcome=OUTCOME.WIN)
    logitems_lost = LogItem.objects.filter(outcome=OUTCOME.LOSS)
    logitems_left = LogItem.objects.filter(outcome=OUTCOME.LEAVE)
    total_games = logitems_won.count() + logitems_lost.count()
    wl_ratio = (float(logitems_won.count())/float(logitems_lost.count()))
    
    logged_in_threshold = datetime.datetime.now() - datetime.timedelta(minutes=10)
    logged_in_profiles = UserProfile.objects.filter(last_activity__gte=logged_in_threshold)

    # do this after wl_ratio calculation
    total_games += logitems_left.count()

    entry = StatisticEntry()
    entry.date = datetime.datetime.now()
    entry.user_count = user_count
    entry.log_count = log_count
    entry.game_count = game_count
    entry.game_win_count = logitems_won.count()
    entry.game_loss_count = logitems_lost.count()
    entry.game_leave_count = logitems_left.count()
    entry.wl_ratio = wl_ratio
    entry.users_online = logged_in_profiles.count()

    entry.save()


