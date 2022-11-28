# Run this one time to create the Application Insights API configuration file
#
if [ ! -f instance_config.ini ]; then
    echo "copy instance_config.ini.template to instance_config.ini and set values and then re-run"
    exit -1
fi
source ./instance_config.ini

# install jq  we need it
if ! command -v jq &> /dev/null
then
    echo "installing jq with snap"
    if ! sudo snap install jq ; then
        sudo apt install -y jq
    fi
else
    echo "jq already installed"
fi
# install az command line
az extension add --name application-insights

#az login

previous_key=$(az monitor app-insights api-key show --api-key $apiKeyName --app $insightsInstanceName --resource-group $insightsResourceGroup)
#echo "Existing key: " $previous_key
api_name=$(jq -r ".name" <<< "$previous_key")

if [[ $api_name == "$apiKeyName" ]]; then
    echo "API key already exists and the api provides no way of recovering it"
else
    echo "Creating API key"
    # this will fail if already exists
    create_result=$( az monitor app-insights api-key create --api-key $apiKeyName --app $insightsInstanceName --resource-group $insightsResourceGroup)
    #echo "Creating AP results: " $create_result
    apiKey=$(jq -r ".apiKey" <<< "$create_result")
    echo "Created api key and saved to api_config.ini : $apiKey"
    echo "apiKey=$apiKey" > api_config.ini

    # https://learn.microsoft.com/en-us/azure/azure-monitor/logs/api/authentication-authorization#authenticating-with-an-api-key
    echo ""
    echo "Azure Monitor Authentication"
    echo "    Custom header: provide the API key in the custom header X-Api-Key"
    echo "    Query parameter: provide the API key in the URL parameter apiKey"

    app_query_result=$(az monitor app-insights component show --app $insightsInstanceName --resource-group $insightsResourceGroup)
    appId=$(jq -r ".appId" <<< "$app_query_result")
    echo "Azure Monitor App Id: $appId"
    echo "appId=$appId" >> api_config.ini
fi

# Looks like this command does not return the actual API key - probably for security reasons
az monitor app-insights component show --app $insightsInstanceName --resource-group $insightsResourceGroup
