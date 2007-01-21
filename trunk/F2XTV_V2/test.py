# -*- coding: cp1252 -*-
import time
print "import des librairies"
from F2XTVlib import *
print
print ">>le __init__.py de F2XTVlib va importer les autres modules qui seront alors accessibles ici."
print
print "Variables d�finies dans le __init__ :"
print "\tHOMEDIR\t",HOMEDIR
print "\tDATAS\t",DATAS
print "\tMEDIAS\t",MEDIAS
print "\tSETTINGSini\t",SETTINGSini
print "\tPROGRAMMESini\t",PROGRAMMESini
print "--------"
print

print "r�cup�ration des param�tres utilisateur :"
settings=utils.OpenIni(SETTINGSini)
for info in settings.options("general"):
    print "\t%s :\t\t%s"%(info , settings.get("general",info))

print "Utilisation du parseur pour manipuler les param�tres."
print " - Cr�ation de l'objet avec \"%s\" : "%SETTINGSini
params = parseur.params( SETTINGSini )
print " -Exemple, ecriture du nom du proxy 'toto'..."
params.SetProxyName( 'toto' )
print " - Lecture des chaines favorites..."
print "\t%s"%params.GetFavChan()
print " - Ajout d'une chaine 999 dans la liste des favorites :"
print "\t%s"%params.AddFavChan(999)
print " - Suppression de la chaine 999 de la liste des favorites :"
print "\t%s"%params.DelFavChan(999)



#le module utils regroupe les fonctions d'ordre g�n�ral
#exemple :
print
print "exemple de fonction utils.\n Formater un nom de fichier de mani�re � le rendre compatible FATX"
print "\tChaine � convertir : \"�����������������\""
print "\tChaine convertie   : \"%s\""%utils.FatX("�����������������")
print




#ajouter un programme dans la liste
print
print "Ajouter une programmation dans le ini :"
print "\t- cr�ation de l'objet programmateur..."
prog = programmateur.programme("F2XTV.ini")
print "\t- Ajout d'un programme ('1136489400.0','120','201','defaut') ..."
prog.new("1167837658.0","120","201","defaut")
print "\t- Liste des programmes avec v�rification des horaires :"
for progobj in prog.getProgs():
    print "objet : %s"%progobj
    print "etat : %s"%prog.VerifHoraire(progobj)
    print time.strftime(">>> d�but le %d/%m/%y � %H:%M",time.localtime(prog.getDatedebut(progobj)))
print
#prog.new("1167829930.365","120","205","defaut")
#for progobj in prog.getProgs():
#    print prog.VerifHoraire(progobj)
#    print time.strftime(">>> d�but le %d/%m/%y � %H:%M",time.localtime(prog.getDatedebut(progobj)))
print
print
print "R�cup�rer le prochain enregistrement � prendre en compte :"
recent=prog.getRecent()
if recent:
    print time.strftime("\t- Prochaine prog (� venir ou en cours) :\n %d/%m/%y � %H:%M",time.localtime(prog.getDatedebut(recent)))
else:
    print "\t- Il n'y a aucun enregistrement en cours ou � venir"
