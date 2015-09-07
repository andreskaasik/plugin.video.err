import os
import sys
import string
import threading
import Queue
import urllib
import urlparse
import xbmcgui
import xbmcplugin

try:
    import feedparser
except:
    sys.path.append(os.path.join(os.path.realpath(os.path.dirname(__file__)),'..','script.module.feedparser','lib'))
    import feedparser

try:
    import requests
except:
    sys.path.append(os.path.join(os.path.realpath(os.path.dirname(__file__)),'..','script.module.requests','lib'))
    import requests

addon_base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

url_etv = xbmcplugin.getSetting(addon_handle,'err.etv.live')
url_etv_logo = xbmcplugin.getSetting(addon_handle,'err.etv.logo')
url_etv2 = xbmcplugin.getSetting(addon_handle,'err.etv2.live')
url_etv2_logo = xbmcplugin.getSetting(addon_handle,'err.etv2.logo')
url_rss = xbmcplugin.getSetting(addon_handle,'err.rss')

def build_url(query):
    return addon_base_url + '?' + urllib.urlencode(query)

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
