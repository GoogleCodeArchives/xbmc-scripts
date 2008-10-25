# -*- coding: utf8 -*-

import sys
def log(txt):
    print txt
    f=open("testresults.txt","a")
    f.write(txt+'\n')
    f.close()
f=open("testresults.txt","w")
f.write("")
f.close()
# déchargement de la librairie allocine pour prendre en compte les modifs
if sys.modules.has_key("allocine"):
    del sys.modules["allocine"]
import allocine as ac


log("très intéressant, nous pouvons créer notre propre fonction de log ")
log("pour remplacer celle de la librairie allocine (qui ne fait que écrire dans un fichier les messages).")
log("Cela permet au client graphique d'afficher tel ou tel type de message,")
log("dans tel ou tel cas.")
log("Par exemple, on peut afficher les infos dans un popup,")
log("afficher les messages D ou E dans un fichier destiné à aider le développeur")
log("et tout simplement ignorer tous les autres messages.")
log("")
log("Dans notre exemple, nous allons faire la même fonction que la librairie,")
log("à l'exception que nous allons afficher les messages au lieu de les écrire dans un fichier")
#définition de notre propre fonction de log :
def myLog(msg,cat="I"):
    u"""Used to write log messages"""
    if not msg:
        cat = "I"
        msg = "------marker------"
    logcats = {"W":"WARNING",
               "I":"INFO",
               "E":"ERROR",
               "D":"DEVELOPER",
               "O":"OTHER"}
    if not cat in logcats.keys(): cat="O"
    print "** ALLOCINE **  %s : %s"%(logcats[cat],msg)
    log(("** ALLOCINE **  %s : %s"%(logcats[cat],msg)).encode("utf8"))
#remplacement du log de la librairie:
ac.Log=myLog




log("Travail préliminaire, installer une langue.")
ac.set_country("FR")
log(ac.COUNTRY)
log(ac.ALLOCINE_DOMAIN)

##log("###########")
##log("# TEST #1 #")
##log("###########")
##log("    - recupere les sorties de la semaine")
##log("      et affiche toutes les informations de tous les films")
##log("")
##
##agenda = ac.agenda("17/10/2008")
##for ID,Title,OriginalTitle,PictureURL,Genre,Lasts,PublicNote in agenda.get_movies_datas():
##    log("--------------------")
##    log("\tID = %s"%str(ID))
##    log("\tTitle = %s"%str(Title))
##    log("\tOriginalTitle = %s"%str(OriginalTitle))
##    log("\tPictureURL = %s"%str(PictureURL))
##    log("\tGenre = %s"%str(Genre))
##    log("\tLasts = %s"%str(Lasts))
##    log("\tPublicNote = %s"%str(PublicNote))
##    log("")
##    log("--------------------")
##    log("")
##log(" Période précédente : %s"%str(agenda.previous_week_date()))
##log(" Période suivante : %s"%str(agenda.next_week_date()))
##log("")
##log("    - on parcours la semaine précédente.")
##log("")
##precedent = ac.agenda(agenda.previous_week_date())#ou agenda("now")
##for ID,Title,OriginalTitle,PictureURL,Genre,Lasts,PublicNote in precedent.get_movies_datas():
##    log("--------------------")
##    log("\tID = %s"%str(ID))
##    log("\tTitle = %s"%str(Title))
##    log("\tOriginalTitle = %s"%str(OriginalTitle))
##    log("\tPictureURL = %s"%str(PictureURL))
##    log("\tGenre = %s"%str(Genre))
##    log("\tLasts = %s"%str(Lasts))
##    log("\tPublicNote = %s"%str(PublicNote))
##    log("")
##    log("--------------------")
##    log("")
##log(" Période précédente : %s"%str(precedent.previous_week_date()))
##log(" Période suivante : %s"%str(precedent.next_week_date()))
##log("")
##log("    - on parcours la semaine suivante.")
##log("")
##suivant = ac.agenda(agenda.next_week_date())#ou agenda("now")
##for ID,Title,OriginalTitle,PictureURL,Genre,Lasts,PublicNote in suivant.get_movies_datas():
##    log("--------------------")
##    log("ID = %s"%str(ID))
##    log("Title = %s"%str(Title))
##    log("OriginalTitle = %s"%str(OriginalTitle))
##    log("PictureURL = %s"%str(PictureURL))
##    log("Genre = %s"%str(Genre))
##    log("Lasts = %s"%str(Lasts))
##    log("PublicNote = %s"%str(PublicNote))
##    log("")
##    log("--------------------")
##    log("")
##log(" Période précédente : %s"%str(suivant.previous_week_date()))
##log(" Période suivante : %s"%str(suivant.next_week_date()))
##log("")

