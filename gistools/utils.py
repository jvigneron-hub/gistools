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
		is_time('12:34:56') # True
		is_time('12:34:56 AM') # False (because it includes AM/PM)
		is_time('12:34:56.123') # True (allows milliseconds)
		is_time('12:34') # False (missing seconds)
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
	"""
	Checks if a number is NaN (Not a Number). 

	Args:
		number: The number to check.

	Returns:
		True if the number is NaN, False otherwise.

	Example:
		isnan(float('nan'))  # True
		isnan(1.0)         # False
		isnan(None)        # False (None is not a number)

	Important Note: 
		While this approach works for checking NaN in Python, it's worth noting that 
		math.isnan is a dedicated function provided by the math module for this purpose. 
		It's recommended to use math.isnan for more explicit and robust NaN checks.
	"""
	return number != number

def is_numeric(literal):
	"""
	Checks if a given string represents a numeric value.
	Credits: http://www.rosettacode.org/wiki/Determine_if_a_string_is_numeric#Python

	Args:
		literal: The string to check.

	Returns:
		True if the string represents a numeric value, False otherwise.

	Example:
		is_numeric("123")     # True (integer)
		is_numeric("12.34")   # True (float)
		is_numeric("1.23e+5") # True (scientific notation)
		is_numeric("0x1A")    # True (hexadecimal)
		is_numeric("0b101")   # True (binary)
		is_numeric("0o123")   # True (octal)
		is_numeric("abc")     # False
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
		number: The number to check.

	Returns:
		True if the number is an integer, False otherwise.

	Example:
		is_integer(10)   # True
		is_integer(10.5) # False
		is_integer("10") # False (string)
		is_integer(10.0) # True (float with no decimal part)
	"""
	try:
		return number == int(number)
	except ValueError:
		return False

def is_numeric_and_integer(arg):
	"""
	Checks if a given argument is both numeric and an integer.

	Args:
		arg: The argument to check.

	Returns:
		True if the argument is both numeric and an integer, False otherwise.

	Example:
		is_numeric_and_integer("123")  # True
		is_numeric_and_integer("12.3") # False (numeric but not an integer)
		is_numeric_and_integer("abc")  # False (not numeric)
		is_numeric_and_integer(123)    # True
		is_numeric_and_integer(12.3)   # False
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
		number: The number to check.

	Returns:
		True if the number is a float, False otherwise.

	Example:
		is_float(10.5)     # True
		is_float(10)       # True (integer can be represented as a float)
		is_float("10.5")   # False (string)
	"""
	try:
		return number == float(number)
	except ValueError:
		return False

def is_number_regex(s):
	"""
	Checks if a string represents a numeric value using regular expressions.

	Args:
		s: The string to check.

	Returns:
		True if the string represents a numeric value, False otherwise.

	Example:
		is_number_regex("123")      # True (integer)
		is_number_regex("12.34")    # True (float)
		is_number_regex("1.23e+5")  # False (scientific notation not handled)
		is_number_regex("0x1A")     # False (hexadecimal not handled)
		is_number_regex("0b101")    # False (binary not handled)
		is_number_regex("0o123")    # False (octal not handled)
		is_number_regex("abc")      # False
	"""
	if re.match("^\d+?\.\d+?$", s) is None:
		return s.isdigit()
	return True

def is_number_repl_isdigit(s):
	"""
	Checks if a string represents a numeric value using string manipulation.

	Args:
		s: The string to check.

	Returns:
		True if the string represents a numeric value, False otherwise.

	Example:
		is_number_repl_isdigit("123")   # True (integer)
		is_number_repl_isdigit("12.34") # True (float)
		is_number_regex("1.23e+5")      # False (scientific notation not handled)
		is_number_regex("0x1A")         # False (hexadecimal not handled)
		is_number_regex("0b101")        # False (binary not handled)
		is_number_regex("0o123")        # False (octal not handled)
		is_number_regex("abc")          # False
	"""
	return s.replace('.','',1).isdigit()

def to_int(element):
	"""
	Attempts to convert a given element to an integer. 

	Args:
		element: The element to convert.

	Returns:
		The integer representation of the element if successful, otherwise NaN.

	Example:
		to_int("123")  # 123
		to_int("12.3") # NaN
		to_int("abc")  # NaN
		to_int(123)    # 123
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
		arg: The float value to format.
		decimals: The number of decimal places to display. Defaults to 2.

	Returns:
		The formatted string representation of the float.

	Example:
		format_float(12.3456) # "12.35"
		format_float(12.0) # "12"
		format_float(12.000) # "12"
		format_float(12.3456, decimals=3) # "12.346"
		format_float(12.3456, decimals=0) # "12"
	"""
	return f"{arg:.{decimals}f}".rstrip("0").rstrip(".")

