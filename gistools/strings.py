import re
import inspect
import unicodedata 
import jellyfish

from unidecode   import unidecode
from collections import OrderedDict
from difflib     import SequenceMatcher

def is_string(val) -> bool:
	""" Determines whether the passed value is a string. 
	"""
	return isinstance(val, str)

def is_list_of_strings(l) -> bool:
	"""Check if an object is a list of strings.
	"""
	return all(isinstance(s, str) for s in l)

def is_empty(s) -> bool:
	"""Check if string is empty.
	"""
	flag = True

	if s is not None:
		if is_string(s) and len(s) > 0:
			flag = False

	return flag

def to_ascii(s) -> str:
	"""remove non ascii characters in a given string.
	"""
	if not isinstance(s, str):
		s = str(s)

	return ''.join([c for c in s if c.isascii()])

def remove_redundant_whitespaces(s: str) -> str:
	""" Substitute all tabs, newlines and other "whitespace-like" characters then remove any leading and trailing whitespaces.
	"""
	return re.sub('\s+', ' ', s).strip()

def replace_character(s: str) -> str:
	""" Remove accents and other undesirable characters (to be used with string distance functions).
	"""
	character_in  = ['é', 'è', 'ê', 'à', 'ù', 'û', 'ç', 'ô', 'î', 'ï', 'â', '-', '*', '.', '_', '{', '}', '!']
	character_out = ['e', 'e', 'e', 'a', 'u', 'u', 'c', 'o', 'i', 'i', 'a', ' ', ' ', ' ', ' ', '' , '' , '' ]

	s_out = s 
	for i in range (len(character_in)):
		s_out = s_out.replace(character_in[i], character_out[i])

	return s_out

def normalize(string: str) -> str:
	return remove_redundant_whitespaces(remove_keywords(replace_character(string.lower())))

def clean(string: str) -> str:
	"""Do a little bit of data cleaning with the help of Unidecode and Regex.
	Things like casing, extra spaces, quotes and new lines can be ignored.
	"""
	cleaned = unidecode(string)
	cleaned = re.sub('  +', ' ', cleaned)
	cleaned = re.sub('\n' , ' ', cleaned)
	cleaned = cleaned.strip().strip('"').strip("'").lower().strip()
	
	if not cleaned or cleaned == '':
		cleaned = None # If data is missing, indicate that by setting the value to `None`		

	return cleaned

def longest_common_substring(s1: str, s2: str) -> str:
	""" Extract the longest substring from 2 given strings.
	"""
	m = [[0] * (1 + len(s2)) for i in range(1 + len(s1))]
	longest, x_longest = 0, 0
	for x in range(1, 1 + len(s1)):
		for y in range(1, 1 + len(s2)):
			if s1[x - 1] == s2[y - 1]:
				m[x][y] = m[x - 1][y - 1] + 1
				if m[x][y] > longest:
					longest = m[x][y]
					x_longest = x
			else:
				m[x][y] = 0
	result = s1[x_longest - longest: x_longest]

	return remove_redundant_whitespaces(result)

def longest_common_subsequence(a: str, b: str) -> str:
	""" Extract the longest subsequence from 2 given strings.
	"""
	lengths = [[0 for j in range(len(b)+1)] for i in range(len(a)+1)]
	# row 0 and column 0 are initialized to 0 already
	for i, x in enumerate(a):
		for j, y in enumerate(b):
			if x == y:
				lengths[i+1][j+1] = lengths[i][j] + 1
			else:
				lengths[i+1][j+1] = max(lengths[i+1][j], lengths[i][j+1])
	# read the substring out from the matrix
	result = ""
	j = len(b)
	for i in range(1, len(a)+1):
		if lengths[i][j] != lengths[i-1][j]:
			result += a[i-1]

	return remove_redundant_whitespaces(result)

def most_frequent(lst: list) -> str:
	return max(set(lst), key=lst.count)

def longest_match(lst: list) -> str:
	s2 = lst[0]
	m = []

	for i in range(1, len(lst)):
		s1 = s2
		s2 = lst[i]
		match = SequenceMatcher(None, s1, s2).find_longest_match(0, len(s1), 0, len(s2))

		m.append(remove_redundant_whitespaces(s1[match.a: match.a + match.size]))

	if len(m) > 0:
		return most_frequent(m) 
	else:
		return m

