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
import lib.demjson as demjson

from xml.sax.saxutils import unescape
from lib.BeautifulSoup import BeautifulSoup

# plugin constants
__plugin__ = "Mugasha"
__author__ = "erix"
__url__ = ""
__svn_url__ = ""
__credits__ = "Team XBMC"
__version__ = "0.0.1"

BASE_URL = "http://mugasha.com"
#BASE_CURRENT_SOURCE_PATH = os.path.join( xbmc.translatePath( "special://profile/" ), "plugin_data", "music", os.path.basename( os.getcwd() ), "tmp.html" )
RTMP_URL = "rtmp://mugasha.com:1935/simplevideostreaming"

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

def retrieve_url(url):
	""" Fetches the HTML from given URL.
		Return empty string if failed
	"""
	try:
		usock = urllib.urlopen( url )
		html = usock.read()
		usock.close()
	except:
		html = ""
		
	return html


def get_sets():
	"""Retrieves the most popular sets from Mugasha"""
#	usock = open(BASE_CURRENT_SOURCE_PATH, "r")
	
	html = retrieve_url(BASE_URL+"/browse/sets")
	soup = BeautifulSoup(html)
	setsHtml = soup.findAll('div', attrs={"class" : "setTabs set-sel-weekly"})
	sets = []
	for	setHtml in setsHtml:
		anchors = setHtml.findAll('a')
		sets.append({"title":anchors[1].string, "thumb_url":anchors[2].img['src'], "browse_path":anchors[1]['href']})
	return sets


def get_byArtist(browse_path):
	"""Fetches the sets by artist"""

	html = retrieve_url( BASE_URL+browse_path )
	# fix the HTML bug in source so that BeautifulSoup would work
	soup = BeautifulSoup(html.replace('title="Myspace"','title="Myspace" '))
	setsHtml = soup('span', "title")

	#ugly hack to remove the extra title element
	setsHtml.pop(0)
	sets = []
	for	setHtml in setsHtml:
		sets.append({"title":setHtml.a['title'], "path":setHtml.a['href']})
	return sets

def get_asset_path(path):
	"""docstring for get_asset_path"""
	html = retrieve_url(BASE_URL+path)
	#find the playlist URL
	paths = re.compile("var setURL = '(.+)'").findall(html)
	return urllib.quote(paths[0])


def get_playlist(path):
	"""Fetches the playlist for a DJ set"""


	#parse the playlist
	playlistXml = retrieve_url(BASE_URL+get_asset_path(path)+'.xml')
	soup = BeautifulSoup(playlistXml)
	tracks = soup.findAll('track')
	playlist = []
	for track in tracks :
		playlist.append({"title":unescape(track.title.string), "artist":unescape(track.creator.string), "file":track.location.string, "start":track.meta.nextSibling})
	return playlist

def get_trackInfos(path):
	"""docstring for get_trackInfos
		[
			{
			u'track': 
				{
				u'dj_set_id': 296, 
			 	u'short_link': 
			 	u'http://bit.ly/2kBCpb', 
			 	u'artist': 
					{
					u'large': u'http://userserve-ak.last.fm/serve/252/192768.jpg',
					u'name': u'Essential Mix',
					u'id': 1896
					},
				u'created_at': u'2009-01-12T22:34:59Z',
				u'trackEndTime': 152,
				u'updated_at': u'2009-08-26T08:05:14Z',
				u'trackTitle': u'Intro',
				u'plays_count': 108,
				u'likes': 0,
				u'buylink_stamp': u'2009-07-20T05:04:06Z',
				u'trackNumber': 1,
				u'trackStartTime': 0,
				u'artist_id': 1896,
				u'id': 4932
				}
			}
		]
	"""
	tracksJson = retrieve_url(BASE_URL + get_asset_path(path) +'.json')
	tracks = demjson.decode(tracksJson)
	return tracks

def show_sets(djSets):
	"""Adds the set list to XBMC"""
	for djSet in djSets:
		item = xbmcgui.ListItem(label=unescape(djSet["title"]), thumbnailImage=djSet["thumb_url"])
		labels ={"title" : unescape(djSet["title"])}
		item.setInfo(type = 'music', infoLabels=labels)
		url = sys.argv[0]+"?mode=SetsByArtist"+"&url="+djSet["browse_path"]#+"&name="+djSet["title"]
		xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, item, True, len(djSets))

def show_byArtist(djSets):
	"""Adds the set by artist list to XBMC"""
	for djSet in djSets:
		item = xbmcgui.ListItem(label=unescape(djSet["title"]))
		labels ={"title" : unescape(djSet["title"])}
		item.setInfo(type = 'music', infoLabels=labels)
		url = sys.argv[0]+"?mode=ShowSet"+"&url="+djSet["path"]#+"&name="+djSet["title"]
		if  not xbmcplugin.addDirectoryItem(int(sys.argv[1]), url, item, True, len(djSets)): break

def show_set(path):
	"""docstring for show_set"""
	tracks = get_trackInfos(path)
	playlist = get_playlist(path)
	i = 0
	for track in tracks:
		playpath = "mp3:"+playlist[i]["file"]
		
		# No way to add different thums for the items because the item URL is the same
		# so XBMC will use the same cached thumbnail for each item
		item = xbmcgui.ListItem()
			#label=track["track"]["trackTitle"])
			#label2=track["track"]["trackTitle"])		
		
		labels={
            "artist": track["track"]["artist"]["name"],
            "title": track["track"]["trackTitle"],
			"duration": track["track"]["trackEndTime"]}

		item.setProperty("Start", playlist[i]["start"])
		item.setProperty("PlayPath", playpath)
		i = i+1

		item.setInfo(type = 'music', infoLabels=labels)
		if not xbmcplugin.addDirectoryItem(int(sys.argv[1]), RTMP_URL, item, False, len(tracks)): break
	

def playSet(path):
	"""Creates an XBMC playlist and plays"""
	xbmcplaylist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
	xbmcplaylist.clear()
	
	playlist = get_playlist(path)
	
	for track in playlist:
		playpath = "mp3:"+track["file"]+"?start="+track["start"]
		item = xbmcgui.ListItem(label=track["artist"]+track["title"])
		xbmc.log( "[PLUGIN] song: %s" % track["title"], xbmc.LOGNOTICE )
		item.setProperty("PlayPath", playpath)
		labels={
            "artist": track['artist'],
            "title": track['name'],
            }
		item.setInfo(type = 'music', infoLabels=labels)
		xbmcplaylist.add(RTMP_URL, item)
	
	xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(xbmcplaylist)
	#xbmc.Player(xbmc.PLAYER_CORE_AUTO).seek(int(track["start"]))
	

	
	
def main():
	
	reload(sys); sys.setdefaultencoding('utf-8')
	xbmc.log( "[PLUGIN] '%s: version %s' initialized!" % ( __plugin__, __version__, ), xbmc.LOGNOTICE )
	
	xbmcplugin.setContent(int(sys.argv[1]), 'music')

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
	elif mode == "ShowSet":
		xbmc.log( "[PLUGIN] invoke mode: %s" % params["url"], xbmc.LOGNOTICE )
		show_set(params["url"])
		
	xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
	xbmcplugin.endOfDirectory(int(sys.argv[1]))


if __name__ == '__main__':
	main()

