import math
import time
import inspect
import operator
import re
import math
import numpy
import pandas
import geopandas
import types
import os
import codecs
import json
import pandas
import csv
import pickle
import collections
import pytz

from operator import eq, ne, lt, le, gt, ge
from datetime import datetime, timezone
from pandas.core.frame import DataFrame

#------------------------------------------------------------------------------
# System utilities
#------------------------------------------------------------------------------

def has_method(arg, method):
	"""Checks if an object has a callable method with the given name.

	Args:
		arg: The object to check for the method.
		method: The name of the method to look for.

	Returns:
		True if the object has a method with the given name that is also callable (a function), False otherwise.
	"""	
	# This function uses two checks:
	# 1. hasattr(arg, method): Checks if the object has an attribute with the given method name.
	# 2. callable(getattr(arg, method)): Checks if the retrieved attribute is actually callable, meaning it's a function. 
	return hasattr(arg, method) and callable(getattr(arg, method))

def get_class_name(obj):
	"""Retrieves the class name of the given object.

	This function takes an object of any type as input and returns the name
	of the class to which it belongs. This can be useful for introspection
	or debugging purposes, where you might need to determine the type
	of an object at runtime.

	Args:
		obj (object): The object whose class name you want to obtain.

	Returns:
		str: The name of the class to which the object belongs.
	"""	
	return type(obj).__name__

def get_class_attr(classname):
	"""Retrieves public attributes of a given class.

	This function takes the name of a class (`classname`) as input and returns
	a list of its public attributes (excluding methods and dunder methods).
	It uses `inspect.getmembers` to introspect the class and filters out
	methods using `inspect.isroutine` and dunder methods (those starting and
	ending with double underscores) using list comprehension.

	Args:
		classname (str): The name of the class to introspect.

	Returns:
		list: A list of public attributes (strings) of the class.
	"""	
	attributes = inspect.getmembers(classname, lambda x : not(inspect.isroutine(x)))
	return [x for x in attributes if not(x[0].startswith('__') and x[0].endswith('__'))]

#------------------------------------------------------------------------------
# Date/Time
#------------------------------------------------------------------------------

def isoformat_as_datetime(s, format_string='%Y-%m-%dT%H:%M:%SZ'):
	"""
	Converts an ISO 8601 formatted string to a datetime object.

	Args:
		s: The ISO 8601 formatted string to convert.
		format_string: The format string to use for parsing. Defaults to '%Y-%m-%dT%H:%M:%SZ'.

	Returns:
		A datetime object representing the parsed date and time.

	Example:
		isoformat_as_datetime('2023-10-26T12:34:56Z') 
		# Output: datetime.datetime(2023, 10, 26, 12, 34, 56)
	"""
	return datetime.strptime(s, format_string)

def str2datetime(s, format_string='%d/%m/%Y %H:%M:%S'):
	"""
	Converts a string representing a date and time to a datetime object.

	Args:
		s: The string representing the date and time.
		format_string: The format string to use for parsing. Defaults to '%d/%m/%Y %H:%M:%S'.

	Returns:
		A datetime object representing the parsed date and time.

	Example:
		str2datetime('26/10/2023 12:34:56') 
		# Output: datetime.datetime(2023, 10, 26, 12, 34, 56)
	"""
	return datetime.strptime(s, format_string)

def datetime2str(d, format_string='%d/%m/%Y %H:%M:%S'):
	"""
	Converts a datetime object to a string representation.

	Args:
		d: The datetime object to convert.
		format_string: The format string to use for the conversion. Defaults to '%d/%m/%Y %H:%M:%S'.

	Returns:
		A string representation of the datetime object in the specified format.

	Example:
		datetime2str(datetime(2023, 10, 26, 12, 34, 56)) 
		# Output: '26/10/2023 12:34:56'
	"""
	return d.strftime(format_string) 

def str2localdatetime(s, format_string='%Y-%m-%dT%H:%M:%S.000Z', timezone='Europe/Paris'):
	"""
	Converts a string representing a UTC datetime to a local datetime object.

	Args:
		s: The string representing the UTC datetime.
		format_string: The format string to use for parsing. Defaults to '%Y-%m-%dT%H:%M:%S.000Z'.
		timezone: The timezone to convert to. Defaults to 'Europe/Paris'.

	Returns:
		A local datetime object representing the parsed date and time in the specified timezone.

	Example:
		str2localdatetime('2023-10-26T12:34:56.000Z', timezone='Europe/London') 
		# Output: datetime.datetime(2023, 10, 26, 13, 34, 56, tzinfo=<DstTzInfo 'Europe/London' LMT+0:00:00 STD>)
	"""
	tz = pytz.timezone(timezone)
	return str2datetime(s, format_string=format_string).astimezone(tz)

