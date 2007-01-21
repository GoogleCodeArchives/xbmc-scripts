# -*- coding: cp1252 -*-              #
#   F2XTV script python pour XBMC     #
#       par ALEXSOLEX                 #
#######################################


# Si vous voulez changer le dossier de destination des enregistrements,
# veuillez indiquer le chemin complet ici.
#   - les \ doivent être absolument doublés
#   - le chemin doit terminer absolument par \\
RECORDS = "E:\\videos\\"
#############
# A PARTIR D'ICI, NE CHANGEZ RIEN SI VOUS NE SAVEZ PAS CE QUE VOUS FAITES
####################################################
#     /!\          /!\         /!\         /!\     #
####################################################

_version = "04/11/06"


import xbmc,xbmcgui
import os
import time
import urllib,re,thread
import socket
import sys
import threading
import shutil,glob
import StringIO

#dossiers, fichiers et liens
HOMEDIR = os.getcwd()[:-1]+"\\"
PICSDIR = HOMEDIR + "pics\\"
LOGODIR = HOMEDIR + "logos\\"

#chemin où se situe le proxy pour tenter de le démarrer
ProxyPath = HOMEDIR + "rtsp2http-0.0.7.py"

#gestion des exceptions d'arrêt d'enregistrement
StopRec = "StopRec"

#Espace libre à conserver en cas de disque plein
MINIFREESPACE = 204800 # int en ko (204800ko = 200Mo)

#taille de fractionnement des fichiers
MAXFILESIZE = 307200 # int en ko (307200ko = 300Mo)

#taille du cache pour la prévisualisation
CACHESIZE = 1024000 # taille en octets

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

def liste_chaines():
    #Récupère le contenu du fichier playlist.m3u dans la freebox
    urllib.urlcleanup()
    m3u=urllib.urlopen("http://mafreebox.freebox.fr/freeboxtv/playlist.m3u").read()

    #liste les chaines contenues dans la playlist
    try:
        #exp = re.compile(r"#EXTINF:0,(\d*?) - (.*?)\nrtsp://mafreebox\.freebox\.fr/freeboxtv/(?:stream\?id=(\d*?)|\d*?)\n")
        exp = re.compile(r"#EXTINF:0,(\d+?) - (.*?)\nrtsp://mafreebox\.freebox.fr/freeboxtv/.*?(\d+)\n")
        M3Uchannels = exp.findall(m3u) # [ (numero de chaine,nom de la chaine,id de la chaine)
    except Exception, erreur:
        print "exception dans la recherche des chaines"
        print erreur
    return M3Uchannels

