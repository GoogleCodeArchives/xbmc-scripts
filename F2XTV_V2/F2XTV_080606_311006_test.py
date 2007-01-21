# -*- coding: cp1252 -*-              #
#   F2XTV script python pour XBMC     #
#       par ALEXSOLEX                 #
#######################################

SETTINGS = "Q\\userdata\\F2XTV\\F2XTV.ini"

# Si vous voulez changer le dossier de destination des enregistrements,
# veuillez indiquer le chemin complet ici.
#   - les \ doivent être absolument doublés
#   - le chemin doit terminer absolument par \\
RECORDS = "E:\\videos\\"
# Liste des chaines dont vous voulez la présence dans la liste
#   - liste complète (au 09/06/06) :
#       [2,3,5,6,7,8,9,11,12,13,14,15,16,17,18,21,22,23,24,37,40,41,42,43,44,52,63,66,75,77,79,80,81,82,83,84,87,96,98,130,131,133,150,151,152,153,154,155,157,158,159,160,209,219,220,224,232,233,239,240,241,242,250,251,252,253,254,259,260,261,262,263,269,270,271,272,288,289,293,294,295,296,297,298,299,300,301,302,303,304,305,306,307,308,310,311,312,313,314,315,316,317,318,319,320,321,322,323,324,999]
MES_CHAINES = [2,3,5,6,7,9,11,13,14,17,18,21,22,23,24,37,44,300,308,319,999]
#############
# A PARTIR D'ICI, NE CHANGEZ RIEN SI VOUS NE SAVEZ PAS CE QUE VOUS FAITES
####################################################
#     /!\          /!\         /!\         /!\     #
####################################################

_version = "30/10/06"


import xbmc,xbmcgui
import os
import time
import urllib,re,thread
import socket
import sys
import threading
import shutil,glob
import StringIO
import thread

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
ACTION_LTRIGGER = 111
ACTION_RTRIGGER = 112
ACTION_SELECT   = 7
ACTION_B        = 9 #back de la télécommande et B rouge du pad
ACTION_Y        = 34
ACTION_X        = 18 #bouton X bleu du pad et display de la télécommande
ACTION_BACK     = 10 #back du pad et 'menu' de la télécommande
ACTION_INFO     = 11 #remote
ACTION_PAUSE    = 12
ACTION_STOP     = 13
ACTION_WHITE    = 117 #bouton title de la télécommande et blanc du pad

#les touches suivantes de la télécommande ne sont pas dispo pour python

#REMOTE_0       = 58  #// remote keys 0-9. are used by multiple windows
#REMOTE_1       = 59  #// for example in videoFullScreen.xml window id=2005 you can
#REMOTE_2       = 60  #// enter time (mmss) to jump to particular point in the movie
#REMOTE_3       = 61
#REMOTE_4       = 62  #// with spincontrols you can enter 3digit number to quickly set
#REMOTE_5       = 63  #// spincontrol to desired value
#REMOTE_6       = 64
#REMOTE_7       = 65
#REMOTE_8       = 66
#REMOTE_9       = 67
#REMOTE_NUM      = [58,59,60,61,62,63,64,65,66,67]

#ACTION_PLAY                 = 68  #// Unused at the moment
#ACTION_OSD_SHOW_LEFT        = 69  #// Move left in OSD. Can b used in videoFullScreen.xml window id=2005
#ACTION_OSD_SHOW_RIGHT       = 70  #// Move right in OSD. Can b used in videoFullScreen.xml window id=2005
#ACTION_OSD_SHOW_UP          = 71  #// Move up in OSD. Can b used in videoFullScreen.xml window id=2005
#ACTION_OSD_SHOW_DOWN        = 72  #// Move down in OSD. Can b used in videoFullScreen.xml window id=2005
#ACTION_OSD_SHOW_SELECT      = 73  #// toggle/select option in OSD. Can b used in videoFullScreen.xml window id=2005
#ACTION_OSD_SHOW_VALUE_PLUS  = 74  #// increase value of current option in OSD. Can b used in videoFullScreen.xml window id=2005
#ACTION_OSD_SHOW_VALUE_MIN   = 75  #// decrease value of current option in OSD. Can b used in videoFullScreen.xml window id=2005
#ACTION_SMALL_STEP_BACK      = 76  #// jumps a few seconds back during playback of movie. Can b used in videoFullScreen.xml window id=2005

