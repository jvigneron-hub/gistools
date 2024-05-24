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

#EOF