##log("###########")
##log("# TEST #2 #")
##log("###########")
##log("       Testes du parser de film et du handler de films")
###déclaration du handler de films
##mh = ac.Movies()
###instance d'agenda pour la date du 17/10/2008
##agenda = ac.agenda("17/10/2008")
###boucle sur les films sortis dans la semaine
##for movie in agenda.get_movies_datas():
##    log("--------------------")
##    #creation d'un objet film en passant par le handler
##    #   movie[0] contient l'ID du film
##    film = mh.new(movie[0])
##    #affichage des infos pour ce film
##    log("ID = %s"%movie[0])
##    log("director = %s"%str(film.director()))
##    log("nationality = %s"%str(film.nationality()))
##    log("title = %s"%str(film.title()))
##    log("infos = %s"%film.infos())
##    log("title = %s"%str(film.title()))
##    log("date = %s"%str(film.date()))
##    log("synopsis = %s"%str(film.synopsis()))
##    log("has_videos? = %s"%str(film.has_videos()))
##    log("has_casting? = %s"%str(film.has_casting()))
##    log("has_photos? = %s"%str(film.has_photos()))
##    log("pictureURL = %s"%str(film.pictureURL()))
##    log("get_photos = %s"%str(film.get_photos()))
##    log("get_casting = %s"%str(film.get_casting()))
##    if film.has_videos():
##        log("get_mediaIDs = %s"%str(film.get_mediaIDs()))
##    else:
##        log("get_mediaIDs = non")
##    try:
##        log("BAurl = %s"%str(film.BAurl()))
##    except ac.AllocineError,msg:
##        log("BAurl = %s"%str(msg))
##    log("XML = %s"%str(film.XML()))
##    log("")
##    log("--------------------")
##    log("")
##
##log("Traitement du handler de films...")
##log("Voici la représentation du handler :")
##log("\t%s"%mh)
##log("")
##log("Liste des films gérés par le handler :")
##for id,title in mh.titles():
##    log("\t%s : %s"%(id,title))
##log("---------------")
##log("")