def str2timestamp(s, format_string='%d/%m/%Y %H:%M:%S'):
	"""
	Converts a string representing a date and time to a Unix timestamp (integer seconds since epoch).

	Args:
		s: The string representing the date and time.
		format_string: The format string to use for parsing. Defaults to '%d/%m/%Y %H:%M:%S'.

	Returns:
		An integer representing the Unix timestamp.

	Example:
		str2timestamp('26/10/2023 12:34:56') 
		# Output: 1703720496
	"""
	return int(math.floor(datetime.timestamp(datetime.strptime(s, format_string))))

def utc_to_local(utc_dt):
	"""
	Converts a UTC datetime object to a local datetime object.

	Args:
		utc_dt: The UTC datetime object to convert.

	Returns:
		A local datetime object representing the same date and time in the local timezone.

	Example:
		utc_dt = datetime(2023, 10, 26, 12, 34, 56, tzinfo=timezone.utc)
		local_dt = utc_to_local(utc_dt)
		# Output: datetime.datetime(2023, 10, 26, 14, 34, 56) (assuming local time is UTC+2)
	"""
	return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

def str2localtimestamp(s, format_string='%Y-%m-%dT%H:%M:%S.%fZ'):
	"""
	Converts a UTC datetime string to a local timestamp (integer seconds since epoch).

	Args:
		s: The string representing the UTC datetime.
		format_string: The format string to use for parsing. Defaults to '%Y-%m-%dT%H:%M:%S.%fZ'.

	Returns:
		An integer representing the local timestamp.

	Example:
		str2localtimestamp('2023-10-26T12:34:56.000Z') 
		# Output: 1703724096 (assuming local time is UTC+2)
	"""
	utc_offset = utc_to_local(datetime.strptime(s, format_string)).utcoffset().seconds
	return str2timestamp(s, format_string)+utc_offset

def str2localdatetime(s, format_string='%Y-%m-%dT%H:%M:%S.000Z', timezone='Europe/Paris'):
	"""
	Converts a UTC datetime string to a local datetime object.

	Args:
		s: The string representing the UTC datetime.
		format_string: The format string to use for parsing. Defaults to '%Y-%m-%dT%H:%M:%S.000Z'.
		timezone: The timezone to convert to. Defaults to 'Europe/Paris'.

	Returns:
		A local datetime object representing the parsed date and time in the specified timezone.

	Example:
		str2localdatetime('2023-10-26T12:34:56.000Z', timezone='Europe/London') 
		# Output: datetime.datetime(2023, 10, 26, 13, 34, 56, tzinfo=<DstTzInfo 'Europe/London' LMT+0:00:00 STD>)
	"""
	return utc_to_local(datetime.strptime(s, format_string))

def timestamp2str(t, format_string='%d/%m/%Y %H:%M:%S'):
	"""
	Converts a Unix timestamp (integer seconds since epoch) to a string representation.

	Args:
		t: The Unix timestamp (integer).
		format_string: The format string to use for the conversion. Defaults to '%d/%m/%Y %H:%M:%S'.

	Returns:
		A string representation of the timestamp in the specified format.

	Example:
		timestamp2str(1703720496) 
		# Output: '26/10/2023 12:34:56'
	"""
	return datetime.fromtimestamp(t).strftime(format_string)

def timestr2seconds(timestr):
	"""
	Converts a time string in HH:MM:SS format to seconds.

	Args:
		timestr: The time string in HH:MM:SS format.

	Returns:
		The time in seconds.

	Example:
		timestr2seconds("01:02:03")
		# Output: 3723
	"""
	ftr = [3600,60,1]
	s = sum([a*b for a, b in zip(ftr, [int(i) for i in timestr.split(":")])])

	return s 

def timestr2minutes(timestr):
	"""
	Converts a time string in MM:SS format to minutes.

	Args:
		timestr: The time string in MM:SS format.

	Returns:
		The time in minutes.

	Example:
		timestr2minutes("02:03")
		# Output: 2.05
	"""
	ftr = [60,1]
	m = sum([a*b for a, b in zip(ftr, [int(i) for i in timestr.split(":")])])

	return m

