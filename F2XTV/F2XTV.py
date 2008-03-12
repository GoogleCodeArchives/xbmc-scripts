# -*- coding: cp1252 -*-              #
#   F2XTV script python pour XBMC     #
#       par ALEXSOLEX                 #
#######################################

# modif du 10/03/2008 par nioc_bertheloneum et AlexSolex:
# - Correction de l'erreur d'absence d'attribut _Thread__stopped du Recorder
# - Suppression de la mise à jour temps réel du label pour afficher le temps d'enregistrement (perturbe l'enregistrement du fichier)
# - changement de bibliothèque pour la récupération du flux dans le Recorder (urllib -> urllib2)
# - suppression de commentaires inutiles

# modif du 23/04/2007 par nioc_bertheloneum:
# - le chemin d'enregistrement est modifiable dans le fichier F2XTV.ini
# - le port du 'proxy' est modifiable dans le fichier F2XTV.ini
# - le skin est modifiable dans le fichier S2XTV.ini (deux choix: 0 ou 1)
# - intégration de la modification du script par piproix
# - intégration de la modification du skin par blondin000

_version = "10/03/08"

import xbmc,xbmcgui
import os
import time
import re
import urllib
import urllib2
import socket
import sys
import threading
import shutil,glob
import StringIO
from ConfigParser import ConfigParser

chemin = os.path.join

#dossiers, fichiers et liens
d = os.getcwd()
if d[-1] == ';': d = d[:-1]

HOMEDIR = d
PICSDIR = chemin(HOMEDIR, "pics")
LOGODIR = chemin(HOMEDIR, "logos")

Config = chemin('Q:', 'userdata', 'F2XTV.ini')
if not os.path.isfile (Config) :
  Config = chemin(HOMEDIR, 'F2XTV.ini')
  

settings = ConfigParser()
settings.read(Config)
RECORDS = settings.get('general','records')
#port du proxy rtsp2http
PORT = settings.get('general', 'port')
ADDRESSFTV = 'http://127.0.0.1:%s/freeboxtv/' % PORT

#indice de l'interface graphique (0 = défaut, 1 = blondin000)
indGUI = settings.getint('general', 'gui')

#chemin où se situe le proxy pour tenter de le démarrer
ProxyPath = chemin(HOMEDIR, "rtsp2http-0.0.7.py")

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

def liste_chaines():
    #Récupère le contenu du fichier playlist.m3u dans la freebox
    urllib.urlcleanup()
    m3u=urllib.urlopen("http://mafreebox.freebox.fr/freeboxtv/playlist.m3u").read()
    
    #liste les chaines contenues dans la playlist
    try:
        # [ (numero de chaine,nom de la chaine,id de la chaine)
        exp = re.compile(r"#EXTINF:0,(\d+?) - (.*?)\nrtsp://mafreebox\.freebox.fr/freeboxtv/.*?(\d+)\n")
        M3Uchannels = exp.findall(m3u)
    except Exception, erreur:
        print "exception dans la recherche des chaines"
        print erreur
    return M3Uchannels

def verifrep(repertoire):
    """cree le repertoire si il n'existe pas deja"""
    try:
        os.makedirs(repertoire)
    except:
        pass

def suppr_balises(data): # OK A GARDER
    """
    Supprime les balises html dans le 'html' (string)
    Renvoi un 'string' sans les balises html.
    Le caractère '&nbsp' est remplacé par un espace
    """
    exp=r"""<.*?>"""
    compile_obj = re.compile(exp,  re.IGNORECASE| re.DOTALL)
    match_obj = compile_obj.search(data)
    retour = compile_obj.subn('',data, 0)[0]
    retour=retour.replace("&nbsp;"," ")
    return retour

def get_freespace(path):
    #freespace = 512000
    try:
        drive=os.path.splitdrive(path)[0][:-1]
        print " **** %s drive freespace ****"%drive
        html=urllib.urlopen("http://127.0.0.1/xbmcCmds/xbmcHttp?command=GetSystemInfoByName&parameter=system.freespace(%s)"%drive).read()
        freespace=int(re.findall(r"(\d+)",html)[0])*1024/1000
        print "Espace disque récupéré avec succès : %s Mo"%freespace
    except:
        print "Problème de récupération de l'espace disque"
        freespace = 0   
    return freespace

