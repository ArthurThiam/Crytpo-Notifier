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

# Detect OS and build notification (WINDOWS + MAC OS TO BE ADDED)
def notify(title, message):
    command = f'''notify-send "{title}" "{message}"'''
    os.system(command)

# Print an overview of settings used by Crypto Alert
def print_overview():  
    print('SETTINGS OVERVIEW:')
    print('update interval [s]: ', update_interval)
    print('API key: ', api_key)
    print('')
    print('ALERTS OVERVIEW')
    #print('     Cardano upper:', cardano_alert_upper)
    #print('     Cardano lower:', cardano_alert_lower)
    print('')
    print('Monitoring markets...')

# Import alert levels from settings.ini
def import_settings():
    asset_list = config.getlist ('Assets', 'asset_list')
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

# Pull price of all tracked assets using API key #TODO: adapt function to keep checking until all tracked assets are found
def pull_price_list(settings):
    api_iterator = 0    # iterates through the data pulled with API key. Resets every time an asset is found.
    asset_iterator = 0  # iterates through the list of tracked assets. Never resets.
    found = False
    asset_id = 1
    asset_list = settings[1]
    price_list = []
    
    #Get data and find requested asset
    r = CoinMarketCapAPI(api_key).cryptocurrency_listings_latest()
    while not found and api_iterator < 100:
        
        # if tracked asset is found, add its price to the price list.
        print(asset_list[asset_iterator])
        print(r.data[api_iterator]["name"])
        #time.sleep(0.5)
        if r.data[api_iterator]["name"] == asset_list[asset_iterator]: 
            
            price_list.append(r.data[api_iterator]["quote"]["USD"]["price"])
            asset_iterator += 1 # move on to next tracked asset
            print('asset found:')
            
            # if this was not the last tracked asset, reset API data iterator
            if asset_iterator < len(asset_list):
                api_iterator = -1
            
            # if this was the last asset, set found to true
            elif asset_iterator == len(asset_list):
                found = True
                print('finished search')
        
        api_iterator += 1
                
    return price_list

# Determine what alerts need to be sent
def update(alerts_dictionary):    
    return 0    


# ====================================== MAIN ================================================

print_overview()
settings = import_settings()
pull_price_list(settings)


while running:
    price = pull_price("Cardano")
    if price > cardano_alert_upper:
        notify("Price Alert","Cardano is pumping! Last price: " + str(round(price,4)))
    elif price < cardano_alert_lower:
        notify("Price Alert","Cardano is dumping! Last price: " + str(round(price,4)))
    time.sleep(update_interval)