def seconds2timestr(duration, format_string='%H:%M:%S'):
	"""
	Converts a duration in seconds to a time string in the specified format.

	Args:
		duration: The duration in seconds.
		format_string: The format string to use for the conversion. Defaults to '%H:%M:%S'.

	Returns:
		A time string representing the duration in the specified format.

	Example:
		seconds2timestr(3723) 
		# Output: '01:02:03'
	"""
	return time.strftime(format_string, time.gmtime(duration))

def to_timestr(seconds):
	"""
	Converts a duration in seconds to a time string in HH:MM:SS format.

	Args:
		seconds: The duration in seconds.

	Returns:
		A time string representing the duration in HH:MM:SS format.

	Example:
		to_timestr(3723) 
		# Output: '01:02:03'
	"""
	m, s = divmod(seconds, 60) 
	h, m = divmod(m, 60)

	return '{:02d}:{:02d}:{:02d}'.format(h,m,s)	

def total_seconds(start, end, format_string='%d/%m/%Y %H:%M:%S'):
	"""
	Calculates the total number of seconds between two datetime strings.

	Args:
		start: The starting datetime string.
		end: The ending datetime string.
		format_string: The format string to use for parsing the datetime strings. Defaults to '%d/%m/%Y %H:%M:%S'.

	Returns:
		The total number of seconds between the two datetime strings.

	Example:
		total_seconds('26/10/2023 12:34:56', '27/10/2023 14:56:00') 
		# Output: 91204.0
	"""
	d1 = datetime.strptime(start, format_string)
	d2 = datetime.strptime(end  , format_string)

	s = (d2-d1).total_seconds()

	return s

def format_datetime(s, format_from='%d/%m/%Y %H:%M:%S', format_to='%Y-%m-%dT%H:%M:%SZ'):
	"""
	Converts a datetime string from one format to another.

	Args:
		s: The datetime string to convert.
		format_from: The format string of the input datetime string. Defaults to '%d/%m/%Y %H:%M:%S'.
		format_to: The format string of the output datetime string. Defaults to '%Y-%m-%dT%H:%M:%SZ'.

	Returns:
		The datetime string in the specified output format.

	Example:
		format_datetime('26/10/2023 12:34:56', format_to='%d-%m-%YT%H:%M:%SZ') 
		# Output: '26-10-2023T12:34:56Z'
	"""
	return datetime.strptime(s, format_from).strftime(format_to)

def is_date(d, format_string='%d/%m/%Y'):
	"""
	Checks if a string represents a valid date in the specified format.

	Args:
		d: The string to check.
		format_string: The format string to use for parsing the date. Defaults to '%d/%m/%Y'.

	Returns:
		True if the string represents a valid date, False otherwise.

	Example:
		is_date('26/10/2023')  # True
		is_date('26/10/2023 12:34:56')  # False (because it includes time)
		is_date('2023-10-26', format_string='%Y-%m-%d')  # True 
	"""
	try:
		datetime.strptime(d, format_string)
		return True
	except ValueError:
		return False

def is_time(t, format_string='%H:%M:%S'):
	"""
	Checks if a string represents a valid time in the specified format.

	Args:
		t: The string to check.
		format_string: The format string to use for parsing the time. Defaults to '%H:%M:%S'.

	Returns:
		True if the string represents a valid time, False otherwise.

	Example:
		is_time('12:34:56')  # True
		is_time('12:34:56 AM')  # False (because it includes AM/PM)
		is_time('12:34:56.123')  # True (allows milliseconds)
		is_time('12:34')  # False (missing seconds)
	"""
	try:
		# Attempt to parse the string using the given format
		time_object = datetime.datetime.strptime(t, format_string)
		# If parsing successful, it's a valid time
		return True
	except ValueError:
		# If parsing fails, it's not a valid time
		return False

def isocalendar(s, format_string='%d/%m/%Y'):
	"""
	Returns the ISO calendar tuple (ISO year, ISO week number, ISO weekday) for a given date string.

	Args:
		s: The date string to convert.
		format_string: The format string to use for parsing the date. Defaults to '%d/%m/%Y'.

	Returns:
		A tuple containing (ISO year, ISO week number, ISO weekday).

	Example:
		isocalendar('26/10/2023') 
		# Output: (2023, 43, 3)  # Wednesday of the 43rd week in 2023
	"""
	return str2datetime(s, format_string).isocalendar()

