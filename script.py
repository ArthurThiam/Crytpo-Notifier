import time
import os
from coinmarketcapapi import CoinMarketCapAPI, CoinMarketCapAPIError
import configparser

# Set initial parameters
running = True
notified = False
config = configparser.ConfigParser(converters={'list': lambda x: [i.strip() for i in x.split(',')]})
config.read("settings.ini")
update_interval = config.getint('General', 'update_interval')
api_key = config.get('General', 'key')
asset_list = config.getlist ('Assets', 'asset_list')

# Detect OS and build notification (WINDOWS + MAC OS TO BE ADDED)
def notify(title, message):
    command = f'''notify-send "{title}" "{message}" --urgency=critical'''
    os.system(command)

# Print an overview of settings used by Crypto Alert
def print_overview(asset_list, alerts_dictionary):  
    print('SETTINGS OVERVIEW:')
    print('update interval [s]: ', update_interval)
    print('API key: ', api_key)
    print('--------------------------------------')
    print('')
    print('ALERTS OVERVIEW')
    for asset in asset_list:
        print(asset, ': ', alerts_dictionary[asset][0], '/', alerts_dictionary[asset][1])

    print('')
    print('--------------------------------------')
    print('Monitoring markets...')

# Import alert levels from settings.ini
def import_settings():    
    alerts_dictionary = {}
    iterator = 0

    for asset in asset_list:    
        # Convert alerts from string to float (.ini file list call passes a string)
        input_alerts = config.getlist(asset, 'alerts')
        for i in range(len(input_alerts)):
            input_alerts[i] = float(input_alerts[i])   
        
        # Add alerts list of asset to dictionary
        alerts_dictionary[asset_list[iterator]] = input_alerts
        
        iterator += 1
    
    return (alerts_dictionary, asset_list)

# Pull price of all tracked assets using API key
def pull_price_list(settings, asset_list):
    api_iterator = 0    # iterates through the data pulled with API key. Resets every time an asset is found.
    asset_iterator = 0  # iterates through the list of tracked assets. Never resets.
    found = False
    asset_id = 1
    asset_list = settings[1]
    price_list = {}
    
    #Get data and find requested asset
    r = CoinMarketCapAPI(api_key).cryptocurrency_listings_latest()
    while not found and api_iterator < 100:
        
        # if tracked asset is found, add its price to the price list.
        #time.sleep(0.5)
        if r.data[api_iterator]["name"] == asset_list[asset_iterator]: 
            
            #price_list.append(r.data[api_iterator]["quote"]["USD"]["price"])            
            price_list[asset_list[asset_iterator]] = r.data[api_iterator]["quote"]["USD"]["price"]
            asset_iterator += 1 # move on to next tracked asset
            
            # if this was not the last tracked asset, reset API data iterator
            if asset_iterator < len(asset_list):
                api_iterator = -1
            
            # if this was the last asset, set found to true
            elif asset_iterator == len(asset_list):
                found = True
        
        api_iterator += 1                
    return price_list

# Determine what alerts need to be sent. currently only supports one lower and one upper boundary.
def update(alerts_dictionary, price_list, asset_list):
    
    for asset in asset_list:
        if price_list[asset] < alerts_dictionary[asset][0]:
            notify("Price Alert", str(asset) + ' is dumping! Last price: ' + str(round(price_list[asset],4)))
        
        elif price_list[asset] > alerts_dictionary[asset][1]:
            notify("Price Alert", str(asset) + ' is pumping! Last price: ' + str(round(price_list[asset],4)))
            
    return 0    


# ====================================== MAIN ================================================

settings = import_settings()
print_overview(asset_list, settings[0])

while running:
    # prepare inputs for update alert check
    alerts_dictionary = settings[0]
    price_list = pull_price_list(settings, asset_list)

    # perform update
    update(alerts_dictionary, price_list, asset_list)
    
    # wait
    time.sleep(update_interval)


