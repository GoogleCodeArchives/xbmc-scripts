# -*- coding: cp1252 -*-
import urllib
import re
import xbmcgui

PLAYLIST_PATH = "Q:\\UserData\\playlists\\video\\"
IP = "127.0.0.1"

plsfreebox = "http://mafreebox.freebox.fr/freeboxtv/playlist.m3u"

#Récupère le contenu du fichier playlist.m3u dans la freebox
urllib.urlcleanup()
m3u=urllib.urlopen(plsfreebox).read()
#Ecrit la playliste récupérée et mise à jour pour le proxy
f=open(PLAYLIST_PATH+"FreeboxProxyPlaylist.m3u","w")
m3u=m3u.replace("rtsp://mafreebox.freebox.fr/","http://%s:8083/"%IP)
m3u=m3u.replace("#EXTINF:0","#EXTINF:-1")
m3u=m3u.replace("stream?id=","")
f.write(m3u)
f.close()

xbmcgui.Dialog().ok("Generateur de playliste freebox",
                    "La playliste mise à jour est disponible dans :",
                    PLAYLIST_PATH)

                                                                    