def weekday(s, format_string='%d/%m/%Y'):
	"""
	Returns the weekday (1-7) for a given date string, where 1 is Monday and 7 is Sunday.

	Args:
		s: The date string to convert.
		format_string: The format string to use for parsing the date. Defaults to '%d/%m/%Y'.

	Returns:
		The weekday (1-7).

	Example:
		weekday('26/10/2023') 
		# Output: 3  # Wednesday
	"""
	return str2datetime(s, format_string).weekday()+1

def weekday_name(s, format_string='%d/%m/%Y'):
	"""
	Returns the full name of the weekday for a given date string.

	Args:
		s: The date string to convert.
		format_string: The format string to use for parsing the date. Defaults to '%d/%m/%Y'.

	Returns:
		The full name of the weekday (e.g., "Monday", "Tuesday", ...).

	Example:
		weekday_name('26/10/2023') 
		# Output: 'Wednesday'
	"""
	d = str2datetime(s, format_string=format_string)
	return d.strftime('%A')

#------------------------------------------------------------------------------
# Numeric
#------------------------------------------------------------------------------

def isnan(number):
	""" Returns True if number of not a number.
	"""
	flag = False
	if str(number) == 'nan':
		flag = True
	
	return flag

def is_numeric(literal):
	""" Returns whether a literal can be parsed as a numeric value
		http://www.rosettacode.org/wiki/Determine_if_a_string_is_numeric#Python
	"""
	castings = [int, float, complex,
			lambda s: int(s, 2), #binary
			lambda s: int(s, 8), #octal
			lambda s: int(s,16)  #hex
		]
	for cast in castings:
		try:
			cast(literal)
			return True
		except ValueError:
			pass

	return False

def is_integer(number):
	""" Returns True if number is an integer. 
	"""
	try:
		return number == int(number)
	except ValueError:
		return False

def is_numeric_and_integer(arg):
	""" Returns True if arg is an integer even if it passed as a string.
	"""
	try:
		if is_numeric(arg):
			return is_integer(int(arg))
	except ValueError:
		pass
	
	return False

def is_float(number):
	""" Returns True if number is a float. 
	"""
	try:
		return number == float(number)
	except ValueError:
		return False

def is_number_regex(s):
	"""  Returns True is string is a number.
	"""
	if re.match("^\d+?\.\d+?$", s) is None:
		return s.isdigit()
	return True

def is_number_repl_isdigit(s):
	""" Returns True is string is a number.
	"""
	return s.replace('.','',1).isdigit()

def to_int(element):
	""" Converts a number into an integer.
	"""
	n = math.nan

	try:
		n = int(element)
	except:
		pass

	return n

def format_float(arg):
	""" Converts a float into a string.
	"""
	return ("%f" % float(arg)).rstrip("0").rstrip(".")

#------------------------------------------------------------------------------
# Lists
#------------------------------------------------------------------------------

def is_list(arg):
	"""Checks if arg is list-like. This excludes strings and dicts.
	https://github.com/googlemaps/google-maps-services-python/blob/master/googlemaps/convert.py
	"""
	if isinstance(arg, dict):
		return False
	if isinstance(arg, str): # Python 3-only, as str has __iter__
		return False

	return (not has_method(arg, "strip") and has_method(arg, "__getitem__") or has_method(arg, "__iter__"))

def is_array(a):
	""" Returns True is a is an array.
	"""
	flag = True
	try:
		len(a)
	except:
		flag = False

	return flag

def is_in_collection(element, collection:iter):
	""" Checks if an element exists in a list.
	"""
	return element in collection

def remove_none(l):
	return list(filter(None.__ne__, l))

def intersection(list1_, list2_): 
	''' Return Intersection of 2 lists.

	Args:
		list1_ (list) 
		list2_ (list) 

	Return:
		list of all those elements which are common to both of the initial lists
	'''
	return list(set(list1_) & set(list2_)) 

def itemgetter(l, key):
	return list(map(operator.itemgetter(key), l))

def is_in_list(l, pattern):
	return all(x in pattern for x in l)

def is_in_list_of_dict(l, key, value):
	return value in itemgetter(l, key)

def drop_duplicates(l):
	return list( dict.fromkeys(l))

def subfinder(l, pattern):
	return [x for x in l if x in set(pattern)]