def verifrep(repertoire): #cree le repertoire si il n'existe pas deja
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
        freespace=int(re.findall(r"(\d+)",html)[0])*1024
        print "Espace disque récupéré avec succès : %s ko"%freespace
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
        self.temps = time.time()
        self.REC=False
        self.MODE="TV" #MODE=TV pour les chaines freebox / MODE=FILE pour les enregistrements effectués
        self.freespace=get_freespace( RECORDS )
        self.chaines=liste_chaines()
        self.proxyrunning=False
        self.Recorder=None #contiendra le thread ### 3ieme solution
        #initialisations
        self.GUI()
        self.FillChannels()
        #création du dossier des enregistrements
        verifrep(RECORDS)

        self.info.setLabel("Espace disque disponible (%s) : %s ko"%(RECORDS,self.freespace))

        #focus initial
        self.setFocus(self.btnMode)


        
    def GUI(self):
        #BACKGROUND
        self.addControl(xbmcgui.ControlImage(0,0,720,576, 'background.png'))

        #logo
        self.addControl(xbmcgui.ControlImage(50,56,196,26, PICSDIR+'freemultiposte.gif'))

        #label d'infos
        self.info=xbmcgui.ControlLabel(50,85,620,50,"démarrage en cours...",'font13','0xFFFFFFFF')
        self.addControl(self.info)

        #label d'enregistrement
        self.reclabel=xbmcgui.ControlLabel(250,56,400,50,"",'font14','0xFFCC1111')
        self.addControl(self.reclabel)

        #bouton de mode
        self.btnMode=xbmcgui.ControlButton(50,110,150,30,' Enregistrements')
        self.addControl(self.btnMode)
        
        #bouton de preview
        self.btnPreview=xbmcgui.ControlButton(50,150,150,30,' Prévisualiser')
        self.addControl(self.btnPreview)
        self.btnPreview.setVisible(False)
        
        #Liste des chaines
        #   Initialisation
        self.ChanList=xbmcgui.ControlList(200,110,415,430,'font13','0xFFFFFFFF',
                                          imageWidth=30,
                                          imageHeight=30,
                                          itemHeight=30,
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
                    label = nomchan,
                    label2 = numchan,
                    thumbnailImage  = LOGODIR+"%s.bmp"%idchan
                    )
                )
            
    def FillRecords(self):
        self.ChanList.reset()
        for rec in glob.glob(RECORDS+ '*.avi'):
            filename=os.path.split(rec)[1]
            size=float(os.path.getsize(RECORDS+filename))
            unites=["o","ko","Mo","Go"]
            for unite in unites:
                if size>1024.0:
                    size=size/1024.0
                else:
                    filesize="%.1f %s"%(size,unite)
                    break
            self.ChanList.addItem(
                xbmcgui.ListItem(
                    label = filename,
                    label2 = filesize,
                    thumbnailImage  = RECORDS+filename[:-3]+"tbn"
                    )
                )


    def hook(self,count_blocks,block_size, total_size):#pour la première solution de reccord
        filesize = count_blocks*block_size/1024
        #rafraichit le label toutes les demi-secondes
        if time.time()-1>self.temps:
            self.info.setLabel("%s Ko - Reste %s Ko d'espace disque disponible sur %s"%(filesize,self.freespace,os.path.splitdrive(RECORDS)[0]))
            self.temps=time.time()
        self.freespace-=block_size/1024
        if self.freespace<=MINIFREESPACE: raise StopRec , "FULL"
        if filesize>=MAXFILESIZE: raise StopRec , "MAX"
        if not(self.REC): raise StopRec , "STOP"


    def record1(self,channel):
        #première solution :
        #-enregistrement par urlretrieve + hook
        #
        #lance l'enregistrement :
        #    channel :: tuple (num chaine, nom chaine, id chaine)

        numchan,nomchan,idchan = channel
        filename = "%s_%s.avi"%(nomchan,time.strftime("%d%m%y_%Hh%M",time.localtime()))
        print "Préparation à l'enregistrement du fichier %s dans %s..."%(RECORDS,filename)
        print "URL : http://127.0.0.1:8083/freeboxtv/%s"%idchan
        try:
            f=open(HOMEDIR+"recording","w")
            f.write("Enregistrement en cours de la chaine %s !"%nomchan)
            f.close()
        except:
            print "Impossible d'écrire le fichier flag 'recording'"
        try:
            starttime=time.time()
            self.REC = True
            urllib.urlcleanup()
            self.reclabel.setLabel("Enregistrement... [%s]"%nomchan)
            #self.temps=time.time()
            recording=urllib.urlretrieve( "http://127.0.0.1:8083/freeboxtv/%s"%idchan, RECORDS + filename, self.hook)
            #tv=urllib.urlopen("http://127.0.0.1:8083/freeboxtv/%s"%idchan)

                
        except StopRec , reason:
            print "L'enregistrement s'est termine : %s"%reason
            try:
                os.remove(HOMEDIR+"recording")
            except:
                print " Le flag d'enregistrement n'a pas pu etre supprime"
            self.REC = False
            #del recording
            if reason=="STOP":
                self.info.setLabel("Enregistrement stoppé. Fichier %s dans %s (%.1f sec)"%(filename,RECORDS,(time.time()-starttime)) )
                self.reclabel.setLabel("")
            elif reason=="MAX": self.info.setLabel("La taille maxi du fichier est atteinte (%s ko)"%MAXFILESIZE)
            elif reason=="FULL": self.info.setLabel("L'espace disque est devenu trop faible !! (reste %s ko)"%MINIFREESPACE)
            else: self.info.setLabel("autre raison de l'arrêt")
    
        #création d'un tbn
        try:
            print LOGODIR+"%s.bmp"%idchan
            print RECORDS+filename[:-3]+"tbn"
            shutil.copyfile(LOGODIR+"%s.bmp"%idchan , RECORDS+filename[:-3]+"tbn")
        except:
            print "Erreur de création du .tbn"
        #return filename
            
