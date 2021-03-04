#!/bin/bash
# Install the speedtest cli from https://www.speedtest.net/apps/cli
# See README.md

# This section is needed if you wish to register results
# Other non-official binaries will conflict with Speedtest CLI
# Run the CLI the first time to accept license conditions
if [ x = y ] ; then
    echo "Installing speedtest tooling - probably in /usr/local/bin"
    sudo apt-get -y install gnupg1 apt-transport-https dirmngr
    export INSTALL_KEY=379CE192D401AB61
    sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys $INSTALL_KEY
    echo "deb https://ookla.bintray.com/debian generic main" | sudo tee  /etc/apt/sources.list.d/speedtest.list
    sudo apt-get -y update
    sudo apt-get -y install speedtest
    speedtest
fi

# This is all that was needed to test on windows so it may be all we actually need
echo "Installing speedtest python sdk - probably CLI apps in ~/.local/bin"
# make python3 by the default and install speedtest library
sudo update-alternatives --install /usr/bin/python python /usr/bin/python2 2
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 3
pip3 install speedtest-cli

echo "Installing Azure Application Insights tooling"
python3 -m pip install opencensus-ext-azure

echo "Done"