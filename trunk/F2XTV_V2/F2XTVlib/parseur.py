# -*- coding: cp1252 -*-
"""
Ce module gère tous les paramètres communs à tous les modules
par l'utilisation d'un fichier ini et de la librairie ConfigParser
"""
from ConfigParser import ConfigParser
import time
import utils

class params:
    """
    params( ConfigParser object ) :
    créé une collection de méthode pour configurer les paramètres
    """
    def __init__(self,inifile):
        self.inifile=inifile
        self.settings = utils.OpenIni(self.inifile)
        pass

    def SetProxyName(self,name):#
        """
        Change le nom du script proxy
        """
        self.settings.set("general","proxyname",name)
        self.save()

    def GetFavChan(self):
        listechaines = []
        for ch in self.settings.get("general","meschainesfavorites").split(","):
            listechaines.append(int(ch))
        return listechaines

    def AddFavChan(self,channum=None):
        """
        Ajoute la chaine numéro channum à la liste des chaines favorite
        Si channum n'est pas donné, retourne la liste simplement sans ajout.
        """
        favchans = self.GetFavChan()
        if channum:
            if int(channum) in favchans:
                print "La chaine existe déjà dans les favoris"
            else:
                favchans.append(int(channum))
        self.SetFavChan(favchans)
        return favchans

    def SetFavChan(self,chanlist):
        """
        Ecrit la liste des chaines favorites.
        """
        chanlist.sort()
        self.settings.set("general","meschainesfavorites",
                          ",".join([str(s) for s in chanlist] ))
        self.save()

    def DelFavChan(self,channum):
        """
        Supprime la chaine channum de la liste des favoris
        """
        favchans = self.GetFavChan()
        try:
            pos = favchans.index(channum)
            favchans.pop(pos)
        except:
            print "La chaine %s n'était pas dans la liste."
            return False
        self.save()
        return True

    def save(self):
        utils.SaveIni(self.settings,self.inifile)
        
        

class programme:
    """
    gère toutes les lectures/écritures dans le fichier des enregistrements programmés
    """
    def __init__(self,inipath):
        self.iniPath = inipath
        pass
    
    def new(self,date,heure,duree,chaineid):
        """
        Créé une nouvelle entrée dans le fichier des programmations
        """
        if not (date and heure and duree and chaineid):
            print "Paramètre(s) manquant(s)"
            return
        
        settings = utils.OpenIni(self.iniPath)
        sectionname = "prog:%s"%(self.MakeTitre(date,heure,duree,chaineid))
        if not(settings.has_section(sectionname)):
            print "Création du programme"
            settings.add_section( sectionname )
        else:
            print "le programme existe déjà. Il va être mis à jour"
        settings.set(sectionname,"date",str(date))
        settings.set(sectionname,"heure",str(heure))
        settings.set(sectionname,"duree",str(duree))
        settings.set(sectionname,"chaineid",str(chaineid))
        utils.SaveIni(settings,self.iniPath)
        
    def suppr(self,progname):
        """
        Supprime du ini le programme défini par 'progname'
        """
        if progname:
            settings = utils.OpenIni(self.iniPath)
            #est-ce que le programme 'progname' existe ?
            if settings.has_section("prog:%s"%progname):
                settings.remove_section("prog:%s"%progname)
                utils.SaveIni(settings,self.iniPath)
                print "%s a été supprimé"%progname
            else:
                print "la programmation \"%s\" n'existe pas"%progname
        else:
            #il manque le 'progname'
            print "Demande de suppresion mais la variable 'progname' n'est pas définie"

    def getProgs(self):
        """
        Recherche tous les programmes du fichier des programmations.
        Renvoi une liste des noms de programmes [prog: progname]
        """
        settings = utils.OpenIni(self.iniPath)
        sections=[]
        for section in settings.sections():
            if section.startswith("prog:"):
                sections.append(section.split(":")[1])
        return sections
                
    def MakeTitre(self,date,heure,duree,chaineid):
        """
        Création du nom de programme 'progname'
        """
        titre = "%s %s %s %s"%(chaineid,date,heure,duree)
        return titre
        
    def TimeObject(self,date,heure):
        return time.strptime("%s%s"%(date,heure),"%d%m%y%H%M")

        



if __name__ == "__main__":
    prog = programme("F2XTV.ini")
    prog.new("051106","2100","60","NT1")
    print prog.getProgs()
    prog.suppr(prog.getProgs()[1])
    print prog.getProgs()
