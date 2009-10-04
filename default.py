#!/usr/bin/env python
# encoding: utf-8
"""
default.py

Created by Erik Simko on 2009-10-02.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import xbmc
import xbmcgui
import xbmcplugin
import urllib
import re

from lib.BeautifulSoup import BeautifulSoup

# plugin constants
__plugin__ = "Mugasha"
__author__ = "erix"
__url__ = ""
__svn_url__ = ""
__credits__ = "Team XBMC"
__version__ = "0.0.1"

BASE_URL = "http://mugasha.com"
BASE_CURRENT_SOURCE_PATH = os.path.join( xbmc.translatePath( "special://profile/" ), "plugin_data", "music", os.path.basename( os.getcwd() ), "tmp.html" )

def get_params(paramstring):
        param=[]
        if len(paramstring)>=2:
                params=paramstring
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param

def get_byArtist(browse_path):
	"""docstring for get_byArtist"""
	
	usock = urllib.urlopen( BASE_URL+browse_path )
	html = usock.read()
	usock.close()
	soup = BeautifulSoup(html)

def get_sets():
	"""Retrieves the most popular sets from Mugasha"""
#	usock = open(BASE_CURRENT_SOURCE_PATH, "r")
	usock = urllib.urlopen( "http://mugasha.com/browse/sets" )
	html = usock.read()
	usock.close()
	soup = BeautifulSoup(html)
	setsHtml = soup.findAll('div', attrs={"class" : "setTabs set-sel-weekly"})
	sets = []
	for	setHtml in setsHtml:
		anchors = setHtml.findAll('a')
		sets.append({"title":anchors[1].string, "thumb_url":anchors[2].img['src'], "browse_path":anchors[1]['href']})
	return sets

def show_sets(djSets):
	"""Adds the set list to XBMC"""
	for djSet in djSets:
		item = xbmcgui.ListItem(label=djSet["title"], thumbnailImage=djSet["thumb_url"])
		url = sys.argv[0]+"?mode=SetsByArtist"+"&url="+djSet["browse_path"]#+"&name="+djSet["title"]
		xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, item, True, len(djSets))


def get_byArtist(browse_path):
	"""docstring for get_byArtist"""

	usock = urllib.urlopen( BASE_URL+browse_path )
	html = usock.read()
	usock.close()
	# fix the HTML bug in source so that BeautifulSoup would work
	soup = BeautifulSoup(html.replace('title="Myspace"','title="Myspace" '))
	setsHtml = soup('span', "title")

	#ugly hack to remove the extra title element
	setsHtml.pop(0)
	sets = []
	for	setHtml in setsHtml:
		sets.append({"title":setHtml.a['title'], "path":setHtml.a['href']})
	return sets

def show_byArtist(djSets):
	"""Adds the set list to XBMC"""
	for djSet in djSets:
		item = xbmcgui.ListItem(label=djSet["title"])
		url = sys.argv[0]+"?mode=PlaySet"+"&url="+djSet["path"]#+"&name="+djSet["title"]
		xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, item, False, len(djSets))


def get_mp3FileName(path):
	"""docstring for get_mp3FileName"""

	usock = urllib.urlopen(BASE_URL+path)
	html = usock.read()
	usock.close()
	#find the playlist URL
	paths = re.compile("var setURL = '(.+)'").findall(html)
	#parse the playlist
	usock = urllib.urlopen( BASE_URL+urllib.quote(paths[0]+'.xml') )
	playlist = usock.read()
	usock.close()
	soup = BeautifulSoup(playlist)
	location = soup.find('location')	
	return location.string


def playSet(path):
	"""docstring for playSet"""
	xbmc.log( "[PLUGIN] playSet", xbmc.LOGNOTICE )
	playpath = "mp3:"+get_mp3FileName(path)
	xbmc.log( "[PLUGIN] playpath: %s" % playpath, xbmc.LOGNOTICE )	
#	playpath = "mp3:EM-2008-07-19.mp3"
	rtmp_url = "rtmp://mugasha.com:1935/simplevideostreaming"
	item = xbmcgui.ListItem(label="")
	item.setProperty("PlayPath", playpath)
	xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(rtmp_url, item)
	
def main():
	reload(sys); sys.setdefaultencoding('utf-8')
	xbmc.log( "[PLUGIN] '%s: version %s' initialized!" % ( __plugin__, __version__, ), xbmc.LOGNOTICE )
	
	
	
	#
	params = get_params(sys.argv[2])
	mode = "PopularSets"
	try:
		mode = params["mode"]
	except:
		pass
	
	xbmc.log( "[PLUGIN] invoke mode: %s" % mode, xbmc.LOGNOTICE )

	if mode == "PopularSets":
		show_sets(get_sets())
	elif mode == "SetsByArtist":
		xbmc.log( "[PLUGIN] invoke mode: %s" % params["url"], xbmc.LOGNOTICE )
		show_byArtist(get_byArtist(params["url"]))
	elif mode == "PlaySet":
		xbmc.log( "[PLUGIN] invoke mode: %s" % params["url"], xbmc.LOGNOTICE )
		playSet(params["url"])
	
	xbmcplugin.endOfDirectory(int(sys.argv[1]))


if __name__ == '__main__':
	main()

