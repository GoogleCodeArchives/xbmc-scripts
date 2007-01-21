# -*- coding: cp1252 -*-
import time
print "import des librairies"
from F2XTVlib import *
print
print ">>le __init__.py de F2XTVlib va importer les autres modules qui seront alors accessibles ici."
print
print "Variables définies dans le __init__ :"
print "\tHOMEDIR\t",HOMEDIR
print "\tDATAS\t",DATAS
print "\tMEDIAS\t",MEDIAS
print "\tSETTINGSini\t",SETTINGSini
print "\tPROGRAMMESini\t",PROGRAMMESini
print "--------"
print

print "récupération des paramètres utilisateur :"
settings=utils.OpenIni(SETTINGSini)
for info in settings.options("general"):
    print "\t%s :\t\t%s"%(info , settings.get("general",info))

print "Utilisation du parseur pour manipuler les paramètres."
print " - Création de l'objet avec \"%s\" : "%SETTINGSini
params = parseur.params( SETTINGSini )
print " -Exemple, ecriture du nom du proxy 'toto'..."
params.SetProxyName( 'toto' )
print " - Lecture des chaines favorites..."
print "\t%s"%params.GetFavChan()
print " - Ajout d'une chaine 999 dans la liste des favorites :"
print "\t%s"%params.AddFavChan(999)
print " - Suppression de la chaine 999 de la liste des favorites :"
print "\t%s"%params.DelFavChan(999)



#le module utils regroupe les fonctions d'ordre général
#exemple :
print
print "exemple de fonction utils.\n Formater un nom de fichier de manière à le rendre compatible FATX"
print "\tChaine à convertir : \"ÃåÅæÆçÇðÐéÉèÈêÊëË\""
print "\tChaine convertie   : \"%s\""%utils.FatX("ÃåÅæÆçÇðÐéÉèÈêÊëË")
print




#ajouter un programme dans la liste
print
print "Ajouter une programmation dans le ini :"
print "\t- création de l'objet programmateur..."
prog = programmateur.programme("F2XTV.ini")
print "\t- Ajout d'un programme ('1136489400.0','120','201','defaut') ..."
prog.new("1167837658.0","120","201","defaut")
print "\t- Liste des programmes avec vérification des horaires :"
for progobj in prog.getProgs():
    print "objet : %s"%progobj
    print "etat : %s"%prog.VerifHoraire(progobj)
    print time.strftime(">>> début le %d/%m/%y à %H:%M",time.localtime(prog.getDatedebut(progobj)))
print
#prog.new("1167829930.365","120","205","defaut")
#for progobj in prog.getProgs():
#    print prog.VerifHoraire(progobj)
#    print time.strftime(">>> début le %d/%m/%y à %H:%M",time.localtime(prog.getDatedebut(progobj)))
print
print
print "Récupérer le prochain enregistrement à prendre en compte :"
recent=prog.getRecent()
if recent:
    print time.strftime("\t- Prochaine prog (à venir ou en cours) :\n %d/%m/%y à %H:%M",time.localtime(prog.getDatedebut(recent)))
else:
    print "\t- Il n'y a aucun enregistrement en cours ou à venir"
