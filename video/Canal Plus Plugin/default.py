# -*- coding: cp1252 -*-
import sys
try:
    del sys.modules['cplusplus']
except:
    pass
import cplusplus as cpp
import xbmc,xbmcgui,xbmcplugin
import os,os.path
import threading


if os.name=='posix':
    # Linux case
    ROOTDIR = os.path.abspath(os.curdir).replace(';','')
else:
    # Xbox and Windows case
    ROOTDIR = os.getcwd().replace(';','')
    
DOWNLOADDIR = os.path.join(ROOTDIR,"downloads")
CACHEDIR = os.path.join(ROOTDIR,"cache")

def show_themes():
    """
    rempli la liste avec la liste des thèmes
    un lien va contenir :
        la commande 'listesubthemes'
        le parametre 'themeid'
    """
    ok = True
    
    themes=cpp.get_themes()
    i=0
    for theme_id,theme_titre,subthemes in themes:
        i=i+1
        url = sys.argv[0]+"?listesubthemes="+theme_id
        item=xbmcgui.ListItem(theme_titre)#,
                              #iconImage=HOME + AlbumID+".jpg",
                              #thumbnailImage=HOME + AlbumID+".jpg")
        item.setInfo(type="Video",infoLabels={ "Title": str(i) } )
        ok = ok and xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                                url=url,
                                                listitem=item,
                                                isFolder=True,
                                                totalItems=len(themes))

    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE)
    return ok

def show_subthemes(theme_id):
    """
    rempli la liste avec la liste des sous-thèmes pour le theme_id fourni
    un lien va contenir :
        la commande 'listevideos'
        les parametres 'themeid' et 'subthemeid'
    """
    ok = True
    subthemes=cpp.get_subthemes(theme_id)
    i=0
    for subtheme_id,subtheme_titre in subthemes:
        i=i+1
        url = sys.argv[0]+"?listevideos="+theme_id+"|"+subtheme_id
        item=xbmcgui.ListItem(subtheme_titre)#,
                              #iconImage=HOME + AlbumID+".jpg",
                              #thumbnailImage=HOME + AlbumID+".jpg")
        item.setInfo(type="Music",infoLabels={ "Title": str(i) } )
        ok = ok and xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                                url=url,
                                                listitem=item,
                                                isFolder=True,
                                                totalItems=len(subthemes))
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE)
    return ok


def show_videos(theme_id,subtheme_id):
    """
    rempli la liste avec la liste des videos
    un lien va contenir :
        la commande 'showvideoinfo'
        le paramètre 'videoID'
    """
    ok = True
    xmlParam = cpp.get_xmlParam()
    i=0
    videos = cpp.get_videos(xmlParam, theme_id=theme_id , subtheme_id = subtheme_id)
    for video in videos:
        i=i+1
        url = sys.argv[0]+"?showvideoinfos="+video["videoID"]
        #cpp.Cache_Pic(video['image.url'],video["videoID"]+".jpg")
        cpp.Cache_Pic(video['image.url'],os.path.join(CACHEDIR,str(video["videoID"])+".jpg"))
        item=xbmcgui.ListItem(label=video["title"],label2=video["publication_date"],
                              iconImage=os.path.join(CACHEDIR,str(video["videoID"])+".jpg"),
                              thumbnailImage=os.path.join(CACHEDIR,str(video["videoID"])+".jpg"))
        item.setInfo(type="Music",infoLabels={ "Date": video["publication_date"] } )
        ok = ok and xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                                url=url,
                                                listitem=item,
                                                isFolder=True,
                                                totalItems=len(videos))
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_DATE)
    return ok
    
