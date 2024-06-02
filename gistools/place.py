import inspect

from gistools.utils     import is_numeric, merge_dicts
from gistools.geometry  import Point
from gistools.plus_code import encode
from gistools.strings   import normalize, similarity, clean
from gistools.gmaps     import set_credentials

'''
geocode("Grevin").describe()
geocode("+33147708505").describe()
autocomplete("Musee Grevin").describe()
text_search("Musee Grevin").describe()
find_place(input_text='Musee Grevin', location=(48.871162, 2.344007), radius=0).describe()
(input_text='23 bd Poissonière Paris', radius=100, keyword='musée')
place_details('ChIJVUrgmz5u5kcRWPSN-T8a730').describe()
'''

__all__ = ['BUSINESS_TYPES', 'Place', 'geocode', 'autocomplete', 'text_search', 'find_place', 'radar', 'place_details']

THRESHOLD_ON_NAME = 0.0
THRESHOLD_ON_CITY = 0.9
THRESHOLD_ON_POSTAL_CODE = 1
THRESHOLD_ON_ADDR = 0.0
THRESHOLD = 0.85

BUSINESS_TYPES = [
    'accounting',
    'airport',
    'amusement_park',
    'aquarium',
    'art_gallery',
    'atm',
    'bakery',
    'bank',
    'bar',
    'beauty_salon',
    'bicycle_store',
    'book_store',
    'bowling_alley',
    'bus_station',
    'cafe',
    'campground',
    'car_dealer',
    'car_rental',
    'car_repair',
    'car_wash',
    'casino',
    'cemetery',
    'church',
    'city_hall',
    'clothing_store',
    'convenience_store',
    'courthouse',
    'dentist',
    'department_store',
    'doctor',
    'drugstore',
    'electrician',
    'electronics_store',
    'embassy',
    'fire_station',
    'florist',
    'funeral_home',
    'furniture_store',
    'gas_station',
    'gym',
    'hair_care',
    'hardware_store',
    'hindu_temple',
    'home_goods_store',
    'hospital',
    'insurance_agency',
    'jewelry_store',
    'laundry',
    'lawyer',
    'library',
    'light_rail_station',
    'liquor_store',
    'local_government_office',
    'locksmith',
    'lodging',
    'meal_delivery',
    'meal_takeaway',
    'mosque',
    'movie_rental',
    'movie_theater',
    'moving_company',
    'museum',
    'night_club',
    'painter',
    'park',
    'parking',
    'pet_store',
    'pharmacy',
    'physiotherapist',
    'plumber',
    'police',
    'post_office',
    'primary_school',
    'real_estate_agency',
    'restaurant',
    'roofing_contractor',
    'rv_park',
    'school',
    'secondary_school',
    'shoe_store',
    'shopping_mall',
    'spa',
    'stadium',
    'storage',
    'store',
    'subway_station',
    'supermarket',
    'synagogue',
    'taxi_stand',
    'tourist_attraction',
    'train_station',
    'transit_station',
    'travel_agency',
    'university',
    'veterinary_care',
    'zoo',
    'establishment',
    'finance',
    'general_contractor',
    'food',
    'health',
	'place_of_worship',
	'grocery_or_supermarket',
	'colloquial_area'
]

def refine_address(record):
	s1 = record['formatted_address']

	s2 = str(record['postal_code']) + ' ' + record['city'] + ', ' + record['country']
	s2 = s2.strip()

	s3 = s1.replace(s2,'').strip()
	s3 = s3.replace(',', '')

	return s3

