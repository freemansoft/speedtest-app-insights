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
OPTIONS=""
# CRON fields - */3 --> every 3 minutes
MINUTES="*/3"
HOURS="*"
DAYS_OF_MONTH="*"
DAYS_OF_WEEK="*"
# Use this if you want to see the logs in this folder - easier for torubleshooting
# REDIRECT_LOGS=">> $DIR/cron.log 2>&1"
REDIRECT_LOGS=""
CRONTAB_LINE="$MINUTES $HOURS $DAYS_OF_MONTH * $DAYS_OF_WEEK cd $DIR && python3 $PYTHON_SCRIPT $OPTONS $REDIRECT_LOGS"

# must quote CRONTAB_LINE so it does expand asterisk
(crontab -l | grep -v -F $PYTHON_SCRIPT ; echo "$CRONTAB_LINE") | crontab -