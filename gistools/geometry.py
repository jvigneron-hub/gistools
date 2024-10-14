"""
Collection of utility functions for working with geographic data in Python.

This module provides a collection of functions and classes for working with geographic data, including:
* Latitude/Longitude Handling.
* Coordinate Transformations.
* Distance Calculations.
* Unit Conversions.
* Nearest Point Finding.
* Format Transformations (Polyline Decoding, Shapely Conversion).

**Constants**
* `EARTH_RADIUS`: The Earth's radius in kilometers (6378.388). See [Earth Radius in Wikipedia](https://en.wikipedia.org/wiki/Earth_radius).
* `POINT`: A list of attributes defining the structure of a Point object.

**Latitude/Longitude Handling**
* `latlon`: Extracts latitude and longitude from various input formats, such as dictionaries, lists, tuples, and Shapely points.
* `latlon2str`: Converts latitude and longitude to a string representation.

**Coordinate Transformations**
* `gps2xy`: Converts Earth-centered coordinates (latitude, longitude) to Cartesian (x,y,z) coordinates.

**Distance Calculations**
* `distance_euclidean`: Calculates the Euclidean distance between two points.
* `distance_manhattan`: Calculates the Manhattan distance (or Taxicab geometry) between two points.
* `distance_haversine`: Calculates the geographical distance (or great-circle) between two points using the Haversine formula.

**Unit Conversions**
* `kilometers_to_miles`: Converts kilometers to miles.
* `miles_to_kilometers`: Converts miles to kilometers.

**Nearest Point Finding**
* `find_nearest_point`: Finds the nearest point from a given row to a set of destination points based on a specified column.

**Polyline Decoding**
* `decode_polyline`: Decodes a polyline encoded string into a list of latitude/longitude coordinates.

**Conversion**
* `to_shapely`: Converts a list of coordinates into a Shapely MultiLineString object.
* `to_geo`: Converts a Pandas DataFrame to a GeoDataFrame.
* 'to_h3': TO DO.
* 'to_h3_boundaries': TO DO.
* 'h3_to_latlng': TO DO.
* 'get_convex_hull': Calculates the convex hull of a GeoDataFrame containing POINT geometries.

**Class Point**
*  Class `Point` provides a convenient way to represent and work with geographic points in your applications.
"""
import numpy
import pandas
import geopandas
import json
import polyline
import shapely
import h3
import h3pandas

from copy import copy, deepcopy
from math import radians, cos, sin, asin, sqrt
from shapely.ops import nearest_points, cascaded_union
from shapely.geometry import MultiLineString, Polygon, MultiPoint
from pandas.core.frame import DataFrame

from gistools.utils     import is_list, is_float, format_float, is_integer
from gistools.utils     import none_dict
from gistools.plus_code import encode

EARTH_RADIUS = 6378.388 
""" The Earth's radius in kilometers (6378.388). See [Earth Radius in Wikipedia](https://en.wikipedia.org/wiki/Earth_radius)."""

__all__ = [
	'EARTH_RADIUS', 
	'latlon', 
	'latlon2str', 
	'gps2xy', 
	'distance_euclidean', 
	'distance_manhattan', 
	'distance_haversine',
	'kilometers_to_miles',
	'miles_to_kilometers',
	'find_nearest_point',
	'decode_polyline',
	'to_shapely',
	'POINT', 
	'Point'
]

def latlon(arg):
	"""
	Extracts latitude and longitude from various input formats.

	Args:  
	- **arg (dict, list, tuple, shapely.geometry.Point)**: The input containing lat/lng information.

	Returns:  
	- **tuple**: A tuple containing (latitude, longitude) if successful, otherwise (None, None).

	Raises:  
	- **TypeError**: If the input format is not recognized.
	"""
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
	"""
	Converts latitude and longitude to a string representation.

	Args:
	- **latitude (float)**: The latitude value.  
	- **longitude (float)**: The longitude value.    

	Returns:  
	- **str**: The formatted latitude/longitude string in the format "latitude,longitude".
	"""
	return '%s,%s' % (format_float(latitude), format_float(longitude))

