#/usr/bin/env python2

import os

stream = open("champions.sql", "r")
stream.readline()

for line in stream:
  if len(line.strip()) > 0:
    line = [x.strip().replace("'", "") for x in line[1:-3].split(",")]
    print('UPDATE log_champion SET image="%s" WHERE id=%s AND name="%s";' % (line[2], line[0], line[1]))

stream.close()