#------------------------------------------------------------------------------
# Lists
#------------------------------------------------------------------------------

def is_list(arg):
	"""
	Checks if an object is a list-like structure.

	Args:
		arg: The object to check.

	Returns:
		True if the object is a list-like structure, False otherwise.

	Notes:
		- This function checks for both `__getitem__` (for indexing) and `__iter__` (for iteration)
		  to cover various list-like objects, including custom classes.
		- It excludes dictionaries (`dict`) and strings (`str`).

	Credits:
		https://github.com/googlemaps/google-maps-services-python/blob/master/googlemaps/convert.py
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
		a: The object to check.

	Returns:
		True if the object is array-like, False otherwise.
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
		element: The element to search for.
		collection: An iterable object (list, tuple, set, etc.) to search in.

	Returns:
		True if the element is found in the collection, False otherwise.

	Example:
		is_in_collection(3, [1, 2, 3, 4])  # True
		is_in_collection('a', {'a', 'b', 'c'})  # True
		is_in_collection(5, [1, 2, 3, 4])  # False
	"""
	return element in collection

def remove_none(l):
	"""
	Removes None values from a list.

	Args:
		l: The list to remove None values from.

	Returns:
		A new list with all None values removed.

	Example:
		remove_none([1, None, 2, None, 3]) # Output: [1, 2, 3]
	"""
	return list(filter(None.__ne__, l))

def intersection(list1_, list2_):
	"""
	Returns the intersection of two lists (elements present in both lists).

	Args:
		list1_: The first list.
		list2_: The second list.

	Returns:
		A new list containing the elements present in both input lists.

	Example:
		intersection([1, 2, 3, 4], [3, 4, 5, 6]) # Output: [3, 4]
	"""
	return list(set(list1_) & set(list2_))

def itemgetter(l, key):
	"""
	Gets a specific item from each element in a list of dictionaries.

	Args:
		l: The list of dictionaries.
		key: The key to extract from each dictionary.

	Returns:
		A new list containing the values for the specified key from each dictionary.

	Example:
		itemgetter([{'a': 1, 'b': 2}, {'a': 3, 'b': 4}], 'a') # Output: [1, 3]
	"""
	return list(map(operator.itemgetter(key), l))

def is_in_list(l, pattern):
	"""
	Checks if all elements in a list are present in another list or pattern.

	Args:
		l: The list to check.
		pattern: The list or pattern to check against.

	Returns:
		True if all elements in `l` are found in `pattern`, False otherwise.

	Example:
		is_in_list([1, 2, 3], [1, 2, 3, 4, 5])  # True
		is_in_list([1, 2, 3], [1, 2, 4, 5])  # False
		is_in_list(['a', 'b', 'c'], 'abcdefg')  # True (pattern can be a string)
	"""
	return all(x in pattern for x in l)

def is_in_list_of_dict(l, key, value):
	"""
	Checks if a specific value exists for a given key in any dictionary within a list of dictionaries.

	Args:
		l: The list of dictionaries.
		key: The key to search for.
		value: The value to search for.

	Returns:
		True if the value is found for the specified key in any dictionary, False otherwise.

	Example:
		is_in_list_of_dict([{'a': 1, 'b': 2}, {'a': 3, 'b': 4}], 'a', 3) # True
		is_in_list_of_dict([{'a': 1, 'b': 2}, {'a': 3, 'b': 4}], 'a', 5) # False
	"""
	return value in itemgetter(l, key)

def drop_duplicates(l):
	"""
	Removes duplicate elements from a list while preserving order.

	Args:
		l: The list to remove duplicates from.

	Returns:
		A new list with duplicate elements removed, preserving the order of the remaining elements.

	Example:
		drop_duplicates([1, 2, 2, 3, 1, 4]) # Output: [1, 2, 3, 4]
	"""
	return list( dict.fromkeys(l))

def subfinder(l, pattern):
	"""
	Finds elements in a list that are present in another list or pattern.

	Args:
		l: The list to search in.
		pattern: The list or pattern to match against.

	Returns:
		A new list containing elements from `l` that are also present in `pattern`.

	Example:
		subfinder([1, 2, 3, 4, 5], [2, 4, 6]) # Output: [2, 4]
	"""
	return [x for x in l if x in set(pattern)]

def split_listoftuples(l: list) -> list:
	"""
	Splits a list of tuples into separate lists based on their elements.

	Args:
		l: The list of tuples to split.

	Returns:
		A new list containing separate lists for each element in the original tuples.

	Example:
		split_listoftuples([(1, 2), (3, 4), (5, 6)]) # Output: [[1, 3, 5], [2, 4, 6]]
	"""
	return list(zip(*l))

