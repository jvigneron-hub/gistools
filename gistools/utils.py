"""
Collection of utility functions for working with data in Python.

This module provides a comprehensive set of functions for common data handling tasks in Python, including:
* Type checking for various data structures (lists, dictionaries, DataFrames, GeoDataFrames).
* Data manipulation functions (e.g., removing duplicates, adding values to lists, merging dictionaries, etc.).
* File handling functions (reading and writing CSV, JSON, and pickle files).
* Path manipulation functions (joining path components, creating directories).
* Date/Time functions for converting between different formats.
* Numeric functions for checking numeric types, converting to integers, and formatting float values.
* System utility functions for checking method existence and retrieving class information.

The module aims to be user-friendly and concise, offering convenient solutions for common data operations.

**System utilities**
* `has_method`: Checks if an object has a specific method. 
* `get_class_name`: Retrieves the class name of the given object.
* `get_class_attr`: Retrieves public attributes of a given class.
* `is_colab`: Checks if a notebook is running in Google Colab.
* `get_package_version`: Gets the version of an installed Python package.

**Date/Time**
* `isoformat_as_datetime`: Converts an ISO 8601 formatted string to a datetime object.
* `str2datetime`: Converts a string representing a date and time to a datetime object.
* `datetime2str`: Converts a datetime object to a string representation.
* `str2localdatetime`: Converts a string representing a UTC datetime to a local datetime object.
* `str2timestamp`: Converts a string representing a date and time to a Unix timestamp.
* `utc_to_local`: Converts a UTC datetime object to a local datetime object.
* `str2localtimestamp`: Converts a UTC datetime string to a local timestamp (integer seconds since epoch).
* `str2localdatetime`: Converts a UTC datetime string to a local datetime object.
* `timestamp2str`: Converts a Unix timestamp (integer seconds since epoch) to a string representation.
* `timestamp_utcoffset`: Calculates the UTC offset (in hours) for a given Unix timestamp.
* `timestr2seconds`: Converts a time string in HH:MM:SS format to seconds.
* `timestr2minutes`: Converts a time string in MM:SS format to minutes.
* `seconds2timestr`: Converts a duration in seconds to a time string in the specified format.
* `to_timestr`: Converts a duration in seconds to a time string in HH:MM:SS format.
* `total_seconds`: Calculates the total number of seconds between two datetime strings.
* `format_datetime`: Converts a datetime string from one format to another.
* `is_date`: Checks if a string represents a valid date in the specified format.
* `is_time`: Checks if a string represents a valid time in the specified format.
* `isocalendar`: Returns the ISO calendar tuple (year, week number, weekday) for a given date string.
* `weekday`: Returns the weekday (1-7) for a given date string, where 1 is Monday and 7 is Sunday.
* `weekday_name`: Returns the full name of the weekday for a given date string.

**Numeric**
* `isnan`: Checks if a number is NaN (Not a Number). 
* `is_numeric`: Checks if a given string represents a numeric value.
* `is_integer`: Checks if a number is an integer.
* `is_numeric_and_integer`: Checks if a given argument is both numeric and an integer.
* `is_float`: Checks if a number is a float (floating-point number).
* `is_number_regex`: Checks if a string represents a numeric value using regular expressions.
* `is_number_repl_isdigit`: Checks if a string represents a numeric value using string manipulation.
* `to_int`: Attempts to convert a given element to an integer. 
* `format_float`: Formats a float value to remove trailing zeros and the decimal point if unnecessary.

**Lists**
* `is_list`: Checks if an object is a list-like structure.
* `is_array`: Checks if an object is array-like (has a length attribute).
* `is_in_collection`: Checks if an element is present in a collection.
* `remove_none`: Removes None values from a list.
* `intersection`: Calculates the intersection of two lists.
* `count_common_items`: Calculates the number of items in a list which are present in another list.
* `itemgetter`: Gets a specific item from each element in a list of dictionaries.
* `is_in_list`: Checks if all elements in a list are present in another list or pattern.
* `is_in_list_of_dict`: Checks if a specific value exists for a given key within a list of dictionaries.
* `drop_duplicates`: Removes duplicate elements from a list while preserving order.
* `subfinder`: Finds elements in a list that are present in another list or pattern.
* `split_listoftuples`: Splits a list of tuples into separate lists based on their elements.
* `find_duplicates`: Finds duplicate elements in a list.
* `add_to`: Adds a value to each element in a list.

**Dictionnaries**
* `merge_dicts`: Merges two dictionaries, giving preference to values from dict2 in case of key conflicts.
* `none_dict`: Creates a dictionary with None values for each key in a given list.
* `zero_dict`: Creates a dictionary with value = 0 for each key in a given list.
* `is_empty`: Checks if a dictionary is empty, optionally considering only specific keys.
* `is_set`: Checks if a key exists in a dictionary.
* `is_set_toint`: Checks if a key exists in a dictionary and its value is an integer.
* `is_set_tofloat`: Checks if a key exists in a dictionary and its value is a float.
* `is_set_tostr`: Checks if a key exists in a dictionary and its value is a string.

**Dataframes**
* `is_dataframe`: Checks if an object is a Pandas DataFrame or a GeoDataFrame.
* `get_columns`: Gets a list of column names from a Pandas DataFrame.
* `from_dict`: Creates a Pandas DataFrame from a dictionary, optionally specifying column order.
* `where`: Applies filtering conditions to a Pandas DataFrame based on a given expression.
* `isin`: Filters a DataFrame to keep rows where the specified column's value is in the given list.
* `not_isin`: Filters a DataFrame to keep rows where the specified column's value is not in the given list.
* `join`: Performs a merge operation between two DataFrames.
* `select`: Applies a mapping from an enumeration to a list, NumPy array, or Pandas DataFrame column.
* `reformat_date`: Reformats a date column in a Pandas DataFrame from one format to another.
* `drop_null_columns`: Drops columns from a Pandas DataFrame where all values are null (NaN).

**I/O**
* `ospathextension`: Gets the file extension from a filename.
* `ospathfilename`: Gets the filename (without the extension) from a filepath.
* `ospathjoin`: Joins a pathname and filename, handling potential None values.
* `make_directory`: Creates a directory if it doesn't exist, optionally within a parent directory.
* `is_tsp_file`: Checks if a filename represents a TSP file.
* `is_vrp_file`: Checks if a filename represents a VRP file.
* `is_csv_file`: Checks if a filename represents a CSV file.
* `is_json`: Checks if a filename represents a JSON file.
* `read_dataframe`: Reads a CSV file into a Pandas DataFrame.
* `to_dataframe`: Saves a Pandas DataFrame to a CSV file.
* `read_pickle`: Reads a pickled object from a file, handling DataFrames and general objects.
* `to_pickle`: Saves an object to a pickle file, handling DataFrames and general objects.
* `read_json`: Reads a JSON file into a dictionary.
* `to_json`: Saves a dictionary to a JSON file.
* `read_csv`: Reads a CSV file into a list of dictionaries.
* `to_csv`: Saves data to a CSV file, handling lists of dictionaries, DataFrames, and GeoDataFrames. 
* `get_pathname`: Returns the full pathname, handling Google Drive mounting if necessary and using environment variables for paths. 
"""
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
import pkg_resources

