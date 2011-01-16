#!/usr/bin/python
# -*- coding: utf8 -*-
"""
"""


# script constantes
__script__       = "Music Quizz"
__author__       = "Alexsolex"
__credits__      = "Help from XBMC-Passion, http://passion-xbmc.org/"
__platform__     = "xbmc media center, WIN32 [LINUX, OS X, XBOX not tested]"
__date__         = "09-01-2011"
__version__      = "0.1"

#bibliothèques généralistes
import sys
import os
import unicodedata
import xbmc,xbmcgui,xbmcaddon
import random
import re
import threading,thread
import time
from os.path import join
from traceback import print_exc


Addon = xbmcaddon.Addon(id='script.music.quizz')

# INITIALISATION CHEMIN RACINE
ROOTDIR = Addon.getAddonInfo('path')
# Shared resources
BASE_RESOURCE_PATH = join( ROOTDIR, "resources" )
sys.path.append( join( BASE_RESOURCE_PATH, "lib" ) )
# append the proper platforms folder to our path, xbox is the same as win32
env = ( os.environ.get( "OS", "win32" ), "win32", )[ os.environ.get( "OS", "win32" ) == "xbox" ]
sys.path.append( join( BASE_RESOURCE_PATH, "platform_libraries", env ) )

__language__ = Addon.getLocalizedString

AUTO_NEXT_SONG         = Addon.getSetting("autonextsong")=="true"
SONGS_TO_PLAY          = int(Addon.getSetting("nsongs"))
TIME_TO_ANSWER         = int(Addon.getSetting("timetoanswer"))
TIME_BETWEEN_SONGS     = int(Addon.getSetting("timebetweensongs"))
TIME_BETWEEN_QUESTIONS = int(Addon.getSetting("timebetweenquestions"))
TIME_TO_SEEK           = int(Addon.getSetting("seektime"))
HELP_AFTER_ERROR       = Addon.getSetting("helpaftererror")=="true"
NEW_QUESTION_AFTER_ERR = Addon.getSetting("newquestionaftererror")=="true"
CONTINUE_PLAYING_LAST  = Addon.getSetting("continueplaylinglast")=="true"

#import platform's librairies
try:
    from pysqlite2 import dbapi2 as sqlite
    print "using pysqlite2"
except:
    from sqlite3 import dbapi2 as sqlite
    print "using sqlite3"
    pass

#variables
db_path=join(xbmc.translatePath( "special://database/" ), "MyMusic7.db")

#les questions (il faudra les sortir dans un fichier dédié et les placer dans le dossier langue qui convient)
##QUESTIONS = {"artist":[("Quel est l'interprète de cette chanson ?","QCM","C'est bien évidemment '%s' qui interprète cette chanson."),
##                       ("L'interprète de cette chanson est '<artist>',","YN","Cette chanson est interprêtée par '%s'")
##                       ],
##             "title":[("Quel est le titre de cette chanson ?","QCM","Cette chanson s'appelle '%s'"),
##                      ("Le titre de cette chanson est '<title>',","YN","Cette chanson s'intitule '%s'")
##                      ],
##             "album":[("De quel album cette chanson est t'elle extraite ?","QCM","On retrouve ce titre dans l'album '%s'."),
##                      ("Cette chanson est extraite de l'album '<album>'","YN","Une chance sur deux... Pas de chance, ce que vous écoutez est extrait de l'album '%s'.")
##                      ],
##             "year":[("De quelle année date cette chanson ?","QCM","C'est en %s que cette chanson est sortie !"),
##                     #("De quelle année date cette chanson ?","INPUT","%s"),
##                     ("Cette chanson est de <year>,","YN","Cette chanson est de %s.")
##                     ]
##             }
QUESTIONS = {"artist":[(__language__(40000),"QCM",__language__(40001)),
                       (__language__(40002),"YN",__language__(40003))
                       ],
             "title":[(__language__(40004),"QCM",__language__(40005)),
                      (__language__(40006),"YN",__language__(40007))
                      ],
             "album":[(__language__(40008),"QCM",__language__(40009)),
                      (__language__(40010),"YN",__language__(40011))
                      ],
             "year":[(__language__(40012),"QCM",__language__(40013)),
                     (__language__(40014),"YN",__language__(40015))
                     ]
             }
