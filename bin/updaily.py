#!/bin/env python
# -*- coding: utf8 -*-
 
from __future__ import print_function
import sys
import csv
import StringIO
import operator
import datetime
import shutil
import re
import calendar
import os

import common

def main(argv):
	global now, nowdate
	now = datetime.datetime.now() - datetime.timedelta(1)
	nowdate = now.strftime('%Y%m%d')

	#if uplist():
	#	return -1

	if upindividual():
		return -1

	return 0


def uplist():
	""" update lists """
	# Download and parse new list
	defparam = ['Symbol', 'Name', 'LastSale', 'MarketCap', 'IPOyear', 'Sector', 'industry', 'Summary Quote']
	infos, caps = {}, {}	# infos: symbol=>info, caps: symbol=>MarketCap
	for mkt in ("nasdaq", "nyse"):
		#url = "http://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&exchange=" + mkt + "&render=download"
		#quotes = common.urlget(url, timeout=30)
		#common.writefile("data/" + mkt + ".csv", quotes)
		quotes = common.readfile("data/" + mkt + ".csv")
		reader = csv.reader(StringIO.StringIO(quotes))
		param = reader.next()
		#eprint(param)
		if param[-1] == "":
			del param[-1]
		if param != defparam:
			eprint("WARNING: list format changed", param)
		isym, iname, icap, iyear, isec, iind = (param.index("Symbol"), param.index("Name"), param.index("MarketCap"),
			param.index("IPOyear"), param.index("Sector"), param.index("industry"))
		for rec in reader:
			rec = [r.replace("\t", " ") for r in rec]
			sym, name, cap, year, sec, ind = operator.itemgetter(isym, iname, icap, iyear, isec, iind)(rec)
			#eprint(sym, name, cap, year, sec, ind, sep="\t")
			infos[sym] = [name, year, sec, ind, mkt]
			caps[sym] = cap
	
	# Read in old list
	oinfos = {}
	try:
		with open("data/info") as fp:
			for line in fp:
				line = line.strip(" \r\n")
				parts = line.split("\t")
				if len(parts) != 6:
					eprint("Invalid info", line)
					continue
				oinfos[parts[0]] = parts[1:]
	except IOError:
		pass
	# Compare new to old
	if len(infos) < len(oinfos) and (len(oinfos) - len(infos)) / float(len(oinfos)) > 0.01:
		eprint("ERROR: Total number decreased", len(oinfos), len(infos))
		return -1
	mod = False
	for sym, info in infos.iteritems():
		if sym not in oinfos:
			mod = True
			continue
		if oinfos[sym] != info:
			mod = True
			# Write to hist file
			with open("data/info.hist", "ab") as fp:
				print(nowdate, sym, "\t".join(oinfos[sym]), sep="\t", file=fp)
		del oinfos[sym]
	for sym, info in oinfos.iteritems():	# sym deleted in new
		with open("data/info.hist", "ab") as fp:
			print(nowdate, sym, "\t".join(info), sep="\t", file=fp)
			mod = True
	osym = None
	if mod:	# overwirte info
		with open("data/info.new", "wb") as fp:
			for sym, info in infos.iteritems():
				print(sym, "\t".join(info), sep="\t", file=fp)
		shutil.move("data/info.new", "data/info")

	# Write marketcap
	with open("data/mktcap", "wb") as fp:
		for sym, cap in caps.iteritems():
			print(sym, cap, sep="\t", file=fp)


def upindividual():
	lasttime = common.readfile("data/last", "20000101")
	syms = set()
	caps = {}
	with open("data/info", "rb") as fp:
		for line in fp:
			line = line.strip(" \r\n")
			parts = line.split("\t")
			if len(parts) != 6:
				eprint("Invalid info", line)
				continue
			syms.add(parts[0])
	for sym in syms:
		symc = common.symbolclean(sym)
		data = getdata_yahoo(sym, lasttime, nowdate)
		if data is -1:
			raise Exception("Failed", sym)
		if not os.path.isdir("data/hist/" + symc):
			os.makedirs("data/hist/" + symc)
		common.writefile("data/hist/" + symc + "/" + nowdate, data)
		#sys.exit(0)


cookie = crumb = None
def getdata_yahoo(sym, start, end):
	""" start and end are strings like "20170131", and are both inclusive """
	if cookie is None or crumb is None:
		if getcred_yahoo(sym):
			return -1
	start, end = int(start), int(end)
	starttime = str(calendar.timegm((start / 10000, start % 10000 / 100, start % 100, 0, 0, 0)))
	endtime = str(calendar.timegm((end / 10000, end % 10000 / 100, end % 100, 23, 59, 59)))
	url = "https://query1.finance.yahoo.com/v7/finance/download/" + sym + "?period1=" + starttime + "&period2=" + endtime + "&interval=1d&events=history&crumb="
	headers = {"Cookie": cookie}

	# download data
	#eprint(url)
	html = None
	try:
		html = common.urlget(url + crumb, headers={"Cookie": cookie})
	except:
		pass
	if html is None:	# failed, force update credentials and try again
		if getcred_yahoo(sym, True):
			return -1
		html = common.urlget(url + crumb, headers={"Cookie": cookie})
	if html is None or html == "":
		return -1
	return html


def getcred_yahoo(sym, force=False):
	""" load or get cookie/crumb """
	global cookie, crumb
	if cookie is not None and crumb is not None and not force:
		return
	if not force:	# try to read buffered cred
		try:
			with open("data/yahoocred", "rb") as fp:
				cookie = fp.readline().strip("\r\n")
				crumb = fp.readline().strip("\r\n")
			return
		except IOError:
			cookie = crumb = None
	# no buffered or is force
	html, info = common.urlget("https://finance.yahoo.com/quote/" + sym + "/history", info=True)
	# get cookie
	if "Set-Cookie" not in info:
		eprint("Failed to find cookie")
		return -1
	#eprint(info["Set-Cookie"])
	match = re.search(r"(^|[^a-zA-Z0-9])B=([^; ]+)", info["Set-Cookie"])
	if not match:
		eprint("Failed to extract cookie")
		return -1
	cookie = "B=" + match.group(2)
	# get crumb
	match = re.search(r'CrumbStore":{"crumb":"(.*?)"}', html)
	if not match:
		eprint("Failed to find crumb")
	crumb = match.group(1)
	#eprint(cookie)
	#eprint(crumb)
	# write to buffer
	with open("data/yahoocred", "wb") as fp:
		print(cookie, file=fp)
		print(crumb, file=fp)


def eprint(*args, **kwargs):
	print(*args, file=sys.stderr, **kwargs)


if __name__ == "__main__":
	sys.exit(main(sys.argv))

# vim: noet ts=4 sw=4 sts=4 tw=0
