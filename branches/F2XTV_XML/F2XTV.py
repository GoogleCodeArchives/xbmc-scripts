# -*- coding: utf-8 -*-

_version = "12/03/08"

import xbmcgui
from time import time as _time, localtime, sleep, strftime

# import xbmc,xbmcgui
# import os
# import time
# import re
# import urllib
# import urllib2
# import socket
# import sys
# import threading
# import shutil,glob
# import StringIO
# from ConfigParser import ConfigParser


from os import getcwd
#dossiers, fichiers et liens
__homedir__ = getcwd().replace(';','')

from os.path import join as chemin
__logodir__ = chemin(__homedir__, "logos")


def getProxyConfig ():
    """
    Récupération de la configuration du Proxy
    """
    from ConfigParser import ConfigParser
    
    Config = chemin(__homedir__, 'F2XTV.ini')
    
    settings = ConfigParser()
    settings.read(Config)
    
    #port du proxy rtsp2http
    port = settings.get('general', 'port')
    
    # version du proxy
    versionProxy = settings.get('general', 'versionProxy')
    
    # chemin où se situe le proxy pour tenter de le démarrer
    proxyPath = chemin(__homedir__, "rtsp2http-%s.py" % versionProxy)
    
    return (port, proxyPath)
    

def getConfig ():
    """
    Récupération de la configuration générale
    """
    
    from ConfigParser import ConfigParser
    
    Config = chemin(__homedir__, 'F2XTV.ini')
    
    settings = ConfigParser()
    settings.read(Config)
    
    # dossier d'enregistrement
    records = settings.get('general','records')
    
    #port du proxy rtsp2http
    port = settings.get('general', 'port')
    
    # adresse pour accéder à une chaine sur le proxy
    adresseLocale = 'http://127.0.0.1:%s/freeboxtv/' % port
    
    return (records, adresseLocale)
    

#gestion des exceptions d'arrêt d'enregistrement
StopRec = "StopRec"

#Espace libre à conserver en cas de disque plein
MINIFREESPACE = 204800 # int en ko (204800ko = 200Mo)

#taille de fractionnement des fichiers
MAXFILESIZE = 307200 # int en ko (307200ko = 300Mo)

#keymap
ACTION_GAUCHE   = 1
ACTION_DROITE   = 2
ACTION_HAUT     = 3
ACTION_BAS      = 4
ACTION_LTRIGGER = 5
ACTION_RTRIGGER = 6
ACTION_SELECT   = 7
ACTION_B        = 9
ACTION_Y        = 18
ACTION_BACK     = 10
ACTION_INFO     = 11
ACTION_PAUSE    = 12
ACTION_STOP     = 13
ACTION_X        = 18 # X Button

# ------------------------------------------------------------------- #
def liste_chaines():
    """
    Récupère le contenu du fichier playlist.m3u dans la freebox
    """
    from urllib import urlcleanup, urlopen
    urlcleanup()
    m3u=urlopen("http://mafreebox.freebox.fr/freeboxtv/playlist.m3u").read().decode('utf8')
    
#     m3u = open(chemin(__homedir__,'playlist.m3u')).read().decode('utf-8')

    #liste les chaines contenues dans la playlist
    try:
        from re import compile
        # [ (numero de chaine,nom de la chaine,id de la chaine)
        exp = compile(r"#EXTINF:0,(\d+?) - ([^\r\n]*?)\nrtsp://mafreebox\.freebox.fr/freeboxtv/.*?(\d+)")
        M3Uchannels = exp.findall(m3u)
    except Exception, erreur:
        print "exception dans la recherche des chaines"
        print erreur
    return M3Uchannels


# ------------------------------------------------------------------- #
def verifrep(repertoire):
    """cree le repertoire si il n'existe pas deja"""
    try:
        os.makedirs(repertoire)
    except:
        pass