##    def record2(self,channel):
##        #2ieme solution :
##        #-enregistrement par urlopen().read() dans une boucle
##        #
##        #lance l'enregistrement :
##        #    channel :: tuple (num chaine, nom chaine, id chaine)
##
##        numchan,nomchan,idchan = channel
##        filename = "%s_%s.avi"%(nomchan,time.strftime("%d%m%y_%Hh%M",time.localtime()))
##        print "Préparation à l'enregistrement du fichier %s dans %s..."%(RECORDS,filename)
##        print "URL : http://127.0.0.1:8083/freeboxtv/%s"%idchan
##        starttime=time.time()
##        try:
##            urllib.urlcleanup()
##            tv=urllib.urlopen("http://127.0.0.1:8083/freeboxtv/%s"%idchan)
##        except:
##            print "Impossible d'ouvrir la connection"
##            return
##        try:
##            rec=open(RECORDS + filename,"wb")
##        except:
##            print "impossible de créer le fichier d'enregistrement"
##        #f=open(HOMEDIR+"recording","w")
##        #f.write("Enregistrement en cours de la chaine %s !"%nomchan)
##        #f.close()
##        self.REC = True
##        filesize=0
##        print "go go go"
##        while self.REC:
##            rec.write(tv.read(1024))
##            filesize+=1
##            self.freespace-=1
##            self.info.setLabel("%s Ko"%(filesize))
##            if self.freespace<=MINIFREESPACE:
##                self.info.setLabel("L'espace disque est devenu trop faible !! (reste %s ko)"%MINIFREESPACE)
##                print "FULL"
##                break
##            elif filesize>=MAXFILESIZE:
##                self.info.setLabel("La taille maxi du fichier est atteinte (%s ko)"%MAXFILESIZE)
##                print "MAX"
##                break
##            elif not(self.REC):
##                self.info.setLabel("Temps écoulé : %.1f secondes"%(time.time()-starttime) )
##        tv.close()
##        rec.close()
##        del tv
##        del rec


    def record(self,channel):
        """3ieme solution : enregistrement sous un thread"""
        numchan,nomchan,idchan = channel
        print numchan
        print nomchan
        print idchan
        self.Recorder = Recorder(label=self.info,chanid=idchan,channame=nomchan,channum=numchan) #création du recorder
        self.Recorder.start()
        self.REC = True
        self.btnPreview.setVisible(True)
        self.btnMode.controlDown(self.btnPreview)
        self.btnPreview.controlUp(self.btnMode)
        self.btnPreview.controlRight(self.ChanList)

            
    def onControl(self,control):
        if control==self.ChanList:
            if self.MODE=="TV":
                #if not(self.REC):
                    item=self.ChanList.getSelectedPosition()
                    numchan,nomchan,idchan = self.chaines[item]
                    #player=MyPlayer()
                    print "play http://127.0.0.1:8083/freeboxtv/%s."%idchan
                    code = ServerStatus("http://127.0.0.1:8083/freeboxtv/%s"%idchan)
                    if code==200:
                        xbmc.executebuiltin("XBMC.PlayMedia(http://127.0.0.1:8083/freeboxtv/%s)"%idchan)
                    elif code==453: # max bandwidth
                        xbmcgui.Dialog().ok("Limite Bande passante","Votre bande passante ne vous permet pas",
                                            "d'obtenir un nouveau flux supplémentaire.")
                    elif not(code):
                        xbmcgui.Dialog().ok("Erreur de proxy","Le proxy ne semble pas être démarré")
                    else:
                        xbmcgui.Dialog().ok(nomchan,
                                            "Le multiposte TV ne vous permet pas d'obtenir",
                                            "cette chaine. Un redémarrage Freebox permet parfois",
                                            "de mettre à jour la liste.")
                    #pls=xbmc.PlayList(3)
                    #pls.add("http://192.168.0.3:8083/freeboxtv/%s"%idchan,nomchan,0)

                    #player = xbmc.Player()#xbmc.PLAYER_CORE_MPLAYER
                    #player.play(pls)
                    #while player.isPlaying():
                    #    pass
                    #del player
                #else:
                #    self.reclabel.setLabel("Enregistrement en cours")
            elif self.MODE == "FILE":
                filename=self.ChanList.getSelectedItem().getLabel()
                print "Lance la lecture de :"
                print RECORDS+filename
                player=MyPlayer()
                player.play(RECORDS+filename)

        if control == self.btnMode:
            if self.MODE=="TV":
                self.MODE="FILE"#bascule de mode
                self.btnMode.setLabel(" Chaines")#nomme le bouton
                self.FillRecords()#actualise la liste
                #self.setFocus(self.ChanList)#donne le focus à la liste
            elif self.MODE=="FILE":
                self.MODE="TV"#bascule de mode
                self.btnMode.setLabel(" Enregistrements")#nomme le bouton
                self.FillChannels()#actualise la liste
                #self.setFocus(self.ChanList)#donne le focus à la liste
    
        if control==self.btnPreview and self.Recorder:#appui sur le bouton preview SI le recorder est lancé
            if self.Recorder.recording:
                self.Recorder.preview = False
                self.Recorder.caching = True
                time.sleep(0.1)
                while not(self.Recorder.preview):
                    pass
                try:
                    player=MyPlayer()
                    player.play(HOMEDIR + "preview.avi")
                except:
                    print "Erreur, impossible de jouer le preview"
                #ici on peut loop pour éviter la détection du bouton B si besoin

           
    def onAction(self, action):
        if action == ACTION_BACK:
            self.REC=False
            self.close()
        if action == ACTION_B:
            if self.MODE == "TV":
                if self.getFocus()==self.ChanList:
                    if self.REC:
                        self.REC=False
                        self.info.setLabel("Enregistrement interrompu")
                        #suppression du bouton preview et de ses mouvements
                        self.btnPreview.setVisible(False)
                        self.btnMode.controlDown(self.btnMode)
                        #arrêt de l'enregistrement
                        self.Recorder.stop()
                    else:
                        item=self.ChanList.getSelectedPosition()
                        numchan,nomchan,idchan = self.chaines[item]
                        dialog=xbmcgui.Dialog()
                        if dialog.yesno(nomchan,"Etes-vous sur de vouloir enregistrer cette chaine ?"):
                            #vérifie si disponibilité
                            code = ServerStatus("http://127.0.0.1:8083/freeboxtv/%s"%idchan)
                            #interprétation de la disponibilité
                            if code==200:
                                self.record(self.chaines[item])
                            elif code==453: # max bandwidth
                                xbmcgui.Dialog().ok("Limite Bande passante","Votre bande passante ne vous permet pas",
                                                    "d'obtenir un nouveau flux supplémentaire.")
                            elif not(code):
                                xbmcgui.Dialog().ok("Erreur de proxy","Le proxy ne semble pas être démarré")
                            else:
                                xbmcgui.Dialog().ok(nomchan,
                                                    "Le multiposte TV ne vous permet pas d'obtenir",
                                                    "cette chaine. Un redémarrage Freebox permet parfois",
                                                    "de mettre à jour la liste.")
                        else:
                            pass
                else:
                    pass
            elif self.MODE == "FILE":
                print "mode : FILE / bouton B"
                #item=self.ChanList.getSelectedPosition()
                listitem = self.ChanList.getSelectedItem()
                #1- on retrouve la vidéo pointé
                filename = listitem.getLabel()
                #2- on supprime le fichier
                if xbmcgui.Dialog().yesno("Suppression",
                                          "Etes vous sur de vouloir supprimer ce fichier :",
                                          "%s"%filename):
                    try:
                        os.remove(RECORDS+filename)
                        os.remove(RECORDS+filename[:-3]+"tbn")
                    except:
                        print "erreur lors de la suppression"
                #3- on actualise la liste
                self.FillRecords()
                pass
            else:#autre mode
                pass
            