def show_video_infos(videoid):
    """
    sera utilisé pour lire une video selon son id
    """
    ok = True

    infos = cpp.get_info(videoid)

    #TITRE
    item=xbmcgui.ListItem("Titre : %s"%infos["title"])
    ok = ok and xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                            url="",
                                            listitem=item,
                                            isFolder=False)

    #RESUME
    item=xbmcgui.ListItem(u"Résumé : %s"%infos["summary"])
    ok = ok and xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                            url="",
                                            listitem=item,
                                            isFolder=False)

    #DATE
    item=xbmcgui.ListItem(u"Publiée le %s"%infos["publication_date"])
    ok = ok and xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                            url="",
                                            listitem=item,
                                            isFolder=False)

    #IMAGE (a faire)
    item=xbmcgui.ListItem(u"Obtenir l'image (A FAIRE)")#%infos["image.url"])#ou smallimage.url
    #item.setInfo("Image",{ "Url": infos["image.url"] } )
    cpp.Cache_Pic(infos['image.url'],xbmc.makeLegalFilename(os.path.join(CACHEDIR,os.path.basename(str(infos["image.url"])))))
    ok = ok and xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                            url=sys.argv[0]+"?showpicture="+os.path.join(CACHEDIR,os.path.basename(str(infos["image.url"]))),#infos["image.url"],
                                            listitem=item,
                                            isFolder=False)

    #LECTURE HI
    item=xbmcgui.ListItem(u"Voir la video (Haute Qualité)")
    ok = ok and xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                            url=infos["video.hi"],
                                            listitem=item,
                                            isFolder=False)

    #LECTURE LO
    item=xbmcgui.ListItem(u"Voir la video (Basse Qualité)")
    ok = ok and xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                            url=infos["video.low"],
                                            listitem=item,
                                            isFolder=False)

    #ENREGISTREMENT HI
    item=xbmcgui.ListItem(u"Télécharger la video (Haute Qualité)")
    ok = ok and xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                            url=sys.argv[0]+"?dlvideo="+infos["video.hi"],
                                            listitem=item,
                                            isFolder=False)

    #ENREGISTREMENT LOW
    item=xbmcgui.ListItem(u"Télécharger la video (Basse Qualité)")
    ok = ok and xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                            url=sys.argv[0]+"?dlvideo="+infos["video.low"],
                                            listitem=item,
                                            isFolder=False)


    #show_dialog("video %s"%videoid,infos["video.hi"])
    #xbmc.Player().play(infos["video.hi"])

    #xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE)
    return ok


def show_dialog(titre,message,message2="",message3=""):
    dialog = xbmcgui.Dialog()
    dialog.ok(titre, message,message2,message3)
    return True

    
#Il faut parser les paramètres
stringparams = sys.argv[2] #les paramètres sont sur le 3ieme argument passé au script
try:
    if stringparams[0]=="?":#pour enlever le ? si il est en début des paramètres
        stringparams=stringparams[1:]
except:
    pass
parametres={}
for param in stringparams.split("&"):#on découpe les paramètres sur le '&'
    try:
        cle,valeur=param.split("=")#on sépare les couples clé/valeur
    except:
        cle=param
        valeur=""
    parametres[cle]=valeur #on rempli le dictionnaire des paramètres
#voilà, 'parametres' contient les paramètres parsés

if "listethemes" in parametres.keys():
    #à priori non utilisé !
    #on liste les themes
    show_themes()
elif "listesubthemes" in parametres.keys():
    #on liste les sous-themes
    show_subthemes(parametres["listesubthemes"])
elif "listevideos" in parametres.keys():
    #on liste les videos
    theme_id,subtheme_id = parametres["listevideos"].split("|")
    show_videos(theme_id,subtheme_id)
elif "showvideoinfos" in parametres.keys():
    #montre les infos de la video
    show_video_infos(parametres["showvideoinfos"])

elif "dlvideo" in parametres.keys():
    #télécharge la vidéo selon l'url fournie
    pDialog = xbmcgui.DialogProgress()
    ret = pDialog.create('CanalPlus', 'Démarrage du téléchargement ...')
    #téléchargement par Thread : FONCTIONNE MAIS TRES MAL : pas convaincant
##    t = threading.Thread(target=cpp.DL_video,args=(parametres["dlvideo"],
##                 os.path.join(DOWNLOADDIR,os.path.basename(parametres["dlvideo"])),
##                 pDialog.update))
##    t.start()
    goDL = cpp.DL_video(parametres["dlvideo"],
                        xbmc.makeLegalFilename(os.path.join(DOWNLOADDIR,os.path.basename(parametres["dlvideo"]))),
                        pDialog.update,pDialog)
    pDialog.close()
    if goDL==1:
        xbmc.executebuiltin("XBMC.Notification(%s,%s)"%("Telechargement termine !",""))
    elif goDL == 0:
        xbmc.executebuiltin("XBMC.Notification(%s,%s)"%("Fichier existant !","Telechargement annule."))
    elif goDL == -1:
        xbmc.executebuiltin("XBMC.Notification(%s,%s)"%("Telechargement annule par l'utilisateur.",""))

elif "showpicture" in parametres.keys():
    #ne fait rien
    pass
else:
    show_themes()
    #show_dialog("erreur","paramètre inconnu")

xbmcplugin.endOfDirectory(int(sys.argv[1]))#il faut cloturer le plugin avec ca pour finaliser la liste
    
    