def gps2xy(lat, lng):
	"""
	Converts Earth-centered coordinates (latitude, longitude) to Cartesian (x,y,z) coordinates.  
	See [stackoverflow](http://stackoverflow.com/questions/1185408/converting-from-longitude-latitude-to-cartesian-coordinates).

	Args:  
	- **lat (float)**: Latitude in degrees.  
	- **lng (float)**: Longitude in degrees.  

	Returns:  
	- **dict**: A dictionary containing 'x', 'y', and 'z' Cartesian coordinates.		
	"""
	lat_rad = radians(lat)
	lng_rad = radians(lng)
	
	x = EARTH_RADIUS * cos(lat_rad) * cos(lng_rad)
	y = EARTH_RADIUS * cos(lat_rad) * sin(lng_rad)
	z = EARTH_RADIUS * sin(lat_rad)
	
	return {'x': x, 'y': y, 'z': z}

def distance_euclidean(p1, p2):
	"""
	Calculates the Euclidean distance between two points.  
	$d(p1, p2) = \sqrt(p1 - p2)^2$

	Args:  
	- **p1 (dict)**: A dictionary containing 'x' and 'y' coordinates of the first point.  
	- **p2 (dict)**: A dictionary containing 'x' and 'y' coordinates of the second point.  

	Returns:  
	- **float**: The Euclidean distance between the two points.
	"""
	dx = p1['x'] - p2['x']
	dy = p1['y'] - p2['y']

	dist = sqrt((dx*dx) + (dy*dy))

	return dist 
	
def distance_manhattan(p1, p2): 
	"""
	Calculates the Manhattan distance (or Taxicab geometry) between two points.

	Args:  
	- **p1 (dict)**: A dictionary containing 'x' and 'y' coordinates of the first point.  
	- **p2 (dict)**: A dictionary containing 'x' and 'y' coordinates of the second point.  

	Returns:  
	- float: The Manhattan distance between the two points.
	"""
	dx = p1['x'] - p2['x']
	dy = p1['y'] - p2['y']

	dist = abs(dx) + abs(dy)

	return dist

def distance_haversine(p1, p2, unit='km'):
	c1 = latlon(p1)
	c2 = latlon(p2)

	dlat = radians(c2[0] - c1[0])
	dlon = radians(c2[1] - c1[1])
	lat1 = radians(c1[0])
	lat2 = radians(c2[0])

	a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
	c = 2*asin(sqrt(a))

	dist = EARTH_RADIUS * c
	if unit == 'meters':
		dist *= 1000

	return dist 

def kilometers_to_miles(km, ratio = 0.621371):
	"""
	Converts kilometers to miles. 1 Kilometer = 0.621371 Mile.

	Args:  
	- **km (float)**: The distance in kilometers.  
	- **ratio (float, optional)**: The conversion ratio (1 Kilometer = 0.621371 Mile). Defaults to 0.621371.  

	Returns:  
	- **float**: The distance in miles.
	"""
	return km * ratio

def miles_to_kilometers(mi, ratio = 0.621371):
	"""
	Converts miles to kilometers. 1 Kilometer = 0.621371 Mile.

	Args:  
	- **mi (float)**: The distance in miles.  
	- **ratio (float, optional)**: The conversion ratio (1 Kilometer = 0.621371 Mile). Defaults to 0.621371.  

	Returns:  
	- **float**: The distance in kilometers.
	"""
	return mi / ratio

def find_nearest_point(row, destination, column, geom_col='geometry'):
	"""
	Finds the nearest point from a given row to a set of destination points based on a specified column.

	Args:  
	- **row (pandas.Series)**: The row containing the point to find the nearest point to.  
	- **destination (pandas.DataFrame)**: The DataFrame containing the destination points.  
	- **column (str)**: The column name in the destination DataFrame to retrieve the value from.  
	- **geom_col (str, optional)**: The name of the geometry column in both row and destination. Defaults to 'geometry'.  

	Returns:  
	- **object**: The value from the specified column in the destination DataFrame corresponding to the nearest point.
	"""
	nearest_geom = nearest_points(row[geom_col], destination[geom_col].unary_union)
	match_geom   = destination.loc[destination.geometry == nearest_geom[1]]
	match_value  = match_geom[column].to_numpy()[0]

	return match_value

