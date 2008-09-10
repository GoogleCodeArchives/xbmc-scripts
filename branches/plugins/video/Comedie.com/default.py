# -*- coding: cp1252 -*-
#############################
# petit hack de comedie.com #
#############################
"""
Cet ébauche de script est simplement le minimum pour
montrer la démarche afin de récupérer les liens stream
du site Comedie.com
1ere étape : on récpère la liste des artistes
2ieme étape : on récupère la liste des vidéos pour cet artiste
3ieme étape : on récupère le lien de la video

"""
#
# import des librairies
#
import urllib,re,sys
import xbmcplugin,xbmcgui,xbmc

# état des variables initiales
BaseUrl = "http://www.comedie.com"

urllib.urlcleanup()


def get_artistes():
    #on récupère la page de base
    html = urllib.urlopen(BaseUrl + "/videos/index_html").read()
    #on parse pour trouver tous les artistes
    exp = re.compile(r'option value="(.+)">\1*?<')
    artistes = exp.findall(html)
    print "artistes trouves :"
    print artistes
    return artistes


def get_videos(artiste):
    #création des paramètres
    params=urllib.urlencode({"origine" : artiste})
    #on télécharge le iframe des videos de l'artiste
    html = urllib.urlopen(BaseUrl + "/videos/choix_videos.html",params).read()
    #on parse pour trouver les ID des videos et le titre de la video
    exp = re.compile(r'<a href="avertissement\.html\?id_videos=(.*?)" class="nav_prog" target="_parent">(.*?)<br></a>')
    videos = exp.findall(html)
    print "parse video: "
    print videos
    return videos


def get_URL(IDvideo):
    #création des paramètres
    params = urllib.urlencode({"id_videos" : IDvideo})
    #téléchargement de la page vidéo
    html = urllib.urlopen(BaseUrl + "/videos/avertissement.html",params).read()
    #on parse pour obtenir l'url de la video
    exp = re.compile(r'<param name="FileName" value=".*?(mms://.*?.wmv)" />')
    lien = exp.findall(html)[0]

    return lien

def show_artistes():
    ok=True
    for artiste in get_artistes():
        url=sys.argv[0]+"?artiste="+urllib.quote_plus(artiste)
        print url
        item=xbmcgui.ListItem(artiste)
        item.setInfo(type="Video",infoLabels={ "Title": artiste } )
        ok = ok and xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=item,isFolder=True)
    return ok

def show_videos(artiste):
    ok=True
    videos = get_videos(urllib.unquote_plus(artiste))
    for IDvid, TitreVid in videos:
        print IDvid+" : "+TitreVid
        url=get_URL(IDvid)#sys.argv[0]+"?play="+IDvid+"&titre="+TitreVid
        item = xbmcgui.ListItem(TitreVid)
        item.setInfo( type="Video", infoLabels={ "Title": TitreVid } )
        ok = ok and xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=item,totalItems=len(videos))
    return ok
    





stringparams = sys.argv[2]
print stringparams
try:
    if stringparams[0]=="?":
        stringparams=stringparams[1:]
except:
    pass
parametres={}
for param in stringparams.split("&"):
    try:
        cle,valeur=param.split("=")
    except:
        cle=param
        valeur=""
    parametres[cle]=valeur

if "artiste" in parametres.keys():
    print "paramètre artiste="+parametres["artiste"]
    #paramètre 'artiste' : on liste les videos de l'artiste
    show_videos(parametres["artiste"])
elif "play" in parametres.keys():
    print "paramètre play=..."
    
    
else:
    #pas de paramètres : début du plugin
    print "pas de paramètres..."
    show_artistes()
xbmcplugin.endOfDirectory(int(sys.argv[1]))
