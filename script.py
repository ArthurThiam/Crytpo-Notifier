import time
import os
from coinmarketcapapi import CoinMarketCapAPI, CoinMarketCapAPIError
import configparser

# Set initial parameters
running = True
notified = False
update_interval = 300

# Detect OS and build notification (WINDOWS + MAC OS TO BE ADDED)
def notify(title, message):
    command = f'''notify-send "{title}" "{message}"'''
    os.system(command)

# Import alert levels from settings.ini
def import_settings():
    config = configparser.ConfigParser(converters={'list': lambda x: [i.strip() for i in x.split(',')]})
    config.read("settings.ini")
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
    
    return alerts_dictionary

# Pull price of a given asset using API key
def pull_price(asset):
    iterator = 0
    found = False
    asset_id = 1
    
    #Get data and find requested asset
    r = CoinMarketCapAPI(config.get('API','key')).cryptocurrency_listings_latest()
    while not found and iterator < 20:
        if r.data[iterator]["name"] == asset:
            found = True
            asset_id = iterator
        iterator += 1
    return r.data[asset_id]["quote"]["USD"]["price"]

#take an input asset and price, determine if an update should be sent
def update(condition):
    return 0
    

print('update interval [s]: ', update_interval)
print('Alerts:')
print('     Cardano upper:', cardano_alert_upper)
print('     Cardano lower:', cardano_alert_lower)
print('')
print('Monitoring markets...')


while running:
    price = pull_price("Cardano")
    if price > cardano_alert_upper:
        notify("Price Alert","Cardano is pumping! Last price: " + str(round(price,4)))
    elif price < cardano_alert_lower:
        notify("Price Alert","Cardano is dumping! Last price: " + str(round(price,4)))
    time.sleep(update_interval)
