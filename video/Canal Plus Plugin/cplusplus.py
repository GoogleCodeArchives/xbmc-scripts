import urllib2, urllib
import cookielib
import os,os.path
import re
from BeautifulSoup import BeautifulStoneSoup
import gzip,StringIO
import socket

# timeout en seconds
#timeout =  10
#socket.setdefaulttimeout(timeout)
#cookies
if os.name=='posix':
    # Linux case
    ROOTDIR = os.path.abspath(os.curdir).replace(';','')
else:
    # Xbox and Windows case
    ROOTDIR = os.getcwd().replace(';','')

CACHEDIR= os.path.join(ROOTDIR,"cache")
COOKIEFILE = os.path.join(CACHEDIR,'cookies.lwp')
cj = cookielib.LWPCookieJar()

if os.path.isfile(COOKIEFILE):
    # si nous avons un fichier cookie d�j� sauvegard�
    #  alors charger les cookies dans le Cookie Jar
    cj.load(COOKIEFILE)
         
xmlParam = "14-1-18/06/2008-0"
videoplayerURL = "http://www.canalplus.fr/flash/xml/module/video-player/"
GetMosaicPage = "getMosaic.php"
EntrysPage = "video-player-filters.php"
ThemesPage = "video-player-thematic.php"
VideoInfoPage = "getVideoInformation.php"

    
def get_page(url,params={},savehtml=True,filename="defaut.html",check_connexion=True,debuglevel=1):
    """
    t�l�charge la page avec les param�tres fournis :
        params : dictionnaire de param�tres
    Renvoi le code html de la page
    """

    #h=urllib2.HTTPHandler(debuglevel=debuglevel)
    h=urllib2.HTTPCookieProcessor(cj)#urllib2.HTTPCookieProcessor(cookiejar)
    request = urllib2.Request(url,urllib.urlencode(params))

    request.add_header('Host','www.canalplus.fr')
    request.add_header('Referer', 'http://www.canalplus.fr/flash/loader/loader_canalplus_V0_1.swf')
    request.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; fr; rv:1.9) Gecko/2008052906 Firefox/3.0')
    request.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
    request.add_header('Accept-Language','fr,fr-fr;q=0.8,en-us;q=0.5,en;q=0.3')
    request.add_header('Accept-Charset','ISO-8859-1,utf-8;q=0.7,*;q=0.7')
    request.add_header('Accept-Encoding','gzip,deflate')
    request.add_header('Keep-Alive','300')
    for index, cookie in enumerate(cj):
        #print index, '  :  ', cookie
        request.add_header('Cookie',cookie)
    request.add_header('Connection','keep-alive')
    request.add_header('Content-type','application/x-www-form-urlencoded')
    request.add_header('Content-length',len(urllib.urlencode(params)))
    opener = urllib2.build_opener(h)
    urllib2.install_opener(opener)
    connexion = opener.open(request)
    #print connexion.headers
    html = connexion.read(int(connexion.headers["Content-Length"]))
    open(os.path.join(CACHEDIR,filename),"w").write(html)
    if connexion.headers["Content-Encoding"]=="gzip":
        compressedstream = StringIO.StringIO(html)
        gzipper = gzip.GzipFile(fileobj=compressedstream)
        data = gzipper.read()
    else:
        data = html
    
    # save the cookies again
    cj.save(COOKIEFILE)
    return data


def get_video_infos(videoID):
    xml = get_page("http://www.canalplus.fr/flash/xml/module/video-player/getVideoInformation.php?video_id="+videoID,
               filename="video info.xml",debuglevel=1)
    soup = BeautifulStoneSoup(xml)
    videoinfos = soup.find("thumbnail")

    return [videoinfos.title.string,
            videoinfos.summary.string,
            videoinfos.publication_date.string,
            videoinfos.image.url.string,
            videoinfos.smallimage.url.string,
            videoinfos.theme.string,
            videoinfos.video.stream_server.string,
            videoinfos.video.hi.string,
            videoinfos.video.low.string]

def get_xmlParam():
    """
    T�l�charge la page d'accueil puis cherche et renvoi le xmlParam
    """
    html=get_page("http://www.canalplus.fr",filename="index.html",debuglevel=1)
    exp=re.compile(r'"http://www\.canalplus\.fr/flash/xml/configuration/configuration-video-player\.php\?xmlParam=([\-/0-9]*)"')
    try:
        return exp.findall(html)[0]
    except:
        return None

def get_themes():
    """
    r�cup�re et retourne une liste des themes et sous th�mes
    [ [ themeid , titre , [ [subtheme_id,titre] , ... ] ] , ... ]
    """
    xml = get_page(videoplayerURL + EntrysPage ,filename="entrys.xml",debuglevel=1)
    #xml = open("entrys.xml").read() #temporaire pour �viter de t�l�charger
    entrysoup = BeautifulStoneSoup(xml)
    xml = get_page(videoplayerURL + ThemesPage ,filename="themes.xml",debuglevel=1)
    #xml = open("themes.xml").read() #temporaire pour �viter de t�l�charger
    themesoup = BeautifulStoneSoup(xml)
    themes=[]
    for theme in entrysoup.findAll("theme"):
        themes.append([theme['id'],themesoup.find(id=theme['id']).label.string,get_subthemes(theme['id'])])
    return themes