def decode_polyline(encoded: str):
	"""
	Decodes a polyline encoded string into a list of latitude/longitude coordinates.

	Args:  
	- **encoded (str)**: The encoded polyline string.  

	Returns:  
	- **list**: A list of [longitude, latitude] coordinates.
	"""
	return [[lon, lat] for lat, lon in polyline.decode(encoded)]

def to_shapely(points): 
	"""
	Converts a list of coordinates into a Shapely MultiLineString object.

	Args:  
	- **points (list)**: A list of [longitude, latitude] coordinates.  

	Returns:  
	- **shapely.geometry.MultiLineString**: The Shapely MultiLineString object representing the points.  
	"""
	return MultiLineString([points])

def to_geo(data: DataFrame, from_=('longitude', 'latitude'), epsg=4326) -> geopandas.GeoDataFrame:
	if from_ == 'geometry':
		gdf = geopandas.GeoDataFrame(
			data=data, geometry=data['geometry'], crs="EPSG:{}".format(epsg)
		)

	else:
		gdf = geopandas.GeoDataFrame(
			data, geometry=geopandas.points_from_xy(x=data.get(from_[0]), y=data.get(from_[1]))
		).set_crs(epsg=epsg)

	return gdf

def to_h3(data, resolution, h3_col='h3'):
	def compute_h3(r, resolution):
		return h3.geo_to_h3(
			r['latitude'], r['longitude'], resolution
		)

	data[h3_col] = data.apply(compute_h3, resolution=resolution, axis='columns')

	return data

def to_h3_boundaries(data, h3_col='h3'):
	return data.set_index(h3_col).h3.h3_to_geo_boundary()

def h3_to_latlng(data, h3_col='h3'):
	latlng = data[h3_col].apply(lambda x: pandas.Series(h3.h3_to_geo(x), index=['latitude', 'longitude']))
	return pandas.concat([data[:], latlng[:]], axis='columns')

def get_convex_hull(gdf):
	"""
		Calculates the convex hull of a GeoDataFrame containing POINT geometries.
	
	Args:
	- **gdf** (geopandas.GeoDataFrame): Input GeoDataFrame with POINT geometry.
	
	Returns:
	- **geopandas.GeoDataFrame**:  A GeoDataFrame containing the convex hull polygon.
	"""
	all_points = MultiPoint(list(gdf.geometry)) # Extract all points from the GeoDataFrame.
	convex_hull = all_points.convex_hull # Calculate the convex hull polygon.
	convex_hull_gdf = geopandas.GeoDataFrame(geometry=[convex_hull], crs=gdf.crs) # Create a new GeoDataFrame for the convex hull.

	return convex_hull_gdf

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
""" A list of attributes defining the structure of a Point object."""

