#!/bin/bash
# SPDX-FileCopyrightText: 2022 Joe Freeman joe@freemansoft.com
#
# SPDX-License-Identifier: MIT
#
# installs NetCheck.py in cron from this working directory and runs it every 10 minutes
# ASSUMES you have NO spaces in path to this directory
#
# You can run this script as many times as you wish. It will UPDATE any previous entry.

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
#echo $DIR
Me=`whoami`

# Can add NetCheck.py options to OPTIONS: --verbose or --download or --upload
PYTHON_SCRIPT="NetCheck.py"

echo "Removing crontab entries for $PYTHON_SCRIPT"
(crontab -l | grep -v -F $PYTHON_SCRIPT) | crontab -

# Can add NetCheck.py options to OPTIONS: --verbose or --download or --upload
PYTHON_SCRIPT="DnsCheck.py"

echo "Removing crontab entries for $PYTHON_SCRIPT"
(crontab -l | grep -v -F $PYTHON_SCRIPT) | crontab -

echo "New crontab for '$Me' is:"
crontab -l