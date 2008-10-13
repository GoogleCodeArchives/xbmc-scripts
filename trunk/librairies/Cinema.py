import sys

###exemple de mesure de performance
##import timeit
##s = """\
##try:
##    del sys.modules["allocine"]
##except:
##    pass
##"""
##t = timeit.Timer(stmt=s)
##print "%.2f usec/pass" % (1000000 * t.timeit(number=100000)/100000)
########################



# déchargement de la librairie allocine pour prendre en compte les modifs
if sys.modules.has_key("allocine"):
    del sys.modules["allocine"]
import allocine


###par défaut la librairie utilise le site francais de allocine.
###pour changer le site pour un pays donné :
##allocine.set_country("EN")
##allocine.set_country("ES")
allocine.set_country("FR")
##allocine.set_country("DE")
##
#parcourir les sorties
##try:
##    #instanciation de l'agenda pour les sorties de la semaine
##    ag = allocine.agenda("now")
##    ##... pour les sorties de la semaine prochaine
##    #ag = allocine.agenda("next")
##    ##... pour les sorties de la semaine jj/mm/aaaa
##    #ag = allocine.agenda("jj/mm/aaaa")
##except allocine.AllocineError,msg:
##    print msg

###boucler sur tous les films de la période pour en afficher des informations
##for (ID,Titre,TitreO,AfficheURL,Genre,Duree,NotePublic) in ag.get_movies_datas():
##    print "%s (%s) [%s]"%(Titre,TitreO,ID)
##    print "\t%s, %s"%(Genre,Duree)
##    print "\tNote : %s"%NotePublic
##    print "\t%s"%AfficheURL
##    print
##
#boucler sur tous les films de la période pour afficher une version textuelle des informations
##for moviedata in ag.get_movies():
##    print allocine.infos_text(moviedata)
##    print "----------"
##
##ag = allocine.agenda("now")
###pour trouver les périodes précédentes et/ou suivante :
##print "\tavec agenda() ou agenda('now')"
###l'instance d'agenda précédente est faite avec le paramètre 'now'
##print "\t\t<< %s | %s >>"%(ag.previous_week_date(),ag.next_week_date())
##print "\tavec agenda('next')"
##ag = allocine.agenda('next')
##print "\t\t<< %s | %s >>"%(ag.previous_week_date(),ag.next_week_date())
##print "\tavec agenda(%s)"%ag.next_week_date()
##ag2 = allocine.agenda(ag.next_week_date())
##print "\t\t<< %s | %s >>"%(ag2.previous_week_date(),ag2.next_week_date())
##print
####print

###collection de films afin de gérer les films déjà chargés lors de la session
##collection=allocine.Movies()
###charger un film par la collection de films
##f=collection.new("123734")
###charger un film directement
###f=allocine.Movie("123734")#"112381")#"123392")
###les infos du film sont parsées lors de l'instanciation
##
###afficher le titre
##print f.title()
###la date
##print f.date()
###le resume
##print f.synopsis()
###l'url de l'affiche
##print f.pictureURL()
###l'URL de la bande annonce principale
##try:
##    print f.BAurl()
##except Exception,msg:
##    print msg
###la liste des bandes annonces est récupérée et peut être traitée ainsi
##print
##try:
##    for IDmedia,PICurl,title in f.get_mediaIDs():
##        print "%s [%s]"%(IDmedia,title)
##        print "\t%s"%PICurl
##        #on peut obtenir l'URL de la video
##        print allocine.get_video_url(IDmedia)
##        print "--------"
##except Exception,msg:
##    print msg


###EFFECTUER UNE RECHERCHE (OBSOLETHE !! UTILISER LA DEUXIEME METHODE)
###1- on instancie la recherche
##s = allocine.Search()
###2- pour connaitre les recherches supportées
##supp= s.supported()
##print  "\n".join(["%s : %s"%(tid,supp[tid]) for tid in supp.keys()])
##print
###3- pour rechercher dans les films:
##for fid,txt,title in s.search(u"paris","3"):
##    print "\t#%s - %s (%s)"%(fid,title,txt)
###4- est-ce qu'il y a encore des résultats
##print "Prochaine page de résultats : "+str(s.has_next())
##print 
###5- quels sont les prochains résultats
##if s.has_next():
##    print "Les prochains résultats sont :"
##    print "\n".join(["\t%s - #%s (%s)"%(title,fid,txt) for fid,txt,title in s.next_results()])
###6- Quels sont tous les résultats trouvés jusque maintenant
##print "\n".join(["\t%s - #%s (%s)"%(title,fid,txt) for fid,txt,title in s.RESULTS_ALL])

###EFFECTUER UNE RECHERCHE 2
###1- on instancie la recherche
##s = allocine.Search(u"Paris","1")
##
###3- pour rechercher dans les films:
##for fid,txt,title in s.start():
##    print "\t#%s - %s (%s)"%(fid,title,txt)
###4- est-ce qu'il y a encore des résultats
##print "Prochaine page de résultats : "+str(s.has_next())
##print 
###5- quels sont les prochains résultats
##if s.has_next():
##    print "Les prochains résultats sont :"
##    print "\n".join(["\t#%s - %s (%s)"%(fid,title,txt) for fid,txt,title in s.next()])


# LES PERSONNALITES
p = allocine.Personality("27633")
print p.name()
print
print "Lien vers sa photo :"
print p.pictureURL()
print
print "voici ses fonctions dans le cinema :"
print p.jobs()
print
print "-----------"
bio,films,perso = p.Biography()
print u"Biographie:"
print bio
print
print u"Films cités dans la bio :"
print films
print
print u"Personnalités citées dans la bio:"
print perso
print
print "-------"
print u"Y'a t'il des photos pour cette personnalité ?"
print p.has_photos()
if p.has_photos():
    print "Il y a %s photos"%len(p.get_photos())
    print u"En voici les 10 premières :"
    for path,title in p.get_photos()[:10]:
        print "%s (%s)"%(title,path)
else:
    print "non il n'y en a pas"
print
print "--------"
print
print "Y'a t'il des videos ?"
print p.has_videos()
if p.has_videos():
    print "il y a %s videos"%len(p.get_mediaIDs())
    for mediaID,picurl,title in p.get_mediaIDs():
        print " - %s (%s)"%(title,mediaID)
else:
    print "pas de videos"
print
print "concernant le dernier media, voici l'url de la video"
print allocine.get_video_url(mediaID)