#Attention, la liste des tags doit correspondre à l'ordre des champs tels que requêtés dans la DB
TAGS   = ["title",    "album",    "year",  "genre",    "artist",    "path",    "filename"]
DBTAGS = ["strTitle", "strAlbum", "iYear", "strGenre", "strArtist", "strPath", "strFileName"]



def load_database(cpt=10):
    """charge 'cpt' titres musicaux dans la DB XBMC.
Retourne une liste de tuples [strTitle, strAlbum, iYear, strGenre, strArtist, strPath, strFileName]"""
    conn = sqlite.connect(db_path)
    conn.text_factory = str
    d = conn.cursor()
    d.execute('SELECT DISTINCT strTitle, strAlbum, iYear, strGenre, strArtist, strPath, strFileName FROM songview WHERE strTitle NOT NULL AND strAlbum NOT NULL AND strGenre NOT NULL AND iYear NOT NULL AND strArtist NOT NULL AND strPath NOT NULL AND strFileName NOT NULL ORDER BY RANDOM() LIMIT %s'%cpt)
    #db=[(item[0].encode("utf8") , item[1].encode("utf8") , str(item[2]) , item[3].encode("utf8") , item[4].encode("utf8"), join(item[5].encode("utf8"),item[6].encode("utf8"))) for item in d]
    db=[item for item in d]
    d.close()
    return db

def get_random(tag,notvalue,nb=1):
    """obtient 'nb' informations pour le tag donné dans la base de données en excluant 'notvalue'"""
    field = DBTAGS[TAGS.index(tag)]    
    conn = sqlite.connect(db_path)
    conn.text_factory = str
    d = conn.cursor()
    d.execute('SELECT DISTINCT %s FROM songview WHERE strTitle NOT NULL AND strAlbum NOT NULL AND strGenre NOT NULL AND iYear NOT NULL AND strArtist NOT NULL AND strPath NOT NULL AND strFileName NOT NULL AND iYear NOT LIKE "0" %s ORDER BY RANDOM() LIMIT %s'%(field,
                                                                                                                                                                                                                                            "AND %s NOT LIKE \"%s\""%(field,notvalue),
                                                                                                                                                                                                                                            nb))

    #db=[str(item[0]).encode("utf8")) for item in d]
    db=[]
    for item in d:
        print type(item[0])
        db.append(str(item[0]))
##        try:
##            db.append(str(item[0]))#.encode("utf8")
##        except:
##            db.append(item[0].__repr__())
    d.close()
    return db

def smart_unicode(s):
    """credit : sfaxman"""
    if not s:
        return ''
    try:
        if not isinstance(s, basestring):
            if hasattr(s, '__unicode__'):
                s = unicode(s)
            else:
                s = unicode(str(s), 'UTF-8')
        elif not isinstance(s, unicode):
            s = unicode(s, 'UTF-8')
    except:
        if not isinstance(s, basestring):
            if hasattr(s, '__unicode__'):
                s = unicode(s)
            else:
                s = unicode(str(s), 'ISO-8859-1')
        elif not isinstance(s, unicode):
            s = unicode(s, 'ISO-8859-1')
    return s

