# -*- coding: cp1252 -*-
import os,shutil
import urllib
import re

HOMEDIR = os.getcwd()
try:
    import xbmc
    HOMEDIR = HOMEDIR[:-1]+"\\"
except:
    HOMEDIR = HOMEDIR+"\\"
    
pls = "http://mafreebox.freebox.fr/freeboxtv/playlist.m3u"

def compatibleFatX(chaine):
    chaine=chaine.replace("Ã©","é")
    chaine=chaine.replace("Ã®","î")
    chaine=chaine.replace("Ã´","ô")
    chaine=chaine.replace("Ã¨","è")
    ancien ="*,/;?|¿+<=>±«»×÷¢£¤¥§©¬®°µ¶·€¼½¾¹²³ªáÁàÀâÂäÄãÃåÅæÆçÇðÐéÉèÈêÊëËíÍìÌîÎïÏñÑºóÓòÒôÔöÖõÕøØßþÞúÚùÙûÛüÜýÝ"
    nouveau="                                    aAaAaAaAaAaAaAcC DeEeEeEeEiIiIiIiInN oOoOoOoOoOoOs  uUuUuUuUyY"
    chaine=chaine[:37] #38 caractères
    for n in range(len(ancien)-1): #remplace les caractères incompatibles
        chaine=chaine.replace(ancien[n],nouveau[n])
    return chaine

def liste_chaines():
    #Récupère le contenu du fichier playlist.m3u dans la freebox
    urllib.urlcleanup()
    m3u=urllib.urlopen("http://mafreebox.freebox.fr/freeboxtv/playlist.m3u").read()
    #Ecrit sur place la playliste récupérée
    f=open(HOMEDIR+"FreeboxProxyPlaylist.m3u","w")
    m3u=m3u.replace("#EXTINF:0","#EXTINF:-1")
    m3u=m3u.replace("rtsp://mafreebox.freebox.fr/","http://127.0.0.1:8083/")
    m3u=m3u.replace("stream?id=","")
    f.write(m3u)
    f.close()
    #liste les chaines contenues dans la playlist
    exp = re.compile(r"#EXTINF:0,(\d*?) - (.*?)\nrtsp://mafreebox\.freebox\.fr/freeboxtv/(?:stream\?id=(\d*?)|\d*?)\n")
    M3Uchannels = exp.findall(m3u) # [ (numero de chaine,nom de la chaine,id de la chaine)
    return M3Uchannels

chaines = liste_chaines()
for num,nom,id in chaines:
    f=open(HOMEDIR+"m3u\\%03d - %s.m3u"%(int(num) , compatibleFatX(nom)),"w")
    f.write("#EXTM3U\n")
    f.write("#EXTINF:-1,%s - %s\n"%(num,nom))
    f.write("http://127.0.0.1:8083/freeboxtv/%s"%id)
#    f=open(HOMEDIR+"strm\\%03d - %s.strm"%(int(num) , compatibleFatX(nom)),"w")
#    f.write("http://127.0.0.1:8083/freeboxtv/%s"%id)
    f.close()
    try:
        shutil.copyfile(HOMEDIR+"logos\\%s.bmp"%id,
                  HOMEDIR+"m3u\\%03d - %s.tbn"%(int(num) , compatibleFatX(nom))
                  )
    except:
        print "%s introuvable. (%s , %s)"%(id,nom,num)


                                                                    