def levenshtein_distance(token1: str, token2: str, normalize=True) -> dict:
	""" Compute the levenshtein distance between 2 strings
	"""
	ldist = 0
	ratio = 0

	if (len(token1) > 0) and (len(token2) > 0):
		if (normalize == True):
			s1 = input_text_normalize = unicodedata.normalize('NFKD', token1).encode('ascii', 'ignore')
			s2 = input_text_normalize = unicodedata.normalize('NFKD', token2).encode('ascii', 'ignore')
		else:
			s1 = token1
			s2 = token2
		
		m = len(s1)
		n = len(s2)
		lensum = float(m + n)
		d = []           
		for i in range(m+1):
			d.append([i])        
		del d[0][0]    
		for j in range(n+1):
			d[0].append(j)       
		for j in range(1,n+1):
			for i in range(1,m+1):
				if s1[i-1] == s2[j-1]:
					d[i].insert(j,d[i-1][j-1])           
				else:
					minimum = min(d[i-1][j]+1, d[i][j-1]+1, d[i-1][j-1]+2)         
					d[i].insert(j, minimum)
		ldist = d[-1][-1]
		ratio = (lensum - ldist)/lensum
	
	return {'distance':ldist, 'ratio':ratio}

def remove_character(input_text: str, character: str):
	return re.sub(character,'', input_text.rstrip()).lstrip()
	
def remove_keywords(input_text: str, to_lower=False, keywords=['cedex', 'Cedex', 'CEDEX']) -> str:
	""" Remove some particular keywords in a given string

	Args:
		input_text(string): given string
		to_lower(bool): if True converts all uppercase characters in the given string into lowercase
		keywords(list): list of keywords to remove

	Return:
		cleaned string
	"""

	if to_lower:
		output_text = input_text.lower()
	else:
		output_text = input_text

	if len(input_text) > 1:
		for keyword in keywords:
			if keyword in output_text:
				output_text = re.sub(keyword,'', output_text.rstrip()).lstrip()

	return remove_redundant_whitespaces(output_text)

def match(s1: str, s2: str, metric='jellyfish.match-rating', lcs=False) -> bool:
	flag = False

	if (s1 is not None) and (s2 is not None):
		if lcs == True:
			s3 = longest_common_subsequence(s2, s1)
		else:
			s3 = s1
			
		if metric == 'jellyfish.match-rating':
			flag = jellyfish.match_rating_comparison(s3, s2)

		else:
			print("Oops! Something went wrong in {}.".format(inspect.currentframe().f_code.co_name))

	return flag
		  
def distance(s1: str, s2: str, metric='jellyfish.jaro-winkler', lcs=False) -> dict:
	s3 = None
	r = 0.0
	
	if (s1 != None) and (s2 != None):  
		d = 0
		l = len(s1)+len(s2)
		
		if lcs == True:
			s3 = longest_common_subsequence(s2, s1)
		else:
			s3 = s1
			
		if   metric == 'jellyfish.levenshtein':
			d = jellyfish.levenshtein_distance(s3, s2)
			r = (l-d)/l
		elif metric == 'jellyfish.damerau-levenshtein':
			d = jellyfish.damerau_levenshtein_distance(s3, s2)
			r = (l-d)/l
		elif metric == 'jellyfish.hamming':
			d = jellyfish.hamming_distance(s3, s2)
			r = (l-d)/l
		elif metric == 'jellyfish.jaro':
			r = jellyfish.jaro_similarity(s3, s2)
		elif metric == 'jellyfish.jaro-winkler':
			r = jellyfish.jaro_winkler_similarity(s3, s2)
			
		else:
			raise ValueError("Oops! Something went wrong in {}.".format(inspect.currentframe().f_code.co_name))
			
	return {'label': s1, 'ratio': r}

def similarity(str_left: str, str_right: str, lcs=False) -> float:
	s1 = str_left.lower()
	s1 = replace_character(s1)
	s1 = remove_keywords(s1)
	s1 = s1.strip()

	s2 = str_right.lower()
	s2 = replace_character(s2)
	s2 = remove_keywords(s2)
	s2 = s2.strip()

	if not lcs:
		cf = levenshtein_distance(s1, s2)

	else:
		if len(s1) <= len(s2):
			s3 = longest_common_subsequence(s1, s2)
			cf = levenshtein_distance(s3, s1)
		else:
			s3 = longest_common_subsequence(s2, s1)
			cf = levenshtein_distance(s3, s2)

	return cf['ratio']

def str2list(s: str, sep=' ') -> list:
	if is_string(s):
		return s.replace('[', '').replace(']', '').replace(',', '').replace("'", '').split(sep)
	else:
		return None
		
def build_sequence(record, keys) -> str:
	s = ''
	
	for k, v in record.items():
		if k in keys:
			if v is not None:
				s += ' ' + str(v)
		
	s = clean(s)
	s = replace_character(s)
	s = remove_keywords(s)
		
	return s

def drop_duplicates(record):
	return ' '.join(OrderedDict((item, True) for item in [str(v) for k, v in record.items()]).keys()).strip()

#EOF