def get_subthemes(theme_id):
    """
    r�cup�re les sous-themes du th�me fourni et renvoi un dictionnaire :
    { subthemeID : titre , ... }
    """
    xml = get_page(videoplayerURL + EntrysPage ,filename="entrys.xml",debuglevel=1)
    #xml = open("entrys.xml").read() #temporaire pour �viter de t�l�charger
    entrysoup = BeautifulStoneSoup(xml)
    subtheme=[]
    theme = entrysoup.find("theme",{"id":theme_id})
    for entry in theme.findAll("entry"):
        subtheme.append([entry['id'],entry.string])
    return subtheme
    
def get_videos(xmlParam,theme_id,subtheme_id):
    """
    retourne l'�quivalent de la mosaique canalplus sous forme d'une liste de dictionnaires
    [ { videoid , title , publication , imageURL , theme , visualized , note , duration } ]
    """
    xml = get_page(videoplayerURL + GetMosaicPage+"?xmlParam="+xmlParam,params={"theme_id":theme_id,"content_id":"","subtheme_id":subtheme_id,"keywords":""},
                   filename="listingmozaic.xml",debuglevel=1)
    #xml = open("listingmozaic.xml").read()
    soup = BeautifulStoneSoup(xml)
    videos=[]
    for thumb in soup.findAll("thumbnail"):
        videos.append( { 'videoID' : thumb['id'],
                         'title': thumb.title.string,
                         'publication_date': thumb.publication_date.string,
                         'image.url': thumb.image.url.string,
                         'theme': thumb.theme.string,
                         'visualized': thumb.visualized.String,
                         'note': thumb.note.string,
                         'duration': thumb.duration.string
                         } )
    return videos

def get_info(videoID):
    """
    retrouve les informations de l'ID de vid�o fourni
    """

    xml = get_page(videoplayerURL +"getVideoInformation.php?video_id=%s"%videoID,filename="video info %s.xml"%videoID,debuglevel=1)
    soup = BeautifulStoneSoup(xml)
    videoinfos = soup.find("thumbnail")
    return {'title' : videoinfos.title.string,
            'summary' : videoinfos.summary.string,
            'publication_date' : videoinfos.publication_date.string,
            'image.url' : videoinfos.image.url.string.decode(),
            'smallimage.url' : videoinfos.smallimage.url.string.decode(),
            'theme' : videoinfos.theme.string,
            'video.stream_server' : videoinfos.video.stream_server.string,
            'video.hi' : videoinfos.video.hi.string,
            'video.low' : videoinfos.video.low.string
            }
def Cache_Pic(url,filename):
    if not os.path.exists(filename):
        urllib.urlretrieve(url,filename)
    else:
        pass
    
    
def DL_video(url,fichier,ProgressUpdate=None,ProgressObject=None,debuglevel=0):
    """
    t�l�charge la video � l'url mentionn�e
    """
    if os.path.exists(fichier):
        for i in range(100):
            try:
                ProgressUpdate(i)
            except:
                pass
        return 0
    h=urllib2.HTTPHandler(debuglevel=debuglevel)
    request = urllib2.Request(url)

    #request.add_header('Host','www.canalplus.fr')
    request.add_header('Referer', 'http://www.canalplus.fr/flash/loader/loader_canalplus_V0_1.swf')
    request.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; fr; rv:1.9) Gecko/2008052906 Firefox/3.0')
    request.add_header('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
    request.add_header('Accept-Language','fr,fr-fr;q=0.8,en-us;q=0.5,en;q=0.3')
    request.add_header('Accept-Charset','ISO-8859-1,utf-8;q=0.7,*;q=0.7')
    #request.add_header('Accept-Encoding','gzip,deflate')
    request.add_header('Keep-Alive','300')
    request.add_header('Connection','keep-alive')
    #request.add_header('Content-type','application/x-www-form-urlencoded')
    #request.add_header('Content-length',len(urllib.urlencode(params)))
    opener = urllib2.build_opener(h)
    urllib2.install_opener(opener)
    connexion = opener.open(request)
    taille = connexion.headers["Content-Length"]
    f=open(fichier,"wb")
    for i in range(1,int(taille),100000):
        f.write(connexion.read(100000))
        try:
            ProgressUpdate(int(float(i)/int(taille)*100),"%s sur %s Ko (%s%%)"%(str(i/1024),str(int(taille)/1024),int(float(i)/int(taille)*100)))
            if ProgressObject.iscanceled():
                f.close()
                return -1
        except:
            pass
    f.write(connexion.read(int(taille)-i))
    #f.write(connexion.read(int(connexion.headers["Content-Length"])))
    # open(filename,"wb").write(connexion.read(int(connexion.headers["Content-Length"])))
    f.close()
    return 1

if __name__ == "__main__":
    ###avant tout, r�cup�rons le xmlParam
    xmlParam = get_xmlParam()
    #xmlParam = "14-1-24/06/2008-0"
    print get_themes()
    print xmlParam
    global infos
    infos = get_info("136491")
    print "\n".join([video['title'] for video in get_videos(xmlParam, theme_id="5" , subtheme_id = "0")])
    ##
    #print get_subthemes(u"23")

