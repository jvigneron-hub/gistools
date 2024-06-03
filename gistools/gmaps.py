"""
This module provides functions for interacting with the Google Maps API.  
It handles authentication, setting API limits, and making API calls for retrieving place information:

* `get_api_key`: Retrieves the Google Maps API key from the specified file or environment variable.
* `set_credentials`: Sets up the Google Maps API client with the specified credentials and limits.
* `get_place_info`: Retrieves information about a place based on a given address.

**Notes:**
* This module depends on the [googlemaps](https://github.com/googlemaps/google-maps-services-python) and [requests](https://requests.readthedocs.io/en/latest/) Python packages.  
* Ensure they are installed before using this module.  
* Remember to [protect your Google Maps API key](https://developers.google.com/maps/api-security-best-practices) and avoid sharing it publicly.  
* Be aware of the [Google Maps API usage limits and billing](https://developers.google.com/maps/billing-and-pricing/billing).  

The get_place_info() function currently retrieves only basic place information. 
You can modify it to retrieve more fields by adding them to the fields parameter in the request.
"""
import os
import requests
import googlemaps

from gistools.utils import read_json

__all__ = ['set_credentials', 'get_api_key', 'get_place_info']

def get_api_key(keyfile=None):
	"""
	Retrieves the Google Maps API key from the specified file or environment variable.

	Args:
	- **keyfile (str, optional)**: The path to a JSON file containing the API key.  
	If not provided, the environment variable `GISTOOLS_GMAPS_KEY_FILE` will be used.
	Defaults to None.

	Returns:
	- **str**: The Google Maps API key as a string, or None if the key is not found.
	"""
	if keyfile is None:
		keyfile = os.getenv('GISTOOLS_GMAPS_KEY_FILE')
		
	return read_json(keyfile).get('api_key', None)

def set_credentials(keyfile=None, queries_per_minute=3000, queries_per_second=None, retry_over_query_limit=True):
	"""
	Sets up the Google Maps API client with the specified credentials and limits.

	Args:
	- **keyfile (str, optional)**: The path to a JSON file containing the API key.  
	If not provided, the environment variable `GISTOOLS_GMAPS_KEY_FILE` will be used.
	Defaults to None.
	- **queries_per_minute (int, optional)**: The maximum number of queries allowed per minute.  
	Defaults to 3000.
	- **queries_per_second (int, optional)**: The maximum number of queries allowed per second.  
	Defaults to None, which means the limit is not set.
	- **retry_over_query_limit (bool, optional)**: If True, the client will automatically retry requests that exceed the query limit.  
	Defaults to True.

	Returns:
	- **googlemaps.Client**: A `googlemaps.Client` object, ready to be used for making API calls.
	"""
	if  keyfile is None:
		keyfile  = os.getenv('GISTOOLS_GMAPS_KEY_FILE')

	return googlemaps.Client(
		key=read_json(keyfile).get('api_key', None),
		queries_per_minute=queries_per_minute,
		queries_per_second=queries_per_second,
		retry_over_query_limit=retry_over_query_limit
	)

def get_place_info(address, api_key):
	"""
	Retrieves information about a place based on a given address using the Google Maps Places API.

	Args:
	- **address (str)**: The address to search for.
	- **api_key (str)**: The Google Maps API key.

	Returns:
	- **dict**: A dictionary containing the place information if the request was successful, or None if there was an error.
	"""
	base_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
	""" Base URL """

	params = {
		"input": address,
		"inputtype": "textquery",
		"fields": "formatted_address,name,business_status,place_id",
		"key": api_key,
	}
	""" Parameters in a dictionary """

	response = requests.get(base_url, params=params) # Send request and capture response
	if response.status_code == 200: # Check if the request was successful
		return response.json()
	else:
		return None

#EOF