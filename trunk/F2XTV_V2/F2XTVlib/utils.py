# -*- coding: cp1252 -*-
import urllib
import os
import re
from ConfigParser import ConfigParser

#fonctions g�n�rales

def verifrep(repertoire):
    """
    Ecrit un dossier si il n'existe pas d�j�
    """
    try:
        os.makedirs(repertoire)
        print "> Cr�ation du r�pertoire \"%s\"."%repertoire
    except:
        pass

def suppr_balises(data): # OK A GARDER
    """
    Supprime les balises html du texte 'data' envoy� (string)
    Renvoi un 'string' sans les balises html.
    Le caract�re '&nbsp' est remplac� par un espace
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
    (Voir si l'encodage ne solutionnerait pas le probl�me)
    """
    chaine=chaine.replace("é","�")
    chaine=chaine.replace("î","�")
    chaine=chaine.replace("è","�")
    chaine=chaine.replace("ô","�")    
    return chaine

def FatX(chaine,decal=0):
    """
    Converti une chaine en un nouvelle chaine compatible FAT-X
    decal sert � tronquer un peu plus la longueur du nom (38char maxi - decal)

    La longueur de la chaine sera limit�e � 38 caract�res maxi (les caract�res en trop sons syst�matiquement supprim�s)
    Un caract�re de la liste 'ancien' sera remplac� par le caract�re � la m�me place de la liste 'nouveau'
    """
    ancien ="*,/;?|�+<=>������������������������������������������������������������Ѻ�������������������������"
    nouveau="                            E   123 aAaAaAaAaAaAaAcC DeEeEeEeEiIiIiIiInN oOoOoOoOoOoOs  uUuUuUuUyY"
    chaine=chaine[:37-decal] #38 caract�res - decal
    for n in range(len(ancien)): #remplace les caract�res incompatibles
        chaine=chaine.replace(ancien[n],nouveau[n])
    return chaine

def get_freespace(path):
    """
    R�cup�re l'espace disque disponible en utilisant le serveur http de XBMC
    Renvoi l'espace libre en ko.
    Il est donc n�cessaire de mettre en marche le serveur http de XBMC.
    TODO: Voir pour utiliser une builtin � la place ou une fonction python
    """
    try:
        drive=os.path.splitdrive(path)[0][:-1]
        print " **** %s drive freespace ****"%drive
        html=urllib.urlopen("http://127.0.0.1/xbmcCmds/xbmcHttp?command=GetSystemInfoByName&parameter=system.freespace(%s)"%drive).read()
        freespace=int(re.findall(r"(\d+)",html)[0])*1024
        print "Espace disque r�cup�r� avec succ�s : %s ko"%freespace
    except:
        print "Probl�me de r�cup�ration de l'espace disque"
        freespace = 0   
    return freespace



def liste_chaines():
    """
    Renvoi une liste des chaines freebox contenus dans la playlist multiposte
    [ ( NumeroDeChaine , NomDeLaChaine , IDdeLaChaine ) , ... ]
    """
    #R�cup�re le contenu du fichier playlist.m3u de la freebox
    urllib.urlcleanup()
    m3u=urllib.urlopen("http://mafreebox.freebox.fr/freeboxtv/playlist.m3u").read()
    m3u=accents(m3u)

    #liste les chaines contenues dans la playlist
    exp = re.compile(r"#EXTINF:0,(\d*?) - (.*?)\nrtsp://mafreebox.freebox.fr/freeboxtv/stream\?id=(.*?)\n")
    M3Uchannels = exp.findall(m3u) # [ (numero de chaine,nom de la chaine,id de la chaine)
    return M3Uchannels

def get_nom_chaine(chanid):
    """
    Renvoi le tuple de la chaine correspondant � l'ID 'chanid'
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
