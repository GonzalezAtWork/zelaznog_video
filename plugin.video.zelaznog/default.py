# -*- coding: utf-8 -*-

""" zelaznog.net
    2015 zelaznog"""

import xbmc,xbmcaddon,xbmcgui,xbmcplugin,urllib,urllib2,os,re,sys,datetime,time,sqlite3
from resources.lib.net import Net
net=Net()

       
####################################################### DATABASE #####################################################

def clean_db(old, new):
	try:
		con = sqlite3.connect(db)
		con.execute("update movie set c22 = '"+ new +"' where c22 = '"+ old +"'")
		con.commit()
		con.execute("update episode set c18 = '"+ new +"' where c18 = '"+ old +"'")
		con.commit()
		con.execute("update files set idPath=2, strFileName = '"+ new +"' where strFileName = '"+ old +"'")
		con.commit()
		con.close()

	except sqlite3.Error as e:
		dberror = db.replace('C:\Users\Decaedro\AppData\Roaming\Kodi','')
		mensagemok("Zelaznog","Could not open database %s: %s" % (dberror,e))

####################################################### CONSTANTES #####################################################

versao = '0.1'
addon_id = 'plugin.video.zelaznog'
MainURL = 'http://zelaznog.net/'
art = '/resources/art/'
user_agent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1468.0 Safari/537.36'
selfAddon = xbmcaddon.Addon(id=addon_id)
wtpath = selfAddon.getAddonInfo('path').decode('utf-8')
pastaperfil = xbmc.translatePath(selfAddon.getAddonInfo('profile')).decode('utf-8')
db = pastaperfil
db = db.replace('\\addon_data\\plugin.video.zelaznog','\\Database\\MyVideos90.db')
db = db.replace('/addon_data/plugin.video.zelaznog','/Database/MyVideos90.db')
db = db.replace('MyVideos90.db/','MyVideos90.db')
db = db.replace('MyVideos90.db\\','MyVideos90.db')
req = sys.argv[0] + sys.argv[2]
mensagemok = xbmcgui.Dialog().ok
mensagemprogresso = xbmcgui.DialogProgress()

username = urllib.quote(selfAddon.getSetting('username'))
password = selfAddon.getSetting('password')
bitrate = urllib.quote(selfAddon.getSetting('bitrate')).replace('kbps','')

########################################################### PLAYER ################################################

def analyzer(user, url):
      mensagemprogresso.create('Zelaznog', 'Conectando...')

      final_url = ''
      final_srt = ''
      final_image = ''
      final_filename = ''
      linkfinal = ''
      final = ''
      try:
            form_d = {'username':username,'password':password,'user':user,'video':url,'bitrate':bitrate}
            ref_data = {'Accept': '*/*', 'Content-Type': 'application/x-www-form-urlencoded','Origin': 'http://zelaznog.net', 'X-Requested-With': 'XMLHttpRequest', 'Referer': 'http://zelaznog.net/','User-Agent':user_agent}
            endlogin = MainURL + 'getVideo.php'
            final = net.http_POST(endlogin,form_data=form_d,headers=ref_data).content.encode('latin-1','ignore')
            final = final.replace('\u0026','&').replace('\u003c','<').replace('\u003e','>').replace('\\','')

            final_url = re.compile('"url":"(.+?)"').findall(final)[0]
            final_image = re.compile('"image":"(.+?)"').findall(final)[0]
            final_filename = re.compile('"file_name":"(.+?)"').findall(final)[0]
      except: pass
      final_url = final_url.replace('\u0026','&').replace('\u003c','<').replace('\u003e','>').replace('\\','')
      final_filename = final_filename.replace('\u0026','&').replace('\u003c','<').replace('\u003e','>').replace('\\','')
      final_filename = final_filename.replace('.mkv','.strm')
      final_filename = final_filename.replace('.avi','.strm')
      final_filename = final_filename.replace('.mp4','.strm')
      final_filename = final_filename.replace('.rmvb','.strm')
      final_filename = final_filename.replace('.mov','.strm')
      final_filename = final_filename.replace('.mpg','.strm')
      final_srt = MainURL + 'streams/Legendas/' + final_filename.replace('.strm','.srt')
      final_srt = final_srt.replace(' ','%20')

      clean_db(final_filename, req)
      mensagemprogresso.close()

      comecarvideo(final_filename, final_image, final_url, legendas=final_srt)

def comecarvideo(name,image_url, url,legendas=None):
        playeractivo = xbmc.getCondVisibility('Player.HasMedia')
        item = urllib.unquote( urllib.unquote( name ) ).decode("utf-8")
        listItem = xbmcgui.ListItem(item)
        listItem.setThumbnailImage(image_url)
        listItem.setIconImage('DefaultVideo.png')
        listItem.setProperty("IsPlayable", "true")
        listItem.select(True)
        listItem.setPath(url)
        listItem.addStreamInfo('subtitle', { 'language': 'br' })
        
        xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=listItem)

        if legendas != None: 
            time.sleep(2)
            xbmc.Player().setSubtitles(legendas.encode("utf-8"))

def addDir(name,url,mode,iconimage,total,pasta,atalhos=False):
      u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
      liz=xbmcgui.ListItem(name,iconImage="DefaultFolder.png", thumbnailImage=iconimage)
      liz.setInfo( type="Video", infoLabels={ "Title": name} )
      liz.setProperty('fanart_image', "%s/fanart.jpg"%selfAddon.getAddonInfo("path"))
      return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=pasta,totalItems=total)

def get_params():
      param=[]
      paramstring=sys.argv[2]
      if len(paramstring)>=2:
            params=sys.argv[2]
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


params = get_params()
url = None
user = None

try: url=urllib.unquote_plus(params["url"])
except: pass
try: user=urllib.unquote_plus(params["user"])
except: pass

if url==None or len(url)<1:
      print "Versao Instalada: v" + versao
      #addDir('[COLOR blue][B]Configurar[/B][/COLOR]',MainURL,6,wtpath + art + 'logo.png',1,True)
else: 
      analyzer(user, url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
