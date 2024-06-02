import os
import requests
import googlemaps

from gistools.utils import read_json

__all__ = ['set_credentials', 'get_api_key']

def get_api_key(keyfile=None):
	if keyfile is None:
		keyfile = os.getenv('GISTOOLS_GMAPS_KEY_FILE')
		
	return read_json(keyfile).get('api_key', None)

def set_credentials(keyfile=None, queries_per_minute=3000, queries_per_second=None, retry_over_query_limit=True):
	if  keyfile is None:
		keyfile  = os.getenv('GISTOOLS_GMAPS_KEY_FILE')

	return googlemaps.Client(
		key=read_json(keyfile).get('api_key', None),
		queries_per_minute=queries_per_minute,
		queries_per_second=queries_per_second,
		retry_over_query_limit=retry_over_query_limit
	)

def get_place_info(address, api_key):
	# Base URL
	base_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"

	# Parameters in a dictionary
	params = {
		"input": address,
		"inputtype": "textquery",
		"fields": "formatted_address,name,business_status,place_id",
		"key": api_key,
	}

	# Send request and capture response
	response = requests.get(base_url, params=params)
	# Check if the request was successful
	if response.status_code == 200:
		return response.json()
	else:
		return None

#EOF