# ------------------------------------------------------------------- #
def get_freespace(path):
    """
    Récupères l'espace libre dans le dossier d'enregistrement
    """
    from os.path import splitdrive
    from xbmc import getInfoLabel
    from re import findall
    
    try:
        drive = splitdrive(path)[0][0]
        print " **** %s drive freespace ****" % drive
        labelFreespace = getInfoLabel ('System.Freespace(%s)' % drive)
        print labelFreespace
        freespace = int(findall(r"(\d+)",labelFreespace)[0])*1024/1000
        print "Espace disque récupéré avec succès : %s Mo"%freespace
    except:
        print "Problème de récupération de l'espace disque"
        freespace = -1
    return freespace


# ------------------------------------------------------------------- #
def ServerStatus(url):
    """
    Vérifies si le serveur est actif sinon retour le code d'erreur
    """
    from urllib import urlcleanup, urlopen
    from re import findall
    try:
        urlcleanup()
        serve = urlopen(url)
        typ = serve.info().getheader("Content-Type","")
        if typ.startswith("text/html"):
            taille = int(serve.info().getheader("Content-Length",""))
            html = serve.read(taille)
            try:
                code = findall(r'\(error (.*?)\)',html)[0]
            except:
                code = '0'
                if html.find("<H1>Not Found</H1>"):
                    code="404"
            return int(code)
        else:
            return 200
    except Exception,erreur:
        return None