from operator import eq, ne, lt, le, gt, ge
from datetime import datetime, timezone
from pandas.core.frame import DataFrame

#------------------------------------------------------------------------------
# System utilities
#------------------------------------------------------------------------------

def has_method(arg, method):
	"""
	Checks if an object has a callable method with the given name.

	Args:
	- **arg**: The object to check for the method.
	- **method**: The name of the method to look for.

	Returns:
	- **boolean**: True if the object has a method with the given name that is also callable (a function), False otherwise.
		
	This function uses two checks:
	- hasattr(arg, method): Checks if the object has an attribute with the given method name.
	- callable(getattr(arg, method): Checks if the retrieved attribute is actually callable, meaning it's a function. 
	"""
	return hasattr(arg, method) and callable(getattr(arg, method))

def get_class_name(obj):
	"""
	Retrieves the class name of the given object.

	This function takes an object of any type as input and returns the name
	of the class to which it belongs. This can be useful for introspection
	or debugging purposes, where you might need to determine the type
	of an object at runtime.

	Args:
	- **obj (object)**: The object whose class name you want to obtain.

	Returns:
	- **str**: The name of the class to which the object belongs.
	"""	
	return type(obj).__name__

def get_class_attr(classname):
	"""
	Retrieves public attributes of a given class.

	This function takes the name of a class (`classname`) as input and returns
	a list of its public attributes (excluding methods and dunder methods).
	It uses `inspect.getmembers` to introspect the class and filters out
	methods using `inspect.isroutine` and dunder methods (those starting and
	ending with double underscores) using list comprehension.

	Args:
	- **classname (str)**: The name of the class to introspect.

	Returns:
	- **list**: A list of public attributes (strings) of the class.
	"""	
	attributes = inspect.getmembers(classname, lambda x : not(inspect.isroutine(x)))
	return [x for x in attributes if not(x[0].startswith('__') and x[0].endswith('__'))]

def is_colab():
	"""
	This function checks if a notebook is running in Google Colab.

	Returns:
	- **boolean** = True  if the notebook is running in Google Colab, False otherwise.
	"""
	return 'google.colab' in str(get_ipython())

def get_package_version(package_name):
	"""
	Gets the version of an installed Python package.

	Args:
	- **package_name**: The name of the package.

	Returns:
	- **string**: The version of the package as a string, or None if the package is not found.
	"""
	try:
		return pkg_resources.get_distribution(package_name).version
	except pkg_resources.DistributionNotFound:
		return None

#------------------------------------------------------------------------------
# Date/Time
#------------------------------------------------------------------------------

def isoformat_as_datetime(s, format_string='%Y-%m-%dT%H:%M:%SZ'):
	"""
	Converts an ISO 8601 formatted string to a datetime object.

	Args:
	- **s**: The ISO 8601 formatted string to convert.  
	- **format_string**: The format string to use for parsing. Defaults to '%Y-%m-%dT%H:%M:%SZ'.

	Returns:
	- **datetime** object representing the parsed date and time.
	"""
	return datetime.strptime(s, format_string)

def str2datetime(s, format_string='%d/%m/%Y %H:%M:%S'):
	"""
	Converts a string representing a date and time to a datetime object.

	Args:
	- **s**: The string representing the date and time.
	- **format_string**: The format string to use for parsing. Defaults to '%d/%m/%Y %H:%M:%S'.

	Returns:
	- **datetime** object representing the parsed date and time.
	"""
	return datetime.strptime(s, format_string)

def datetime2str(d, format_string='%d/%m/%Y %H:%M:%S'):
	"""
	Converts a datetime object to a string representation.

	Args:
	- **d**: The datetime object to convert.
	- **format_string**: The format string to use for the conversion. Defaults to '%d/%m/%Y %H:%M:%S'.

	Returns:
	- **string** representation of the datetime object in the specified format.
	"""
	return d.strftime(format_string) 

