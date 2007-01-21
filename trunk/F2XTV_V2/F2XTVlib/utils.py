# -*- coding: cp1252 -*-
import urllib
import os
import re
from ConfigParser import ConfigParser

#fonctions générales

def verifrep(repertoire):
    """
    Ecrit un dossier si il n'existe pas déjà
    """
    try:
        os.makedirs(repertoire)
        print "> Création du répertoire \"%s\"."%repertoire
    except:
        pass

def suppr_balises(data): # OK A GARDER
    """
    Supprime les balises html du texte 'data' envoyé (string)
    Renvoi un 'string' sans les balises html.
    Le caractère '&nbsp' est remplacé par un espace
    """
    exp=r"""<.*?>"""
    compile_obj = re.compile(exp,  re.IGNORECASE| re.DOTALL)
    match_obj = compile_obj.search(data)
    retour = compile_obj.subn('',data, 0)[0]
    retour=retour.replace("&nbsp;"," ")
    return retour

def accents(chaine):
    """
    Substitue des accents de la playlist
    (Voir si l'encodage ne solutionnerait pas le problème)
    """
    chaine=chaine.replace("Ã©","é")
    chaine=chaine.replace("Ã®","î")
    chaine=chaine.replace("Ã¨","è")
    chaine=chaine.replace("Ã´","ô")    
    return chaine

def FatX(chaine,decal=0):
    """
    Converti une chaine en un nouvelle chaine compatible FAT-X
    decal sert à tronquer un peu plus la longueur du nom (38char maxi - decal)

    La longueur de la chaine sera limitée à 38 caractères maxi (les caractères en trop sons systématiquement supprimés)
    Un caractère de la liste 'ancien' sera remplacé par le caractère à la même place de la liste 'nouveau'
    """
    ancien ="*,/;?|¿+<=>±«»×÷¢£¤¥§©¬®°µ¶·€¼½¾¹²³ªáÁàÀâÂäÄãÃåÅæÆçÇðÐéÉèÈêÊëËíÍìÌîÎïÏñÑºóÓòÒôÔöÖõÕøØßþÞúÚùÙûÛüÜýÝ"
    nouveau="                            E   123 aAaAaAaAaAaAaAcC DeEeEeEeEiIiIiIiInN oOoOoOoOoOoOs  uUuUuUuUyY"
    chaine=chaine[:37-decal] #38 caractères - decal
    for n in range(len(ancien)): #remplace les caractères incompatibles
        chaine=chaine.replace(ancien[n],nouveau[n])
    return chaine

def get_freespace(path):
    """
    Récupère l'espace disque disponible en utilisant le serveur http de XBMC
    Renvoi l'espace libre en ko.
    Il est donc nécessaire de mettre en marche le serveur http de XBMC.
    TODO: Voir pour utiliser une builtin à la place ou une fonction python
    """
    try:
        drive=os.path.splitdrive(path)[0][:-1]
        print " **** %s drive freespace ****"%drive
        html=urllib.urlopen("http://127.0.0.1/xbmcCmds/xbmcHttp?command=GetSystemInfoByName&parameter=system.freespace(%s)"%drive).read()
        freespace=int(re.findall(r"(\d+)",html)[0])*1024
        print "Espace disque récupéré avec succès : %s ko"%freespace
    except:
        print "Problème de récupération de l'espace disque"
        freespace = 0   
    return freespace



def liste_chaines():
    """
    Renvoi une liste des chaines freebox contenus dans la playlist multiposte
    [ ( NumeroDeChaine , NomDeLaChaine , IDdeLaChaine ) , ... ]
    """
    #Récupère le contenu du fichier playlist.m3u de la freebox
    urllib.urlcleanup()
    m3u=urllib.urlopen("http://mafreebox.freebox.fr/freeboxtv/playlist.m3u").read()
    m3u=accents(m3u)

    #liste les chaines contenues dans la playlist
    exp = re.compile(r"#EXTINF:0,(\d*?) - (.*?)\nrtsp://mafreebox.freebox.fr/freeboxtv/stream\?id=(.*?)\n")
    M3Uchannels = exp.findall(m3u) # [ (numero de chaine,nom de la chaine,id de la chaine)
    return M3Uchannels

def get_nom_chaine(chanid):
    """
    Renvoi le tuple de la chaine correspondant à l'ID 'chanid'
    """
    pls = liste_chaines()
    for chan in pls:
        if chan[2] == chanid:
            return chan
        else: pass
    return None
    
def OpenIni(inifile):
    "ouvre le fichier .ini et renvoi l'objet ConfigParser"
    sets = ConfigParser()
    sets.read(inifile)#self.iniPath)
    return sets

def SaveIni(iniobject,inifile):
    "Sauve l'objet ConigParser dans le fichier ini"
    try:
        f=open(inifile,"w")
        iniobject.write(f)
        f.close()
        print "SaveIni --> sauvegarde ok"
    except:
        print "SaveIni --> Echec de sauvegarde"