# ------------------------------------------------------------------- #
class F2XTV (xbmcgui.WindowXML):

    def __init__(self,strXMLname, strFallbackPath, strDefaultName, forceFallback=1):
        try:
            (self.records,self.adresseLocale) = getConfig ()
            
            #création du dossier des enregistrements
            verifrep(self.records)
            
            #variables
            self.eteindre     = "NON"
            self.decale       = False
            self.temps        = _time()
            self.REC          = False
            self.MODE         = "TV"           #  pour les chaines freebox
            #self.MODE         = "FILE"         # pour les enregistrements effectués
            self.freespace    = get_freespace( self.records )
            self.chaines      = liste_chaines()
            self.proxyrunning = False
            self.Recorder     = None
            
            self.firstStart   = True
            
        except Exception, erreur:
            print '__init__: erreur'
            print erreur
            import traceback
            traceback.print_exc()
            self.quit()
    
    def onInit (self):
        try:
          if self.firstStart:
              #initialisations
              if self.MODE == 'TV' : self.FillChannels()
              else:                  self.FillRecords()
              
              self.info    = self.getControl(100) # label d'infos
              self.labelB  = self.getControl(101) # label du bouton B
              self.labelX  = self.getControl(102) # label du bouton X
              self.labelA  = self.getControl(103) # label du bouton A
              self.btnMode = self.getControl(105) # bouton de mode
              
              self.info.setLabel("    Espace disque disponible (%s) : %s Mo." % (self.records,self.freespace))
              
              self.firstStart = False
        except Exception, erreur:
            print 'onInit: erreur'
            print erreur
            import traceback
            traceback.print_exc()
            self.quit()
        
    
    def FillChannels(self):
        self.clearList()
        for (numchan,nomchan,idchan) in self.chaines:
            self.addItem(
                xbmcgui.ListItem(
                    nomchan,
                    numchan,
                    chemin (__logodir__, '%s.bmp'%idchan),
                    chemin (__logodir__, '%s.bmp'%idchan)
                    )
                )
        
    
    def FillRecords(self):
        self.clearList()
        from glob import glob
        from os.path import split, getsize
        for rec in glob(chemin(self.records, '*.avi')):
            filename = split(rec)[1]
            size = float(getsize(chemin(self.records,filename)))
            unites = ["o","kio","Mio","Gio"]
            for unite in unites:
                if size > 1024.0:
                    size = size/1024.0
                else:
                    filesize = "%.1f %s" % (size,unite)
                    break
            self.ChanList.addItem(
                xbmcgui.ListItem(
                    filename,
                    filesize,
                    chemin(self.records, filename[:-3]+"tbn")
                    )
                )
        
    
    ## GESTION de l'attente avant le debut de l'enregistrement ##
    def testdate(self):
        while self.decale==True:
            y, mo, d, h, mi = localtime()[:5]
            if self.heurechoix == '%.2d:%.2d' % (h, mi):
                if self.jourchoix == '%.2d/%.2d/%d' % (d, mo, y):
                    self.decale = False

                    # vérifie si disponible
                    code = ServerStatus ( "%s%s" % (self.adresseLocale, self.idchandecale) )

                    # interprétation de la disponibilité
                    if code == 200:
                        self.ImageBoutons(" Lecture"," Arreter"," -")
                        self.finenregis = False
                        self.record(self.chainesdecale)
                        self.testfin()

                    elif code==453: # max bandwidth
                        xbmcgui.Dialog().ok("Limite Bande passante",
                            "Votre bande passante ne vous permet pas",
                            "d'obtenir un nouveau flux supplémentaire.")

                    elif not(code):
                        xbmcgui.Dialog().ok("Erreur de proxy",
                            "Le proxy ne semble pas être démarré")

                    else:
                        xbmcgui.Dialog().ok("%s (error code %s)" % (self.nomchandecale, code),
                            "Le multiposte TV ne vous permet pas d'obtenir",
                            "cette chaine. Un redémarrage Freebox permet parfois",
                            "de mettre à jour la liste.")
        
    
    ## GESTION du temps d'enregistrement ##
    def testfin(self):
        while not self.finenregis:
            sleep(2) # evite de lire l'heure en permanence (enfin je crois)
            if self.heurefinchoix == '%.2d:%.2d' % localtime()[3:5]:
                self.ImageBoutons(" Regarder TV"," Quick Rec."," Prog Rec.")
                self.finenregis = True
                self.REC = False
                self.info.setLabel("      Enregistrement fini")
                self.Recorder.stop()        #arrêt de l'enregistrement
                if self.eteindre == "OUI":    #test si souhait eteindre
                    self.close()
                    sleep(2) # pourquoi 2: pour etre sur de ne pas eteindre sur l'enregistrement(?)
                    from xbmc import shutdown
                    shutdown()


    def ImageBoutons(self,imageA,imageB,imageX):
        self.labelA.setLabel ("%s" % imageA)
        self.labelB.setLabel ("%s" % imageB)
        self.labelX.setLabel ("%s" % imageX)


    def record(self,channel):
        self.ImageBoutons(" Regarder TV"," Arreter"," -")
        numchan,nomchan,idchan = channel
        nomchan = unicode(nomchan,'utf8')[:21]
        self.info.setLabel("Enregistrement de %s en cours ..."%nomchan)
        self.Recorder = Recorder( label    = self.info,
                                  chanid   = idchan,
                                  channame = nomchan,
                                  channum  = numchan) #création du recorder
        self.Recorder.start()
        self.REC = True

    
    def onClick(self, controlID):
        print "onClick(): controlID=%3i" % controlID
        if controlID == 50 and self.Mode == 'TV':
            self.playCanal()
        elif controlID == 50 and self.Mode == 'FILE':
            self.playFile()
        elif controlID == 104 and self.Mode == 'TV':
            self.toggleOnFile()
        elif controlID == 104 and self.Mode == 'FILE':
            self.toggleOnTV()
        
    
    def playCanal (self):
        item = self.getSelectedPosition()
        numchan,nomchan,idchan = self.chaines[item]
        print "play %s%s."%(self.adresseLocale,idchan)
        code = ServerStatus("%s%s"%(self.adresseLocale,idchan))
        if code == 200:
            from xbmc import executebuiltin
            executebuiltin("XBMC.PlayMedia(%s%s)"%(self.adresseLocale,idchan))
        
        elif code == 453: # max bandwidth
            xbmcgui.Dialog().ok("Limite Bande passante",
                "Votre bande passante ne vous permet pas",
                "d'obtenir un nouveau flux supplémentaire.")

        elif not(code):
            xbmcgui.Dialog().ok("Erreur de proxy",
                "Le proxy ne semble pas être démarré")

        else:
            xbmcgui.Dialog().ok(nomchan,
                "Le multiposte TV ne vous permet pas d'obtenir",
                "cette chaine. Un redémarrage Freebox permet parfois",
                "de mettre à jour la liste.")
        
    
    def playFile (self):
        filename = self.getSelectedItem().getLabel()
        print "Lance la lecture de : %s" % chemin (self.records, filename)
        player = MyPlayer()
        player.play(chemin (self.records, filename))
        
    
    def toggleOnFile (self):
        self.MODE = "FILE" # bascule de mode
        self.btnMode.setLabel(" Chaines") # nomme le bouton
        if self.REC == True:
            self.ImageBoutons(" ...fichier"," Eviter..."," ...manip...")
        else:
            self.ImageBoutons(" Lecture"," Effacer"," -")
        self.FillRecords() # actualise la liste
        
    
    def toggleOnTV (self):
        self.MODE="TV" # bascule de mode
        self.btnMode.setLabel(" Enregistrements") # nomme le bouton
        if self.REC == True:
            self.ImageBoutons(" Regarder TV"," Arreter"," -")
        elif self.decale == True:
            self.ImageBoutons(" Regarder TV"," Annuler P."," -")
        else:
            self.ImageBoutons(" Regarder TV"," Quick Rec."," Prog. Rec.")
        self.FillChannels() # actualise la liste

    
    def onFocus (self, controlID):
        print 'onFocus: controlID %i' % controlID
        pass
    
    def onAction(self, action):
        actionID   = action.getId()
        print "onAction(): actionID=%3i" % actionID
        
        if actionID == ACTION_BACK:
            self.quit()
        elif actionID == ACTION_X and self.MODE == "TV" and not self.decale and not self.REC:
            self.progRec()
        elif actionID == ACTION_B:
            if self.MODE == "TV" and self.getFocusID() == 50:
                if self.decale:
                    self.cancelProg()
                else:
                    if self.REC:
                        self.stopRec()
                    else:
                        self.quickRec()
            elif self.MODE == "FILE":
                self.delFile()
        
    def quit(self):
        if self.REC:
            self.REC=False
            sleep(2) # Pour permettre de terminer l'enregistrement proprement
        self.close()
        
    
    def progRec(self):
        item = self.getSelectedPosition()
        self.numchandecale, self.nomchandecale, self.idchandecale = self.chaines[item]
        self.chainesdecale = self.chaines[item]
        keyboard = xbmcgui.Dialog()
        self.jourchoix = keyboard.numeric(1, 'Entrer le jour')
        self.jourchoix = self.jourchoix.replace(" ","0")
        self.heurechoix = keyboard.numeric(2, 'Entrer l heure de début')
        self.heurechoix = self.heurechoix.replace(" ","0")
        self.heurefinchoix = keyboard.numeric(2, 'Entrer l heure de fin')
        self.heurefinchoix = self.heurefinchoix.replace(" ","0")
        dialog = xbmcgui.Dialog()
        if dialog.yesno(unicode(self.nomchandecale,'ut8'),
            "Voulez-vous eteindre la console à la fin",
            "de l'enregistrement ?!"):
            self.eteindre="OUI"
        else:
            self.eteindre="NON"
        dialog=xbmcgui.Dialog()
        if dialog.yesno("%s le %s"%(unicode(self.nomchandecale, 'utf8'), self.jourchoix),
            "Heure de Début %s - Heure de Fin %s"%(self.heurechoix,self.heurefinchoix),
            "Eteindre la console après l'enregistrement : %s"%(self.eteindre),
            "                                       Valider ?"):
            self.ImageBoutons(" Regarder TV"," Annuler P."," -")
            self.info.setLabel("      %s le %s, de %s à %s."%(unicode(self.nomchandecale,'utf8'),self.jourchoix,self.heurechoix,self.heurefinchoix))
            self.decale = True
            self.testdate()
        
    
    def cancelProg(self):
        self.decale = False
        self.info.setLabel(" Programmation interrompu")
        self.ImageBoutons(" Regarder TV"," Quick Rec."," Prog. Rec.")
        
    
    def stopRec(self):
        self.finenregis = True
        self.REC = False
        self.Recorder.stop() # arrêt de l'enregistrement
        self.info.setLabel(" Enregistrement interrompu")
        self.ImageBoutons(" Regarder TV"," Quick Rec."," Prog. Rec.")
        
    
    def quickRec(self):
        item = self.getSelectedPosition()
        numchan,nomchan,idchan = self.chaines[item]
        dialog = xbmcgui.Dialog()
        if dialog.yesno(unicode(nomchan,'utf8'),
            "Etes-vous sur de vouloir enregistrer cette chaine ?"):
            #vérifie si disponibilité
            code = ServerStatus("%s%s"%(ADDRESSFTV,idchan))

            #interprétation de la disponibilité
            if code == 200:
                self.record(self.chaines[item])

            elif code == 453: # max bandwidth
                xbmcgui.Dialog().ok("Limite Bande passante",
                    "Votre bande passante ne vous permet pas",
                    "d'obtenir un nouveau flux supplémentaire.")

            elif not(code):
                xbmcgui.Dialog().ok("Erreur de proxy",
                    "Le proxy ne semble pas être démarré")

            else:
                xbmcgui.Dialog().ok(nomchan,
                    "Le multiposte TV ne vous permet pas d'obtenir",
                    "cette chaine. Un redémarrage Freebox permet parfois",
                    "de mettre à jour la liste.")
        
    
    def delFile(self):
        print "mode : FILE / bouton B"
        filename = self.getSelectedItem().getLabel() #1- on retrouve la vidéo pointée
        if xbmcgui.Dialog().yesno("Suppression", #2- on supprime le fichier
            "Etes vous sur de vouloir supprimer ce fichier :",
            "%s"%filename):
            try:
                from os import remove
                remove(chemin(self.records,filename))
                remove(chemin(self.records,filename[:-3]+"tbn"))
            except:
                print "erreur lors de la suppression"
        self.FillRecords()                          #3- on actualise la liste


