#!/usr/bin/env python

import requests
import sys
import argparse

# Argument Parsing
parser = argparse.ArgumentParser(description="Query a nodejs-pool mining pool API to get current mining hashrate for a given account.  Default is total hasrate for the user.  May also specify a worker name to query only for the hashrate of that worker.")
parser.add_argument("-w", metavar="HASHRATE", type=int, dest="warnThresh", help="Warning threshold", required=True)
parser.add_argument("-c", metavar="HASHRATE", type=int, dest="critThresh", help="Critical threshold", required=True)
parser.add_argument("-u", metavar="URL", dest="url", help="URL to pool's API (include port)", required=True)
parser.add_argument("-a", metavar="ADDRESS", dest="payAddress", help="Payment address to query on", required=True)
parser.add_argument("--worker", metavar="WORKERNAME", dest="workerName", help="Query the hashrate for a single worker named WORKERNAME", default=None)



args = parser.parse_args()

# Verify parameters passed in

warnThresh = args.warnThresh
critThresh = args.critThresh
url = args.url.rstrip("/")
payAddress = args.payAddress
workerName = args.workerName


if warnThresh < critThresh:
	print "Error: Warning threshold must be greater than critical threshold"
	sys.exit(3)


# Variables
exitCode=3
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}


url+="/miner/{}/stats".format(payAddress)

if workerName!=None:
	url+="/allWorkers"


# Get the data & parse it

response = requests.get(url=url)

if response.status_code == requests.codes.ok:
	apiData = response.json()
	
	# Extract the relevant hashrate data	
	# If a specific worker was specified, extract that data
	if workerName!=None:
		# Fire an error if the specified workername isn't in the JSON object from the server
		try:
			hashRate=apiData[workerName]["hash"]
		except KeyError:
			exitCode=3
			print "Error - Worker name not found"
			sys.exit(exitCode)
	# Otherwise just grab the global hashrate
	else:
		hashRate=apiData["hash"]

	
	# Evaluate the returned data to determine our monitor state & ouput
	if hashRate < critThresh:
		exitCode=2
		output="Critical - Hash rate: {} H/s".format(hashRate)
	elif hashRate < warnThresh:
		exitCode=1
		output="Warning - Hash rate: {} H/s".format(hashRate)
	else:
		exitCode=0
		output="OK - Hash rate: {} H/s".format(hashRate)

	output += " | Hashrate={};{};{};;".format(hashRate, warnThresh, critThresh)
	print output

else:
	exitCode=3
	print "HTTP Error: {}".format(response.status_code)

sys.exit(exitCode)