#ACTION_PLAYER_FORWARD       = 77  #// FF in current file played. global action, can be used anywhere
#ACTION_PLAYER_REWIND        = 78  #// RW in current file played. global action, can be used anywhere
#ACTION_PLAYER_PLAY          = 79  #// Play current song. Unpauses song and sets playspeed to 1x. global action, can be used anywhere

#ACTION_DELETE_ITEM          = 80  #// delete current selected item. Can be used in myfiles.xml window id=3 and in myvideoTitle.xml window id=25
#ACTION_COPY_ITEM            = 81  #// copy current selected item. Can be used in myfiles.xml window id=3
#ACTION_MOVE_ITEM            = 82  #// move current selected item. Can be used in myfiles.xml window id=3
#ACTION_SHOW_MPLAYER_OSD     = 83  #// toggles mplayers OSD. Can be used in videofullscreen.xml window id=2005
#ACTION_OSD_HIDESUBMENU      = 84  #// removes an OSD sub menu. Can be used in videoOSD.xml window id=2901
#ACTION_TAKE_SCREENSHOT      = 85  #// take a screenshot
#ACTION_POWERDOWN            = 86  #// restart
#ACTION_RENAME_ITEM          = 87  #// rename item

#ACTION_VOLUME_UP            = 88
#ACTION_VOLUME_DOWN          = 89
#ACTION_MUTE                 = 91

def liste_chaines():
    #Récupère le contenu du fichier playlist.m3u dans la freebox
    urllib.urlcleanup()
    m3u=urllib.urlopen("http://mafreebox.freebox.fr/freeboxtv/playlist.m3u").read()
    m3u=accents(m3u)

    #liste les chaines contenues dans la playlist
    exp = re.compile(r"#EXTINF:0,(\d*?) - (.*?)\nrtsp://mafreebox.freebox.fr/freeboxtv/stream\?id=(.*?)\n")
    M3Uchannels = exp.findall(m3u) # [ (numero de chaine,nom de la chaine,id de la chaine)
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

def accents(chaine):
    chaine=chaine.replace("Ã©","é")
    chaine=chaine.replace("Ã®","î")
    chaine=chaine.replace("Ã¨","è")
    chaine=chaine.replace("Ã´","ô")    
    return chaine

def FatX(chaine,decal=0):
    ancien ="*,/;?|¿+<=>±«»×÷¢£¤¥§©¬®°µ¶·€¼½¾¹²³ªáÁàÀâÂäÄãÃåÅæÆçÇðÐéÉèÈêÊëËíÍìÌîÎïÏñÑºóÓòÒôÔöÖõÕøØßþÞúÚùÙûÛüÜýÝ"
    nouveau="                                    aAaAaAaAaAaAaAcC DeEeEeEeEiIiIiIiInN oOoOoOoOoOoOs  uUuUuUuUyY"
    chaine=chaine[:37-decal] #38 caractères - decal
    for n in range(len(ancien)): #remplace les caractères incompatibles
        chaine=chaine.replace(ancien[n],nouveau[n])
    return chaine



