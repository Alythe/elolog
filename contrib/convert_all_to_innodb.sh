#!/bin/bash
DATABASENAME=elolog
USER=root

stty -echo
read -p "Password: " PASSWORD; echo
stty echo

for t in `echo "show tables" | mysql -u $USER -p$PASSWORD --batch --skip-column-names $DATABASENAME`; do mysql -u $USER -p$PASSWORD $DATABASENAME -e "ALTER TABLE $t ENGINE = InnoDB DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;"; done
