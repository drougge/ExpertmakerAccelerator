# a few things that differ between python2 and python3

from __future__ import print_function
from __future__ import division

import sys

if sys.version_info[0] == 2:
	PY2 = True
	PY3 = False
	import __builtin__ as builtins
	import cPickle as pickle
	from urllib import quote_plus, unquote_plus, urlencode
	from urllib2 import urlopen, Request, URLError, HTTPError
	from itertools import izip, imap, ifilter
	from Queue import Queue
	from types import NoneType
	str_types = (str, unicode,)
	int_types = (int, long,)
	num_types = (int, float, long,)
	unicode = builtins.unicode
	long = builtins.long
	def iterkeys(d):
		return d.iterkeys()
	def itervalues(d):
		return d.itervalues()
	def iteritems(d):
		return d.iteritems()
	from io import open
else:
	PY2 = False
	PY3 = True
	import builtins
	import pickle
	from urllib.parse import quote_plus, unquote_plus
	from urllib.request import urlopen, Request
	from urllib.error import URLError, HTTPError
	izip = zip
	imap = map
	ifilter = filter
	from queue import Queue
	NoneType = type(None)
	str_types = (str,)
	int_types = (int,)
	num_types = (int, float,)
	unicode = str
	open = builtins.open
	long = int
	def iterkeys(d):
		return iter(d.keys())
	def itervalues(d):
		return iter(d.values())
	def iteritems(d):
		return iter(d.items())
	def urlencode(query):
		from urllib.parse import urlencode
		return urlencode(query).encode('utf-8')

def first_value(d):
	return next(itervalues(d) if isinstance(d, dict) else iter(d))

def uni(s):
	if s is None:
		return None
	if isinstance(s, bytes):
		try:
			return s.decode('utf-8')
		except UnicodeDecodeError:
			return s.decode('iso-8859-1')
	return unicode(s)
