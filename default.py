import sys
import string
import threading
import Queue
import urllib
import urlparse
import xbmcgui
import xbmcplugin
from resources.lib import requests
from resources.lib import feedparser

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
url_etv = 'rtsp://194.36.162.51:80/live/etv'
url_etv_logo = 'http://etv2.err.ee/Content/images/global/etv-logo.png'
url_etv2 = 'rtsp://194.36.162.51:80/live/etv2'
url_etv2_logo = 'http://etv2.err.ee/Content/images/global/etv2-logo.png'
url_rss = 'http://uudised.err.ee/rss'

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

def read_post(p,q):
    session = requests.Session()
    p.html = session.get(p.link).text
    q.put(p)

def parse_video_url(html):
    video_url = ''
    pos1 = string.find(html, '://media.err.ee:80/')
    if pos1 > -1:
        pos2 = string.find(html, '@', pos1)
        pos3 = string.find(html, '.mp4', pos2)
        if pos2 > -1 and pos3 > 1:
            video_url = 'rtsp' + html[pos1:pos3] + '/mp4:' + html[pos2 + 1:pos3]
    return video_url

mode = args.get('mode', None)
	
if mode is None:
    url = build_url({'mode': 'live'})
    li = xbmcgui.ListItem('Live', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
    url = build_url({'mode': 'videos'})
    li = xbmcgui.ListItem('Videos', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

elif mode[0] == 'live':
    li = xbmcgui.ListItem('ETV', iconImage=url_etv_logo)
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url_etv, listitem=li)
    li = xbmcgui.ListItem('ETV2', iconImage=url_etv2_logo)
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url_etv2, listitem=li)

elif mode[0] == 'videos':
    feed = feedparser.parse(url_rss)
    q = Queue.Queue()
    threads = [threading.Thread(target=read_post, args = (p,q)) for p in feed.entries]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    while not q.empty():
        p = q.get()
        video_url = parse_video_url(p.html)
        if video_url != '':
            li = xbmcgui.ListItem(p.title, iconImage='DefaultVideo.png')
            xbmcplugin.addDirectoryItem(handle=addon_handle, url=video_url, listitem=li)

xbmcplugin.endOfDirectory(addon_handle)
xbmcplugin.setContent(addon_handle, 'movies')