def split_listoftuples(l: list) -> list:
	"""Convert a list of tuples to a matrix  

	Args:
		l (list): list of tuples e.g. [(x1, y1), (x2, y2), ...]

	Returns:
		list: matrix e.g. [[x1, x2, ...], [y1, y2, ..]]
	"""
	return list(zip(*l))

def find_duplicates(l: list) -> list:
	return [item for item, count in collections.Counter(l).items() if count > 1]

def add_to(l, value):
	"""Add value to each Element in a list using map() with a lambda expression
	"""
	return list(map(lambda x: x+value, l))

#------------------------------------------------------------------------------
# Dictionnaries
#------------------------------------------------------------------------------

def merge_dicts(dict1, dict2):
	"""Merge 2 dictionnaries.

	Args:
		dict1 (dict) 1st dict
		dict2 (dict) 2nd dict

	Returns:
		dict1 + dict2
	"""
	return {**dict1, **dict2}

def none_dict(from_list):
	"""Create a empty dictionnary from a list of keywords.

	Args:
		from_list (list of strings): Keywords.

	Returns:
		Empty dictionnary.
	"""
	return {key: None for key in from_list}

def is_empty(d: dict, usecols=None) -> bool:
	"""Check if a dictionary is made of empty inputs.

	Args:
		d (dict): input dictionary.
		usecols (list of strings, optional): check only specified keys. Defaults to None.

	Returns:
		bool: True if empty.
	"""
	l = 0

	if usecols is None:
		for _, v in d.items():
			l += len(str(v))
	
	else:
		if not all(isinstance(s, str) for s in usecols):
			raise TypeError("Oops! Expected a list of strings but got %s" % type(usecols).__name_)
		
		for k in usecols:
			l += len(str(d.get(k)))	

	return l == 0

def is_set(record, key) -> bool:
	""" Check if an element exists in a dict.
	"""
	if key in record:
		if record[key] is not None: 
			if isinstance(record[key], str) or isinstance(record[key], list):
				return True
			if not math.isnan(record[key]):
				return True

	return False

def is_set_toint(record, key) -> bool:
	""" Check if an element 1st exists in a dict and 2nd is an integer.
	"""
	flag = False

	if is_set(record, key):
		if is_integer(record[key]):
			flag = True

	return flag

def is_set_tofloat(record, key) -> bool:
	""" Check if an element 1st exists in a dict and 2nd is a float.
	"""
	flag = False

	if is_set(record, key):
		if is_float(record[key]):
			flag = True

	return flag

def is_set_tostr(record, key) -> bool:
	""" Check if an element 1st exists in a dict and 2nd is a string.
	"""
	flag = False

	if is_set(record, key):
		flag = isinstance(record[key], str)

	return flag

#------------------------------------------------------------------------------
# Dataframes
#------------------------------------------------------------------------------

def is_dataframe(records):
	return isinstance(records, pandas.DataFrame) or isinstance(records, geopandas.GeoDataFrame)

def get_dataframe(obj):
	if hasattr(obj, 'data'):
		obj = obj.data

	return obj if is_dataframe(obj) else from_dict(obj)

def get_columns(df, empty=False):
	s = df.isnull().any()

	return s[s == empty].index.tolist()

def from_dict(d: dict, columns=None) -> DataFrame:
	"""Create DataFrame object from dictionary by columns.

	Args:
		d (dict), 
		columns (list of strings).

	Returns:
		DataFrame object.
	"""
	df = pandas.DataFrame.from_dict(d)
	if columns is not None:
		df = df.reindex (columns=columns)

	return df

def where(df, expr):
	"""
	Applies filtering conditions to a Pandas DataFrame based on a given expression.

	Args:
		df: The Pandas DataFrame to filter.
		expr: A tuple, list of tuples, or a single tuple defining the filtering criteria.
		- Single Tuple: (column_name, operator, value)
		- List of Tuples: [(column_name, operator, value), ...]
		- Tuple of Tuples: ((column_name, operator, value), ...) 

	Returns:
		A new DataFrame filtered based on the provided expression.

	Supported Operators:
		- '==', '!=', '>', '<', '>=', '<='
		- 'isin' (for membership in a list)
		- '~isin' (for negation of membership in a list)

	Example:
		- where(df, ('col1', '>', 10))
		- where(df, [('col2', '==', 'value'), ('col3', 'isin', [1, 2, 3])])
	"""
	if isinstance(expr, tuple):
		expr = [expr]

	if isinstance(expr, (list, tuple)):	
		for item in expr:
			if   item[1] == 'isin' and isinstance(item[2], list):
				df = df[ df[item[0]].isin(item[2])]

			elif item[1] =='~isin' and isinstance(item[2], list):
				df = df[~df[item[0]].isin(item[2])]

			elif item[0] in df.columns and item[2] is not None:
				op_table = {
					'==': eq,
					'!=': ne,
					'>' : gt,
					'<' : lt,
					'>=': ge,
					'<=': le
				}

				op_ = item[1] if isinstance(item[1], types.BuiltinFunctionType) else op_table.get(item[1], None)
				df = df[op_(df[item[0]], item[2])]

	return df