def str2localdatetime(s, format_string='%Y-%m-%dT%H:%M:%S.000Z', timezone='Europe/Paris'):
	"""
	Converts a UTC datetime string to a local datetime object.

	Args:
	- **s**: The string representing the UTC datetime.
	- **format_string**: The format string to use for parsing. Defaults to '%Y-%m-%dT%H:%M:%S.000Z'.
	- **timezone**: The timezone to convert to. Defaults to 'Europe/Paris'.

	Returns:
	- **local datetime** object representing the parsed date and time in the specified timezone.
	"""
	return utc_to_local(datetime.strptime(s, format_string))

def str2timestamp(s, format_string='%d/%m/%Y %H:%M:%S'):
	"""
	Converts a string representing a date and time to a Unix timestamp (integer seconds since epoch).

	Args:
	- **s**: The string representing the date and time.
	- **format_string**: The format string to use for parsing. Defaults to '%d/%m/%Y %H:%M:%S'.

	Returns:
	- **integer** representing the Unix timestamp.
	"""
	return int(math.floor(datetime.timestamp(datetime.strptime(s, format_string))))

def utc_to_local(utc_dt):
	"""
	Converts a UTC datetime object to a local datetime object.

	Args:
		utc_dt: The UTC datetime object to convert.

	Returns:
		A local datetime object representing the same date and time in the local timezone.
	"""
	return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

def str2localtimestamp(s, format_string='%Y-%m-%dT%H:%M:%S.%fZ'):
	"""
	Converts a UTC datetime string to a local timestamp (integer seconds since epoch).

	Args:
	- **s**: The string representing the UTC datetime.
	- **format_string**: The format string to use for parsing. Defaults to '%Y-%m-%dT%H:%M:%S.%fZ'.

	Returns:
	- **integer** representing the local timestamp.
	"""
	utc_offset = utc_to_local(datetime.strptime(s, format_string)).utcoffset().seconds
	return str2timestamp(s, format_string)+utc_offset

def timestamp2str(t, format_string='%d/%m/%Y %H:%M:%S'):
	"""
	Converts a Unix timestamp (integer seconds since epoch) to a string representation.

	Args:
	- **t**: The Unix timestamp (integer).
	- **format_string**: The format string to use for the conversion. Defaults to '%d/%m/%Y %H:%M:%S'.

	Returns:
	- **string** representation of the timestamp in the specified format.
	"""
	return datetime.fromtimestamp(t).strftime(format_string)

def timestamp_utcoffset(t):
	"""
	Calculates the UTC offset (in hours) for a given Unix timestamp.

	Args:
	- **t**: The Unix timestamp (integer seconds since epoch).

	Returns:
	- **integer** representing the UTC offset in hours.	
	"""
	return int((datetime.fromtimestamp(t)-datetime.utcfromtimestamp(t)).total_seconds()/3600)

def timestr2seconds(timestr):
	"""
	Converts a time string in HH:MM:SS format to seconds.

	Args:
	- **timestr**: The time string in HH:MM:SS format.

	Returns:
	- **integer** representing the time in seconds.
	"""
	ftr = [3600,60,1]
	s = sum([a*b for a, b in zip(ftr, [int(i) for i in timestr.split(":")])])

	return s 

def timestr2minutes(timestr):
	"""
	Converts a time string in MM:SS format to minutes.

	Args:
	- **timestr**: The time string in MM:SS format.

	Returns:
	- ** integer** representing the time in minutes.
	"""
	ftr = [60,1]
	m = sum([a*b for a, b in zip(ftr, [int(i) for i in timestr.split(":")])])

	return m

def seconds2timestr(duration, format_string='%H:%M:%S'):
	"""
	Converts a duration in seconds to a time string in the specified format.

	Args:
	- **duration**: The duration in seconds.
	- **format_string**: The format string to use for the conversion. Defaults to '%H:%M:%S'.

	Returns:
	- **string** representing the duration in the specified format.
	"""
	return time.strftime(format_string, time.gmtime(duration))

def to_timestr(seconds):
	"""
	Converts a duration in seconds to a time string in HH:MM:SS format.

	Args:
	- **seconds**: The duration in seconds.

	Returns:
	- **string** representing the duration in HH:MM:SS format.
	"""
	m, s = divmod(seconds, 60) 
	h, m = divmod(m, 60)

	return '{:02d}:{:02d}:{:02d}'.format(h,m,s)	

def total_seconds(start, end, format_string='%d/%m/%Y %H:%M:%S'):
	"""
	Calculates the total number of seconds between two datetime strings.

	Args:
		- **start**: The starting datetime string.
		- **end**: The ending datetime string.
		- **format_string**: The format string to use for parsing the datetime strings. Defaults to '%d/%m/%Y %H:%M:%S'.

	Returns:
		The total number of seconds between the two datetime strings.
	"""
	d1 = datetime.strptime(start, format_string)
	d2 = datetime.strptime(end  , format_string)

	s = (d2-d1).total_seconds()

	return s

def format_datetime(s, format_from='%d/%m/%Y %H:%M:%S', format_to='%Y-%m-%dT%H:%M:%SZ'):
	"""
	Converts a datetime string from one format to another.

	Args:
	- **s**: The datetime string to convert.
	- **format_from**: The format string of the input datetime string. Defaults to '%d/%m/%Y %H:%M:%S'.
	- **format_to**: The format string of the output datetime string. Defaults to '%Y-%m-%dT%H:%M:%SZ'.

	Returns:
	- **string** representing the datetime in the specified output format.
	"""
	return datetime.strptime(s, format_from).strftime(format_to)