def ServerStatus(url):
    try:
        serve = urllib.urlopen(url)
        type = serve.info().getheader("Content-Type","")
        if type.startswith("text/html"):
            taille = int(serve.info().getheader("Content-Length",""))
            html = serve.read(taille)
            try:
                exp=re.compile(r'\(error (.*?)\)')
                code=exp.findall(html)[0]
            except:
                if html.find("<H1>Not Found</H1>"):
                    code="404"
            return int(code)
        else:
            return 200
    except Exception,erreur:
        return None

class main(xbmcgui.Window):
    
    def __init__(self):
        self.setCoordinateResolution(6)
        xbmcgui.Window.__init__(self)
        
        #variables
        self.eteindre    = "NON"
        self.decale        = False
        self.temps        = time.time()
        self.REC        = False
        self.MODE        ="TV" #  pour les chaines freebox
        #self.MODE         = "FILE" pour les enregistrements effectués
        self.freespace    = get_freespace( RECORDS )
        self.chaines    = liste_chaines()
        self.proxyrunning = False
        self.Recorder    = None
        
        #initialisations
        self.GUI()
        self.FillChannels()
        
        #création du dossier des enregistrements
        verifrep(RECORDS)
        
        self.info.setLabel("    Espace disque disponible (%s) : %s Mo." % (RECORDS,self.freespace))
        
        #focus initial
        self.setFocus(self.btnMode)
    
    
    def GUI(self):
        
        # background
        if indGUI == 1: # Blondin basé sur PMIII
            x, y, w, h, image = 0, 0, 720, 576, chemin (PICSDIR, 'Freebox.png')
        else: # AlexSolex basé sur PMIII
            x, y, w, h, image = 0, 0, 720, 576, 'background.png'
        self.addControl(xbmcgui.ControlImage(x, y, w, h, image))
        
        #logo
        if indGUI == 1: # Blondin basé sur PMIII
            x, y, w, h, image = 50, 473, 196, 20, chemin(PICSDIR, 'freemultiposte.gif')
        else: # AlexSolex basé sur PMIII
            x, y, w, h, image = 50,  56, 196, 26, chemin(PICSDIR, 'freemultiposte.gif')
        self.addControl(xbmcgui.ControlImage(x, y, w, h, image))
        
        #label d'infos
        if indGUI == 1: # Blondin basé sur PMIII
            x, y, w, h, label, font, textColor = 250, 470, 620, 50, "démarrage en cours...", 'font13', '0xFFFFFFFF'
        else: # AlexSolex basé sur PMIII
            x, y, w, h, label, font, textColor =  50,  85, 620, 50, "démarrage en cours...", 'font13', '0xFFFFFFFF'
        self.info = xbmcgui.ControlLabel(x, y, w, h, label, font, textColor)
        self.addControl(self.info)
        
        #label d'enregistrement
        # AlexSolex et Blondin basé sur PMIII
        x, y, w, h, label, font, textColor = 250, 56, 400, 50, "", 'font14', '0xFFCC1111'
        self.addControl(xbmcgui.ControlLabel(x, y, w, h, label, font, textColor))
        
        #bouton de mode
        if indGUI == 1: # Blondin basé sur PMIII
            x, y, w, h, label = 87, 230,  15, 15, '     Voir Enregistrements'
        else: # AlexSolex basé sur PMIII
            x, y, w, h, label = 50, 110, 150, 30, ' Enregistrements'
        self.btnMode = xbmcgui.ControlButton(x, y, w, h, label)
        self.addControl(self.btnMode)
        
        #label B
        if indGUI == 1: # Blondin basé sur PMIII
            x, y, w, h, image =  82, 265, 25, 25, chemin(PICSDIR, 'Btn_b.png')
        else: # AlexSolex basé sur PMIII
            x, y, w, h, image = 290,  56, 25, 25, chemin(PICSDIR, 'Btn_b.png')
        self.addControl(xbmcgui.ControlImage(x, y, w, h, image))
        if indGUI == 1: # Blondin basé sur PMIII
            x, y, w, h, label, font, textColor = 114, 266, 620, 50, ' Enregistrement Rapide', 'font13', '0xFFFFFFFF'
        else: # AlexSolex basé sur PMIII
            x, y, w, h, label, font, textColor = 320,  59, 620, 50, ' Quick Rec.', 'font13', '0xFFFFFFFF'
        self.labelB = xbmcgui.ControlLabel(x, y, w, h, label, font, textColor)
        self.addControl(self.labelB)
        
        #label X
        if indGUI == 1: # Blondin basé sur PMIII
            x, y, w, h, image =  82, 306, 25, 25, chemin(PICSDIR, 'Btn_x.png')
        else: # AlexSolex basé sur PMIII
            x, y, w, h, image = 410,  56, 25, 25, chemin(PICSDIR, 'Btn_x.png')
        self.addControl(xbmcgui.ControlImage(x, y, w, h, image))
        if indGUI == 1: # Blondin basé sur PMIII
            x, y, w, h, label, font, textColor = 114, 306, 620, 50, ' Programmation', 'font13', '0xFFFFFFFF'
        else: # AlexSolex basé sur PMIII
            x, y, w, h, label, font, textColor = 440,  59, 620, 50, ' Prog Rec.', 'font13', '0xFFFFFFFF'
        self.labelX = xbmcgui.ControlLabel(x, y, w, h, label, font, textColor)
        self.addControl(self.labelX)
        
        #label A
        if indGUI == 1: # Blondin basé sur PMIII
            x, y, w, h, image =  82, 344, 25, 25, chemin(PICSDIR, 'Btn_a.png')
        else: # AlexSolex basé sur PMIII
            x, y, w, h, image = 530,  56, 25, 25, chemin(PICSDIR, 'Btn_a.png')
        self.addControl(xbmcgui.ControlImage(x, y, w, h, image))
        if indGUI == 1: # Blondin basé sur PMIII
            x, y, w, h, label, font, textColor = 114, 345, 620, 50, ' Regarder TV', 'font13', '0xFFFFFFFF'
        else: # AlexSolex basé sur PMIII
            x, y, w, h, label, font, textColor = 560,  59, 620, 50, ' Regarder TV', 'font13', '0xFFFFFFFF'
        self.labelA = xbmcgui.ControlLabel(x, y, w, h, label, font, textColor)
        self.addControl(self.labelA)
        
        #Liste des chaines
        #   Initialisation
        if indGUI == 1: # Blondin basé sur PMIII
            x, y, w, h, font, textColor, iW, iH, itH = 320, 150, 380, 380, 'font13', '0xFFFFFFFF', 60, 60, 60
        else: # AlexSolex basé sur PMIII
            x, y, w, h, font, textColor, iW, iH, itH = 200, 110, 415, 430, 'font13', '0xFFFFFFFF', 30, 30, 30
        self.ChanList=xbmcgui.ControlList(x, y, w, h, font, textColor,
                                          imageWidth=iW,
                                          imageHeight=iH,
                                          itemHeight=itH,
                                          )
        self.addControl(self.ChanList)
        self.ChanList.setPageControlVisible(True)
        
        #navigation
        self.btnMode.controlRight(self.ChanList)
        self.ChanList.controlLeft(self.btnMode)
    
    
    def FillChannels(self):
        self.ChanList.reset()
        for (numchan,nomchan,idchan) in self.chaines:
            self.ChanList.addItem(
                xbmcgui.ListItem(
                    label    = unicode(nomchan,'utf8'),
                    label2    = numchan,
                    thumbnailImage = chemin (LOGODIR, "%s.bmp"%idchan)
                    )
                )
    
    
    def FillRecords(self):
        self.ChanList.reset()
        for rec in glob.glob(chemin(RECORDS, '*.avi')):
            filename = os.path.split(rec)[1]
            size = float(os.path.getsize(chemin(RECORDS,filename)))
            unites = ["o","kio","Mio","Gio"]
            for unite in unites:
                if size > 1024.0:
                    size = size/1024.0
                else:
                    filesize = "%.1f %s" % (size,unite)
                    break
            self.ChanList.addItem(
                xbmcgui.ListItem(
                    label    = filename,
                    label2    = filesize,
                    thumbnailImage = chemin(RECORDS, filename[:-3]+"tbn")
                    )
                )
    
    ## GESTION de l'attente avant le debut de l'enregistrement ##
    
    def testdate(self):
        while self.decale==True:
            y, mo, d, h, mi = time.localtime()[:5]
            if self.heurechoix == '%.2d:%.2d' % (h, mi):
                if self.jourchoix == '%.2d/%.2d/%d' % (d, mo, y):
                    self.decale = False
                    
                    # vérifie si disponible
                    code = ServerStatus ( "%s%s" % (ADDRESSFTV, self.idchandecale) )
                    
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
                        xbmcgui.Dialog().ok(self.nomchandecale, 
                            "Le multiposte TV ne vous permet pas d'obtenir",
                            "cette chaine. Un redémarrage Freebox permet parfois",
                            "de mettre à jour la liste.")
    
    ## GESTION du temps d'enregistrement ##
    def testfin(self):
        while not self.finenregis:
            time.sleep(2) # evite de lire l'heure en permanence (enfin je crois)
            if self.heurefinchoix == '%.2d:%.2d' % time.localtime()[3:5]:
                if indGUI == 1:
                    self.ImageBoutons(" Regarder TV"," Enregistremment Rapide"," Programmation")
                else:
                    self.ImageBoutons(" Regarder TV"," Quick Rec."," Prog Rec.")
                self.finenregis = True
                self.REC = False
                self.info.setLabel("      Enregistrement fini")
                self.Recorder.stop()        #arrêt de l'enregistrement
                if self.eteindre == "OUI":    #test si souhait eteindre
                    self.close()
                    time.sleep(2) # pourquoi 2: pour etre sur de ne pas eteindre sur l'enregistrement(?)
                    xbmc.shutdown()
    
    
    def ImageBoutons(self,imageA,imageB,imageX):
        self.labelA.setLabel ("%s" % imageA)
        self.labelB.setLabel ("%s" % imageB)
        self.labelX.setLabel ("%s" % imageX)
    
    
    def record(self,channel):
        self.ImageBoutons(" Regarder TV"," Arreter"," -")
        numchan,nomchan,idchan = channel
        nomchan = unicode(nomchan,'utf8')[:21]
        print numchan
        print nomchan
        print idchan
        self.info.setLabel("Enregistrement de %s en cours ..."%nomchan)
        self.Recorder = Recorder( label    = self.info, 
                                  chanid   = idchan, 
                                  channame = nomchan,
                                  channum  = numchan) #création du recorder
        self.Recorder.start()
        self.REC = True
    
    
    def onControl(self,control):
        if control == self.ChanList:
            if self.MODE == "TV":
                item = self.ChanList.getSelectedPosition()
                numchan,nomchan,idchan = self.chaines[item]
                print "play %s%s."%(ADDRESSFTV,idchan)
                code = ServerStatus("%s%s"%(ADDRESSFTV,idchan))
                if code == 200:
                    xbmc.executebuiltin("XBMC.PlayMedia(%s%s)"%(ADDRESSFTV,idchan))
                
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
            
            elif self.MODE == "FILE":
                filename = self.ChanList.getSelectedItem().getLabel()
                print "Lance la lecture de : %s" % chemin (RECORDS, filename)
                player = MyPlayer()
                player.play(chemin (RECORDS, filename))
        
        elif control == self.btnMode:
            if self.MODE=="TV":
                self.MODE = "FILE" # bascule de mode
                if indGUI == 1:
                    self.btnMode.setLabel("     Chaines") # nomme le bouton
                else:
                    self.btnMode.setLabel(" Chaines") # nomme le bouton
                if self.REC == True:
                    self.ImageBoutons(" ...fichier"," Eviter..."," ...manip...")
                else:
                    self.ImageBoutons(" Lecture"," Effacer"," -")
                self.FillRecords() # actualise la liste
            
            elif self.MODE == "FILE":
                self.MODE="TV" # bascule de mode
                if indGUI == 1:
                    self.btnMode.setLabel("     Voir Enregistrements") # nomme le bouton
                else:
                    self.btnMode.setLabel(" Enregistrements") # nomme le bouton
                if self.REC == True:
                    self.ImageBoutons(" Regarder TV"," Arreter"," -")
                elif self.decale == True:
                    self.ImageBoutons(" Regarder TV"," Annuler P."," -")
                else:
                    if indGUI == 1:
                        self.ImageBoutons(" Regarder TV"," Enregistremment Rapide"," Programmation")
                    else:
                        self.ImageBoutons(" Regarder TV"," Quick Rec."," Prog. Rec.")
                self.FillChannels() # actualise la liste
    
    
    def onAction(self, action):
        
        if action == ACTION_BACK:
            self.REC=False
            self.close()
        
        ## GESTION de la touche X pour le delai ##
        elif action == ACTION_X:
            if self.MODE == "TV" and not self.decale and not self.REC:
                item = self.ChanList.getSelectedPosition()
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
        
        elif action == ACTION_B:
            if self.MODE == "TV":
                if self.getFocus() == self.ChanList:
                    if self.decale:
                        self.decale = False
                        self.info.setLabel(" Programmation interrompu")
                        if indGUI == 1:
                            self.ImageBoutons(" Regarder TV"," Enregistremment Rapide"," Programmation")
                        else:
                            self.ImageBoutons(" Regarder TV"," Quick Rec."," Prog. Rec.")
                    else:
                        if self.REC:
                            self.finenregis = True
                            self.REC = False
                            self.Recorder.stop() # arrêt de l'enregistrement
                            self.info.setLabel(" Enregistrement interrompu")
                            if indGUI == 1:
                                self.ImageBoutons(" Regarder TV"," Enregistremment Rapide"," Programmation")
                            else:
                                self.ImageBoutons(" Regarder TV"," Quick Rec."," Prog. Rec.")
                        else:
                            item = self.ChanList.getSelectedPosition()
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
                
            elif self.MODE == "FILE":
                print "mode : FILE / bouton B"
                listitem = self.ChanList.getSelectedItem()
                filename = listitem.getLabel()           #1- on retrouve la vidéo pointé
                if xbmcgui.Dialog().yesno("Suppression", #2- on supprime le fichier
                    "Etes vous sur de vouloir supprimer ce fichier :",
                    "%s"%filename):
                    try:
                        os.remove(chemin(RECORDS,filename))
                        os.remove(chemin(RECORDS,filename[:-3]+"tbn"))
                    except:
                        print "erreur lors de la suppression"
                self.FillRecords()                          #3- on actualise la liste