class Place(Point):
	def __init__(self, address=None, components={'country': 'france'}, language='fr', code_length=10, isbusiness=False):
		Point.__init__(self, address, code_length=code_length)

		if isinstance(address, str):
			self._data['input_text'] = address
			
		self._components = components
		self._language   = language
		self._isbusiness = isbusiness

		self.set_thresholds(
			threshold_on_name = THRESHOLD_ON_NAME,
			threshold_on_city = THRESHOLD_ON_CITY,
			threshold_on_postal_code = THRESHOLD_ON_POSTAL_CODE,
			threshold_on_addr = THRESHOLD_ON_ADDR,
			threshold = THRESHOLD
		)

		self._resp = {}
		
	def _init_record(self, query=None):
		return query
	
	@property
	def data(self):
		return self._data
	
	@data.setter
	def data(self, query):
		self._init_record(query)

	@property
	def language(self):
		return self._language

	@language.setter
	def language(self, value):
		self._language = value

	@property
	def components(self):
		return self._components

	@components.setter
	def components(self, value):
		self._components = value

	@property
	def response(self):
		return self._resp

	def set_thresholds(self, **kwargs):
		if isinstance(self._data, dict):
			for arg in kwargs:
				if arg in ['threshold_on_name', 'threshold_on_city', 'threshold_on_postal_code', 'threshold_on_addr', 'threshold']:
					self._data[arg] = kwargs.get(arg)

		return self

	@staticmethod
	def __gc_get_formatted_address(input_text, geocoding):
		best_ratio = 0.0
		best_k = -1
		formatted_address = None

		s1 = normalize(input_text)

		if len(geocoding) > 0:
			for k, gc in enumerate(geocoding):
				s2 = normalize(gc.get('formatted_address', ''))

				cf = similarity(s1, s2, lcs=True)
				if cf > best_ratio:
					best_ratio = cf
					best_k  = k

			formatted_address = geocoding[best_k].get('formatted_address') if best_k >= 0 else None

		return best_k, formatted_address, round(best_ratio, 2)
		
	@staticmethod
	def __gc_get_geometry(geocoding, index=0):
		lat = geocoding[index]['geometry']['location']['lat']
		lng = geocoding[index]['geometry']['location']['lng']

		return lat, lng

	@staticmethod
	def __gc_get_street_number(geocoding, index=0):
		street_number = ''
		nb_components = len(geocoding[index]['address_components'])

		for k in range(nb_components):
			if (geocoding[index]['address_components'][k]['types'][0] == 'street_number'):
				street_number = geocoding[index]['address_components'][k]['long_name']
				break

		return street_number

	@staticmethod
	def __gc_get_street(geocoding, index=0):
		street = ''
		nb_components = len(geocoding[index]['address_components'])
		
		for k in range(nb_components):
			if (geocoding[index]['address_components'][k]['types'][0] == 'route'):
				street = geocoding[index]['address_components'][k]['long_name']
				break

			if (geocoding[index]['address_components'][k]['types'][0] == 'colloquial_area'):
				street = geocoding[index]['address_components'][k]['long_name']
				break
				
		return street

	@staticmethod
	def __gc_get_city(geocoding, index=0):
		city = ''
		nb_components = len(geocoding[index]['address_components'])

		for k in range(nb_components):
			types = geocoding[index]['address_components'][k]['types']
			if ('locality' in types) or ('postal_town' in types):
				city = geocoding[index]['address_components'][k]['long_name']
				break

		return city

	@staticmethod
	def __gc_get_sub_locality(geocoding, index=0):
		sub_locality = ''
		nb_components = len(geocoding[index]['address_components'])

		for k in range(nb_components):
			types = geocoding[index]['address_components'][k]['types']
			if ('sublocality' in types):
				sub_locality = geocoding[index]['address_components'][k]['long_name']
				break

		return sub_locality

	@staticmethod
	def __gc_get_postal_code(geocoding, index=0):
		postal_code = ''
		nb_components = len(geocoding[index]['address_components'])

		for k in range(nb_components):
			if (geocoding[index]['address_components'][k]['types'][0] == 'postal_code'):
				postal_code = geocoding[index]['address_components'][k]['long_name']
				break

		return postal_code

	@staticmethod
	def __gc_get_admin_area_level_2(geocoding, index=0):
		admin_area_level_2 = ''
		nb_components = len(geocoding[index]['address_components'])

		for k in range(nb_components):
			if (geocoding[index]['address_components'][k]['types'][0] == 'administrative_area_level_2'):
				admin_area_level_2 = geocoding[index]['address_components'][k]['long_name']
				break

		return admin_area_level_2

	@staticmethod
	def __gc_get_admin_area_level_1(geocoding, index=0):
		admin_area_level_1 = ''
		nb_components = len(geocoding[index]['address_components'])

		for k in range(nb_components):
			if (geocoding[index]['address_components'][k]['types'][0] == 'administrative_area_level_1'):
				admin_area_level_1 = geocoding[index]['address_components'][k]['long_name']
				break

		return admin_area_level_1

	@staticmethod
	def __gc_get_country(geocoding, index=0):
		country = ''
		nb_components = len(geocoding[index]['address_components'])

		for k in range(nb_components):
			if (geocoding[index]['address_components'][k]['types'][0] == 'country'):
				country = geocoding[index]['address_components'][k]['long_name']
				break

		return country

	@staticmethod
	def __gc_get_country_code(geocoding, index=0):
		country_code = ''
		nb_components = len(geocoding[index]['address_components'])

		for k in range(nb_components):
			if (geocoding[index]['address_components'][k]['types'][0] == 'country'):
				country_code = geocoding[index]['address_components'][k]['short_name']
				break

		return country_code.lower()

	@staticmethod
	def __gc_get_location_type(geocoding, index=0):
		location_type = geocoding[index]['geometry']['location_type']

		if location_type is None:
			location_type = 'NOT_FOUND' 

		return location_type

	@staticmethod
	def __gc_get_place_id(geocoding, index=0):
		return geocoding[index]['place_id']

	@staticmethod
	def __gc_get_plus_code(geocoding, index=0):
		lat = geocoding[index]['geometry']['location']['lat']
		lng = geocoding[index]['geometry']['location']['lng']

		return encode(lat, lng)
	
	@staticmethod
	def __pl_get_formatted_address(place_details=None, input_text=None, places=None):
		best_ratio = 0.0
		best_k = -1
		formatted_address = None

		if place_details is not None:
			best_k = 0
			formatted_address = place_details['result']['formatted_address']

			if input_text is not None:
				best_ratio = similarity(
					normalize(input_text), 
					normalize(formatted_address), 
					lcs=True
				)

		elif len(places) > 0:
			for k, pl in enumerate(places):
				s1 = normalize(input_text)

				try:
					s2 = pl.get('formatted_address', '')
					if len(s2) == 0:
						s2 = pl.get('vicinity', '')

					s2 = normalize(s2)

				except:
					s2 = ''

				cf = similarity(s1, s2, lcs=True)
				if cf > best_ratio:
					best_ratio = cf
					best_k = k

			formatted_address = places[best_k].get('formatted_address') if best_k >= 0 else None

		return best_k, formatted_address, round(best_ratio, 2)

	@staticmethod
	def __pl_get_geometry(place_details):
		lat = place_details['result']['geometry']['location']['lat']
		lng = place_details['result']['geometry']['location']['lng']

		return lat, lng

	@staticmethod
	def __pl_get_street_number(place_details):
		street_number = ''

		nb_components = len(place_details['result']['address_components'])

		for k in range(nb_components):
			if (place_details['result']['address_components'][k]['types'][0] == 'street_number'):
				street_number = place_details['result']['address_components'][k]['long_name']
				break

		return street_number

	@staticmethod
	def __pl_get_street(place_details):
		street = ''
		nb_components = len(place_details['result']['address_components'])

		for k in range(nb_components):
			if (place_details['result']['address_components'][k]['types'][0] == 'route'):
				street = place_details['result']['address_components'][k]['long_name']
				break

		return street

	@staticmethod
	def __pl_get_city(place_details):
		city = ''
		nb_components = len(place_details['result']['address_components'])

		for k in range(nb_components):
			types = place_details['result']['address_components'][k]['types']
			if ('locality' in types) or ('postal_town' in types):
				city = place_details['result']['address_components'][k]['long_name']
				break

		return city

	@staticmethod
	def __pl_get_sub_locality(place_details):
		sub_locality = ''
		nb_components = len(place_details['result']['address_components'])

		for k in range(nb_components):
			types = place_details['result']['address_components'][k]['types']
			if 'sublocality' in types:
				sub_locality = place_details['result']['address_components'][k]['long_name']
				break

		return sub_locality

	@staticmethod
	def __pl_get_postal_code(place_details):
		postal_code = ''
		nb_components = len(place_details['result']['address_components'])

		for k in range(nb_components):
			if (place_details['result']['address_components'][k]['types'][0] == 'postal_code'):
				postal_code = place_details['result']['address_components'][k]['long_name']
				break

		return postal_code

	@staticmethod
	def __pl_get_admin_area_level_2(place_details):
		admin_area_level_2 = ''
		nb_components = len(place_details['result']['address_components'])

		for k in range(nb_components):
			if (place_details['result']['address_components'][k]['types'][0] == 'administrative_area_level_2'):
				admin_area_level_2 = place_details['result']['address_components'][k]['long_name']
				break

		return admin_area_level_2

	@staticmethod
	def __pl_get_admin_area_level_1(place_details):
		admin_area_level_1 = ''
		nb_components = len(place_details['result']['address_components'])

		for k in range(nb_components):
			if (place_details['result']['address_components'][k]['types'][0] == 'administrative_area_level_1'):
				admin_area_level_1 = place_details['result']['address_components'][k]['long_name']
				break

		return admin_area_level_1

	@staticmethod
	def __pl_get_country(place_details):
		country = ''
		nb_components = len(place_details['result']['address_components'])

		for k in range(nb_components):
			if (place_details['result']['address_components'][k]['types'][0] == 'country'):
				country = place_details['result']['address_components'][k]['long_name']
				break

		return country

	@staticmethod
	def __pl_get_country_code(place_details):
		country_code = ''
		nb_components = len(place_details['result']['address_components'])

		for k in range(nb_components):
			if (place_details['result']['address_components'][k]['types'][0] == 'country'):
				country_code = place_details['result']['address_components'][k]['short_name']
				break

		return country_code.lower()

	@staticmethod
	def __pl_get_location_type(place_details):
		return 'ROOFTOP'

	@staticmethod
	def __pl_get_place_id(place_details):

		return place_details['result']['place_id']

	@staticmethod
	def __pl_get_place_name(place_details):
		
		return place_details['result']['name']

	@staticmethod
	def __pl_get_place_type(place_details):

		return place_details['result']['types']

	@staticmethod
	def __pl_get_place_main_type(place_details):

		return place_details['result']['types'][0]

	@staticmethod
	def __pl_get_plus_code(place_details):
		lat = place_details['result']['geometry']['location']['lat']
		lng = place_details['result']['geometry']['location']['lng']

		return encode(lat, lng)

	@staticmethod
	def __pl_get_place_url(place_details):
		r = ''

		if 'establishment' in place_details['result']['types']:
			r = place_details['result'].get('url', '')

		return r
		
	@staticmethod
	def __pl_get_website(place_details):
		r = ''

		if 'establishment' in place_details['result']['types']:
			r = place_details['result'].get('website', '')

		return r
	
	@staticmethod
	def __pl_get_phone_number(place_details):
		r = ''

		if 'establishment' in place_details['result']['types']:
			r = place_details['result'].get('international_phone_number', '')

		return r
		
	@staticmethod
	def __pl_get_opening_hours(place_details):
		def to_timestr(s):
			return '{}:{}'.format(s[:2],s[-2:])

		labels = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

		r = {}

		if 'establishment' in place_details['result']['types']:
			try:
				for p in place_details['result']['opening_hours']['periods']:
					l = labels[int(p.get('open').get('day'))-1]
					tw = to_timestr(p.get('open').get('time')) + '-' + to_timestr(p.get('close').get('time'))
					r[l] = tw if not l in r.keys() else r[l] + '|' + tw
			except:
				pass

		for l in labels:
			if not l in r.keys():
				r[l] = None

		return r
	
	@staticmethod
	def __get_confidence_on_name(record, result):
		c = 0.0

		if record.get('name', None) is not None:
			if result.get('place_name', None) is not None:
				c = similarity(str(record.get('name')), str(result.get('place_name')), lcs=True)

		return round(c, 2)

	@staticmethod
	def __get_confidence_on_addr(record, result):
		c = 0.0

		if record.get('input_address', None) is not None:
			if result.get('address', None) is not None:
				c = similarity(record.get('input_address'), result.get('address'), lcs=False)

		return round(c, 2)

	@staticmethod
	def __get_confidence_on_city(record, result):
		c = 0.0

		if record.get('input_city', None) is not None:
			c1 = 0.0
			c2 = 0.0

			if result.get('city', None) is not None:
				c1 = similarity(record.get('input_city'), result.get('city'), lcs=False)
			if result.get('sub_locality', None) is not None:
				c2 = similarity(record.get('input_city'), result.get('sub_locality'), lcs=False)

			c = max(c1, c2)

		return round(c, 2)

	@staticmethod
	def __get_confidence_on_postal_code(record, result):
		c = 1

		input_postal_code = record.get('input_postal_code', None)

		if input_postal_code is not None:
			c = 0

			postal_code = result.get('postal_code', None)
			if postal_code is not None:
				if int(input_postal_code) == int(postal_code):
					c = 1

		return round(c, 2)

	@staticmethod
	def __get_confidence_on_country(record, result):
		c = 0.0

		if record.get('input_country', None) is not None:
			if result.get('country', None) is not None:
				c = similarity(record.get('input_country'), result.get('country'), lcs=True)

		return round(c, 2)

	@staticmethod
	def __get_location_accuracy(record):
		location_acc = {
			'NOT_FOUND'          : 0, 
			'APPROXIMATE'        : 1,
			'GEOMETRIC_CENTER'   : 2,
			'RANGE_INTERPOLATED' : 3, 
			'ROOFTOP'            : 4
		}
		location_accuracy = -1

		try:
			location_accuracy = location_acc[record.get('location_type')]
		except:
			pass

		return location_accuracy

	@staticmethod
	def __get_address(record):
		if len(record['street']) == 0:
			record['street'] = refine_address(record)
		addr = str(record['street_number']) + ' ' + record['street']
		addr = addr.strip()
		record['address'] = addr

		return record

	@staticmethod
	def __build_query(record, fields=None):
		if fields is None:
			query = record.get('input_text', None)
		
		else:
			query = ''
			for field in fields:
				if record[field] != 0:
					query += str(record[field]) + ' '

			query = clean(query)
			query = normalize(query) if query is not None else '' 

		return query

	@staticmethod
	def __init_result():
		return {
			'formatted_address': '',
			'street_number': '',
			'street': '',
			'address': '',
			'city': '',
			'city_id': '',
			'sub_locality': '',
			'postal_code': '',
			'admin_area_level_2': '',
			'admin_area_level_1': '',
			'country': '',
			'country_code': '',
			'latitude': 0.0,
			'longitude': 0.0,
			'location_type': 'NOT_FOUND',
			'location_accuracy': 0,
			'place_id': '',
			'place_name': '',
			'place_type': '',
			'place_main_type': '',
			'place_main_type_id': '',
			'place_brand': '',
			'plus_code': '',
			'confidence': 0.0,
			'confidence_on_name': 0.0,
			'confidence_on_addr': 0.0,
			'confidence_on_city': 0.0,
			'confidence_on_postal_code': 0.0,
			'confidence_on_country': 0.0,
			'accepted' : False,
			'api_used' : '',
			'maps_URL' : '',
			'place_URL': '',
			'website'  : '',
			'phone'    : '',
			'email'    : '',
			'monday'   : '',
			'tuesday'  : '',
			'wednesday': '',
			'thursday' : '',
			'friday'   : '',
			'saturday' : '',
			'sunday'   : '',
		}

	@staticmethod
	def __init_stub(stub):
		if stub is None:
			stub = set_credentials()

		return stub
	
	def __get_accuracy_and_confidence(self, record):
		record['confidence_on_name']        = self.__get_confidence_on_name(self._data, record)
		record['confidence_on_addr']        = self.__get_confidence_on_addr(self._data, record)
		record['confidence_on_city']        = self.__get_confidence_on_city(self._data, record)
		record['confidence_on_postal_code'] = self.__get_confidence_on_postal_code(self._data, record)
		record['confidence_on_country']     = self.__get_confidence_on_country(self._data, record)

		record['location_accuracy'] = self.__get_location_accuracy(record)

		return record

	def __gc_parse_response(self, input_text, record, response):
		k = 0

		if input_text is not None:
			k, record['formatted_address'], record['confidence'] = self.__gc_get_formatted_address(input_text, response)
		else:
			record['formatted_address'] = response[k]['formatted_address']

		if k != -1:
			record['street_number']                 = self.__gc_get_street_number(response, k)
			record['street']                        = self.__gc_get_street(response, k)
			record['city']                          = self.__gc_get_city(response, k)
			record['sub_locality']                  = self.__gc_get_sub_locality(response, k)
			record['postal_code']                   = self.__gc_get_postal_code(response, k)
			record['admin_area_level_2']            = self.__gc_get_admin_area_level_2(response, k)
			record['admin_area_level_1']            = self.__gc_get_admin_area_level_1(response, k)
			record['country']                       = self.__gc_get_country(response, k)
			record['country_code']                  = self.__gc_get_country_code(response, k)
			record['latitude'], record['longitude'] = self.__gc_get_geometry(response, k)
			record['location_type']                 = self.__gc_get_location_type(response, k)
			record['place_id']                      = self.__gc_get_place_id(response, k)
			record['plus_code']                     = self.__gc_get_plus_code(response, k)

			record['maps_URL' ] = 'https://www.google.com/maps/search/?api=1&query={:.6f}%2C{:.6f}&query_place_id={}'.format(
				record['latitude'], record['longitude'], record['place_id']
			)

		return record

	def __gc_get_place_details(self, record, response):
		record['place_name']      = self.__pl_get_place_name(response)
		record['place_type']      = self.__pl_get_place_type(response)
		record['place_main_type'] = self.__pl_get_place_main_type(response)
		record['place_URL']       = self.__pl_get_place_url(response)
		record['website']         = self.__pl_get_website(response)
		record['phone']           = self.__pl_get_phone_number(response)

		opening_hours = self.__pl_get_opening_hours(response)
		if len(opening_hours) > 0:
			record = merge_dicts(record, opening_hours)

		return record

	def __pl_details_parse_response(self, input_text, record, response):
		if input_text is not None:
			_, record['formatted_address'], record['confidence'] = self.__pl_get_formatted_address(response, input_text)
		else:
			_, record['formatted_address'], _ = self.__pl_get_formatted_address(response)

		record['street_number']                 = self.__pl_get_street_number(response)
		record['street']                        = self.__pl_get_street(response)
		record['city']                          = self.__pl_get_city(response)
		record['sub_locality']                  = self.__pl_get_sub_locality(response)
		record['postal_code']                   = self.__pl_get_postal_code(response)
		record['admin_area_level_2']            = self.__pl_get_admin_area_level_2(response)
		record['admin_area_level_1']            = self.__pl_get_admin_area_level_1(response)
		record['country']                       = self.__pl_get_country(response)
		record['country_code']                  = self.__pl_get_country_code(response)
		record['latitude'], record['longitude'] = self.__pl_get_geometry(response)
		record['location_type']                 = self.__pl_get_location_type(response)
		record['place_id']                      = self.__pl_get_place_id(response)
		record['place_name']                    = self.__pl_get_place_name(response)
		record['place_type']                    = self.__pl_get_place_type(response)
		record['place_main_type']               = self.__pl_get_place_main_type(response)
		record['plus_code']                     = self.__pl_get_plus_code(response)
		record['place_URL']                     = self.__pl_get_place_url(response)
		record['website']                       = self.__pl_get_website(response)
		record['phone']                         = self.__pl_get_phone_number(response)
		
		record['maps_URL' ] = 'https://www.google.com/maps/search/?api=1&query={:.6f}%2C{:.6f}&query_place_id={}'.format(
			record['latitude'], record['longitude'], record['place_id']
		)

		opening_hours = self.__pl_get_opening_hours(response)
		if len(opening_hours) > 0:
			record = merge_dicts(record, opening_hours)

		return record
	
	def empty(self):
		self._data = self._init_record({
			**self._data, **self.__init_result()
		})

		return self

	def check_query(self, fields=None):
		query = self.__build_query(self._data, fields)

		if fields is not None:
			self._data['input_text'] = query

		return self

	def reverse_geocode(self, stub=None, response=None):
		r     = self.__init_result()
		stub  = self.__init_stub(stub)

		try:
			if response is not None:
				self._resp['reverse_geocode'] = response['reverse_geocode']
			else:
				self._resp['reverse_geocode'] = stub.reverse_geocode(latlng=self.coordinates, language=self._language)

			r = self.__gc_parse_response(None, r, self._resp['reverse_geocode'])
			r = self.__get_address(r)

			if self._isbusiness:
				self._resp['place_details'] = stub.place(place_id=r['place_id'], language=self._language)
				r = self.__gc_get_place_details(r, self._resp['place_details'])

			r['api_used'] = "reverse_geocode"

		except:
			#raise ValueError("Oops! Something went wrong in {}.".format(inspect.currentframe().f_code.co_name))
			pass

		finally:
			self._data = self._init_record({**self._data, **r})

		return self

	def geocode(self, stub=None, fields=None, response=None):
		r     = self.__init_result()
		stub  = self.__init_stub(stub)
		query = self.__build_query(self._data, fields)

		if fields is not None:
			self._data['input_text'] = query

		try:
			if is_numeric(query):
				if response is not None:
					self._resp['geocode'] = response['geocode']
				else:
					self._resp['geocode'] = stub.find_place(input=query, input_type='phonenumber')

					if len(self._resp['geocode']['candidates']) > 0:
						if response is not None:
							self._resp['place_details'] = response['place_details']
						else:
							self._resp['place_details'] = stub.place(place_id=self._resp['geocode']['candidates'][0]['place_id'])

						r = self.__pl_details_parse_response(input_text=None, record=r, response=self._resp['place_details'])
						r = self.__get_address(r)

					r['api_used'] = "find_place"

			else:
				if response is not None:
					self._resp['geocode'] = response['geocode']
				else:
					self._resp['geocode'] = stub.geocode(address=query, components=self._components, language=self._language)

				r = self.__gc_parse_response(query, r, self._resp['geocode'])
				r = self.__get_address(r)

				if self._isbusiness:
					self._resp['place_details'] = stub.place(place_id=r['place_id'], language=self._language)
					r = self.__gc_get_place_details(r, self._resp['place_details'])

				r = self.__get_accuracy_and_confidence(r)

				r['api_used'] = "geocode"

		except:
			#raise ValueError("Oops! Something went wrong in {}.".format(inspect.currentframe().f_code.co_name))
			pass

		finally:
			self._data = self._init_record({**self._data, **r})

		return self

	def autocomplete(self, stub=None, fields=None, response=None):
		r     = self.__init_result()
		stub  = self.__init_stub(stub)
		query = self.__build_query(self._data, fields)

		if fields is not None:
			self._data['input_text'] = query
		
		try:
			if response is not None:
				self._resp['autocomplete'] = response['autocomplete']
			else:
				self._resp['autocomplete'] = stub.places_autocomplete(input_text = query, offset = len(query), language=self._language) 

				if (len(self._resp['autocomplete']) > 0):
					if response is not None:
						self._resp['place_details'] = response['place_details']
					else:
						self._resp['place_details'] = stub.place(place_id=self._resp['autocomplete'][0]['place_id'])

					r = self.__pl_details_parse_response(input_text=None, record=r, response=self._resp['place_details'])
					r = self.__get_address(r)
					r = self.__get_accuracy_and_confidence(r)

			r['api_used'] = "autocomplete"

		except:
			#raise ValueError("Oops! Something went wrong in {}.".format(inspect.currentframe().f_code.co_name))
			pass

		finally:
			self._data = self._init_record({**self._data, **r})

		return self

	def text_search(self, stub=None, fields=None, location=None, radius=None, business_type=None, response=None):
		r     = self.__init_result()
		stub  = self.__init_stub(stub)
		query = self.__build_query(self._data, fields)

		if fields is not None:
			self._data['input_text'] = query
		
		try:
			if response is not None:
				self._resp['text_search'] = response['text_search']
			else:
				self._resp['text_search'] = stub.places(query=query, location=location, radius=radius, language=self._language, type=business_type)

				if self._resp['text_search']['status'] == 'OK':
					if response is not None:
						self._resp['place_details'] = response['place_details']
					else:
						self._resp['place_details'] = stub.place(place_id=self._resp['text_search']['results'][0]['place_id'])

					r = self.__pl_details_parse_response(input_text=query, record=r, response=self._resp['place_details'])
					r = self.__get_address(r)
					r = self.__get_accuracy_and_confidence(r)

			r['api_used'] = "text_search"

		except:
			#raise ValueError("Oops! Something went wrong in {}.".format(inspect.currentframe().f_code.co_name))
			pass

		finally:
			self._data = self._init_record({**self._data, **r})

		return self

	def find_place(self, stub=None, fields=None, location=None, radius=None, response=None):
		r     = self.__init_result()
		stub  = self.__init_stub(stub)
		query = self.__build_query(self._data, fields)

		if fields is not None:
			self._data['input_text'] = query

		input_type = 'phonenumber' if is_numeric(query) else 'textquery'

		try:
			if location is not None:
				if radius is None:
					location_bias = 'point:{:.5f},{:.5f}'.format(location[0], location[1])
				else:
					location_bias = 'circle:{:d}@{:.5f},{:.5f}'.format(radius, location[0], location[1])

			if response is not None:
				self._resp['find_place'] = response['find_place']
			else:
				self._resp['find_place'] = stub.find_place(
					input=query,
					input_type=input_type,
					location_bias=location_bias
				)

			if (len(self._resp['find_place']) > 0):
				if response is not None:
					self._resp['place_details'] = response['place_details']
				else:
					self._resp['place_details'] = stub.place(place_id=self._resp['find_place']['candidates'][0]['place_id'])

				r = self.__pl_details_parse_response(input_text=query, record=r, response=self._resp['place_details'])
				r = self.__get_address(r)
				r = self.__get_accuracy_and_confidence(r)

			r['api_used'] = "find_place"

		except:
			#raise ValueError("Oops! Something went wrong in {}.".format(inspect.currentframe().f_code.co_name))
			pass

		finally:
			self._data = self._init_record({**self._data, **r})

		return self

	def radar(self, stub=None, radius=None, keyword=None, business_type=None, response=None):
		r     = self.__init_result()
		stub  = self.__init_stub(stub)

		candidates = None

		try:
			if self.input_text is not None:
				location = self.geocode().coordinates
			else:
				location = self.coordinates

			if response is not None:
				self._resp['radar'] = response['radar']

			else:
				self._resp['radar'] = stub.places_nearby(
					location=location, 
					radius=radius, 
					keyword=keyword, 
					language=self._language, 
					type=business_type
				)

			candidates = [
				{
					'place_id': p['place_id'], 
					'distance': Point(p['geometry']['location']).distance(Point(location))
				} 
					for p in self._resp['radar']['results']
			]

		except:
			#raise ValueError("Oops! Something went wrong in {}.".format(inspect.currentframe().f_code.co_name))
			pass

		return candidates

	def place_details(self, stub=None, distance=None, response=None):
		r     = self.__init_result()
		stub  = self.__init_stub(stub)

		try:
			if response is not None:
				self._resp['place_details'] = response['place_details']
			else:
				self._resp['place_details'] = stub.place(place_id=self._data.get('input_text'))

			r = self.__pl_details_parse_response(input_text=None, record=r, response=self._resp['place_details'])
			r = self.__get_address(r)
			
			if distance is not None:
				r['distance'] = distance

			r['api_used'] = "place_details"

		except:
			#raise ValueError("Oops! Something went wrong in {}.".format(inspect.currentframe().f_code.co_name))
			pass

		finally:
			self._data = self._init_record({**self._data, **r})

		return self

	def compare_with(self, record, lcs=False):
		for token in [
			('input_text'   , 'formatted_address', 'confidence'           ), 
			('name'         , 'place_name'       , 'confidence_on_name'   ), 
			('input_address', 'address'          , 'confidence_on_addr'   ), 
			('input_city'   , 'city'             , 'confidence_on_city'   ), 
			('input_country', 'country'          , 'confidence_on_country')
		]:
			r1 = record.get    (token[0], None)
			r2 = self._data.get(token[1], None)

			if r1 is not None and r2 is not None:
				self._data[token[2]] = round(similarity(r1, r2, lcs=lcs), 2)

		return self

	def check(self):
		accepted = True

		if self._components is not None:
			for k, v in self._components.items():
				if self._data.get(k).lower() != str(v).lower():
					accepted = False
					break

		if accepted:
			accept_both = [True, True]

			if self.threshold_on_postal_code > 0:
				s1 = str(self._data['input_postal_code'])
				s2 = str(self._data['postal_code'])

				if len(s1) and len(s2):
					if s1[:2] != s2[:2]:
						accept_both[0] = False

					elif self.confidence_on_postal_code < self.threshold_on_postal_code:
						accept_both[0] = False

			if self.threshold_on_city > 0:
				if self.confidence_on_city < self.threshold_on_city:
					accept_both[1] = False

			accepted = accept_both[0] or accept_both[1]

		if accepted:
			if self.threshold_on_addr > 0:
				if self.confidence_on_addr < self.threshold_on_addr:
					accepted = False
		if accepted:
			if self.threshold > 0:
				if self.confidence < self.threshold:
					accepted = False

		if accepted:
			if self.location_accuracy <= 1:
				accepted = False

		self.accepted =  accepted

		return self

	def is_better(self, other):
		flag = True

		if other is not None:
			if not (self.accepted == True and other.accepted == False):
				if self.threshold_on_postal_code > 0:
					if self.confidence_on_postal_code < other.confidence_on_postal_code:
						flag = False

				if self.threshold_on_city > 0:
					if self.confidence_on_city < other.confidence_on_city:
						flag = False     

				if self.location_accuracy < other.location_accuracy:
					flag = False

				if self.location_accuracy > 1:
					if self.threshold_on_addr > 0:
						if self.confidence_on_addr < other.confidence_on_addr:
							flag = False

					if self.threshold_on_name > 0:
						if self.confidence_on_name < other.confidence_on_name:
							flag = False

					if self.threshold > 0:
						if self.confidence > other.confidence:
							if self.location_accuracy <= other.location_accuracy:
								flag = False

			if flag:
				accept_both = [True, True]

				if self.confidence_on_postal_code > other.confidence_on_postal_code:
					accept_both[0] = True

				if self.confidence_on_city > other.confidence_on_city:
					accept_both[0] = True

				flag = accept_both[0] or accept_both[1]

		return flag

	@property
	def threshold(self):
		return self._data.get('threshold', None)
	
	@threshold.setter
	def threshold(self, value):
		self._data['threshold'] = value
	
	@property
	def threshold_on_name(self):
		return self._data.get('threshold_on_name', None)
	
	@threshold_on_name.setter
	def threshold_on_name(self, value):
		self._data['threshold_on_name'] = value
	
	@property
	def threshold_on_addr(self):
		return self._data.get('threshold_on_addr', None)
	
	@threshold_on_addr.setter
	def threshold_on_addr(self, value):
		self._data['threshold_on_addr'] = value
	
	@property
	def threshold_on_postal_code(self):
		return self._data.get('threshold_on_postal_code', None)
	
	@threshold_on_postal_code.setter
	def threshold_on_postal_code(self, value):
		self._data['threshold_on_postal_code'] = value
	
	@property
	def threshold_on_city(self):
		return self._data.get('threshold_on_city', None)
	
	@threshold_on_city.setter
	def threshold_on_city(self, value):
		self._data['threshold_on_city'] = value
	
	@property
	def input_text(self):
		return self._data.get('input_text', None)
	
	@input_text.setter
	def input_text(self, value):
		if type(value) == str:
			self._data['input_text'] = value
		else:
			self._data['input_text'] = self.__build_query(self._data, fields=value)
	
	@property
	def formatted_address(self):
		return self._data.get('formatted_address', None)
	
	@property
	def street_number(self):
		return self._data.get('street_number', None)
	
	@property
	def street(self):
		return self._data.get('street', None)
	
	@property
	def city(self):
		return self._data.get('city', None)
	
	@property
	def sub_locality(self):
		return self._data.get('sub_locality', None)
	
	@property
	def postal_code(self):
		return self._data.get('postal_code', None)
	
	@property
	def admin_area_level_2(self):
		return self._data.get('admin_area_level_2', None)
	
	@property
	def admin_area_level_1(self):
		return self._data.get('admin_area_level_1', None)
	
	@property
	def country(self):
		return self._data.get('country', None)

	@property
	def country_code(self):
		return self._data.get('country_code', None)

	@property
	def location_type(self):
		return self._data.get('location_type', None)
	
	@property
	def location_accuracy(self):
		return self._data.get('location_accuracy', None)
	
	@property
	def place_id(self):
		return self._data.get('place_id', None)
	
	@property
	def place_name(self):
		return self._data.get('place_name', None)
	
	@property
	def place_type(self):
		return self._data.get('place_type', None)
	
	@property
	def place_main_type(self):
		return self._data.get('place_main_type', None)

	@property
	def place_brand(self):
		return self._data.get('place_brand', None)

	@property
	def plus_code(self):
		return self._data.get('plus_code', None)
	
	@property
	def address(self):
		return self._data.get('address', None)
	
	@property
	def confidence(self):
		return self._data.get('confidence', 0)
	
	@property
	def confidence_on_name(self):
		return self._data.get('confidence_on_name', 0)
	
	@property
	def confidence_on_addr(self):
		return self._data.get('confidence_on_addr', 0)
	
	@property
	def confidence_on_postal_code(self):
		return self._data.get('confidence_on_postal_code', 0)
	
	@property
	def confidence_on_city(self):
		return self._data.get('confidence_on_city', 0)
	
	@property
	def confidence_on_country(self):
		return self._data.get('confidence_on_country', 0)
	
	@property
	def accepted(self):
		return self._data.get('accepted', False)
	
	@accepted.setter
	def accepted(self, value):
		self._data['accepted'] = value
	
	@property
	def api_used(self):
		return self._data.get('api_used', None)

	@property
	def maps_URL(self):
		return self._data.get('maps_URL', None)

	@property
	def place_URL(self):
		return self._data.get('place_URL', None)

	@property
	def website(self):
		return self._data.get('website', None)

	@property
	def distance_haversine(self):
		return self._data.get('distance', None)

	def describe(self, all_=False):
		if not all_:
			print('id:                       ', self.id)
			print('input text:               ', self.input_text) 
			print('place name:               ', self.place_name)    
			print('place type:               ', self.place_type)    
			print('Maps URL:                 ', self.maps_URL)    
			print('formatted address:        ', self.formatted_address)
			print('longitude:                ', '%.6f' % self.longitude) 
			print('latitude:                 ', '%.6f' % self.latitude) 
			print('confidence:               ', '%.2f' % self.confidence) 
			print('location type:            ', self.location_type)

		else:
			print('id:                       ', self.id)
			print('name:                     ', self.name)
			print('input text:               ', self.input_text) 
			print('geocoder:                 ', self.api_used)
			print('place ID:                 ', self.place_id)
			print('place name:               ', self.place_name)    
			print('place type:               ', self.place_type)    
			print('place main type:          ', self.place_main_type)
			print('Maps URL:                 ', self.maps_URL)    
			print('place URL:                ', self.place_URL)    
			print('website:                  ', self.website)
			print('brand:                    ', self.place_brand)
			print('formatted address:        ', self.formatted_address)
			print('adress:                   ', self.address)
			print('postal code:              ', self.postal_code)
			print('city:                     ', self.city)
			print('longitude:                ', '%.6f' % self.longitude) 
			print('latitude:                 ', '%.6f' % self.latitude) 
			print('plus code:                ', self.plus_code)
			print('confidence:               ', '%.2f' % self.confidence) 
			print('confidence on name:       ', '%.2f' % self.confidence_on_name)
			print('confidence on addr:       ', '%.2f' % self.confidence_on_addr)
			print('confidence on city:       ', '%.2f' % self.confidence_on_city)
			print('confidence on postal code:', '%.0f' % self.confidence_on_postal_code)
			print('confidence on country:    ', '%.2f' % self.confidence_on_country)
			print('location type:            ', self.location_type)
			print('location accuracy:        ', self.location_accuracy)
			print('accepted:                 ', self.accepted)

		distance_from = self._data.get('distance', None)
		if distance_from is not None:
			print('distance:                 ', '%.0f m' % distance_from)

		print('')

		return self