class Point:
	"""
	Represents a geographic point with latitude, longitude, and optional metadata.

	Attributes:  
		- `id`(str, optional): Unique identifier for the point.  
		- `external_id`(str, optional): External identifier for the point.  
		- `name`(str, optional): Name of the point.  
		- `description`(str, optional): Description of the point.  
		- `longitude`(float): Longitude coordinate of the point.  
		- `latitude`(float): Latitude coordinate of the point.  
		- `plus_code`(str, optional): Plus Code representation of the point.  
		- `code_length`(int): Length of the Plus Code to generate. Defaults to 10.  

	Methods:  
		- `__init__`(data=None, code_length=10): Initializes a Point object.  
		- `__repr__`(): Returns a string representation of the Point object.  
		- `__getitem__`(key): Allows accessing attributes as dictionary keys.  
		- `__setitem__`(key, value): Allows setting attributes as dictionary keys.  
		- `__eq__`(other): Checks if two Point objects are equal based on their data.  
		- `__ne__`(other): Checks if two Point objects are not equal based on their data.  
		- `data`: Returns the data dictionary containing all attributes.  
		- `id`: Returns the ID of the point.  
		- `name`: Returns the name of the point.  
		- `latitude`: Returns the latitude of the point.  
		- `longitude`: Returns the longitude of the point.  
		- `coordinates`: Returns a tuple of latitude and longitude coordinates.  
		- `code_length`: Returns the length of the Plus Code.  
		- `plus_code`: Returns the Plus Code representation of the point.  
		- `copy()`: Returns a shallow copy of the Point object.  
		- `deepcopy()`: Returns a deep copy of the Point object.  
		- `distance`(other): Calculates the Haversine distance between this point and another.  
		- `to_dict`(): Returns the data dictionary containing all attributes.  
		- `to_json`(indent=4): Serializes the object to a JSON formatted string.  
		- `to_WKT`(precision=6): Returns the Well-Known Text (WKT) representation of the point.  
	"""
	def __init__(self, data=None, code_length=10):
		"""
		Initializes a Point object.

		Args:
		- **data (dict, optional)**: Dictionary containing point data. Defaults to None.
		- **code_length (int, optional)**: Length of the Plus Code to generate. Defaults to 10.

		Raises:
		- **TypeError**: If data is not a dictionary.
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
	def external_id(self):
		"""
		Returns the external identifier of the point.
		"""
		return self._data.get('external_id', None)

	@external_id.setter
	def external_id(self, value):
		"""
		Sets the external identifier of the point.
		"""
		self._data['external_id'] = value

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
	def description(self):
		"""
		Returns the description of the point.
		"""
		return self.data.get('description', None)

	@description.setter
	def description(self, value):
		"""
		Sets the description of the point.
		"""
		self._data['description'] = value

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
		"""
		Returns the length of the Plus Code.
		"""
		return self._code_length
	
	@code_length.setter
	def code_length(self, code_length):
		"""
		Sets the length of the Plus Code.
		"""
		self._code_length = code_length

	@property
	def plus_code(self):
		"""
		Returns the Plus Code representation of the point.
		"""
		return self._data.get('plus_code', None)

	#--------------------------------------------------------------------------
	# Basic Transformations
	#--------------------------------------------------------------------------

	def copy(self):
		"""
		Returns a shallow copy of the Point object.
		"""
		return copy(self)
	
	def deepcopy(self):
		"""
		Returns a deep copy of the Point object.
		"""
		return deepcopy(self)

	#--------------------------------------------------------------------------
	# Computational tools
	#--------------------------------------------------------------------------

	def distance(self, other):
		"""
		Calculates the Haversine distance between this point and another.

		Args:  
		- **other (Point)**: The other point to calculate the distance to.

		Returns:  
		- **float**: The distance in meters between the two points.
		"""
		from_ = (self.latitude, self.longitude)
		to_   = (other.latitude, other.longitude)

		return distance_haversine(from_, to_)

	#--------------------------------------------------------------------------
	# IO methods (to / from other formats)
	#--------------------------------------------------------------------------

	def to_dict(self):
		"""
		Returns the data dictionary containing all attributes.
		"""
		return self._data

	def to_json(self, indent=4) -> str:
		"""
		Serialize object to a JSON formatted string.

		Args:
		- **indent (int, optional)**: object members will be pretty-printed with that indent level.   
		An indent level of 0 will only insert newlines.  
		None is the most compact representation. Defaults to 4.

		Returns:
		- **str**: JSON representation of this object.
		"""
		return json.dumps(self._data, indent=indent)

	def to_WKT(self, precision=6):
		"""
		Returns the Well-Known Text (WKT) representation of the point.

		Args:
		- **precision(int, optional)**: the number of decimal places to round the coordinates to.   
		Defaults to 6.

		Returns:
		- **str**: The WKT representation of the point.
		"""
		return 'POINT(%s %s)' % (round(self.longitude, precision), round(self.latitude, precision)) 
	
#EOF