def isin(df: DataFrame, key: str, values: list):
	return df[df[key].isin([values] if isinstance(values, str) else values)]

def not_isin(df: DataFrame, key: str, values: list):
	return df[~df[key].isin([values] if isinstance(values, str) else values)]

def join(left, right, left_on, right_on, how='left', output=None):
	"""Merge 2 DataFrame or named Series objects with a database-style join.

	Args:
		left (DataFrame) : left object.
		right (DataFrame): right object to merge with.
		left_on (string) : column or index level names to join on in the left DataFrame.
		right_on (string): column or index level names to join on in the right DataFrame.
		how (str, optional): type of merge to be performed. Defaults to 'left'.
		output (DataFrame or list, optional): DataFrame of the tow merged objects or select column. Defaults to None.

	Returns:
		DataFrame object.
	"""
	df = pandas.merge(left, right, left_on=left_on, right_on=right_on, how=how)

	if output is not None:
		return df[output].tolist()
	else:
		return df

def to_geo(data: DataFrame, from_=('longitude', 'latitude'), epsg=4326) -> geopandas.GeoDataFrame:
	"""Extend the input DataFrame to allow spatial operations.

	Args:
		data (DataFrame): table to convert
		from_ (tuple, optional): columns where to find longitude and latitude respectively. Defaults to ('longitude', 'latitude').
		epsg (int, optional): coordinate system. Defaults to 4326 (WGS84).

	Returns:
		GeoDataFrame object.
	"""
	return geopandas.GeoDataFrame(
		data, geometry=geopandas.points_from_xy(x=data.get(from_[0]), y=data.get(from_[1]))
	).set_crs(epsg=epsg)

def select(data, enum, on=None):
	""" Return an array built from values retrieved in a dictionary depending on their corresponding keys (conditions) drawn from a DataFrame column. 
	"""
	conditions = []
	choices    = []

	v = None 

	if isinstance(data, list):
		v = data
	elif isinstance(data, numpy.ndarray):
		v = data
	elif is_dataframe(data):
		if on is not None:
			if on in data.columns:
				v = data[on]

	if v is None:
		raise ValueError("Oops! Something went wrong.")

	for key in enum.keys():
		conditions.append(v == key)
		choices.append(enum[key])

	return numpy.select(conditions, choices, default=numpy.nan)

#------------------------------------------------------------------------------
# I/O
#------------------------------------------------------------------------------

def ospathextension(filename):
	"""Extract the extension from a filename.
	"""
	return os.path.splitext(filename)[1]

def ospathfilename(filename):
	"""Extract the name from a filename without extension.
	"""
	return os.path.splitext(filename)[0]

def ospathjoin(pathname, filename):
	"""Join a path and a filename.
	"""
	if pathname is not None:
		return os.path.join(pathname, filename)
	else:
		return filename	

def make_directory(path, folder=None):
	"""Create a directory.
	"""
	if folder is not None:
		if not isinstance(folder, str):
			folder = str(folder)
		path = os.path.join(path, folder)
	if not os.path.exists(path):
		os.mkdir(path)	

	return path

def is_tsp_file(filename):
	"""Return True if .TSP file. 
	"""
	if isinstance(filename, str):
		return filename.lower().endswith('.tsp')
	else:
		return False

def is_vrp_file(filename):
	"""Return True if .VRP file.
	"""
	if isinstance(filename, str):
		return filename.lower().endswith('.vrp')
	else:
		return False

def is_csv_file(filename):
	"""Return True if .CSV file.
	"""
	if isinstance(filename, str):
		return filename.lower().endswith('.csv')
	else:
		return False

def is_json(filename):
	"""Return True if .json file.
	"""
	if isinstance(filename, str):
		return filename.lower().endswith('.json')
	else:
		return False