def get_question(titreInfos):
    """Génère aléatoirement une question avec ses choix et sa solution.
    plsDB : liste de tuples de la playliste de titres"""
    print "#"*10
    print "-> get_question"
    #select a field to ask a question about (artist, title, album or year)
    tag = random.sample(QUESTIONS.keys(),1)[0]
    print "Question about [%s]"%tag
    #get a random question for the given field, with the kind of question (Y/N or Multi Choice), and the solution sentence
    question,type_reponse,solution = random.sample(QUESTIONS[tag],1)[0]#une question au hasard pour le tag donné
    print "%s (%s) = %s"%(question.encode("utf8"),type_reponse,solution.encode("utf8"))
    #fetch the correct answer for the question
    bonne_rep = str(titreInfos[TAGS.index(tag)]).decode("utf8").encode("utf8","?")#correspond à la bonne info pour le titre concerné,
    try:
        question = question.decode("utf8").encode("utf8","?")
    except:
        question = question
    print type(bonne_rep)
    print "and the correct answer is '%s'"%bonne_rep#.decode("utf8").encode("utf8","?")
    #create the set of proposal including the correct one and randomize it
    if type_reponse == "QCM": #multichoice proposal
        mauvaises_rep = get_random(tag,bonne_rep,3)
        proposal = [(bonne_rep,True),
                    (mauvaises_rep[0],False),
                    (mauvaises_rep[1],False),
                    (mauvaises_rep[2],False)]
        random.shuffle(proposal) #on mélange les solutions !!
    elif type_reponse =="YN": #yes/no proposal
        bon_choix = random.choice([__language__(100),__language__(101)])# set if 'YES' or 'NO' will be the correct answer
        #a YES/NO question include the field and this need to be replaced
        match = re.search(ur"\[{2}(\w+)\]{2}",question)
        if match: tag = match.group(1)
        else: raise "no match for [[...]] in question"
        if bon_choix == __language__(100): #if correct answer is YES
            #include the correct answer in the question
            question = re.sub(ur'\[{2}(\w+)\]{2}',bonne_rep,question) 
        else:#else, correct answer is NO
            #include a wrong answer in the question
            question = re.sub('\[{2}(\w+)\]{2}',get_random(tag,bonne_rep,1)[0],question)
        #make the yes no proposal list with solution
        proposal = [(__language__(100),bon_choix==__language__(100)),
                    (__language__(101),bon_choix==__language__(101))]
    elif type_reponse == "INPUT": #not handle (yet ?) ; made for question with direct keyboard input
        proposal = None
    print "<- get_question"
    print "#"*10
    return question,type_reponse,proposal,solution%unicode(bonne_rep,"utf8")

 
#On attributs des noms aux actions correspondant aux touches du clavier (cf. keymap.xml)
ACTION_PREVIOUS_MENU = 10
ACTION_PLAYER_PAUSE = 12
ACTION_PLAYER_STOP = 13
ACTION_PLAYER_NEXT = 14
ACTION_PLAYER_PREVIOUS = 15

class joueur:
    """Idée de la classe joueur :
mémoriser le score du joueur
garder une copie des stats du joueur"""
    def __init__(self,name=None):
        if not name:
            name = "Invite"
        self.name = name
        self.score = 0

    def raz(self):
        self.score=0
        
    def __add__(self,add):
        self.score+=add
        return self.score

    def save(self):
        f=open(self.name,"w")
        f.write(self.score)
        f.close()

class Conductor: #unused yet
    """Gère la phase de jeu : TODO"""
    def __init__(self):
        self.etapes={0 :"intro",
                     1 :"start",
                     2 :"question",
                     3 :"proposal",
                     4 :"answer",
                     5 :"timeout",
                     6 :"score",
                     7 :"outro"
                     }
        self.etape=0
    def next(self):
        pass
    

