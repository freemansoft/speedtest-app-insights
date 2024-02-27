# SPDX-FileCopyrightText: 2022 Joe Freeman joe@freemansoft.com
#
# SPDX-License-Identifier: MIT
#
# Installer script for windows, people who don't do bash

# Install components for speedtest
# This will route you to the store to install python if it is not installed
python3 --version
python3 -m pip install -r requirements.txt

# should add the setup for dns testing - see 0-setup.sh
