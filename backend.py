#!/usr/bin/env python

import redis
import urllib
import simplejson
import re
import sys
from pprint import pprint
import logging

r = redis.Redis()
r.info()


def get_song_data(username,page):
    statspage = 'http://www.thesixtyone.com/%s/stats/bumps/%s/' % (username,page)
    sp = urllib.urlopen(statspage).read()
    songdata_raw = [c for c in sp.split('\n') if c.count('t61.song.data')][0]
    songdata_json = songdata_raw[songdata_raw.find('t61.song.data')+ 16:-1] 
    songdata = simplejson.loads(songdata_json)
    bumpdata = re.findall('song_metadata_(.*?)\".*?bump_report.*?>.*?<b>\+(.*?)rep</b>.*?\(.*?(\d+).*?(\d+)',
                           ''.join(sp.split()), re.MULTILINE|re.IGNORECASE)
    try:
        numpages = int(re.search('.*<a[^>]+>(.*?)</a>.*nextpage',''.join(sp.split('\n'))).group(1))
    except:
        numpages = None
    return songdata['by_id'],bumpdata,numpages

def store_song_data(username,songdata,bumpdata):
    for s in songdata.keys():
        r.set('%s.song.%s' % (username,s), songdata[s])
        r.sadd('%s.song.ids' % username,s)

    for b in bumpdata:
        r.set('%s.songs.reps.%s' % (username,b[0]),int(b[1]))

def rep_sort(username):
    res = []
    try:
        for s in r.sort('%s.song.ids' % username, 
                        by='%s.songs.reps.*' % username, 
                        get='%s.song.*' % username,desc=True):
            s = eval(s)
            rep = r.get('%s.songs.reps.%s' % (username,s['id']))
            name = s['name']
            photo_base_url = s['photo_base_url']
            artist = s['artist']
            score= s['score']
            key = s['key']
            id = s['id']
            artist_username=s['artist_username']
            res.append((rep,name,artist,score,key,id,photo_base_url,artist_username))
            
    except redis.ResponseError:
        logging.error('no song.ids for user %s' % username)
        return None
    return res

if __name__ == '__main__':
    try:
        page = sys.argv[1]
        print '----------------'
        print 'processing page ',page
        print '----------------'
        songdata,bumpdata,numpages = get_song_data('durdn',page=page)
        store_song_data('durdn',songdata,bumpdata)
        rep_sort('durdn')
    except IndexError:
        print '* processing page ',1
        songdata,bumpdata,numpages = get_song_data('durdn',page=1)
        store_song_data('durdn',songdata,bumpdata)
        for p in range(numpages-1):
            print '* processing page ',p+2
            songdata,bumpdata,numpages = get_song_data('durdn',page=p+2)
            store_song_data('durdn',songdata,bumpdata)
        rep_sort('durdn')

