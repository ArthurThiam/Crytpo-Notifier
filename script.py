import time
import os
from coinmarketcapapi import CoinMarketCapAPI, CoinMarketCapAPIError
import configparser

# Set initial parameters
running = True
notified = False
update_interval = 300

# Build notification
def notify(title, message):
    command = f'''notify-send "{title}" "{message}"'''
    os.system(command)

#Import alert levels
config = configparser.ConfigParser()
config.read("alerts.ini")
cardano_alert_lower = config.getfloat('Cardano','alert_lower')
cardano_alert_upper = config.getfloat('Cardano','alert_upper')
print('Using API key:', config.get('API','key'))

#iterate through listings (until 20) until ada is found
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

print('update interval [s]: ', update_interval)
print('Alerts:')
print('     Cardano upper:', cardano_alert_upper)
print('     Cardano lower:', cardano_alert_lower)
print('')
print('Monitoring markets...')


while running:
    price = pull_price("Cardano")
    if price > cardano_alert_upper:
        notify("Price Alert","Cardano is pumping! Last price: " + str(round(price, 4)))
    elif price < cardano_alert_lower:
        notify("Price Alert","Cardano is dumping! Last price: " + str(round(price,4)))
    time.sleep(update_interval)
