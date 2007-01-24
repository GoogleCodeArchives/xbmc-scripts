# -*- coding: cp1252 -*-
menucontextuel = contextuel("chaines","France 2")
menucontextuel.doModal()
RetourControl = menucontextuel.retour
del menucontextuel

#pour d�couper les playlistes qui seront envoy�es par le serveur :
#   chanidlist contient la liste ordonn�e des chaines
#   playlist est un dictionnaire contenant toutes les infos selon l'id (num name et url)
playlist = {}
chanidlist = []
for itemchannel in m3u.strip().split("\n"):
    chanid,num,name,url = itemchannel.split(",")
    chanidlist.append(chanid)
    playlist[chanid]={"num" : num,
                      "name" : name,
                      "url" : url
                      }
print "Exemple :"
print "\tplaylist[\"201\"][\"name\"] renvoi : %s"%playlist["201"]["name"]

#fonction pour retourner le nom de la chaine par son id
def getname(chanid):
    return

class contextuel(xbmcgui.WindowDialog):
    """
    Affichage d'un menu contextuel sur appel dans la liste avec le bouton blanc
    """
    def __init__(self,contexte,titre="Menu contextuel"):
        self.contexte = contexte
        self.titre = titre
        #variable qui m�morisera le control press� (none par d�faut)
        self.retour = None
        #affichage des controls g�n�raux
        print "d�claration initiale du fond d'�cran"
        print "d�claration initiale du label pour le titre du menu contextuel : \"%s\""%titre
        #affichage des boutons du menu contextuel :
        self.drawContexte(contexte)

    def drawContexte(contexte):
        if contexte == "chaines":
            """
            Menu contextuel de la liste des chaines
            """
            print "cr�ation des boutons pour le menu contextuel des chaines"
            print "\t- Regarder"
            print "\t- Enregistrer"
            print "\t- Supprimer"
            print "\t- G�rer la liste des chaines"
            print "\t- etc..."
            print "\t- Annuler"
            print
            print "Puis liaisons logiques des mouvements entre les controles"
            print "  (par appel d'une fonction mouvements avec la liste des contr�les en argument)"
            print
            print "Pour finir, activation du focus sur le premier bouton"
            
        elif contexte == "progs":
            """
            Menu contextuel de la liste des programmations
            """
            print "cr�ation des boutons pour le menu contextuel des programmations"
            print "\t- Editer"
            print "\t- Copier"
            print "\t- Supprimer"
            print "\t- etc..."
            print "\t- Nouvelle programmation"
            print "\t- Annuler"
            print
            print "Puis liaisons logiques des mouvements entre les controles"
            print "  (par appel d'une fonction mouvements avec la liste des contr�les en argument)"
            print
            print "Pour finir, activation du focus sur le premier bouton"

        elif contexte == "enreg":
            """
            Menu contextuel de la liste des enregistrements
            """
            print "cr�ation des boutons pour le menu contextuel des enregistrements"
            print "\t- Regarder"
            print "\t- D�placer"
            print "\t- Supprimer"
            print "\t- Renommer"
            print "\t- etc..."
            print "\t- Annuler"
            print
            print "Puis liaisons logiques des mouvements entre les controles"
            print "  (par appel d'une fonction mouvements avec la liste des contr�les en argument)"
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
