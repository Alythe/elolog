from django.core.management.base import BaseCommand, CommandError
from log.models import Log, LogItem, StatisticEntry, OUTCOME, UserProfile
from django.contrib.auth.models import User
import datetime

class Command(BaseCommand):
  args = ''
  help = 'Takes a statistical snapshot and stores it into the database'

  def handle(self, *args, **options):
    stats = StatisticEntry.objects.all().reverse()

    old = None
    for stat in stats:
      if old == None:
        old = stat
        continue

      time_diff = stat.date - old.date

      if time_diff <= datetime.timedelta(hours=2):
        break
     
      diff = {}
      hours = (time_diff.total_seconds() / 3600)
      diff['user_count']        = (stat.user_count        - old.user_count)
      diff['log_count']         = (stat.log_count         - old.log_count)
      diff['game_count']        = (stat.game_count        - old.game_count)
      diff['game_win_count']    = (stat.game_win_count    - old.game_win_count)
      diff['game_loss_count']   = (stat.game_loss_count   - old.game_loss_count)
      diff['game_leave_count']  = (stat.game_leave_count  - old.game_leave_count)
      diff['wl_ratio']          = (stat.wl_ratio          - old.wl_ratio)
      diff['users_online']      = (stat.users_online      - old.users_online)

      for i in range(1, int(hours)):
        entry = StatisticEntry()
        entry.date              = old.date + datetime.timedelta(hours=i)
        print("Inserting date %s ..." % (entry.date))
        entry.user_count        = old.user_count + (diff["user_count"]/hours) * i
        entry.log_count         = old.log_count + (diff["log_count"]/hours) * i
        entry.game_count        = old.game_count + (diff["game_count"]/hours) * i
        entry.game_win_count    = old.game_win_count + (diff["game_win_count"]/hours) * i
        entry.game_loss_count   = old.game_loss_count + (diff["game_loss_count"]/hours) * i
        entry.game_leave_count  = old.game_leave_count + (diff["game_leave_count"]/hours) * i
        entry.wl_ratio          = old.wl_ratio + (diff["wl_ratio"]/hours) * i
        entry.users_online      = old.users_online + (diff["users_online"]/hours) * i
        entry.save()

      old = stat
    """entry = StatisticEntry()
    entry.date = datetime.datetime.now()
    entry.user_count = user_count
    entry.log_count = log_count
    entry.game_count = game_count
    entry.game_win_count = logitems_won.count()
    entry.game_loss_count = logitems_lost.count()
    entry.game_leave_count = logitems_left.count()
    entry.wl_ratio = wl_ratio
    entry.users_online = logged_in_profiles.count()

    entry.save()"""