class MyPlayer( xbmc.Player ) :
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
        self.caching = False # activation du cache pour générer la preview
        self.preview = False # disponibilité de la preview
        self.filename = "%s_%s.avi"%(channame,time.strftime("%d%m%y_%Hh%M",time.localtime()))
        self.filesize = 0
        self.memfile = StringIO.StringIO() # fichier mémoire recevant les données le temps de la mise en cache

    def run(self):
        TV = urllib.urlopen("http://127.0.0.1:8083/freeboxtv/%s"%self.chanid)
        self.recording = True
##        try:
##            rec = os.open(RECORDS + self.filename,os.O_RDWR)
##            print "REC EST OK avec os.open"
##        except:
##            print "ERREUR DE CREATION DU REC"
        rec = open(RECORDS + self.filename,"wb")
            
        starttime=time.time()
        while self.recording:
            self.info.setLabel("%.3f ko en %i sec."%(self.filesize/1024.0,time.time()-starttime) )
            datas = TV.read(1024)
            rec.write(datas)
            #os.write(rec,datas)
            self.filesize+=1
            if self.caching:
                self.memfile.write(datas)
                if self.memfile.len > CACHESIZE: #si le cache est rempli :
                    print "Fin du caching ! Ecriture de preview.avi"
                    # - on écrit le fichier preview
                    f = open(HOMEDIR + "preview.avi","wb")
                    f.write(self.memfile.getvalue())
                    f.close()
                    # - on réinitialise pour la suite
                    self.caching = False #fin de la mise en cache
                    self.preview = True #fichier de preview disponible
                    self.memfile.close()
                    self.memfile = StringIO.StringIO()
                else:
                    pass
            else: #pas de mise en cache demandée
                pass
        #l'enregistrement doit se terminer
        # - fermeture des fichiers
        TV.close()
        rec.close()
        #os.close(rec)
        self.memfile.close()
        del TV, rec, self.memfile
        #création d'un tbn
        try:
            print LOGODIR+"%s.bmp"%self.chanid
            print RECORDS+self.filename[:-3]+"tbn"
            shutil.copyfile(LOGODIR+"%s.bmp"%self.chanid , RECORDS+self.filename[:-3]+"tbn")
        except:
            print "Erreur de création du .tbn"        
        #réinitialisation
        self.preview=False

    def stop(self):
        self.recording = False


#teste si le proxy est déjà lancé
if not(ServerStatus("http://127.0.0.1:8083/bla")):
    xbmc.executescript(ProxyPath)


socket.setdefaulttimeout(2)
            
go=main()
go.doModal()
del go