class MyPlayer (xbmc.Player):
    def __init__ ( self ):
        xbmc.Player.__init__( self )
        
    def onPlayBackStarted(self):
        print 'playback started'


class Recorder(threading.Thread):
    
    def __init__(self,label,chanid,channame,channum):
        self.recording = False
        self.chanid = chanid
        self.channum = channum
        self.channame = channame
        self.info = label
        self.filename = "%s_%s.avi"%(channame,time.strftime("%d%m%y_%Hh%M",time.localtime()))
        threading.Thread.__init__(self)
#        self.filesize=0
    
    def run(self):
        TV = urllib2.Request("%s%s"%(ADDRESSFTV,self.chanid))
        try:
            handle = urllib2.urlopen(TV)
        except urllib2.HTTPError, e:
            self.filename = self.filename[:-3] + 'htm'
            open ( chemin(RECORDS, self.filename), 'wb', 1 ).write(handle.read(2048))
        else:
            self.recording = True
            rec = open ( chemin(RECORDS, self.filename), 'wb', 1 )
        starttime=time.time()
        while self.recording:
#            self.info.setLabel("   %.3f Mo en %i sec."%(self.filesize/1024.0,time.time()-starttime) )
            datas = handle.read(1024)
            rec.write ( datas )
#            self.filesize += 1

        rec.close()
        del TV, rec, handle
        #création d'un tbn
        try:
            shutil.copyfile(chemin (LOGODIR, "%s.bmp"%self.chanid) , chemin (RECORDS, self.filename[:-3]+"tbn"))
        except:
            print "Erreur de création du .tbn"   
    
    def stop(self):
        self.recording = False


#teste si le proxy est déjà lancé
if not(ServerStatus("http://127.0.0.1:%s/bla"%PORT)):
    xbmc.executescript(ProxyPath)


socket.setdefaulttimeout(2)

go=main()
go.doModal()
del go