#On définit la class gérant l'affichage en windowXML
class MainGUI(xbmcgui.WindowXML):
    
    def __init__(self,*args, **kwargs):
        xbmcgui.WindowXML.__init__( self, *args, **kwargs )
        # Changing the three varibles passed won't change, anything
        # Doing strXMLname = "bah.xml" will not change anything.
        # don't put GUI sensitive stuff here (as the xml hasn't been read yet
        # Idea to initialize your variables here
        pass
     
    def onInit(self):
        #xbmcgui.WindowXML.__init__( self )
        #xbmcgui.lock()
        #Init button id
        self.lbl_question = 602
        self.lbl_numtitre = 603
        self.lbl_timer    = 604
        self.lbl_score    = 605
        self.btn_proposal = [130,131,132,133]
        self.btn_next     = 134
        #self.progressBar = 200
        #self.getControl(self.progressBar).setPercent(0)
        #self.getControl(self.lbl_question).setAnimations([('hidden', 'effect=slide start=0,0 end=-660,0 time=1000',)])

        #masque au début les boutons proposition et la question
        xbmc.executebuiltin( "Skin.SetString(showok,0)")
        xbmc.executebuiltin( "Skin.SetString(showquestion,0)")
        for pos,btnid in enumerate(self.btn_proposal):
            xbmc.executebuiltin( "Skin.SetString(showproposal%s,0)"%(pos) )
            

        #si on comptait le score ??
        self.myscore = 0
        self.getControl(self.lbl_score).setLabel( __language__(102)+" : " + str(self.myscore) )

        


        #xbmcgui.unlock()#débloque l'interface

        
        #MusicPlayer.TimeRemaining : à utiliser ce label si on veut le temps restant de la chanson

        #instancie le lecteur
        self.player = monlecteur()
        #le player est il en train de jouer de la musique
        if self.player.isPlayingAudio():
            self.player.stop()
        else:
            pass
        #lancer le mix de soirée
        #xbmc.executebuiltin("PlayerControl(Partymode(music))")

        #créer une playliste depuis la base de données
        self.create_Random_Playlist(SONGS_TO_PLAY)
        #iinitialisation d'un timer
        self.timer=myTimer(self.hook_TimerEnd,#fonction exécutée à la fin du timer
                         #self.getControl(self.lbl_timer).setLabel,#fonction d'affichage d'une chaine
                         self.setLabel_chrono,
                         TIME_TO_ANSWER) #temps du timer en secondes
        #settings.openSettings() #affiche la config

        #affiche les questions/propositions
        #self.Show_Question_Proposal(False)
        self.getControl(self.btn_next).setVisible(True)#affiche le bouton de démarrage
        self.setFocusId(self.btn_next) #active le focus sur le bouton de démarrage
        self.getControl(self.btn_next).setLabel(__language__( 105 ).encode("utf8"))#label démarrer le quizz
        #self.player.play(self.pls)
        
        
    def create_Random_Playlist(self,nb_songs):
        #on prépare une playliste musicale
        self.pls=xbmc.PlayList(0)
        #on efface son contenu
        self.pls.clear()
        #on charge 'nb_questions' morceaux de musique depuis la base de données
        global plsDB
        plsDB = load_database(nb_songs)
        
        for count,songinfo in enumerate(plsDB):
            #on créé un listitem
            listitem = xbmcgui.ListItem('Music Quizz Question %s'%count,
                                        '',
                                        "",
                                        "No_thumb.jpg",
                                        os.path.join(unicode(songinfo[-2],"utf8"),unicode(songinfo[-1],"utf8")) )#unicode(songinfo[-1],"utf8") )#filepath
            #pour plus tard, pour afficher le thumbnail de l'item :
            #    self.list.getSelectedItem().setThumbnailImage('emailread.png')
            #on configure tous les paramètres de la playliste pour masquer les infos lors de la visualisation
            listitem.setInfo('music', { "tracknumber" : 0,
                                        "year"        : 0,
                                        "genre"       : "Music Quizz "+__language__(107),
                                        "album"       : "Music Quizz "+__language__(107),
                                        "artist"      : "Music Quizz "+__language__(107),
                                        "title"       : "Music Quizz "+__language__(107)
                                        }
                             )

            self.pls.add(os.path.join(unicode(songinfo[-2],"utf8"),unicode(songinfo[-1],"utf8")),listitem)#on ajoute l'élément de liste à la playliste
        
    def setLabel_chrono(self,label):
        self.getControl(self.lbl_timer).setVisible(True)
        self.getControl(self.lbl_timer).setLabel(__language__(108)%label)

    def Set_Question(self):
        #self.timer.stop()
        #self.getControl(self.progressBar).setPercent(self.pls.getposition()*20)
        #print self.getControl(self.progressBar).getPercent()
        
        #récup question/propositions
        self.question,type_reponse,self.proposal,self.solution = get_question(plsDB[self.pls.getposition()])
        #bouton next masqué
        self.getControl(self.btn_next).setVisible(False)#on masque le bouton 'next'
        #affiche
        self.Show_Question_Proposal(True)
        xbmc.sleep(50)
        self.setFocusId(self.btn_proposal[0])
        #la question est posée, on lance le chrono
        self.timer.raz()
        self.timer.start() # GO !!


    def Show_Question_Proposal(self,booleen):
        #self.getControl(self.lbl_question).setVisible(booleen)
        if booleen: vis = "1"
        else: vis = "0"
        
        #self.getControl(self.lbl_question).setLabel(self.question)
        if booleen:
            self.getControl(self.lbl_question).setLabel(self.question)
            xbmc.executebuiltin( "Skin.SetString(showquestion,%s)"%vis )
        print "show_question_proposal"
        print self.btn_proposal
        print type(self.btn_proposal)
        print enumerate(self.btn_proposal)
        for pos,btnid in enumerate(self.btn_proposal):
            try:
                self.getControl(btnid).setLabel(self.proposal[pos][0])
                xbmc.executebuiltin( "Skin.SetString(showproposal%s,%s)"%(pos,vis) )
            except:
                xbmc.executebuiltin( "Skin.SetString(showproposal%s,0)"%(pos) )
        if booleen:
            xbmc.sleep(100)
            self.setFocus(self.getControl(self.btn_proposal[0]))

    def hook_TimerEnd(self):
        #fin du timer, on interromp la question, et on passe à la suite
        self.timer.stop()
        print "Wait for timer to stop..."
        try:
            self.timer.join(1.5)
        except:
            print "Timer join raises an exception !"
        dialog=xbmcgui.Dialog()
        ## TODO : REMPLACER les dialogs par des labels ds le skin
        if self.pls.getposition()==self.pls.size()-1:#le dernier item de la playliste
            ok = dialog.ok("Music Quizz",__language__(200),__language__(201),__language__(202))
        else:
            ok = dialog.ok("Music Quizz",__language__(203),__language__(204),__language__(205))

        self.score(False)
        if NEW_QUESTION_AFTER_ERR:
            xbmc.sleep(TIME_BETWEEN_QUESTIONS*1000)
            self.Set_Question()#change la question
        else:
            if AUTO_NEXT_SONG:
                xbmc.sleep(TIME_BETWEEN_SONGS*1000)
                self.PlayNext()
            else:
                #on affiche le bouton next si la chanson n'est pas la dernière
                self.getControl(self.btn_next).setLabel( __language__( 104 ).encode("utf8"))#prochaine chanson
                self.getControl(self.btn_next).setVisible(not self.pls.getposition() == self.pls.size()-1)
                #A FAIRE : afficher un message d'erreur

    
    def PlayNext(self):
        if self.pls.getposition()==self.pls.size()-1:#le dernier item de la playliste
            self.Show_Question_Proposal(False)
            if not CONTINUE_PLAYING_LAST:
                self.player.stop()
            self.timer.stop()
            print "Wait for timer to stop..."
            try:
                self.timer.join(1.5)
            except:
                print "Timer join raises an exception !"
            self.getControl(self.lbl_timer).setVisible(False)#setLabel("...")#affiche le score
            
            #self.getControl(self.lbl_timer).setVisible(False)
        elif AUTO_NEXT_SONG:
            self.player.playnext()#chanson suivante
            

    def score(self,isSuccess):
        self.Show_Question_Proposal(False)
        
        if isSuccess:
            self.myscore+=1
            self.timer.stop()
            print "Wait for timer to stop..."
            try:
                self.timer.join(1.5)
            except:
                print "Timer join raises an exception !"
            xbmc.sleep(100)
            #self.getControl(self.lbl_timer).setLabel(random.choice(__language__(40050).split("|")).encode("utf8"))#choisi parmis les félicitations
            self.getControl(self.lbl_timer).setLabel(__language__(301).encode("utf8"))
            #xbmc.sleep(TIME_BETWEEN_SONGS*1000)
        else:
            self.myscore-=1
            self.timer.stop()
            print "Wait for timer to stop..."
            try:
                self.timer.join(1.5)
            except:
                print "Timer join raises an exception !"
            xbmc.sleep(100)
            if HELP_AFTER_ERROR:
                self.getControl(self.lbl_timer).setLabel(self.solution.decode("utf8"))
            else:
                #self.getControl(self.lbl_timer).setLabel(random.choice(__language__(40051).split("|")).encode("utf8"))#choisi parmi les messages d'erreur
                self.getControl(self.lbl_timer).setLabel(__language__(303).encode("utf8"))
            #xbmc.sleep(TIME_BETWEEN_SONGS*1000)
        self.getControl(self.lbl_score).setLabel( __language__(102)+" : " + str(self.myscore) )


    def onAction(self, action):
        if action.getId() == 107: return
        print "onaction = %s"%action.getId()
        #Close the script
        if action == ACTION_PREVIOUS_MENU :
            #self.tempo.stop()
            self.timer.stop()
            print "Wait for timer to stop..."
            try:
                self.timer.join(1.5)
            except:
                print "Timer join raises an exception !"
            try:
                self.player.stop()#on arrête le player
            except:
                pass
            self.close()#on ferme la classe windowxml
        elif action == ACTION_PLAYER_PAUSE:
            if not(self.timer.end):#si le compteur est en marche
                #statut de la pause
                p=self.timer.pause
                #pause/dé-pause le compteur
                self.timer.Pause()
                #masque les controles question et réponses
                self.Show_Question_Proposal(p)
                #affiche un bouton pause
                #TODO
            
        elif action == ACTION_PLAYER_STOP:
            self.timer.stop()
            print "Wait for timer to stop..."
            try:
                self.timer.join(1.5)
            except:
                print "Timer join raises an exception !"
            self.close()
        elif action == ACTION_PLAYER_NEXT or action == ACTION_PLAYER_PREVIOUS:
            self.timer.stop()
            print "Wait for timer to stop..."
            try:
                self.timer.join(1.5)
            except:
                print "Timer join raises an exception !"
        else:
            pass
            #print str(action.getId())
            #self.getControl(self.lbl_numtitre).setLabel( str(action.getId()) )
            #self.getControl(self.lbl_numtitre).setLabel( str(action.getButtonCode()) )

    def onClick(self, controlID):
        """
            Notice: onClick not onControl
            Notice: it gives the ID of the control not the control object
        """

        #gestion de la réponse donnée
        if controlID in self.btn_proposal:
            choix = self.btn_proposal.index(controlID)#choix est le bouton de la réponse donné (0 à 3)
            #BONNE REPONSE
            if self.proposal[choix][1]:
                xbmc.executebuiltin( "Skin.SetString(showok,1)")
                xbmc.sleep(1000)
                self.score(True)
                #CHANSON SUIVANTE AUTOMATIQUE
                if AUTO_NEXT_SONG:
                    xbmc.sleep(TIME_BETWEEN_SONGS*1000)
                    if self.pls.getposition() == self.pls.size()-1:
                        #si la chanson est la dernière
                        self.getControl(self.btn_next).setLabel( __language__( 106 ).encode("utf8"))#recommencer
                        self.getControl(self.btn_next).setVisible(True)
                        xbmc.sleep(100)
                        self.setFocusId(self.btn_next)
                #CHANSON SUIVANTE MANUELLEMENT
                else:
                    #on affiche le bouton next 
                    if not self.pls.getposition() == self.pls.size()-1:
                        #si la chanson n'est pas la dernière
                        self.getControl(self.btn_next).setLabel( __language__( 104 ).encode("utf8"))#prochaine chanson
                    else:
                        #il s'agit de la dernière chanson
                        self.getControl(self.btn_next).setLabel( __language__( 106 ).encode("utf8"))#recommencer
                    self.getControl(self.btn_next).setVisible(True)
                    xbmc.sleep(100)
                    self.setFocusId(self.btn_next)
                xbmc.executebuiltin( "Skin.SetString(showok,0)")
                xbmc.sleep(1000)
                self.PlayNext()                        

            #MAUVAISE REPONSE
            else:
                self.score(False)
                #QUESTION TANT QUE LA REPONSE EST MAUVAISE
                if NEW_QUESTION_AFTER_ERR:
                    xbmc.sleep(TIME_BETWEEN_QUESTIONS*1000)
                    self.Set_Question()#change la question
                #UNE SEULE QUESTION PAR CHANSON
                else:
                    #CHANSON SUIVANTE AUTOMATIQUE
                    if AUTO_NEXT_SONG:
                        xbmc.sleep(TIME_BETWEEN_SONGS*1000)
                        self.PlayNext()
                    #CHANSON SUIVANTE MANUELLEMENT
                    else:
                        #on affiche le bouton next si la chanson n'est pas la dernière
                        self.getControl(self.btn_next).setLabel( __language__( 104 ).encode("utf8"))#prochaine chanson
                        self.getControl(self.btn_next).setVisible(not self.pls.getposition() == self.pls.size()-1)
                        xbmc.sleep(100)
                        self.setFocusId(self.btn_next)
                        #A FAIRE : afficher un message d'erreur

                       
        #BOUTON SUITE
        if controlID == self.btn_next: #si l'utilisateur ne veut pas attendre la prochaine chanson
            self.getControl(self.btn_next).setVisible(False)
