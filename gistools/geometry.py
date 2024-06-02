import numpy
import json
import polyline
import shapely

from copy import copy, deepcopy
from math import radians, cos, sin, asin, sqrt
from shapely.ops import nearest_points
from shapely.geometry import MultiLineString

from gistools.utils     import is_list, is_float, format_float, is_integer
from gistools.utils     import none_dict
from gistools.plus_code import encode

EARTH_RADIUS = 6378.388 # https://en.wikipedia.org/wiki/Earth_radius

__all__ = ['EARTH_RADIUS', 'POINT', 'Point']

def latlon(arg):
	if isinstance(arg, shapely.geometry.Point):
		return arg.y, arg.x

	else:
		if isinstance(arg, dict):
			if 'geometry' in arg:
				return arg['geometry'].y, arg['geometry'].x

			elif "lat" in arg and "lng" in arg:
				return arg["lat"], arg["lng"]
			elif "Lat" in arg and "Lng" in arg:
				return arg["Lat"], arg["Lng"]
			elif "latitude" in arg and "longitude" in arg:
				return arg["latitude"], arg["longitude"]
			elif "Latitude" in arg and "Longitude" in arg:
				return arg["Latitude"], arg["Longitude"]
			elif "lat" in arg and "lon" in arg:
				return arg["lat"], arg["lon"]
			elif "Lat" in arg and "Lon" in arg:
				return arg["Lat"], arg["Lon"]

		elif is_list(arg) or isinstance(arg, tuple):
			if is_float(arg[0]) and is_float(arg[1]):
				return arg[0], arg[1]
			else:
				raise TypeError("Oops! Expected a lat/lng dict or tuple but got %s" % type(arg).__name__)

	return None, None

def latlon2str(latitude, longitude):
	return '%s,%s' % (format_float(latitude), format_float(longitude))

def gps2xy(lat, lng):
	""" Convert Earth-centered coordinates given as latitude and longitude (WGS84) to Cartesian (x,y,z) coordinates. 
	# http://stackoverflow.com/questions/1185408/converting-from-longitude-latitude-to-cartesian-coordinates
	"""
	lat_rad = radians(lat)
	lng_rad = radians(lng)
	
	x = EARTH_RADIUS * cos(lat_rad) * cos(lng_rad)
	y = EARTH_RADIUS * cos(lat_rad) * sin(lng_rad)
	z = EARTH_RADIUS * sin(lat_rad)
	
	return {'x': x, 'y': y, 'z': z}

def distance_euclidean(p1, p2):
	""" Return the Euclidean distance between p1 and p2.
	https://en.wikipedia.org/wiki/Euclidean_distance
	"""
	dx = p1['x'] - p2['x']
	dy = p1['y'] - p2['y']

	dist = sqrt((dx*dx) + (dy*dy))

	return dist 
	
def distance_manhattan(p1, p2): 
	""" Return the Manhattan distance (or Taxicab geometry) between p1 and p2.
	"""
	dx = p1['x'] - p2['x']
	dy = p1['y'] - p2['y']

	dist = abs(dx) + abs(dy)

	return dist

def distance_haversine(p1, p2):
	""" Return the geographical distance (or great-circle) between p1 and p2 using the Haversine formula.
	"""
	c1 = latlon(p1)
	c2 = latlon(p2)

	dlat = radians(c2[0] - c1[0])
	dlon = radians(c2[1] - c1[1])
	lat1 = radians(c1[0])
	lat2 = radians(c2[0])

	a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
	c = 2*asin(sqrt(a))
	dist = EARTH_RADIUS * c * 1000

	return dist

def kilometers_to_miles(km, ratio = 0.621371):
	""" Convert km to mi. 1 Kilometer = 0.621371 Mile
	"""
	return km * ratio

def miles_to_kilometers(mi, ratio = 0.621371):
	""" Convert mi to km. 1 Kilometer = 0.621371 Mile
	"""
	return mi / ratio

def find_nearest_point(row, destination, column, geom_col='geometry'):
	nearest_geom = nearest_points(row[geom_col], destination[geom_col].unary_union)
	match_geom   = destination.loc[destination.geometry == nearest_geom[1]]
	match_value  = match_geom[column].to_numpy()[0]

	return match_value

def decode_polyline(encoded: str):
	return [[lon, lat] for lat, lon in polyline.decode(encoded)]

def to_shapely(points): 
	return MultiLineString([points])

#==============================================================================
#
#   P o i n t 
#
#==============================================================================

POINT = [
	'id',
	'external_id',
	'name',
	'description',
	'longitude',
	'latitude',
	'plus_code',
	'geometry'
]