class main(xbmcgui.Window):
    def __init__(self):
        self.setCoordinateResolution(6)
        xbmcgui.Window.__init__(self)

        #variables
        self.temps = time.time()
        self.REC=False
        self.MODE="TV" #MODE=TV pour les chaines freebox / MODE=FILE pour les enregistrements effectués
        self.ouinon=False
        self.freespace=get_freespace( RECORDS )
        self.chaines=liste_chaines()
        self.meschaines=[]
        for num,nom,cid in self.chaines:
            if int(num) in MES_CHAINES:
                self.meschaines.append((num,nom,cid))
        self.proxyrunning=False
        self.Recorder=None #contiendra le thread ### 3ieme solution
        #initialisations
        self.GUI()
        self.FillChannels()

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
        
        #bouton de settings
        self.btnSettings=xbmcgui.ControlButton(50,150,150,30,' Paramètres')
        self.addControl(self.btnSettings)
        #self.btnSettings.setVisible(True)

        #bouton de preview
        self.btnPreview=xbmcgui.ControlButton(50,190,150,30,' Prévisualiser')
        self.addControl(self.btnPreview)
        self.btnPreview.setVisible(False)

        
        #Liste des chaines
        #   Initialisation
        self.ChanList=xbmcgui.ControlList(200,110,490,430,'font13','0xFFFFFFFF',
                                          imageWidth=30,
                                          imageHeight=30,
                                          itemHeight=30,
                                          )
        self.addControl(self.ChanList)
        self.ChanList.setPageControlVisible(True)

        #navigation
        self.btnMode.controlRight(self.ChanList)
        self.btnMode.controlDown(self.btnSettings)
        self.btnSettings.controlUp(self.btnMode)
        self.btnSettings.controlRight(self.ChanList)
        self.ChanList.controlLeft(self.btnMode)

    def yesno(self,titre="F2XTV",ligne1="",ligne2=""):
        if not(self.ouinon):
            self.ouinoncontrols=[]
            self.bkgd=xbmcgui.ControlImage(0,0,720,576, 'background.png')
            self.addControl(self.bkgd)
            self.ouinoncontrols.append(self.bkgd)
            self.titre=xbmcgui.ControlLabel(50,85,620,50,titre,'font13','0xFFFFFFFF')
            self.addControl(self.titre)
            self.ouinoncontrols.append(self.titre)
            self.texte1=xbmcgui.ControlLabel(200,110,620,40,ligne1,'font13','0xFFFFFFFF')
            self.addControl(self.texte1)
            self.ouinoncontrols.append(self.texte1)
            self.texte2=xbmcgui.ControlLabel(200,140,620,40,ligne2,'font13','0xFFFFFFFF')
            self.addControl(self.texte2)
            self.ouinoncontrols.append(self.texte2)
            self.OUIbtn=xbmcgui.ControlButton(50,110,150,30,' OUI')
            self.addControl(self.OUIbtn)
            self.ouinoncontrols.append(self.OUIbtn)
            self.NONbtn=xbmcgui.ControlButton(50,110,150,30,' NON')
            self.addControl(self.NONbtn)
            self.OUIbtn.controlLeft(self.NONbtn)
            self.ouinoncontrols.append(self.NONbtn)
            
            self.NONbtn.controlRight(self.OUIbtn)
            self.OUIbtn.controlUp(self.NONbtn)
            self.NONbtn.controlDown(self.OUIbtn)
            self.setFocus(self.NONbtn)
            #self.ouinon=True
        else:
            #self.ouinon=False
            for control in self.ouinoncontrols:
                self.removeControl(control)
        
        
    
    def FillChannels(self):
        self.ChanList.reset()
        for (numchan,nomchan,idchan) in self.meschaines:
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
                    thumbnailImage  = RECORDS + filename[:-3]+"tbn"
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
                if not(self.REC):
                    item=self.ChanList.getSelectedPosition()
                    numchan,nomchan,idchan = self.meschaines[item]
                    player=MyPlayer()
                    xbmc.executebuiltin("XBMC.PlayMedia(http://127.0.0.1:8083/freeboxtv/%s)"%idchan)
                    while player.isPlaying():
                        pass
                    del player
                else:
                    self.reclabel.setLabel("Enregistrement en cours")
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
                #thread.start_new_thread(self.playpreview,())
                    print "FIN DU PREVIEW"
                except:
                    print "Erreur, impossible de jouer le preview"
                #ici on peut loop pour éviter la détection du bouton B si besoin
        if control==self.OUIbtn:
            #on pourra ici supprimer le fichier
            filename=self.ChanList.getSelectedItem().getLabel()
            try:
                os.remove(RECORDS+filename)
                os.remove(RECORDS+filename[:-3]+"tbn")
            except:
                print "erreur lors de la suppression"
            self.FillRecords()#actualise la liste
            #maintenant on ferme 
            
            #oui au dialog
                
