import json
import requests
from math import floor, log10

# Make it work for Python 2+3 and with Unicode
import io
try:
    to_unicode = unicode
except NameError:
    to_unicode = str


#define currency varibles for bittrex
btc="USDT-BTC"
eth="USDT-ETH"
omg="USDT-OMG"
currencies=[btc, eth, omg]
names=["BTC", "ETH", "OMG" ]
statvals_dict={}



   # Thresholds gives us an event trigger
   # The normal swings of the currencies are $300 for BTC, $20 for ETH, and $0.50 for OMG 
   # Below we use a linear approximation of what these triggers should be
   # If you compare these values to the current prices for the currencies you get the following swings:
   # 4.5% for BTC, 6% for ETH, and 8.4% for OMG
#thresholds=[4.5, 6, 8.4]

#Run this loop 3 times, once for each currency
for x in range(0,3):

   #get the currency and get the data from bittrex
   currency=currencies[x]
   url="https://bittrex.com/api/v1.1/public/getmarketsummary?market="+currency
   response = requests.get(url)
   data = response.json()
   trades= data["result"][0]
   lastvalue=trades["Last"]
   lowvalue=trades["Low"]
   highvalue=trades["High"]

   # We're going to grab the data from the current trade database
   # This database is created by Bittrex_DB_Populate.py
   with open('/XXXXXX/PATH_TO_FILE/CryptoDB.json') as data_file:    
      DBdata = json.load(data_file)

   #grab the 3 letter name which is the dictionary entry for the currency data
   directory=names[x]

   #reset three varibles
   summation=0
   variancesum=0
   sigxy_sum=0

   #pull data from database and set up a loop
   TradeVals=DBdata[directory]
   length=len(TradeVals)
   
   # The first loop sums all previous last trades in the database and gets a value that we need for simple linear regression
   for mean_int in range(length):
      summation=summation+TradeVals[mean_int]

      #for simple linear regression we need to calculate the sum of x*y where x is just the integer location of the value in the list.
      #sigxy_sum is part of calculating the sample covariance
      #We reverse "x" value because array goes from last (latest quote) to first
      sigxy_sum=sigxy_sum+(72-mean_int)*TradeVals[mean_int]

   # Grab the mean trade value by dividing the sum by the amount of entries
   mean=summation/length

   # Bravo is the slope parameter of the simple linear regression model
   # Bravo is the sample covariance divided by the sample variance
   # There is no need to calcuate the estimator so we won't do that
   Bravo=(sigxy_sum-2628*summation/72)/(127020-(2628**2)/72)

   #process another loop to calcuate the sum of variances
   for variance_int in range(length):
      variancesum=variancesum+(TradeVals[variance_int]-mean)**2

   #calculate the variance by dividing the sum by the amount of entries
   variance=variancesum/(length)

   # calculate standard deviation 
   standev = variance ** 0.5


   #If the data fits a normal distribution, 95% of the trades should be 2 Standard Deviations from the mean
   # As such, on a normal day 4 SD should be near equivalent to the "threshold" list
   variability=4*standev

   #calculate the order of magnitude of the last trade
   magnitude=log10(lastvalue)

   # Threshold gives us an event trigger
   # The normal swings of the currencies are $300 for BTC, $20 for ETH, and $0.50 for OMG 
   # If you compare these values to the current prices for the currencies you get the following swings:
   # 4.5% for BTC, 6% for ETH, and 8.4% for OMG
   # These values can be linerized as 8.6% - 1.3% * Magnitude of currency
   # e.g. 8.6% - 1.3% * 3 (BTC) = 4.5%
   # See the beginning of the file is you want hard coded values instead of the formula
   threshold_percent=8.4-1.3*(magnitude)
   threshold=(threshold_percent/100)*lastvalue

   #We are going to 
   if (Bravo > ((threshold/2)/72)):
	   trend_str='positive'	
   elif (Bravo < -((threshold/2)/72)):
	   trend_str='negative'	
   else:
	   trend_str='flat'

   #cleaning up text print later
   stdev_str=str(standev)
   vartexttemp = str(variability)
   lastvaluetemp = str(lastvalue)
   highvaluetemp = str(highvalue)
   lowvaluetemp = str(lowvalue)
   thresholdtemp = str(threshold)
   meantemp=str(mean)
   trunc_val=magnitude+4
   lastvalue_str=lastvaluetemp[:trunc_val]
   highvalue_str=highvaluetemp[:trunc_val]
   lowvalue_str=lowvaluetemp[:trunc_val]
   threshold_str=thresholdtemp[:trunc_val]
   mean_str=meantemp[:trunc_val]
   vartext=vartexttemp[:trunc_val]

   

# send the data to slack

# this statement can be used if you want to use the threshold list. Be default we will use the equation
#   if (variability > thresholds[x]):
   if (variability > 1.5*threshold):


   


      headers = {'Content-type': 'application/json'}
      payload = '{"text":"ALERT: ' + names[x] + ' movement of: $' + vartext + ' in the last 24hrs. The normal movement is: $' + threshold_str +'\n \nLast trade: $' + lastvalue_str + ' \nThe current trend is: ' + trend_str + '\n \n24hr High: $' +highvalue_str +'\n24hr Low: $' + lowvalue_str + '\n24hr Average: $' + mean_str +' \n ------------" }'

#Transmit webhook to SLACK
      r = requests.post('SLACK_WEBHOOKADDRESS', data=payload, headers=headers)

   tname=names[x]+"_stdev"
   statvals_dict.update({tname:standev})
   tname=names[x]+"_mean"
   statvals_dict.update({tname:mean})


# Write JSON file
with io.open('/XXXXXXX/PATH_TO_FILE/CryptoStats.json', 'w', encoding='utf8') as outfile:
    str_ = json.dumps(statvals_dict,
                      indent=4, sort_keys=True,
                      separators=(',', ': '), ensure_ascii=False)
    outfile.write(to_unicode(str_))