class Point:
	"""
	Represents a geographic point with latitude, longitude, and optional metadata.

	Attributes:
		id (str, optional): Unique identifier for the point.
		external_id (str, optional): External identifier for the point.
		name (str, optional): Name of the point.
		description (str, optional): Description of the point.
		longitude (float): Longitude coordinate of the point.
		latitude (float): Latitude coordinate of the point.
		plus_code (str, optional): Plus Code representation of the point.
		geometry (dict, optional): GeoJSON representation of the point.
		code_length (int): Length of the Plus Code to generate. Defaults to 10.

	Example:
		>>> point = Point({'latitude': 37.7749, 'longitude': -122.4194})
		>>> point.id = '12345'
		>>> point.name = 'Golden Gate Bridge'
		>>> print(point.plus_code)
		>>> print(point.to_WKT())
		>>> print(point.to_json())
	"""
	def __init__(self, data=None, code_length=10):
		"""
		Initializes a Point object.

		Args:
			data (dict, optional): Dictionary containing point data. Defaults to None.
			code_length (int, optional): Length of the Plus Code to generate. Defaults to 10.

		Raises:
			TypeError: If data is not a dictionary.
		"""
		self._data = none_dict(POINT)
		self._code_length = code_length

		if data is not None:
			if isinstance(data, dict):
				for k, v in data.items():
					self._data[k] = v
			
			self._data['latitude'], self._data['longitude'] = latlon(data)

			if self.latitude is not None and self.longitude is not None:
				self._data['plus_code'] = encode(
					self.latitude, self.longitude, 
					codeLength=self._code_length
				)

	#--------------------------------------------------------------------------
	# Magic methods
	#--------------------------------------------------------------------------

	def __repr__(self) -> str:
		"""
		Returns a string representation of the Point object.
		"""
		return '<{}>'.format(getattr(self, '__name__', self.__class__.__name__))

	def __getitem__(self, key):
		"""
		Allows accessing attributes as dictionary keys.
		"""
		return getattr(self, key)

	def __setitem__(self, key, value):
		"""
		Allows setting attributes as dictionary keys.
		"""
		setattr(self, key, value)

	def __eq__(self, other):
		"""
		Checks if two Point objects are equal based on their data.
		"""
		return self.data == other.data

	def __ne__(self, other):
		"""
		Checks if two Point objects are not equal based on their data.
		"""
		return self.data != other.data

	#--------------------------------------------------------------------------
	# Getters & Setters
	#--------------------------------------------------------------------------

	@property
	def data(self):
		"""
		Returns the data dictionary containing all attributes.
		"""
		return self._data

	@data.setter
	def data(self, value):
		"""
		Sets the data dictionary.
		"""
		self._data = value

	@property
	def id(self):
		"""
		Returns the ID of the point.
		"""
		return self._data.get('id', None)

	@id.setter
	def id(self, value):
		"""
		Sets the ID of the point.
		"""
		self._data['id'] = value

	@property
	def name(self):
		"""
		Returns the name of the point.
		"""
		return self.data.get('name', None)

	@name.setter
	def name(self, value):
		"""
		Sets the name of the point.
		"""
		self._data['name'] = value

	@property
	def latitude(self):
		"""
		Returns the latitude of the point.
		"""
		return self._data.get('latitude', None)
	
	@property
	def longitude(self):
		"""
		Returns the longitude of the point.
		"""
		return self._data.get('longitude', None)

	@property
	def coordinates(self):
		"""
		Returns a tuple of latitude and longitude coordinates.
		"""
		return (self.latitude, self.longitude)	

	@property
	def code_length(self):
		return self._code_length
	
	@code_length.setter
	def code_length(self, code_length):
		self._code_length = code_length

	@property
	def plus_code(self):
		return self._data.get('plus_code', None)

	#--------------------------------------------------------------------------
	# Basic Transformations
	#--------------------------------------------------------------------------

	def copy(self):
		return copy(self)
	
	def deepcopy(self):
		return deepcopy(self)

	#--------------------------------------------------------------------------
	# Computational tools
	#--------------------------------------------------------------------------

	def distance(self, other):
		from_ = (self.latitude, self.longitude)
		to_   = (other.latitude, other.longitude)

		return distance_haversine(from_, to_)

	#--------------------------------------------------------------------------
	# IO methods (to / from other formats)
	#--------------------------------------------------------------------------

	def to_dict(self):
		return self._data

	def to_json(self, indent=4) -> str:
		"""Serialize object to a JSON formatted string.

		Args:
			indent (int, optional): object members will be pretty-printed with that indent level. 
			An indent level of 0 will only insert newlines. 
			None is the most compact representation. 
			Defaults to 4.

		Returns:
			str: JSON representation of this object.
		"""
		return json.dumps(self._data, indent=indent)

	def to_WKT(self, precision=6):
		return 'POINT(%s %s)' % (round(self.longitude, precision), round(self.latitude, precision)) 
	
#EOF