# ------------------------------------------------------------------- #
from xbmc import Player
class MyPlayer (Player):
    def __init__ ( self ):
        Player.__init__( self )

    def onPlayBackStarted(self):
        print 'playback started'


# ------------------------------------------------------------------- #
from threading import Thread
class Recorder(Thread):

    def __init__(self,label,chanid,channame,channum):
        self.recording = False
        self.chanid = chanid
        self.channum = channum
        self.channame = channame
        self.info = label
        self.filename = "%s_%s.avi"%(channame,strftime("%d%m%y_%Hh%M",localtime()))
        (self.records, self.adresseLocale) = getConfig()
        Thread.__init__(self)
#        self.filesize=0
        
    
    def run(self):
        from urllib2 import Request, urlopen, HTTPError
        TV = Request("%s%s"%(self.adresseLocale,self.chanid))
        try:
            handle = urlopen(TV)
        except HTTPError, e:
            self.filename = self.filename[:-3] + 'htm'
            open ( chemin(self.records, self.filename), 'wb', 1 ).write(handle.read(2048))
        else:
            self.recording = True
            rec = open ( chemin(self.records, self.filename), 'wb', 1 )
            starttime=_time()
            while self.recording:
#                 self.info.setLabel("   %.3f Mo en %i sec."%(self.filesize/1024.0,_time()-starttime) )
                datas = handle.read(1024)
                rec.write ( datas )
#                 self.filesize += 1
            
            rec.close()
            del rec, handle
            
            # création d'un tbn
            try:
                from shutil import copyfile
                copyfile(chemin (__logodir__, "%s.bmp"%self.chanid) , chemin (self.records, self.filename[:-3]+"tbn"))
            except:
                print "Erreur de création du .tbn"
        del TV
        
    
    def stop(self):
        self.recording = False


# ------------------------------------------------------------------- #
if __name__ == '__main__':
    
    # Configuration du temps limite pour attendre une réponse du serveur
    from socket import setdefaulttimeout
    setdefaulttimeout (2.0) # 2 secondes
    
    (port, proxyPath) = getProxyConfig ()
    
    # Lances le proxy s'il n'est pas déjà actif
    if not (ServerStatus("http://127.0.0.1:%s/bla" % port)):
        from xbmc import executescript
        executescript(proxyPath)
    
    w = F2XTV('script_F2XTV.xml', __homedir__, 'Default')
    w.doModal()
    del w
    