def is_date(d, format_string='%d/%m/%Y'):
	"""
	Checks if a string represents a valid date in the specified format.

	Args:
	- **d**: The string to check.
	- **format_string**: The format string to use for parsing the date. Defaults to '%d/%m/%Y'.

	Returns:
	- **boolean** = True if the string represents a valid date, False otherwise.
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
	- **t**: The string to check.
	- **format_string**: The format string to use for parsing the time. Defaults to '%H:%M:%S'.

	Returns:
	- **boolean** = True if the string represents a valid time, False otherwise.
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
	- **s**: The date string to convert.
	- **format_string**: The format string to use for parsing the date. Defaults to '%d/%m/%Y'.

	Returns:
	- **tuple** containing (ISO year, ISO week number, ISO weekday).
	"""
	return str2datetime(s, format_string).isocalendar()

def weekday(s, format_string='%Y-%m-%d'):
	"""
	Returns the weekday (1-7) for a given date string, where 1 is Monday and 7 is Sunday.

	Args:
	- **s**: The date string to convert.
	- **format_string**: The format string to use for parsing the date. Defaults to '%Y-%m-%d'.

	Returns:
	- **integer** representing the weekday (1-7).
	"""
	return str2datetime(s, format_string).weekday()+1

def weekday_name(s, format_string='%Y-%m-%d'):
	"""
	Returns the full name of the weekday for a given date string.

	Args:
	- **s**: The date string to convert.
	- **format_string**: The format string to use for parsing the date. Defaults to '%Y-%m-%d'.

	Returns:
	- **string** representing the full name of the weekday (e.g., "Monday", "Tuesday", ...).
	"""
	d = str2datetime(s, format_string=format_string)
	return d.strftime('%A')

#------------------------------------------------------------------------------
# Numeric
#------------------------------------------------------------------------------

def isnan(number):
	"""
	Checks if a number is NaN (Not a Number). 

	Args:
	- **number**: The number to check.

	Returns:
	- **boolean** = True if the number is NaN, False otherwise.

	Important Note:  
		While this approach works for checking NaN in Python, it's worth noting that 
		math.isnan is a dedicated function provided by the math module for this purpose.
		It's recommended to use math.isnan for more explicit and robust NaN checks.
	"""
	return number != number