##            if not(self.player.isPlayingAudio()):

            if self.pls.getposition() == self.pls.size()-1:
                #si la chanson est la dernière, le bouton next relance le quizz
                self.player.stop()
                xbmc.sleep(500)
            if not(self.player.isPlayingAudio()):
                self.myscore = 0
                self.getControl(self.lbl_score).setLabel( __language__(102)+" : " + str(self.myscore) )
                self.pls.clear()
                self.create_Random_Playlist(SONGS_TO_PLAY)
                self.player.play(self.pls)
            else:
                self.player.playnext() #on lance la prochaine question manuellement
        
  
    def onFocus(self, controlID):
        pass



#on reconstruit la classe xbmc.player afin d'intercepter les évènements du lecteur
class monlecteur(xbmc.Player):
    def __init__(self):
        xbmc.Player.__init__( self )

    def onPlayBackStarted(self):#lors de la lecture ou du passage à une nouvelle chanson
        #appelé à chaque début de lecture
        self.seekTime(TIME_TO_SEEK) #on passe un temps pour éviter l'intro
        w.getControl(w.lbl_numtitre).setLabel(__language__(103).encode("utf8")%(w.pls.getposition()+1,w.pls.size()))
        xbmc.sleep(100)#on attend le chargement de la chanson pour maintenir l'animation des boutons qui va suivre
        w.Set_Question()#on charge la nouvelle question

    def onPlayBackStopped(self):#lors d'un arrêt volontaire de la musique
        pass
    
    def onPlayBackEnded(self):#à la fin de la lecture (ou playliste)
        w.Show_Question_Proposal(False)