def geocode(input_text, fields=None, components={'country': 'france'}, language='fr', isbusiness=False, stub=None, **kwargs) -> Place:
	p = Place(
		address=input_text, 
		components=components, language=language,
		isbusiness=isbusiness, 
		code_length=10
	)

	if kwargs is not None:
		p.set_thresholds(**kwargs)

	return p.geocode(stub=stub, fields=fields)

def reverse_geocode(input_text, language='fr', stub=None, **kwargs) -> Place:
	p = Place(
		address=input_text, 
		language=language
	)
	
	return p.reverse_geocode(stub=stub)

def autocomplete(input_text, fields=None, components={'country': 'france'}, language='fr', isbusiness=False, stub=None, **kwargs) -> Place:
	p = Place(
		address=input_text, 
		components=components, language=language,
		isbusiness=isbusiness, 
		code_length=10
	)

	if kwargs is not None:
		p.set_thresholds(**kwargs)

	return p.autocomplete(stub=stub, fields=fields)

def text_search(input_text, fields=None, location=None, radius=None, business_type=None, components={'country': 'france'}, language='fr', stub=None, **kwargs) -> Place:
	p = Place(
		address=input_text, 
		components=components, language=language,
		isbusiness=True, 
		code_length=10
	)

	if kwargs is not None:
		p.set_thresholds(**kwargs)

	return p.text_search(stub=stub, fields=fields, location=location, radius=radius, business_type=business_type)

def find_place(input_text, fields=None, location=None, radius=None, components={'country': 'france'}, language='fr', stub=None, **kwargs) -> Place:
	p = Place(
		address=input_text, 
		components=components, language=language,
		isbusiness=True, 
		code_length=10
	)

	if kwargs is not None:
		p.set_thresholds(**kwargs)

	return p.find_place(stub=stub, fields=fields, location=location, radius=radius)

def radar(input_text, components={'country': 'france'}, language='fr', radius=None, keyword=None, business_type=None, stub=None) -> list:
	p = Place(
		address=input_text, 
		components=components, language=language,
		isbusiness=True, 
		code_length=10
	)

	return p.radar(stub=stub, radius=radius, keyword=keyword, business_type=business_type)

def place_details(input_text, components={'country': 'france'}, language='fr', stub=None) -> Place:
	p = Place(
		address=input_text,
		components=components, language=language,
		isbusiness=True, 
		code_length=10
	)

	return p.place_details(stub=stub)

#EOF