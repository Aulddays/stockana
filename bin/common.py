#!/bin/env python
# -*- coding: utf8 -*-
 

from __future__ import print_function
import sys
import time
import urllib2
import os
import shutil

defua = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0"
def urlget(url, timeout=20, retry=3):
	headers = {"User-Agent": defua}
	req = urllib2.Request(url, headers=headers)
	lasterror = None
	for i in range(retry + 1):
		try:
			html = urllib2.urlopen(req, timeout=timeout).read()
			return html
		except HTTPError as e:
			raise Exception("HTTP %d, %s" % (e.code, url))
		except Exception as e:
			lasterror = e
		time.sleep(5 * (1 << retry))
	raise lasterror

def writefile(name, cont):
	""" write (overwrite) cont to file. first write to a temp file, then rename it """
	filename = os.path.basename(name)
	dirname = os.path.dirname(name)
	if dirname == "":
		dirname = "."
	with open(dirname + "/." + "filename" + ".tmp", "w") as fp:
		fp.write(cont)
	shutil.move(dirname + "/." + "filename" + ".tmp", name)

def readfile(name):
	""" read entire file and return content """
	with open(name) as fp:
		return fp.read()

def eprint(*args, **kwargs):
	print(*args, file=sys.stderr, **kwargs)

if __name__ == "__main__":
    eprint("common.py")

# vim: noexpandtab ts=4 sw=4 sts=4