##    def playpreview(self):
##        while not(self.Recorder.preview):
##            pass
##        try:
##            player=MyPlayer()
##            player.play(HOMEDIR + "preview.avi")
##            print "FIN DU PREVIEW"
##        except:
##            print "Erreur, impossible de jouer le preview"
           
    def onAction(self, action):
        if action == ACTION_BACK:
            self.REC=False
            self.close()
        if action == ACTION_B:
            if self.MODE == "TV":
                #if self.getFocus()==self.ChanList:
                    if self.REC:
                        self.REC=False
                        self.info.setLabel("Enregistrement interrompu")
                        #suppression du bouton preview et de ses mouvements
                        self.btnPreview.setVisible(False)
                        self.btnMode.controlDown(self.btnMode)
                        self.Recorder.stop()
                    elif self.getFocus()==self.ChanList:
                        item=self.ChanList.getSelectedPosition()
                        numchan,nomchan,idchan = self.meschaines[item]
                        dialog=xbmcgui.Dialog()
                        if dialog.yesno(nomchan,"Etes-vous sur de vouloir enregistrer cette chaine ?"):
                            print "lance l'enregistrement :"
                            self.record(self.meschaines[item])
                        else:
                            pass
                #else:
                #    pass
            elif self.MODE == "FILE":
                print "mode : FILE / bouton B"
                if not(self.ouinon):
                    #affichage du dialog oui non
                    self.ouinon="suppr"
                    self.yesno("Confirmation de la suppresion","Voulez vous supprimer cet enregistrement ?")
                else:
                    #cas du bouton B lorsqu'on est dans le dialog ouinon
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
        self.filename = "%s_%s.avi"%(FatX(channame,decal=13),time.strftime("%d%m%y_%Hh%M",time.localtime()))
        #print self.filename,str(len(self.filename))
        self.filesize = 0
        self.memfile = StringIO.StringIO() # fichier mémoire recevant les données le temps de la mise en cache

    def run(self):
        try:
            TV = urllib.urlopen("http://127.0.0.1:8083/freeboxtv/%s"%self.chanid)
            self.recording = True
        except IOError:
            print "Impossible d'ouvrir le flux (timeout)"
            self.recording=False
        
        rec = open(RECORDS + self.filename,"wb",32768)
        starttime=time.time()
        while self.recording:
            self.info.setLabel("%.1f Mo en %i sec."%(self.filesize/1024.0,time.time()-starttime))
            datas = TV.read(2048)
            rec.write(datas)
            self.filesize+=2
            if self.caching:
                self.memfile.write(datas)
                if self.memfile.len > CACHESIZE: #si le cache est rempli :
                    print "Fin du caching ! Ecriture de preview.avi"
                    # - on écrit le fichier preview
                    f = open(HOMEDIR + "preview.avi","wb")
                    f.write(self.memfile.getvalue())
                    f.close()
                    #print self.memfile
                    #thread.start_new_thread(self.previewcache,())
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
        try:
            TV.close()
            del TV
        except:
            print "impossible de fermer la connection au proxy"

        rec.close()
        self.memfile.close()
        del rec, self.memfile
        #création du thumbnail
        try:
            print LOGODIR+"%s.bmp"%self.chanid
            print RECORDS+self.filename[:-3]+"tbn"
            shutil.copyfile(LOGODIR+"%s.bmp"%self.chanid , RECORDS+self.filename[:-3]+"tbn")
        except:
            print "erreur lors de la création de la miniature"
        #réinitialisation
        self.preview=False

    def previewcache(self):
        self.caching = False #fin de la mise en cache
        f = open(HOMEDIR + "preview.avi","wb",1024)
        f.write(self.memfile.getvalue())
        f.close()
        self.preview = True #fichier de preview disponible
        self.memfile.close()
        self.memfile = StringIO.StringIO()
        print "PREVIEWCACHE TERMINE"

    def stop(self):
        self.recording = False




###teste si le proxy est déjà lancé
###(présence du module dummyproxy qui est chargé par le proxy)
##if "dummyproxy" in sys.modules.keys():
##    pass
##else:
##    print "Chargement du proxy..."
##    #xbmc.executescript(ProxyPath)
##    #xbmc.executebuiltin("XBMC.RunScript(%s)"%ProxyPath)
##    

socket.setdefaulttimeout(3)

#création des dossiers :
verifrep(RECORDS)
            
go=main()
###teste si le proxy est démarré dans le cas où il n'aurait pas
###été démarré lors du test précédent
### si il n'est toujours pas démarré, le script n'est pas lancé
##if not("dummyproxy" in sys.modules.keys()):
##    dialog=xbmcgui.Dialog()
##    dialog.ok("Erreur Proxy","Le proxy n'est pas démarré et n'a pas pu être démarré","Le script ne peut donc pas foncionner")
##    go.close()
##    del dialog
##
##            
##else:
##    go.doModal()
go.doModal()
del go
