#!/bin/bash
# SPDX-FileCopyrightText: 2022 Joe Freeman joe@freemansoft.com
#
# SPDX-License-Identifier: MIT
#
# installs NetCheck.py in cron from this working directory and runs it every 10 minutes
# ASSUMES you have NO spaces in path to this directory
#
# You can run this script as many times as you wish. It will UPDATE any previous entry.

# Run from the root directory to pick up the config files
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
#echo $DIR
Me=`whoami`

# Can add NetCheck.py options to OPTIONS: --verbose or --download or --upload
PYTHON_SCRIPT="src/NetCheck.py"

OPTIONS_PING_IT=""
OPTIONS_UP_DOWN="--upload --download"

# ping test every 3 minutes
MINUTES_PING_IT="*/3"
HOURS_PING_IT="*"

# ping test every 3 minutes
MINUTES_DNS_IT="*/6"
HOURS_DNS_IT="*"

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

# this really isn't ready for primetime
DNS_SCRIPT="DnsCheck.py"
CRONTAB_LINE_DNS="$MINUTES_DNS_IT $HOURS_DNS_IT $DAYS_OF_MONTH * $DAYS_OF_WEEK cd $DIR && python3 $DNS_SCRIPT $REDIRECT_LOGS"
(crontab -l | grep -v -F $DNS_SCRIPT ; echo "$CRONTAB_LINE_DNS" ) | crontab -
echo "New crontab for '$Me' is"
crontab -l