def find_duplicates(l: list) -> list:
	"""
	Finds duplicate elements in a list.

	Args:
		l: The list to search for duplicates.

	Returns:
		A new list containing only the duplicate elements.

	Example:
		find_duplicates([1, 2, 2, 3, 1, 4]) # Output: [1, 2]
	"""
	return [item for item, count in collections.Counter(l).items() if count > 1]

def add_to(l, value):
	"""
	Adds a value to each element in a list.

	Args:
		l: The list to modify.
		value: The value to add to each element.

	Returns:
		A new list with the value added to each element.

	Example:
		add_to([1, 2, 3], 5) # Output: [6, 7, 8]
	"""
	return list(map(lambda x: x+value, l))

#------------------------------------------------------------------------------
# Dictionnaries
#------------------------------------------------------------------------------

def merge_dicts(dict1, dict2):
	return {**dict1, **dict2}

def none_dict(from_list):
	return {key: None for key in from_list}

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
	if key in record:
		if record[key] is not None: 
			if isinstance(record[key], str) or isinstance(record[key], list):
				return True
			if not math.isnan(record[key]):
				return True

	return False

def is_set_toint(record, key) -> bool:
	flag = False

	if is_set(record, key):
		if is_integer(record[key]):
			flag = True

	return flag

def is_set_tofloat(record, key) -> bool:
	flag = False

	if is_set(record, key):
		if is_float(record[key]):
			flag = True

	return flag

def is_set_tostr(record, key) -> bool:
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
	df = pandas.DataFrame.from_dict(d)
	if columns is not None:
		df = df.reindex (columns=columns)

	return df

def where(df, expr):
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
	df = pandas.merge(left, right, left_on=left_on, right_on=right_on, how=how)

	if output is not None:
		return df[output].tolist()
	else:
		return df

def to_geo(data: DataFrame, from_=('longitude', 'latitude'), epsg=4326) -> geopandas.GeoDataFrame:
	return geopandas.GeoDataFrame(
		data, geometry=geopandas.points_from_xy(x=data.get(from_[0]), y=data.get(from_[1]))
	).set_crs(epsg=epsg)

def select(data, enum, on=None):
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
	return os.path.splitext(filename)[1]

def ospathfilename(filename):
	return os.path.splitext(filename)[0]

def ospathjoin(pathname, filename):
	if pathname is not None:
		return os.path.join(pathname, filename)
	else:
		return filename	

def make_directory(path, folder=None):
	if folder is not None:
		if not isinstance(folder, str):
			folder = str(folder)
		path = os.path.join(path, folder)
	if not os.path.exists(path):
		os.mkdir(path)	

	return path

def is_tsp_file(filename):
	if isinstance(filename, str):
		return filename.lower().endswith('.tsp')
	else:
		return False

def is_vrp_file(filename):
	if isinstance(filename, str):
		return filename.lower().endswith('.vrp')
	else:
		return False

def is_csv_file(filename):
	if isinstance(filename, str):
		return filename.lower().endswith('.csv')
	else:
		return False

def is_json(filename):
	if isinstance(filename, str):
		return filename.lower().endswith('.json')
	else:
		return False

def read_dataframe(filename, pathname=None, columns=None, encoding='utf-8', delimiter=';', decode=False, index=None):
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
	obj = None

	if from_ == 'dataframe':
		obj = pandas.read_pickle(ospathjoin(pathname, filename))
	else:
		with open(ospathjoin(pathname, filename), 'rb') as f:
			obj = pickle.load(f)	

	return obj

def to_pickle(obj, filename, pathname=None):
	if is_dataframe(obj):
		obj.to_pickle(ospathjoin(pathname, filename))
	else:
		with open(ospathjoin(pathname, filename), 'wb') as f:
			pickle.dump(obj, f)

	return None

def read_json(filename, pathname=None):
	with open(ospathjoin(pathname, filename), "r") as read_file:
		json_dict = json.load(read_file)
	return json_dict

def to_json(json_dict, filename, pathname=None, indent=4):
	with open(ospathjoin(pathname, filename), "w") as write_file:
		json.dump(json_dict, write_file, indent=indent)
	return None

def read_csv(filename, pathname=None, delimiter=';'):
	data = None

	try:
		with open(ospathjoin(pathname, filename), newline='') as csvfile:
			data = [row for row in csv.DictReader(csvfile, delimiter=';')]
	except IOError:
		print('Oops! I/O error.')	

	return data

def to_csv(data, filename, pathname=None, encoding='utf-8', delimiter=';', with_index=False, usecols=None):
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