# Install components for speedtest 
# This will route you to the store to install python if it is not installed
python3 --version

# all that is required for the core part
python3 -m pip install speedtest-cli
python3 -m pip install opencensus-ext-azure

# should add the setup for dns testing - see 0-setup.sh
