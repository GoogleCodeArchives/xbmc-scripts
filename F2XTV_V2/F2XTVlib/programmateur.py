# -*- coding: cp1252 -*-
from ConfigParser import ConfigParser
import time


class programme:
    def __init__(self,inipath):
        self.iniPath = inipath
    
##    def new(self,date,heure,duree,chaineid):
    def new(self,datedebut,duree,chaineid,actionfin="defaut"):
        if not (datedebut and duree and chaineid):
            print "Paramètre(s) manquant(s)"
            return False

        settings = self.OpenIni()
        sectionname = "prog:%s"%(self.SectionTitre(datedebut,chaineid))
        if not(settings.has_section(sectionname)):
            print "Création du programme"
            settings.add_section( sectionname )
        else:
            print "le programme existe déjà. Il va être mis à jour"
        settings.set(sectionname,"datedebut",str(datedebut))
        settings.set(sectionname,"duree",str(duree))
        settings.set(sectionname,"chaineid",str(chaineid))
        settings.set(sectionname,"actionfin",str(actionfin))
        self.SaveIni(settings)
        return True
        
    def suppr(self,progname):
        if progname:
            settings = self.OpenIni()
            if settings.has_section("prog:%s"%progname):
                settings.remove_section("prog:%s"%progname)
                self.SaveIni(settings)
                print "%s a été supprimé"%progname
            else:
                print "la programmation \"%s\" n'existe pas"%progname

    def getProgs(self):
        settings = self.OpenIni()
        sections=[]
        for section in settings.sections():
            if section.startswith("prog:"):
                sections.append(section.split(":")[1])
        return sections
                
    def VerifHoraire(self,progname):
        """
        Confronte l'heure du programme avec l'heure en cours.
        Renvoi :
        -1  si le programme est dépassé
        0   si le programme est en cours
        +1  si le programme est futur
        """
        maintenant = time.time()
        settings = self.OpenIni()
        datedebut = float(settings.get("prog:%s"%progname,"datedebut"))
        duree = int(settings.get("prog:%s"%progname,"duree"))
        datefin = datedebut + float(duree)*60
##        print "%s :"%progname
        if (datedebut < maintenant) and (datefin > maintenant):
            #période d'enregistrement en cours
##            print "\tenregistrement en cours"
##            print "\t (%s secondes écoulées. Il reste %s secondes)"%(maintenant-datedebut , datefin-maintenant)
            return 0
        elif datefin < maintenant:
##            print "\tenregistrement dépassé"
            return -1
        elif datedebut > maintenant:
##            print "\tenregistrement futur"
            return 1
        print

    def getRecent(self):
        """
        Retourne le nom de programme le plus récent (déjà commencé ou à venir)
        """
        nextprogs={}
        for progname in self.getProgs():
            if not(self.VerifHoraire(progname)<0): #si commencé ou à venir
                datedebut = self.getDatedebut(progname)
                nextprogs[datedebut] = progname
                print time.strftime(">>> %d/%m/%y à %H:%M",time.localtime(datedebut))
        listdates = nextprogs.keys()
        if listdates:
            listdates.sort()
            return nextprogs[listdates[0]]
        else:
            return None
        

    def getDatedebut(self,progname):
        settings = self.OpenIni()
        return float(settings.get("prog:%s"%progname,"datedebut"))

    def getDuree(progname):
        settings = self.OpenIni()
        return int(settings.get("prog:%s"%progname,"duree"))
    
    def SectionTitre(self,datedebut,chaineid):
        titre = "%s %s"%(chaineid,datedebut)
        return titre
        
##    def TimeObject(self,date,heure):
##        return time.strptime("%s%s"%(date,heure),"%d%m%y%H%M")

    def OpenIni(self):
        "ouvre le fichier .ini et renvoi l'objet ConfigParser"
        sets = ConfigParser()
        sets.read(self.iniPath)
        return sets
        
    def SaveIni(self,ini):
        "Sauve l'objet ConigParser dans le fichier ini"
        try:
            f=open("F2XTV.ini","w")
            ini.write(f)
            f.close()
            print "SaveIni --> sauvegarde ok"
        except:
            print "SaveIni --> Echec de sauvegarde"


if __name__ == "__main__":
    prog = programme("F2XTV.ini")
    #prog.new("1136489400.0","120","201","defaut")
    for progobj in prog.getProgs():
        print prog.VerifHoraire(progobj)
        print time.strftime(">>> début le %d/%m/%y à %H:%M",time.localtime(prog.getDatedebut(progobj)))
    #prog.new("1167829930.365","120","205","defaut")
    #for progobj in prog.getProgs():
    #    print prog.VerifHoraire(progobj)
    #    print time.strftime(">>> début le %d/%m/%y à %H:%M",time.localtime(prog.getDatedebut(progobj)))

    print
    print "prochain enregistrement"
    recent=prog.getRecent()
    if recent:
        print time.strftime("ce prog est le plus récent : %d/%m/%y à %H:%M",time.localtime(prog.getDatedebut(recent)))
    else:
        print "Il n'y a aucun enregistrement en cours ou à venir"
    

