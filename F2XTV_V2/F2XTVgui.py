import xbmc , xbmcgui
import sys
from os import path


ExtrasPath      =   sys.path[0] +  '\\datas\\'
sys.path.append(sys.path[0] + '\\libs')
ImagePath       = ExtrasPath + 'images'
SkinPath        = ExtrasPath + 'skins\\'

#actions keymap
ACTION_BACK         = [275, #pad : "back button"
                       216] #remote : "back" button
ACTION_B            = [257, #pad : Red B
                       221] #remote : skip-
ACTION_CONTEXT      = [261, #pad : white button
                       247]  #remote 'menu'
ACTION_Y            = [259, #pad : yellow Y
                       260, #pad : black button
                       223]  #remote : skip+
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

class main(xbmcgui.Window):
    def __init__(self):
        import guibuilder
        guibuilder.GUIBuilder(self,  SkinPath + 'F2XTV_PMIII.xml', ImagePath, debug=True)
        if (not self.SUCCEEDED): self.exitScript()
        else:
            for item in range(20):
                l = xbmcgui.ListItem('This is item #%d of 20 items' % (item +1,),
                                     'item# %d' % (item +1,),
                                     '',
                                     'defaultAlbumCover.png')
                self.controls[30].addItem(l)

    def exitScript(self):
        self.close()
        
    def onAction(self,action):
        if action.getButtonCode() in ACTION_BACK:
            self.close()
        elif action.getButtonCode() in ACTION_CONTEXT and \
        self.getFocus()==self.controls[30]:
        #appui du bouton blanc sur un élément de liste
            #on récupère l'élément
            item=self.controls[30].getSelectedPosition()
            #if self.contexte == "chaines":
            menucontextuel = contextuel(self.contexte,"France 2")
            menucontextuel.doModal()
            RetourControl = menucontextuel.retour
            del menucontextuel
            #traitement du retour
            

    def onControl(self,control):
        pass


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