def read_dataframe(filename, pathname=None, columns=None, encoding='utf-8', delimiter=';', decode=False, index=None):
	"""Read a comma-separated values (csv) file into DataFrame.
	"""
	full_filename = ospathjoin(pathname, filename)
	if decode:
		full_filename = codecs.open(full_filename, 'rU','utf-16')

	if columns is not None:
		dataframe = pandas.read_csv(
			full_filename, 
			encoding=encoding, 
			delimiter=delimiter, 
			usecols=columns
		)
	else:
		dataframe = pandas.read_csv(
			full_filename, 
			encoding=encoding, 
			delimiter=delimiter
		)

	if index is not None:
		dataframe = dataframe.set_index(index, drop=False)

	return dataframe

def to_dataframe(dataframe, filename, pathname=None, encoding='utf-8', delimiter=';', with_index=False, usecols=None):
	"""Write DataFrame to a CSV file.
	"""
	full_filename = ospathjoin(pathname, filename)

	if usecols is not None:
		dataframe.to_csv(
			full_filename, 
			encoding=encoding, 
			sep=delimiter, 
			index=with_index, 
			columns=usecols
		)
	else:
		dataframe.to_csv(
			full_filename, 
			encoding=encoding, 
			sep=delimiter, 
			index=with_index
		)

	return None

def read_pickle(filename, pathname=None, from_=None):
	"""Read a pickle file into DataFrame.
	"""
	obj = None

	if from_ == 'dataframe':
		obj = pandas.read_pickle(ospathjoin(pathname, filename))
	else:
		with open(ospathjoin(pathname, filename), 'rb') as f:
			obj = pickle.load(f)	

	return obj

def to_pickle(obj, filename, pathname=None):
	"""Write obj to a picke file.
	"""
	if is_dataframe(obj):
		obj.to_pickle(ospathjoin(pathname, filename))
	else:
		with open(ospathjoin(pathname, filename), 'wb') as f:
			pickle.dump(obj, f)

	return None

def read_json(filename, pathname=None):
	"""Read a json file into dict.
	"""
	with open(ospathjoin(pathname, filename), "r") as read_file:
		json_dict = json.load(read_file)
	return json_dict

def to_json(json_dict, filename, pathname=None, indent=4):
	"""Write dict to a json file.
	"""
	with open(ospathjoin(pathname, filename), "w") as write_file:
		json.dump(json_dict, write_file, indent=indent)
	return None

def read_csv(filename, pathname=None, delimiter=';'):
	"""Read a comma-separated values (csv) file into a list of dict.

	Args:
		filename (str): File name.
		pathname (str, optional): File path. Defaults to None.
		delimiter(str, optional): Field delimiter for the output file. Defaults to ';'.

	Returns:
		list of dict.
	"""
	data = None

	try:
		with open(ospathjoin(pathname, filename), newline='') as csvfile:
			data = [row for row in csv.DictReader(csvfile, delimiter=';')]
	except IOError:
		print('Oops! I/O error.')	

	return data

def to_csv(data, filename, pathname=None, encoding='utf-8', delimiter=';', with_index=False, usecols=None):
	"""Write data to a comma-separated values (csv) file.

	Args:
		data : list of dict or pandas.DataFrame or geopandas.GeoDataFrame.
		filename (str): File name.
		pathname (str, optional): File path. Defaults to None.
		encoding (str, optional): Encoding to use for UTF when reading/writing. Defaults to 'utf-8'.
		delimiter(str, optional): Field delimiter for the output file. Defaults to ';'.
		with_index (boolean, optional): Write index column if True. Defaults to False.
		usecols (list of str, optional): Columns to write if not None. Defaults to None.
	"""
	if is_dataframe(data):
		to_dataframe(
			data       = data, 
			pathname   = pathname, 
			filename   = filename, 
			encoding   = encoding, 
			delimiter  = delimiter, 
			with_index = with_index, 
			usecols    = usecols
		)

	elif isinstance(data, (list, dict)):
		try:
			with open(ospathjoin(pathname, filename), 'w', newline='') as csvfile:
				writer = csv.DictWriter(
					csvfile, 
					fieldnames=[k for k in data[0].keys()], 
					delimiter=delimiter
				)
				writer.writeheader()
				for row in data:
					writer.writerow(row)
		except IOError:
			print("Oops! Something went wrong.")

#EOF