##log("###########")
##log("# TEST #3 #")
##log("###########")
##log("       Recherches")
##TermeRecherche = u"abc".encode(ac.ALLOCINE_ENCODING)
##log("Recherche de film pour '%s'"%TermeRecherche)
###instanciation de la recherche
##cherche = ac.Search(TermeRecherche,"1")#1 pour films, 2 pour personnalités, 3 pour salle
##trouve = cherche.search()
##log("La recherche a retourné %s résultats"%cherche.nbresults())
###lancement de la recherche
##for id,texte,titre in trouve:
##    log("---------------------")
##    log("\tid = %s"%id)
##    log("\ttexte = %s"%texte.encode(ac.ALLOCINE_ENCODING))
##    log("\t\t%s"%ac.download_pic(texte.encode(ac.ALLOCINE_ENCODING)))
##    log("\ttitre = %s"%titre.encode(ac.ALLOCINE_ENCODING))
##    log("---------------------")
##log("Page précédente = %s"%str(cherche.has_previous()))
##log("Page actuelle = %s"%str(cherche.current()))
##log("Page suivante = %s"%str(cherche.has_next()))
##log("")
##log("Récupération des résultats sur les pages suivantes :")
###Test de récupération des prochains résultats
##while cherche.has_next():
##    log("  Résultats pour la page suivante n°%s"%str(cherche.has_next()))
##    for id,texte,titre in cherche.search(cherche.has_next()):#next():#recherche des résultats suivants
##        log("---------------------")
##        log("\tid = %s"%id)
##        log("\ttexte = %s"%texte.encode(ac.ALLOCINE_ENCODING))
##        log("\t\t%s"%ac.download_pic(texte.encode(ac.ALLOCINE_ENCODING)))
##        log("\ttitre = %s"%titre.encode(ac.ALLOCINE_ENCODING))
##        log("---------------------")
##    log("<%s< | %s | >%s>"%(cherche.has_previous(),cherche.current(),cherche.has_next()))
##    log("Page précédente = %s"%str(cherche.has_previous()))
##    log("Page actuelle = %s"%str(cherche.current()))
##    log("Page suivante = %s"%str(cherche.has_next()))
##    log("")
###
### on reprend les mêmes tests pour les personnalités ...
###
##log("Recherche de personnalités pour '%s'"%TermeRecherche)
###instanciation de la recherche
##cherche = Search(TermeRecherche,"2")#1 pour films, 2 pour personnalités, 3 pour salle
###lancement de la recherche
##for id,texte,titre in cherche.search():
##    log("---------------------")
##    log("\tid = %s"%id)
##    log("\ttexte = %s"%texte.encode(ac.ALLOCINE_ENCODING))
##    log("\ttitre = %s"%titre.encode(ac.ALLOCINE_ENCODING))
##    log("---------------------")
##log("Page précédente = %s"%str(cherche.has_previous()))
##log("Page actuelle = %s"%str(cherche.current()))
##log("Page suivante = %s"%str(cherche.has_next()))
##log("")
##log("Récupération des résultats sur les pages suivantes :")
###Test de récupération des prochains résultats
##while cherche.has_next():
##    log("  Résultats pour la page suivante n°%s"%str(cherche.has_next()))
##    for id,texte,titre in cherche.next():#recherche des résultats suivants
##        log("---------------------")
##        log("\tid = %s"%id)
##        log("\ttexte = %s"%texte.encode(ac.ALLOCINE_ENCODING))
##        log("\ttitre = %s"%titre.encode(ac.ALLOCINE_ENCODING))
##        log("---------------------")
##    log("Page précédente = %s"%str(cherche.has_previous()))
##    log("Page actuelle = %s"%str(cherche.current()))
##    log("Page suivante = %s"%str(cherche.has_next()))
##    log("")
###
### on reprend les mêmes tests pour les salles ...
###
##log("Recherche de salles pour '%s'"%TermeRecherche)
###instanciation de la recherche
##cherche = ac.Search(TermeRecherche,"3")#1 pour films, 2 pour personnalités, 3 pour salle
###lancement de la recherche
##try: cherche.search()
##except ac.AllocineError,msg:
##    log("recherche 3 exception : %s"%msg)
##for id,texte,titre in cherche.search():
##    log("---------------------")
##    log("\tid = %s"%id)
##    log("\ttexte = %s"%texte.encode(ac.ALLOCINE_ENCODING))
##    log("\ttitre = %s"%titre.encode(ac.ALLOCINE_ENCODING))
##    log("---------------------")
##log("Page précédente = %s"%str(cherche.has_previous()))
##log("Page actuelle = %s"%str(cherche.current()))
##log("Page suivante = %s"%str(cherche.has_next()))
##log("")
##log("Récupération des résultats sur les pages suivantes :")
###Test de récupération des prochains résultats
##while cherche.has_next():
##    log("  Résultats pour la page suivante n°%s"%str(cherche.has_next()))
##    for id,texte,titre in cherche.next():#recherche des résultats suivants
##        log("---------------------")
##        log("\tid = %s"%id)
##        log("\ttexte = %s"%texte.encode(ac.ALLOCINE_ENCODING))
##        log("\t\t%s"%ac.download_pic(texte.encode(ac.ALLOCINE_ENCODING)))
##        log("\ttitre = %s"%titre.encode(ac.ALLOCINE_ENCODING))
##        log("---------------------")
##    log("Page précédente = %s"%str(cherche.has_previous()))
##    log("Page actuelle = %s"%str(cherche.current()))
##    log("Page suivante = %s"%str(cherche.has_next()))
##    log("")
###Test de recherche page précédente
##log(" Recherche dans la page précédente")
##for id,texte,titre in cherche.previous():
##    log("---------------------")
##    log("\tid = %s"%id)
##    log("\ttexte = %s"%texte.encode(ac.ALLOCINE_ENCODING))
##    log("\t\t%s"%ac.download_pic(texte.encode(ac.ALLOCINE_ENCODING)))
##    log("\ttitre = %s"%titre.encode(ac.ALLOCINE_ENCODING))
##    log("---------------------")
##log("")
##log("Recherche qui n'existe pas...")
##TermeRecherche = "wwxxqqppmm"
##log("  Recherche de film pour '%s'"%TermeRecherche)
###instanciation de la recherche
##cherche = ac.Search(TermeRecherche,"1")#1 pour films, 2 pour personnalités, 3 pour salle
###lancement de la recherche
##for id,texte,titre in cherche.search():
##    log("---------------------")
##    log("\tid = %s"%id)
##    log("\ttexte = %s"%texte.encode(ac.ALLOCINE_ENCODING))
##    log("\t\t%s"%ac.download_pic(texte.encode(ac.ALLOCINE_ENCODING)))
##    log("\ttitre = %s"%titre.encode(ac.ALLOCINE_ENCODING))
##    log("---------------------")
##log("Page précédente = %s"%str(cherche.has_previous()))
##log("Page actuelle = %s"%str(cherche.current()))
##log("Page suivante = %s"%str(cherche.has_next()))
##log("")
##
##log("Test d'une recherche non gérée par le site")
##log(" type = 99")
###instanciation de la recherche
##try:
##    cherche = ac.Search("parrain","99")#1 pour films, 2 pour personnalités, 3 pour salle
##except ac.AllocineError,msg:
##    log(str(msg))
##log("")
##log("Test d'une recherche non gérée par la librairie")
##log(" type = 4")
###instanciation de la recherche
##try:
##    cherche = ac.Search("parrain","4")#1 pour films, 2 pour personnalités, 3 pour salle
##except ac.AllocineError,msg:
##    log(str(msg))
log("")
log("###########")
log("# TEST #4 #")
log("###########")
log("       Les salles")
log("")
s = ac.Cinema('B0084')#B0084')#P0983
log("Cinema.address() = %s"%s.address().encode(ac.ALLOCINE_ENCODING))
log("Cinema.name() = %s"%s.name().encode(ac.ALLOCINE_ENCODING))
log("Cinema.TIMETABLE")
s.movies()
##for MID in s.TIMETABLE.keys():
##    log(MID)
##    log("".join(["\t%s : %s"%(day.encode(ac.ALLOCINE_ENCODING),schedule.encode(ac.ALLOCINE_ENCODING)) for day,schedule in s.TIMETABLE[MID]]))
##    #print("Cinema.get_schedule(%s) = %s"%(MID,s.get_schedule(MID)))
##log("Cinema.isplaying(1234) = %s"%s.isplaying("1234"))
##log("Cinema.isplaying(60038) = %s"%s.isplaying("60038"))
##log("")
##log("")
##log("###########")
##log("# TEST #5 #")
##log("###########")
##log("       Les favoris")
##log("")
##log("permet de conserver une trace des favoris films, persos, cinema")
##log("")
###instanciation de la classe Favourite
##fav = ac.Favourite()
##fav.add(("CINEMA","P0983","Cinecity à Troyes"))
##fav.add(("MOVIE","12345","Titre du film"))
##log("Sauvegarde des favoris...")
##fav.save("mes favoris",path="",replace=True)
##log("Ajout d'un élément")
##fav.add(("MOVIE","12345","Titre du film")) #existe déjà mais l'utilisateur ne le sais pas
##fav.add(("MOVIE","4321","quel beau film"))
##log("Chargement d'un favoris avec accumulation des favoris temporaires et celui chargé")
##fav.load("mes favoris",path="",append=True)
##log("Suppression d'un élément")
##fav.remove(("MOVIE","4321","quel beau film"))
##log("Autre solution : on sauvegarde avec replace = False et on accumule le temporaire et le fichier existant")
##fav.save("mes favoris",path="",replace=False)
##log("")

