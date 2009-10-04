#!/usr/bin/env python
# encoding: utf-8
"""
test.py

Created by Erik Simko on 2009-10-03.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""

import sys
import os
from lib.BeautifulSoup import BeautifulSoup
import urllib
#import urllib2
import re

HEADER = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1.1) Gecko/20090715 Firefox/3.5.1'
BASE_URL = "http://mugasha.com"

def get_sets():
	"""Retrieves the most popular sets from Mugasha"""

	usock = open("tmp.html", "r")
#	usock = urllib.urlopen( "http://mugasha.com/browse/sets" )
	html = usock.read()
	usock.close()
	soup = BeautifulSoup(html)
	setsHtml = soup.findAll('div', attrs={"class" : "setTabs set-sel-weekly"})
	sets = []
	for	setHtml in setsHtml:
		anchors = setHtml.findAll('a')
		sets.append({"title":anchors[1].string, "thumb_url":anchors[2].img['src'], "browse_path":anchors[1]['href']})
	return sets
	pass

def add_sets(djSets):
	"""Adds the set list to XBMC"""
	for djSet in djSets:
		#item = xbmcgui.ListItem(label=djSet["title"], thumbnailImage=djSet["thumb_url"])
		#xbmcplugin.addDirectoryItem(int(sys.argv[1]), BASE_URL+djSet["browse_url"], item, True, len(djSets))
		print BASE_URL+djSet["browse_path"]
		print djSet["title"]
		print djSet["thumb_url"]
	pass


def get_mp3FileName(path):
	"""docstring for get_mp3FileName"""

	usock = urllib.urlopen(BASE_URL+path)
	html = usock.read()
	usock.close()
	f = open("swf.html", "r")
	html = f.read()
	f.close()
	#find the playlist URL
	paths = re.compile("var setURL = '(.+)'").findall(html)
	
	#parse the playlist
	print BASE_URL+urllib.quote(paths[0]+'.xml')
	usock = urllib.urlopen( BASE_URL+urllib.quote(paths[0]+'.xml') )
	playlist = usock.read()
	usock.close()
	soup = BeautifulSoup(playlist)
	location = soup.find('location')	
	return location.string
	

def get_byArtist(browse_path):
	"""docstring for get_byArtist"""

	usock = urllib.urlopen( BASE_URL+browse_path )
	html = usock.read()
	usock.close()
	
	# fix the HTML bug in source so that BeautifulSoup would work
	soup = BeautifulSoup(html.replace('title="Myspace"','title="Myspace" '))
	setsHtml = soup('span', "title")
	#print setsHtml
	#ugly hack to remove the extra title element
	setsHtml.pop(0)
	sets = []
	for	setHtml in setsHtml:
		#print setHtml.a['title']
		sets.append({"title":setHtml.a['title'], "path":setHtml.a['href']})
		
	return sets

		
def main():
	#encoding hack
	reload(sys); sys.setdefaultencoding('utf-8')
#	add_sets(get_sets())
#	print get_byArtist("/browse/Essential-Mix")#"/browse/Radio-KUL")#"/browse/Andy-Caldwell-Podcast")
	get_mp3FileName("/Essential-Mix/July-19")	


if __name__ == '__main__':
	main()

