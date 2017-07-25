#!/bin/env python
# -*- coding: utf8 -*-
 

from __future__ import print_function
import sys
import time
import urllib2
import os
import shutil

defua = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0"
def urlget(url, headers={}, timeout=20, retry=3, info=False):
	if "User-Agent" not in headers:
		headers["User-Agent"] = defua
	#eprint(headers)
	req = urllib2.Request(url, headers=headers)
	lasterror = None
	for i in range(retry + 1):
		try:
			response = urllib2.urlopen(req, timeout=timeout)
			html = response.read()
			return html if not info else (html, response.info())
		except urllib2.HTTPError as e:
			raise Exception("HTTP %d, %s" % (e.code, url))
		except StandardError as e:
			lasterror = e
		time.sleep(5 * (1 << retry))
	raise lasterror

def writefile(name, cont):
	""" write (overwrite) cont to file. first write to a temp file, then rename it """
	filename = os.path.basename(name)
	dirname = os.path.dirname(name)
	if dirname == "":
		dirname = "."
	with open(dirname + "/." + filename + ".tmp", "w") as fp:
		fp.write(cont)
	shutil.move(dirname + "/." + filename + ".tmp", name)

def readfile(name, defcont=False):
	""" read entire file and return content """
	try:
		with open(name) as fp:
			return fp.read()
	except:
		if defcont is False:
			raise
		return defcont

def symbolclean(symbol):
	""" convert special chars in symbo into '_' """
	return "".join((c if c.isalnum() else '_') for c in symbol)

def eprint(*args, **kwargs):
	print(*args, file=sys.stderr, **kwargs)

if __name__ == "__main__":
    eprint("common.py")

# vim: noexpandtab ts=4 sw=4 sts=4 tw=0
