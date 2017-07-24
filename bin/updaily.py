#!/bin/env python
# -*- coding: utf8 -*-
 
from __future__ import print_function
import sys
import csv
import StringIO

import common

def main(argv):
	list()
	return 0


def list():
	""" update lists """
	for mkt in ("nasdaq", "nyse"):
		#url = "http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=" + mkt + "&render=download"
		#quotes = common.urlget(url, timeout=30)
		#common.writefile("data/" + mkt + ".csv", quotes)
		quotes = common.readfile("data/" + mkt + ".csv")
		for r in csv.reader(StringIO.StringIO(quotes)):
			#print("\t".join(r))
			#break


def eprint(*args, **kwargs):
	print(*args, file=sys.stderr, **kwargs)


if __name__ == "__main__":
	sys.exit(main(sys.argv))

# vim: noet ts=4 sw=4 sts=4