def is_numeric(literal):
	"""
	Checks if a given string represents a numeric value.
	Credit: [Rosetta Code](http://www.rosettacode.org/wiki/Determine_if_a_string_is_numeric#Python)

	Args:
	- **literal**: The string to check.

	Returns:
	- **boolean** = True if the string represents a numeric value, False otherwise.
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
	"""
	Checks if a number is an integer.

	Args:
	- **number**: The number to check.

	Returns:
	- **boolean** = True if the number is an integer, False otherwise.
	"""
	try:
		return number == int(number)
	except ValueError:
		return False

def is_numeric_and_integer(arg):
	"""
	Checks if a given argument is both numeric and an integer.

	Args:
	- **arg**: The argument to check.

	Returns:
	- **boolean** = True if the argument is both numeric and an integer, False otherwise.
	"""
	try:
		if is_numeric(arg):
			return is_integer(int(arg))
	except ValueError:
		pass
	
	return False

def is_float(number):
	"""
	Checks if a number is a float (floating-point number).

	Args:
	- **number**: The number to check.

	Returns:
	- **boolean** = True if the number is a float, False otherwise.
	"""
	try:
		return number == float(number)
	except ValueError:
		return False

def is_number_regex(s):
	"""
	Checks if a string represents a numeric value using regular expressions.

	Args:
	- **s**: The string to check.

	Returns:
	- **boolean** = True if the string represents a numeric value, False otherwise.
	"""
	if re.match("^\d+?\.\d+?$", s) is None:
		return s.isdigit()
	return True

def is_number_repl_isdigit(s):
	"""
	Checks if a string represents a numeric value using string manipulation.

	Args:
	- **s**: The string to check.

	Returns:
	- **boolean** = True if the string represents a numeric value, False otherwise.
	"""
	return s.replace('.','',1).isdigit()

def to_int(element):
	"""
	Attempts to convert a given element to an integer. 

	Args:
	- **element**: The element to convert.

	Returns:
	- **integer** representing the element if successful, otherwise NaN.
	"""
	n = math.nan

	try:
		n = int(element)
	except:
		pass

	return n

def format_float(arg, decimals=2):
	"""
	Formats a float value to remove trailing zeros and the decimal point if unnecessary,
	allowing for customization of the number of decimal places.

	Args:
	- **arg**: The float value to format.
	- **decimals**: The number of decimal places to display. Defaults to 2.

	Returns:
	- **string** representation of the float.
	"""
	return f"{arg:.{decimals}f}".rstrip("0").rstrip(".")

#------------------------------------------------------------------------------
# Lists
#------------------------------------------------------------------------------

def is_list(arg):
	"""
	Checks if an object is a list-like structure.  
	Credit: [Python client for Google Maps Platform Services](https://github.com/googlemaps/google-maps-services-python/blob/master/googlemaps/convert.py)

	Args:
	- **arg**: The object to check.

	Returns:
	- **boolean** = True if the object is a list-like structure, False otherwise.

	Notes:  
	This function checks for both `__getitem__` (for indexing) and `__iter__` (for iteration) to cover various list-like objects, 
	including custom classes. It excludes dictionaries (`dict`) and strings (`str`).
	"""
	if isinstance(arg, dict):
		return False
	if isinstance(arg, str):  # Python 3-only, as str has __iter__
		return False

	return (hasattr(arg, "__getitem__") and not hasattr(arg, "strip")) or hasattr(arg, "__iter__")

def is_array(a):
	"""
	Checks if an object is array-like (has a length attribute).

	Args:
	- **a**: The object to check.

	Returns:
	- **boolean** = True if the object is array-like, False otherwise.
	"""
	flag = True

	try:
		len(a)
	except:
		flag = False

	return flag

def is_in_collection(element, collection: iter):
	"""
	Checks if an element is present in a collection.

	Args:
	- **element**: The element to search for.
	- **collection**: An iterable object (list, tuple, set, etc.) to search in.

	Returns:
	- **boolean** = True if the element is found in the collection, False otherwise.
	"""
	return element in collection

def remove_none(l):
	"""
	Removes None values from a list.

	Args:
	- **l**: The list to remove None values from.

	Returns:
	- A new **list** with all None values removed.
	"""
	return list(filter(None.__ne__, l))

def intersection(list1_, list2_):
	"""
	Returns the intersection of two lists (elements present in both lists).

	Args:
	- **list1_**: The first list.
	- **list2_**: The second list.

	Returns:
	- A new **list** containing the elements present in both input lists.
	"""
	return list(set(list1_) & set(list2_))

def count_common_items(list1_, list2_):
	"""
	Calculates the number of items in a list which are present in another list.

	Args:
	- **list1_**: The first list.
	- **list2_**: The second list.

	Returns:
	- **integer** containing the number of common items.
	"""
	count = 0
	for item in list2_:
		if item in list1_:
			count += 1

	return count

def itemgetter(l, key):
	"""
	Gets a specific item from each element in a list of dictionaries.

	Args:
	- **l**: The list of dictionaries.
	- **key**: The key to extract from each dictionary.

	Returns:
	- A new **list** containing the values for the specified key from each dictionary.
	"""
	return list(map(operator.itemgetter(key), l))

def is_in_list(l, pattern):
	"""
	Checks if all elements in a list are present in another list or pattern.

	Args:
	- **l**: The list to check.
	- **pattern**: The list or pattern to check against.

	Returns:
	- **boolean** = True if all elements in `l` are found in `pattern`, False otherwise.
	"""
	return all(x in pattern for x in l)

def is_in_list_of_dict(l, key, value):
	"""
	Checks if a specific value exists for a given key in any dictionary within a list of dictionaries.

	Args:
	- **l**: The list of dictionaries.
	- **key**: The key to search for.
	- **value**: The value to search for.

	Returns:
	- **boolean** = True if the value is found for the specified key in any dictionary, False otherwise.
	"""
	return value in itemgetter(l, key)

def drop_duplicates(l):
	"""
	Removes duplicate elements from a list while preserving order.

	Args:
	- **l**: The list to remove duplicates from.

	Returns:
	- A new **list** with duplicate elements removed, preserving the order of the remaining elements.
	"""
	return list( dict.fromkeys(l))

def subfinder(l, pattern):
	"""
	Finds elements in a list that are present in another list or pattern.

	Args:
	- **l**: The list to search in.
	- **pattern**: The list or pattern to match against.

	Returns:
	- A new **list** containing elements from `l` that are also present in `pattern`.
	"""
	return [x for x in l if x in set(pattern)]

def split_listoftuples(l: list) -> list:
	"""
	Splits a list of tuples into separate lists based on their elements.

	Args:
	- **l**: The list of tuples to split.

	Returns:
	- A new **list** containing separate lists for each element in the original tuples.
	"""
	return list(zip(*l))

def find_duplicates(l: list) -> list:
	"""
	Finds duplicate elements in a list.

	Args:
	- **l**: The list to search for duplicates.

	Returns:
	- A new **list** containing only the duplicate elements.
	"""
	return [item for item, count in collections.Counter(l).items() if count > 1]

def add_to(l, value):
	"""
	Adds a value to each element in a list.

	Args:
	- **l**: The list to modify.
	- **value**: The value to add to each element.

	Returns:
	- A new **list** with the value added to each element.
	"""
	return list(map(lambda x: x+value, l))

#------------------------------------------------------------------------------
# Dictionnaries
#------------------------------------------------------------------------------

def merge_dicts(dict1, dict2):
	"""
	Merges two dictionaries, giving preference to values from dict2 in case of key conflicts.

	Args:
	- **dict1**: The first dictionary.
	- **dict2**: The second dictionary.

	Returns:
	- A new **dictionary** containing all key-value pairs from both input dictionaries,
	with values from dict2 taking precedence in case of overlapping keys.
	"""
	return {**dict1, **dict2}

def none_dict(from_list):
	"""
	Creates a dictionary with None values for each key in a given list.

	Args:
	- **from_list**: The list of keys for the dictionary.

	Returns:
	- A **dictionary** with None values for each key in the input list.
	"""
	return {key: None for key in from_list}

def zero_dict(from_list):
	"""
	Create a empty dictionnary from a list of keywords.

	Args:
	- **from_list**: The list of keys for the dictionary.

	Returns:
	- A **dictionary** with value = 0 for each key in the input list.
	"""
	return {key: 0 for key in from_list}

def is_empty(d: dict, usecols=None) -> bool:
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
	"""
	Checks if a dictionary is empty, optionally considering only specific keys.

	Args:
	- **d**: The dictionary to check.
	- **usecols**: A list of keys to consider for emptiness. If None, checks all keys. Defaults to None.

	Returns:
	- **boolean** with value = True if the dictionary is empty or all specified keys have empty values, False otherwise.

	Raises:
	- **TypeError**: If 'usecols' is not a list of strings.
	"""
	if key in record:
		if record[key] is not None: 
			if isinstance(record[key], str) or isinstance(record[key], list):
				return True
			if not math.isnan(record[key]):
				return True

	return False

def is_set_toint(record, key) -> bool:
	"""
	Checks if a key exists in a dictionary and its value is an integer.

	Args:
	- **record**: The dictionary to check.
	- **key**: The key to check for.

	Returns:
	- **boolean** with value = True if the key exists and its value is an integer, False otherwise.
	"""
	flag = False

	if is_set(record, key):
		if is_integer(record[key]):
			flag = True

	return flag

def is_set_tofloat(record, key) -> bool:
	"""
	Checks if a key exists in a dictionary and its value is a float.

	Args:
	- **record**: The dictionary to check.
	- **key**: The key to check for.

	Returns:
	- **boolean** with value = True if the key exists and its value is a float, False otherwise.
	"""
	flag = False

	if is_set(record, key):
		if is_float(record[key]):
			flag = True

	return flag

def is_set_tostr(record, key) -> bool:
	"""
	Checks if a key exists in a dictionary and its value is a string.

	Args:
	- **record**: The dictionary to check.
	- **key**: The key to check for.

	Returns:
	- **boolean** with value = True if the key exists and its value is a string, False otherwise.
	"""
	flag = False

	if is_set(record, key):
		flag = isinstance(record[key], str)

	return flag

#------------------------------------------------------------------------------
# Dataframes
#------------------------------------------------------------------------------

def is_dataframe(records):
	"""
	Checks if an object is a Pandas DataFrame or a GeoDataFrame.

	Args:
	- **records**: The object to check.

	Returns:
	- **boolean** with value = True if the object is a Pandas DataFrame or a GeoDataFrame, False otherwise.
	"""
	return isinstance(records, pandas.DataFrame) or isinstance(records, geopandas.GeoDataFrame)

def get_columns(df, empty=False):
	"""
	Gets a list of column names from a Pandas DataFrame.

	Args:
	- **df**: The Pandas DataFrame.
	- **empty**: If True, returns only column names that have at least one missing value (NaN). If False, returns all column names. Defaults to False.

	Returns:
	- **list** of column names.
	"""
	s = df.isnull().any()

	return s[s == empty].index.tolist()

def from_dict(d: dict, columns=None) -> DataFrame:
	"""
	Creates a Pandas DataFrame from a dictionary, optionally specifying column order.

	Args:
	- **d**: The dictionary to convert to a DataFrame.
	- **columns**: A list of column names to specify the order of columns in the DataFrame. If None, columns are ordered alphabetically. Defaults to None.

	Returns:
	- **Pandas DataFrame**.
	"""
	df = pandas.DataFrame.from_dict(d)
	if columns is not None:
		df = df.reindex (columns=columns)

	return df

def where(df, expr):
	"""
	Applies filtering conditions to a Pandas DataFrame based on a given expression.

	Args:
	- **df**: The Pandas DataFrame to filter.
	- **expr**: A tuple, list of tuples, or a single tuple defining the filtering criteria:
	- **Single Tuple**: (column_name, operator, value)
	- **List of Tuples**: [(column_name, operator, value), ...]
	- **Tuple of Tuples**: ((column_name, operator, value), ...) 

	Returns:
	- **DataFrame** filtered based on the provided expression.

	Supported Operators:
	- '==', '!=', '>', '<', '>=', '<='
	- 'isin' (for membership in a list)
	- '~isin' (for negation of membership in a list)
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
	"""
	Filters a DataFrame to keep rows where the specified column's value is in the given list.

	Args:
	- **df**: The DataFrame to filter.
	- **key**: The name of the column to check.
	- **values**: The list of values to check against. If a string is provided, it's treated as a single value.

	Returns:
	- **DataFrame** containing only the rows where the column value is in the list.
	"""
	return df[df[key].isin([values] if isinstance(values, str) else values)]

def not_isin(df: DataFrame, key: str, values: list):
	"""
	Filters a DataFrame to keep rows where the specified column's value is NOT in the given list.

	Args:
	- **df**: The DataFrame to filter.
	- **key**: The name of the column to check.
	- **values**: The list of values to check against. If a string is provided, it's treated as a single value.

	Returns:
	- **DataFrame** containing only the rows where the column value is NOT in the list.
	"""
	return df[~df[key].isin([values] if isinstance(values, str) else values)]

def join(left, right, left_on, right_on, how='left', output=None):
	"""
	Performs a merge operation between two DataFrames.

	Args:
	- **left**: The left DataFrame.
	- **right**: The right DataFrame.
	- **left_on**: The column name in the left DataFrame to use for merging.
	- **right_on**: The column name in the right DataFrame to use for merging.
	- **how**: The type of merge to perform ('left', 'right', 'inner', 'outer'). Defaults to 'left'.
	- **output**: The name of the column to extract from the merged DataFrame. If None, returns the entire merged DataFrame. Defaults to None.

	Returns:
	- **DataFrame** or a list containing the specified column from the merged DataFrame.
	"""
	df = pandas.merge(left, right, left_on=left_on, right_on=right_on, how=how)

	if output is not None:
		return df[output].tolist()
	else:
		return df

def select(data, enum, on=None):
	"""
	Applies a mapping from an enumeration to a list, NumPy array, or Pandas DataFrame column.

	Args:
	- **data**: The list, NumPy array, or Pandas DataFrame to apply the mapping to.
	- **enum**: A dictionary representing the mapping from keys to values.
	- **on**: The name of the column in the DataFrame to apply the mapping to. Required if 'data' is a DataFrame.

	Returns:
	- **NumPy** array with the mapped values.

	Raises:
	- **ValueError**: If 'data' is not a valid type or if 'on' is not a valid column in the DataFrame.
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

def reformat_date(df, column, from_='%d/%m/%Y', to_='%Y-%m-%d'):
	"""
	Reformats a date column in a Pandas DataFrame from one format to another.

	Args:
	- **df**: The Pandas DataFrame.
	- **column**: The name of the column containing the dates to reformat.
	- **from_**: The format string of the input date column. Defaults to '%d/%m/%Y'.
	- **to_**: The format string of the output date column. Defaults to '%Y-%m-%d'.

	Returns:
	- **Pandas Series** containing the reformatted dates.
	"""
	df[column] = pandas.to_datetime(df[column], format=from_).dt.strftime(to_)
	
	return df

def drop_null_columns(df, columns=None):
	"""
	Drops columns from a Pandas DataFrame where all values are null (NaN).

	Args:
	- **df**: The Pandas DataFrame to modify.
	- **columns**: A list of column names to consider. If None, all columns are considered. Defaults to None.

	Returns:
	- **DataFrame** with the specified null columns dropped.
	"""
	if columns is None:
		columns_to_drop = list(df.columns)
	else:
		columns_to_drop = columns

	for c in columns_to_drop:
		if df[c].isnull().sum() != len(df):
			columns_to_drop.remove(c)

	return df.drop(columns=columns_to_drop)

#------------------------------------------------------------------------------
# I/O
#------------------------------------------------------------------------------

def ospathextension(filename):
	"""
	Gets the file extension from a filename using the os.path.splitext function.

	Args:
	- **filename**: The filename to extract the extension from.

	Returns:
	- **string** representing the file extension (including the dot), or an empty string if no extension is found.
	"""
	return os.path.splitext(filename)[1]

def ospathfilename(filename):
	"""
	Gets the filename (without the extension) from a filepath using the os.path.splitext function.

	Args:
	- **filename**: The filepath to extract the filename from.

	Returns:
	- **string** representing the filename (without the extension), or the entire filepath if no extension is found.
	"""
	return os.path.splitext(filename)[0]

def ospathjoin(pathname, filename):
	"""
	Joins a pathname and filename, handling potential None values.

	Args:
	- **pathname**: The pathname to join. Can be None if no pathname is required.
	- **filename**: The filename to join.

	Returns:
	- **string** representing the joined path, or the filename itself if pathname is None.
	"""
	if pathname is not None:
		return os.path.join(pathname, filename)
	else:
		return filename	

def make_directory(path, folder=None):
	"""
	Creates a directory if it doesn't exist, optionally within a parent directory.

	Args:
	- **path**: The base path to create the directory in.
	- **folder**: The name of the subdirectory to create. If None, creates the directory at the specified path. Defaults to None.

	Returns:
	- **string** representing the full path to the created directory.
	"""
	if folder is not None:
		if not isinstance(folder, str):
			folder = str(folder)
		path = os.path.join(path, folder)
	if not os.path.exists(path):
		os.mkdir(path)	

	return path

def is_tsp_file(filename):
	"""
	Checks if a filename represents a TSP (Traveling Salesperson Problem) file.

	Args:
	- **filename**: The filename to check.

	Returns:
	- **boolean** with value = True if the filename ends with '.tsp' (case-insensitive), False otherwise.
	"""
	if isinstance(filename, str):
		return filename.lower().endswith('.tsp')
	else:
		return False

def is_vrp_file(filename):
	"""
	Checks if a filename represents a VRP (Vehicle Routing Problem) file.

	Args:
	- **filename**: The filename to check.

	Returns:
	- **boolean** with value = True if the filename ends with '.vrp' (case-insensitive), False otherwise.
	"""
	if isinstance(filename, str):
		return filename.lower().endswith('.vrp')
	else:
		return False

def is_csv_file(filename):
	"""
	Checks if a filename represents a CSV (Comma-Separated Values) file.

	Args:
	- **filename**: The filename to check.

	Returns:
	- **boolean** with value = True if the filename ends with '.csv' (case-insensitive), False otherwise.
	"""
	if isinstance(filename, str):
		return filename.lower().endswith('.csv')
	else:
		return False

def is_json(filename):
	"""
	Checks if a filename represents a JSON (JavaScript Object Notation) file.

	Args:
	- **filename**: The filename to check.

	Returns:
	- **boolean** with value = True if the filename ends with '.json' (case-insensitive), False otherwise.
	"""
	if isinstance(filename, str):
		return filename.lower().endswith('.json')
	else:
		return False

def read_dataframe(filename, pathname=None, columns=None, encoding='utf-8', delimiter=';', decode=False, index=None):
	"""
	Reads a CSV file into a Pandas DataFrame.

	Args:
	- **filename**: The name of the CSV file.
	- **pathname**: The optional pathname of the directory containing the file. Defaults to None.
	- **columns**: A list of column names to read. If None, reads all columns. Defaults to None.
	- **encoding**: The encoding of the CSV file. Defaults to 'utf-8'.
	- **delimiter**: The delimiter used in the CSV file. Defaults to ';'.
	- **decode**: If True, decodes the file using 'utf-16' encoding. Defaults to False.
	- **index**: The name of the column to use as the index. If None, no index is set. Defaults to None.

	Returns:
	- **Pandas DataFrame** containing the data from the CSV file.
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
	"""
	Saves a Pandas DataFrame to a CSV file.

	Args:
	- **dataframe**: The Pandas DataFrame to save.
	- **filename**: The name of the CSV file to save.
	- **pathname**: The optional pathname of the directory to save the file in. Defaults to None.
	- **encoding**: The encoding to use for the CSV file. Defaults to 'utf-8'.
	- **delimiter**: The delimiter to use in the CSV file. Defaults to ';'.
	- **with_index**: If True, includes the index in the CSV file. Defaults to False.
	- **usecols**: A list of column names to save. If None, saves all columns. Defaults to None.

	Returns:
	- **None**.
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
	"""
	Reads a pickled object from a file, handling DataFrames and general objects.

	Args:
	- **filename**: The name of the pickled file.
	- **pathname**: The optional pathname of the directory containing the file. Defaults to None.
	- **from_**: If 'dataframe', assumes the file contains a pickled DataFrame. Otherwise, reads as a general pickled object. Defaults to None.

	Returns:
	- The loaded object (DataFrame or general object).
	"""
	obj = None

	if from_ == 'dataframe':
		obj = pandas.read_pickle(ospathjoin(pathname, filename))
	else:
		with open(ospathjoin(pathname, filename), 'rb') as f:
			obj = pickle.load(f)	

	return obj

def to_pickle(obj, filename, pathname=None):
	"""
	Saves an object to a pickle file, handling DataFrames and general objects.

	Args:
	- **obj**: The object to save. Can be a Pandas DataFrame or any other picklable object.
	- **filename**: The name of the pickle file to save.
	- **pathname**: The optional pathname of the directory to save the file in. Defaults to None.

	Returns:
	- **None**.
	"""
	if is_dataframe(obj):
		obj.to_pickle(ospathjoin(pathname, filename))
	else:
		with open(ospathjoin(pathname, filename), 'wb') as f:
			pickle.dump(obj, f)

	return None

def read_json(filename, pathname=None):
	"""
	Reads a JSON file into a dictionary.

	Args:
	- **filename**: The name of the JSON file.
	- **pathname**: The optional pathname of the directory containing the file. Defaults to None.

	Returns:
	- **dictionary** containing the data from the JSON file.
	"""
	with open(ospathjoin(pathname, filename), "r") as read_file:
		json_dict = json.load(read_file)
	return json_dict

def to_json(json_dict, filename, pathname=None, indent=4):
	"""
	Saves a dictionary to a JSON file.

	Args:
	- **json_dict**: The dictionary to save as JSON.
	- **filename**: The name of the JSON file to save.
	- **pathname**: The optional pathname of the directory to save the file in. Defaults to None.
	- **indent**: The number of spaces to use for indentation in the output JSON. Defaults to 4.

	Returns:
	- **None**.
	"""
	with open(ospathjoin(pathname, filename), "w") as write_file:
		json.dump(json_dict, write_file, indent=indent)
	return None

def read_csv(filename, pathname=None, delimiter=';'):
	"""
	Reads a CSV file into a list of dictionaries.

	Args:
	- **filename**: The name of the CSV file.
	- **pathname**: The optional pathname of the directory containing the file. Defaults to None.
	- **delimiter**: The delimiter used in the CSV file. Defaults to ';'.

	Returns:
	- **list** of dictionaries, where each dictionary represents a row in the CSV file. The keys of the dictionaries are the column names from the CSV file.
	"""
	data = None

	try:
		with open(ospathjoin(pathname, filename), newline='') as csvfile:
			data = [row for row in csv.DictReader(csvfile, delimiter=';')]
	except IOError:
		print('Oops! Something went wrong.')	

	return data

def to_csv(data, filename, pathname=None, encoding='utf-8', delimiter=';', with_index=False, usecols=None):
	"""
	Saves data to a CSV file, handling lists of dictionaries, DataFrames, and GeoDataFrames.

	Args:
	- **data**: The data to save. Can be a list of dictionaries, a Pandas DataFrame, or a GeoDataFrame.
	- **filename**: The name of the CSV file to save.
	- **pathname**: The optional pathname of the directory to save the file in. Defaults to None.
	- **encoding**: The encoding to use for the CSV file. Defaults to 'utf-8'.
	- **delimiter**: The delimiter to use in the CSV file. Defaults to ';'.
	- **with_index**: If True, includes the index in the CSV file. Defaults to False.
	- **usecols**: A list of column names to save. If None, saves all columns. Defaults to None.

	Returns:
	- **None**.
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

def get_pathname(google_drive, folder=None):
	"""
	Returns the full pathname, handling Google Drive mounting if necessary and using environment variables for paths.

	Args:
		- **google_drive**: A boolean flag indicating whether to mount Google Drive.
		- **folder**: An optional subfolder name to append to the pathname. Defaults to None.

	Returns:
		- **string** containing  the full pathname, including the mounted Google Drive root (if `google_drive` is True) and the specified subfolder (if `folder` is provided).
	"""
	if not google_drive:
		pathname = os.environ.get('LOCAL_DATASET')

	else:
		from google.colab import drive

		root = '/content/drive'
		drive.mount('{}'.format(root), force_remount=True)
		pathname = '{}/{}'.format(root, os.environ.get('DRIVE_DATASET'))

	if folder is not None:
		pathname = '{}/{}'.format(pathname, folder)

	return pathname

#EOF