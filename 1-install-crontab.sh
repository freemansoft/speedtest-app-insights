#!/bin/bash
# installs NetCheck.py in cron from this working directory and runs it every 10 minutes
# ASSUMES you have NO spaces in path to this directory
#
# You can run this script as many times as you wish. It will UPDATE any previous entry.

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
#echo $DIR
Me=`whoami`

# Can add NetCheck.py options to OPTIONS: --verbose or --download or --upload 
PYTHON_SCRIPT="NetCheck.py"

OPTIONS_PING_IT=""
OPTIONS_UP_DOWN="--upload --download"

# ping test every 3 minutes
MINUTES_PING_IT="*/3"
HOURS_PING_IT="*"

# up down test once per day
MINUTES_UP_DOWN="13"
HOURS_UP_DOWN="*/4"

DAYS_OF_MONTH="*"
DAYS_OF_WEEK="*"
# Use this if you want to see the logs in this folder - easier for torubleshooting
# REDIRECT_LOGS=">> $DIR/cron.log 2>&1"
REDIRECT_LOGS=""

echo "Installing crontab entries for ping and upload/download."
#echo "Ignore any messages that say 'no crontab for $Me'"
# must quote CRONTAB_LINE so it does expand asterisk
CRONTAB_LINE_PING="$MINUTES_PING_IT $HOURS_PING_IT $DAYS_OF_MONTH * $DAYS_OF_WEEK cd $DIR && python3 $PYTHON_SCRIPT $OPTIONS_PING_IT $REDIRECT_LOGS"
CRONTAB_LINE_UP_DOWN="$MINUTES_UP_DOWN $HOURS_UP_DOWN $DAYS_OF_MONTH * $DAYS_OF_WEEK cd $DIR && python3 $PYTHON_SCRIPT $OPTIONS_UP_DOWN $REDIRECT_LOGS"
(crontab -l | grep -v -F $PYTHON_SCRIPT ; echo "$CRONTAB_LINE_PING" ; echo "$CRONTAB_LINE_UP_DOWN") | crontab -
echo "New crontab for '$Me' is"
crontab -l

# uncomment this line to get the cron output in your mailbox
#sudo apt-get install postfix
