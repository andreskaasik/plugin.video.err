import sys
import string
import threading
import Queue
import urllib
import urlparse
import xbmcgui
import xbmcplugin
from resources.lib import feedparser

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
url_etv = 'rtsp://194.36.162.51:80/live/etv'
url_etv_logo = 'http://etv2.err.ee/Content/images/global/etv-logo.png'
url_etv2 = 'rtsp://194.36.162.51:80/live/etv2'
url_etv2_logo = 'http://etv2.err.ee/Content/images/global/etv2-logo.png'
url_err_rss = 'http://uudised.err.ee/rss'

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

def read_post(post, queue):
    data = urllib.urlopen(post.link).read()
    media_count = string.count(data, '://media.err.ee:80/')
    if media_count == 1:
        print(post.title.encode('utf8'))
        print '  ' + post.link
        pos1 = string.find(data, '://media.err.ee:80/')
        pos2 = string.find(data, '@', pos1)
        pos3 = string.find(data, '.mp4', pos2)
        url_media = 'rtsp' + data[pos1:pos3]
        post.video = url_media + '/mp4:' + data[pos2 + 1:pos3]
        print post.video
        queue.put(post)

def fetch_videos():
    feed = feedparser.parse(url_err_rss)
    result = Queue.Queue()
    threads = [threading.Thread(target=read_post, args = (post,result)) for post in feed.entries]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return result

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
    q = fetch_videos()
    while not q.empty():
        post = q.get()
        li = xbmcgui.ListItem(post.title, iconImage='DefaultVideo.png')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=post.video, listitem=li)

xbmcplugin.endOfDirectory(addon_handle)
xbmcplugin.setContent(addon_handle, 'movies')
