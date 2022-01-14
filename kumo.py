#!/usr/bin/env /usr/bin/python

# Forked from https://github.com/szumlins/Scripts on Jan 12, 2021
# Adapted to Python 3 and revised by Michael Gillett

# This script is a simple tool to automate getting and setting of KUMO cross points via python
# Requires installation of Requests module, can be installed with 'pip install requests'

import requests
import json
import sys


def error(code):
	if code == 1:
		sys.exit("\nERROR: Can't connect to KUMO (check your URL or network)\n")
	elif code == 2:
		sys.exit('\nERROR: destination out of range (not enough destinations in router)\n')
	elif code == 3:
		sys.exit('\nERROR: source is out of range (not enough sources in router)\n')
	elif code == 4:
		sys.exit('\nERROR: No destination defined, exiting.\n')


def get_kumo_io_count(address, command):
	try:
		r = requests.get(address + command)
		j = json.loads(r.text)
		return j['value']
	except requests.ConnectionError:
		error(1)


def kumo_config_main(address='', source=0, destination=0):
	# set our Kumo URL
	kumo = f'http://{address}/options'

	source_count = get_kumo_io_count(kumo, '?action=get&paramid=eParamID_NumberOfSources')
	destination_count = get_kumo_io_count(kumo, '?action=get&paramid=eParamID_NumberOfDestinations')

	print(f'\nConnected to Kumo Router: {address}')

	# if there isn't a source set on the cli, simply look up the source of the supplied destination
	if not source:
		# if destination is larger than router size, exit with error
		if destination > int(destination_count):
			# destination out of range
			error(2)

		# try getting source for defined destination
		r = requests.get(
			kumo + '?action=get&paramid=eParamID_XPT_Destination' + str(destination) + '_Status',
			timeout=0.2)

		j = json.loads(r.text)
		# if we get an error, print it, other wise print out source
		if j['value'] == '-1':
			# destination out of range
			error(2)
		else:
			print(f"\nAJA CURRENT CONFIG:\nSource: {j['value']} > Destination: {destination}\n")

	else:
		# if source is larger than router size, exit with error
		if source > int(source_count):
			# source is out of range
			error(3)

		# there is a source defined, so switch it
		post_data = {
			'paramName': 'eParamID_XPT_Destination' + str(destination) + '_Status',
			'newValue': str(source)
		}

		r = requests.post(kumo, data=post_data, timeout=0.2)
		j = json.loads(r.text)

		# if we have an error, just return -2, if not return source, destination
		if j['value'] == '-1':
			# Destination out of range
			error(2)
		else:
			print(f"\nAJA REMAP CONFIRMATION:\nSource: {j['value']} mapped to destination {str(destination)}\n")


