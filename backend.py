#!/usr/bin/env python

import redis
import urllib
import simplejson
import re
import sys
from pprint import pprint
import logging
import tempfile

r = redis.Redis()
r.info()


def get_song_data(username,page):
    statspage = 'http://www.thesixtyone.com/%s/stats/bumps/%s/' % (username,page)
    sp = urllib.urlopen(statspage).read()
#    tmp =file(tempfile.mkstemp(prefix='statpage',suffix='.html')[1],'w')
#    tmp.write(sp)
#    tmp.close()
    songdata_raw = [c for c in sp.split('\n') if c.count('t61.song.data')][0]
    songdata_json = songdata_raw[songdata_raw.find('t61.song.data')+ 16:-1] 
    songdata = simplejson.loads(songdata_json)
    bumpdata = re.findall('song_metadata_(.*?)\".*?bump_report.*?>.*?<b>\+(.*?)rep</b>.*?\(.*?(\d+).*?(\d+)(.*?)\)',
                          ''.join(sp.split()), re.MULTILINE|re.IGNORECASE)
    enriched = []
    for b in bumpdata:
        b = list(b)
        times = re.search('<b>x(\d+)</b>',b[4])
        if times:
            b[4] = times.group(1)
        else:
            b[4] = '1'
        enriched.append(tuple(b))

    logging.debug('bump data: %s' % str(enriched))
    try:
        if re.search('nextpage',sp):
            match = re.search('.*<a[^>]+>(.*?)</a>.*nextpage',''.join(sp.split('\n')))
            if match:
                numpages = int(match.group(1))
            else:
                numpages = 1
        else:
            numpages = 1
    except:
        numpages = 1

    logging.info('scrapped %s songs, %s bumpdata, %s numpages' % (len(songdata['by_id'].keys()),len(enriched),numpages))
    return songdata['by_id'],enriched,numpages

def store_song_data(username,songdata,bumpdata):
    for s in songdata.keys():
        r.set('%s.song.%s' % (username,s), songdata[s])
        r.sadd('%s.song.ids' % username,s)

    for b in bumpdata:
        r.set('%s.songs.reps.%s' %  (username,b[0]),int(b[1]))
        r.set('%s.songs.stats.%s' % (username,b[0]),(b[2],b[3],b[4]))

def rep_sort(username):
    res = []
    try:
        for s in r.sort('%s.song.ids' % username, 
                        by='%s.songs.reps.*' % username, 
                        get='%s.song.*' % username,desc=True):
            s = eval(s)
            rep = r.get('%s.songs.reps.%s' % (username,s['id']))
            stats = eval(r.get('%s.songs.stats.%s' % (username,s['id'])))
            name = s['name']
            photo_base_url = s['photo_base_url']
            artist = s['artist']
            score= s['score']
            key = s['key']
            id = s['id']
            hearts = stats[2]
            fromr = stats[0]
            tor = stats[1]
            artist_username=s['artist_username']
            res.append((rep,name,artist,score,key,id,photo_base_url,artist_username,hearts))
            
    except redis.ResponseError:
        logging.error('no songs stored for user %s' % username)
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
        print rep_sort('durdn')
    except IndexError:
        print '* processing page ',1
        songdata,bumpdata,numpages = get_song_data('durdn',page=1)
        store_song_data('durdn',songdata,bumpdata)
        for p in range(numpages-1):
            print '* processing page ',p+2
            songdata,bumpdata,numpages = get_song_data('durdn',page=p+2)
            store_song_data('durdn',songdata,bumpdata)
        print rep_sort('durdn')

