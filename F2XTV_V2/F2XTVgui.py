import xbmc , xbmcgui
import sys
import urllib
from os import path


HOMEPATH = sys.path[0] + '\\'
PICSPATH = HOMEPATH + 'images\\'
LOGOPATH = PICSPATH + 'logos\\'
SKINPATH = HOMEPATH + 'skins\\'


#actions keymap
ACTION_CONTEXT      = [261, #pad : white button
                       247] #remote 'menu'
ACTION_BACK         = [275, #pad : "back button"
                       216] #remote : "back" button
ACTION_DEFAULT      = [256, #pad : "A" button
                       11]  #remote : "select" button
ACTION_B            = [257, #pad : Red B
                       221] #remote : skip-
ACTION_Y            = [259, #pad : yellow Y
                       260, #pad : black button
                       223] #remote : skip+
ACTION_EDIT         = [] #not used yet
#   key :       remote code :       pad code:
#   up          166                 210
#   down        167                 211
#   right       168                 213
#   left        169                 212
#   back        216                 275
#   select      11                  /
#   menu        247                 /
#   display     213                 /
#   skip+       223                 /
#   skip-       221                 /
#   forward     227                 /
#   reverse     226                 /
#   play        234                 /
#   stop        224                 /
#   pause       230                 /
#   title       229                 /
#   info        195                 /
#   0           207                 /
#   1           206                 /
#   2           205                 /
#   ...         ...                 /
#   9           198                 /
#   start       /                   274
#   white       /                   261
#   black       /                   260
#   RstickUp    /                   266
#   RstickDwn   /                   267
#   RstickLft   /                   268
#   RstickRght  /                   269
#   Rstickclic  /                   277
#   LstickUp    /                   280
#   LstickDwn   /                   281
#   LstickLft   /                   282
#   LstickRght  /                   283
#   Lstickclic  /                   276
#   Ltrigger    /                   278
#   Rtrigger    /                   279
#   A           /                   256
#   B           /                   257
#   X           /                   258
#   Y           /                   259

#default constant for contextual display
CHANNELS = 1
PROGRAMS = 2
RECORDS  = 3
SETTINGS = 4

def ServerSettings():
    #TODO
    return "127.0.0.1","8083"

def loadplaylist(tvserver):
    """
    Load a given playlist
    return a list contening all the channel IDs and a dict containing all channel infos
    """
    #fetch server infos
    server,port = ServerSettings()
    
    plscontent = urllib.urlopen("http://%s:%s/%s/GUIPlaylist"%(server,port,tvserver)).read()
    playlist = {}
    chanidlist = []
    for itemchannel in m3u.strip().split("\n"):
        chanid,num,name,url = itemchannel.split(",")
        chanidlist.append(chanid)
        playlist[chanid]={"num" : num,
                          "name" : name,
                          "url" : url
                         }
    return chanidlist,playlist