#timer

class myTimer(threading.Thread):
    def __init__(self,out_func,label_func=None,temps=10):
        threading.Thread.__init__(self)
        self.temps=temps
        self.labelfunc=label_func #recoit le chrono
        self.outfunc=out_func #la classe appelante
        self.running=False
        self.pause=False
        self.end=False
        self.time=0
        self.memtime=0
        self.hooking=True
        
    def raz(self):
        self.running = False
        self.pause=False
        self.end=False
        self.time=0
        self.memtime=0
        self.hooking=True
        
    def run(self):
        self.end=False
        self.running=True
        starttime = time.time()
        while self.time<self.temps and not self.end:
            while not(self.pause) and self.time<self.temps and not self.end:
                self.time = time.time()-starttime+self.memtime
                time.sleep(0.01)
                if self.labelfunc:  self.labelfunc("%i"%(self.temps-self.time+1))
                #print self.time
            t=time.time()
            #if self.labelfunc: self.labelfunc("Pause...")
            while self.pause and not self.end:#pause
                time.sleep(0.01)
                pass
            starttime=time.time()
            self.memtime=self.time
        if self.end:
            #if self.labelfunc: self.labelfunc("TERMINE à %0.1f secondes"%self.time)
            if self.hooking: self.outfunc()
        else:
            #if self.labelfunc: self.labelfunc("TEMPS ECOULE !!!")
            if self.hooking: self.outfunc()

    def Pause(self):
        self.pause = not(self.pause)

    def stop(self):
        self.running=False
        self.hooking=False
        self.end=True
        
# Lancement de l'interface
if  __name__ == "__main__":
    print
    print
    # Appel de la class
    w = MainGUI("musicquizz.xml", ROOTDIR, "DefaultSkin")
    xbmc.sleep(100)
    w.doModal()
    print
    print
    print w.timer.running
    print "thread"
    print threading.activeCount() 

    del w
