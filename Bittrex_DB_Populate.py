# -*- coding: utf-8 -*-
import json
import requests
import time

# Make it work for Python 2+3 and with Unicode
import io
try:
    to_unicode = unicode
except NameError:
    to_unicode = str


# start by opening the DB and seeing if it was updated 2 hours ago or less
# Read JSON file
with open('/home/andrew/enviroments/CryptoDB.json') as data_file:
    data_loaded = json.load(data_file)

previoustime=data_loaded["time"]
currenttime=time.time()

#load the current quotes for currencies
BTCurl="https://bittrex.com/api/v1.1/public/getmarketsummary?market=USDT-BTC"
response = requests.get(BTCurl)
data = response.json()
tradetemp = data["result"][0]
BTCVal=tradetemp["Last"]
   
ETHurl="https://bittrex.com/api/v1.1/public/getmarketsummary?market=USDT-ETH"
response = requests.get(ETHurl)
data = response.json()
tradetemp = data["result"][0]
ETHVal=tradetemp["Last"]

OMGurl="https://bittrex.com/api/v1.1/public/getmarketsummary?market=USDT-OMG"
response = requests.get(OMGurl)
data = response.json()
tradetemp = data["result"][0]
OMGVal=tradetemp["Last"]

LTCurl="https://bittrex.com/api/v1.1/public/getmarketsummary?market=USDT-LTC"
response = requests.get(LTCurl)
data = response.json()
tradetemp = data["result"][0]
LTCVal=tradetemp["Last"]

#If the data is over 2 hours old, create a new database to start over
#This prevents errant high standard deviation readings from old data
if (currenttime-previoustime>7200):
   
   #define reset val   
   BTCPricelist=[]
   ETHPricelist=[]
   OMGPricelist=[]
   LTCPricelist=[]
   #The list is re-initialized with 72 entries of the last trade
   for x in range(0,72):
      BTCPricelist.append(BTCVal)
      ETHPricelist.append(ETHVal)
      OMGPricelist.append(OMGVal)
      LTCPricelist.append(LTCVal)
   
   # Define data for output
   data = {"time": currenttime,
           "BTC": BTCPricelist,
           "OMG": OMGPricelist,
           "LTC": LTCPricelist,
           "ETH": ETHPricelist }

#If the last data point is recent, delete the last entry (oldest) and add the new quote
#This also keeps our list at 72 entries
else:
   data=data_loaded
   data["BTC"].pop()
   data["BTC"].insert(0,BTCVal)
   data["ETH"].pop()
   data["ETH"].insert(0,ETHVal)
   data["OMG"].pop()
   data["OMG"].insert(0,OMGVal)
   data["LTC"].pop()
   data["LTC"].insert(0,LTCVal)
   #update time entry
   data["time"]=currenttime


# Write JSON file
with io.open('/home/andrew/enviroments/CryptoDB.json', 'w', encoding='utf8') as outfile:
    str_ = json.dumps(data,
                      indent=4, sort_keys=True,
                      separators=(',', ': '), ensure_ascii=False)
    outfile.write(to_unicode(str_))
