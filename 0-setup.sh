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
echo "Configuring python"
# make python3 by the default and install speedtest library
sudo update-alternatives --install /usr/bin/python python /usr/bin/python2 2
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3 3
sudo apt install python3-pip

# TODO put this in requirements.txt!
echo "Installing speedtest python sdk - probably CLI apps in ~/.local/bin"
# https://linuxconfig.org/how-to-run-a-speed-test-from-command-line-using-speedtest-cli#h6-using-the-csv-or-json-formats-for-the-results
pip3 install speedtest-cli
# CLI api changed requiring an update. Uncomment if v2.1.3 or later not available.  
#sudo wget https://raw.githubusercontent.com/sivel/speedtest-cli/v2.1.3/speedtest.py -O ~/.local/lib/python3.7/site-packages/speedtest.py 

# echo "Installing dnspython for future work"
# pip3 install dnspython
# pip3 install cymruwhois
# cheating and installing dnsdiag which I know will install compatible dnspython and cymrwhois
# need 2.0.1 or later - so git clone and install instead of relying on distribution
echo "Installing DNS diag for future work - propbably in ~/.local/bin"
# pip3 install dnsdiag
# could test with dnseval --json - www.apple.com

# have to do this if on ARM / like Raspberry Pi - so just do it for all to get the latest
git clone https://github.com/farrokhi/dnsdiag.git
cd dnsdiag
pip3 install -r requirements.txt .
cd ..
rm -rf dnsdiag

echo "Installing Azure Application Insights tooling"
python3 -m pip install opencensus-ext-azure

echo "Done"