class main(xbmcgui.Window):
    def __init__(self):
        """import guibuilder
        guibuilder.GUIBuilder(self,  SkinPath + 'F2XTV_PMIII.xml', ImagePath, debug=True)
        if (not self.SUCCEEDED): self.exitScript()
        else:
            for item in range(20):
                l = xbmcgui.ListItem('This is item #%d of 20 items' % (item +1,),
                                     'item# %d' % (item +1,),
                                     '',
                                     'defaultAlbumCover.png')
                self.controls[30].addItem(l)"""
        #dessin de l'interface
        self.GUI()
        #mise en place des labels
        self.Labels('french')

        #contexte par défaut
        self.context = CHANNELS

        #chargement de la playliste
        self.chanidlist,self.playlist = loadplaylist("freeboxtv")

        #remplissage de la liste
        self.FillMainList()
        
        #focus initial
        self.setFocus(self.btnChaines)
        
    def GUI(self):
        #BACKGROUND
        self.addControl(xbmcgui.ControlImage(0,0,720,576, 'background.png'))

        #logo
        self.addControl(xbmcgui.ControlImage(50,56,196,26, PICSPATH+'freemultiposte.gif'))

        #label d'infos
        self.info=xbmcgui.ControlLabel(50,85,620,50,"<%ScriptIsStarting...%>",'font13','0xFFFFFFFF')
        self.addControl(self.info)

        #label d'enregistrement
        self.reclabel=xbmcgui.ControlLabel(250,56,400,50,"",'font14','0xFFCC1111')
        self.addControl(self.reclabel)

        #bouton des chaines
        self.btnChaines=xbmcgui.ControlButton(50,110,150,30,'<%channels%>')
        self.addControl(self.btnChaines)
        
        #bouton des enregistrements
        self.btnEnreg=xbmcgui.ControlButton(50,150,150,30,'<%recordings%>')
        self.addControl(self.btnEnreg)

        #bouton des enregistrements programmés
        self.btnProg=xbmcgui.ControlButton(50,190,150,30,'<%programmations%>')
        self.addControl(self.btnProg)

        #bouton des paramètres
        self.btnParams=xbmcgui.ControlButton(50,230,150,30,'<%parameters%>')
        self.addControl(self.btnParams)
        
        #Liste principale
        #   Initialisation
        self.MainList=xbmcgui.ControlList(200,110,490,430,'font13','0xFFFFFFFF',
                                          imageWidth=30,
                                          imageHeight=30,
                                          itemHeight=30,
                                          )
        self.addControl(self.MainList)
        self.MainList.setPageControlVisible(True)

        #navigation
        self.MainList.controlLeft(self.btnChaines)
        self.btnChaines.controlRight(self.MainList)
        self.btnEnreg.controlRight(self.MainList)

        self.btnChaines.controlDown(self.btnEnreg)
        self.btnEnreg.controlDown(self.btnProg)
        self.btnProg.controlDown(self.btnParams)
        self.btnParams.controlDown(self.btnChaines)
        
        self.btnParams.controlUp(self.btnProg)
        self.btnProg.controlUp(self.btnEnreg)
        self.btnEnreg.controlUp(self.btnChaines)        
        self.btnChaines.controlUp(self.btnParams)

    def Labels(self,language):
        #chargement du fichier de langage
        print "chargement du fichier de langage : à faire"
        #
        self.info.setLabel("Chargement en cours...")
        self.btnChaines.setLabel(" Chaines")
        self.btnEnreg.setLabel(" Enregistrements")        
        self.btnProg.setLabel(" Programmations")
        self.btnParams.setLabel(" Paramètres")

    def FillMainList(self):
        """
        Fill the list depending on actual context
        """
        if self.context == CHANNELS:
            self.MainList.reset()
            for chanid in self.chanidlist:
                self.MainList.addItem(
                    xbmcgui.ListItem(
                        label = self.playlist[chanid]["name"],
                        label2 = self.playlist[chanid]["num"],
                        thumbnailImage  = LOGOPATH+"%s.bmp"%chanid
                        )
                        )
        elif self.context == PROGRAMS:
            print "remplissage de la liste avec les programmations"
            print "\t1- récupère les programmations sur le serveur"
            print "\t2- rempli la liste avec le jour et heure de début et la durée, la chaine et le status"
        elif self.context == RECORDS:
            print "remplissage de la liste avec les enregistrements"
            print "\t1- récupère les programmations sur le serveur"
            print "\t2- rempli la liste avec le jour et heure de début et la durée, la chaine et le status"
        elif self.context == PARAMS:
            print "remplissage de la liste avec les éléments de configuration"
        
    def onAction(self,action):
        if action.getButtonCode() in ACTION_BACK:
            self.close()
        elif action.getButtonCode() in ACTION_CONTEXT and self.getFocus()==self.MainList: #focus est sur mainlist
            #appui du bouton blanc sur un élément de liste
            #on récupère l'élément
            item=self.MainList.getSelectedPosition()
            if self.contexte == "chaines":
                menucontextuel = contextuel(self.context,"France 2")
                menucontextuel.doModal()
                RetourControl = menucontextuel.retour
                del menucontextuel
                #traitement du retour
            

    def onControl(self,control):
        pass
    
    def exitScript(self):
        self.close()
    

class contextuel(xbmcgui.WindowDialog):
    """
    Affichage d'un menu contextuel sur appel dans la liste avec le bouton blanc
    """
    def __init__(self,contexte,titre="Menu contextuel"):
        self.contexte = contexte
        self.titre = titre
        #variable qui mémorisera le control pressé (none par défaut)
        self.retour = None
        #affichage des controls généraux
        print "déclaration initiale du fond d'écran"
        print "déclaration initiale du label pour le titre du menu contextuel : \"%s\""%titre
        #affichage des boutons du menu contextuel :
        self.drawContexte(contexte)

    def drawContexte(contexte):
        if contexte == "chaines":
            """
            Menu contextuel de la liste des chaines
            """
            print "création des boutons pour le menu contextuel des chaines"
            print "\t- Regarder"
            print "\t- Enregistrer"
            print "\t- Supprimer"
            print "\t- Gérer la liste des chaines"
            print "\t- etc..."
            print "\t- Annuler"
            print
            print "Puis liaisons logiques des mouvements entre les controles"
            print "  (par appel d'une fonction mouvements avec la liste des contrôles en argument)"
            print
            print "Pour finir, activation du focus sur le premier bouton"
            
        elif contexte == "progs":
            """
            Menu contextuel de la liste des programmations
            """
            print "création des boutons pour le menu contextuel des programmations"
            print "\t- Editer"
            print "\t- Copier"
            print "\t- Supprimer"
            print "\t- etc..."
            print "\t- Nouvelle programmation"
            print "\t- Annuler"
            print
            print "Puis liaisons logiques des mouvements entre les controles"
            print "  (par appel d'une fonction mouvements avec la liste des contrôles en argument)"
            print
            print "Pour finir, activation du focus sur le premier bouton"

        elif contexte == "enreg":
            """
            Menu contextuel de la liste des enregistrements
            """
            print "création des boutons pour le menu contextuel des enregistrements"
            print "\t- Regarder"
            print "\t- Déplacer"
            print "\t- Supprimer"
            print "\t- Renommer"
            print "\t- etc..."
            print "\t- Annuler"
            print
            print "Puis liaisons logiques des mouvements entre les controles"
            print "  (par appel d'une fonction mouvements avec la liste des contrôles en argument)"
            print
            print "Pour finir, activation du focus sur le premier bouton"

    def onAction(self,action):
        print action

    def onControl(self,control):
        print control
        if control == "bouton annuler":
            self.control = None
        else:
            self.retour = control
        self.close()


m = main()
if (m.SUCCEEDED): m.doModal()
del m
