#!/usr/bin/python
# -*- coding: utf8 -*-
"""
TODO :
  - upgrade iptcinfo library (need some unicode improvement)
"""
import os,sys
try:
    import xbmc
    makepath=xbmc.translatePath(os.path.join)
except:
    makepath=os.path.join
home = os.getcwd().replace(';','')
#these few lines are taken from AppleMovieTrailers script
# Shared resources
BASE_RESOURCE_PATH = makepath( home, "resources" )
DATA_PATH = xbmc.translatePath( "special://profile/addon_data/plugin.image.mypicsdb/")
PIC_PATH = makepath( BASE_RESOURCE_PATH, "images")
DB_PATH = xbmc.translatePath( "special://database/")
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )
# append the proper platforms folder to our path, xbox is the same as win32
env = ( os.environ.get( "OS", "win32" ), "win32", )[ os.environ.get( "OS", "win32" ) == "xbox" ]
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "platform_libraries", env ) )


import urllib
import re
import xbmcplugin,xbmcgui,xbmc,xbmcaddon
import os.path

Addon = xbmcaddon.Addon(id='plugin.image.mypicsdb')
__language__ = Addon.getLocalizedString
sys_enc = sys.getfilesystemencoding()
   
if sys.modules.has_key("MypicsDB"):
    del sys.modules["MypicsDB"]
import MypicsDB as MPDB
    
global pictureDB
pictureDB = os.path.join(DB_PATH,"MyPictures.db")
                               
        

def clean2(s): # remove \\uXXX
    """credit : sfaxman"""
    pat = re.compile(r'\\u(....)')
    def sub(mo):
        return unichr(int(mo.group(1), 16))
    return pat.sub(sub, smart_unicode(s))

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

def unescape(text):
    u"""
    credit : Fredrik Lundh
    found : http://effbot.org/zone/re-sub.htm#unescape-html"""
    import htmlentitydefs
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)





class _Info:
    def __init__( self, *args, **kwargs ):
        self.__dict__.update( kwargs )
    def has_key(key):
        return key in self.__dict__

class Main:
    def __init__(self):
        self.get_args()

    def get_args(self):
        print sys.argv[2][1:].replace("&",", ")
        exec "self.args = _Info(%s)" % ( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ), )

    def Title(self,title):
        xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=urllib.unquote_plus(title.encode("utf-8")) )
        
    def addDir(self,name,params,action,iconimage,fanart=None,contextmenu=None,total=0,info="*",replacemenu=True):
        #params est une liste de tuples [(nomparametre,valeurparametre),]
        #contitution des paramètres
        print params
        try:
            parameter="&".join([param+"="+repr(urllib.quote_plus(valeur.encode("utf-8"))) for param,valeur in params])
        except:
            parameter=""
        #création de l'url
        u=sys.argv[0]+"?"+parameter+"&action="+repr(str(action))+"&name="+repr(urllib.quote_plus(name.encode("utf8")))
        ok=True
        #création de l'item de liste
        liz=xbmcgui.ListItem(name, thumbnailImage=iconimage)
        if fanart:
            liz.setProperty( "Fanart_Image", fanart )
        #adjonction d'informations
        #liz.setInfo( type="Pictures", infoLabels={ "Title": name } )
        #menu contextuel
        if contextmenu :
            liz.addContextMenuItems(contextmenu,replacemenu)
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True,totalItems=total)
        return ok
    
    def addPic(self,picname,picpath,info="*",fanart=None,contextmenu=None,replacemenu=True):
        ok=True
        liz=xbmcgui.ListItem(picname,info)
        liz.setLabel2(info)
        if contextmenu:
            liz.addContextMenuItems(contextmenu,replacemenu)
        if fanart:
            liz.setProperty( "Fanart_Image", fanart )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=os.path.join(picpath,picname),listitem=liz,isFolder=False)
        
    def show_home(self):
        # par années
        self.addDir(unescape(__language__(30101)),[("period","year"),("value",""),("viewmode","view")],
                    "showdate",os.path.join(PIC_PATH,"dates.png"),
                    fanart=os.path.join(PIC_PATH,"fanart-date.png"))
        # par dossiers
        self.addDir(unescape(__language__(30102)),[("method","folders"),("folderid",""),("onlypics","non"),("viewmode","view")],
                    "showfolder",os.path.join(PIC_PATH,"folders.png"),
                    fanart=os.path.join(PIC_PATH,"fanart-folder.png"))
        # par mots clés
        self.addDir(unescape(__language__(30103)),[("kw",""),("viewmode","view")],"showkeywords",
                    os.path.join(PIC_PATH,"keywords.png"),
                    fanart=os.path.join(PIC_PATH,"fanart-keyword.png"))
        # période
        self.addDir(unescape(__language__(30105)),[("period",""),("viewmode","view"),],"showperiod",
                    os.path.join(PIC_PATH,"period.png"),
                    fanart=os.path.join(PIC_PATH,"fanart-period.png"))
        # Collections
        self.addDir(unescape(__language__(30150)),[("collect",""),("method","show"),("viewmode","view")],"showcollection",
                    os.path.join(PIC_PATH,"collection.png"),
                    fanart=os.path.join(PIC_PATH,"fanart-collection.png"))
        # recherche globale
        self.addDir(unescape("Global search"),[("searchterm",""),("viewmode","view")],"globalsearch",
                    os.path.join(PIC_PATH,"search.png"),
                    fanart=os.path.join(PIC_PATH,"fanart-search.png"))
        # chemin scannés
        self.addDir(unescape("Chemins racines"),[("do","showroots"),("viewmode","view")],"rootfolders",
                    os.path.join(PIC_PATH,"search.png"),
                    fanart=os.path.join(PIC_PATH,"fanart-search.png"))
        
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE)
        xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=urllib.unquote_plus("My Pictures Library".encode("utf-8")) )
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def show_date(self):
        #period = year|month|date
        #value  = "2009"|"12/2009"|"25/12/2009"
        action="showdate"
        if self.args.period=="year":
            listperiod=MPDB.get_years()
            nextperiod="month"
            allperiod =""
            action="showdate"
        elif self.args.period=="month":
            listperiod=MPDB.get_months(self.args.value)
            nextperiod="date"
            allperiod="year"
            action="showdate"
        elif self.args.period=="date":
            listperiod=MPDB.get_dates(self.args.value)
            nextperiod="date"
            allperiod = "month"
            action="showpics"
        else:
            listperiod=[]
            nextperiod=None

        if not None in listperiod:
            self.addDir(name      = __language__(30100)%(self.args.value,MPDB.countPeriod(allperiod,self.args.value)), #libellé#"All the period %s (%s pics)"%(self.args.value,MPDB.countPeriod(allperiod,self.args.value)), #libellé
                        params    = [("method","date"),("period",allperiod),("value",self.args.value),("viewmode","view")],#paramètres
                        action    = "showpics",#action
                        iconimage = os.path.join(PIC_PATH,"dates.png"),#icone
                        fanart    = os.path.join(PIC_PATH,"fanart-date.png"),
                        contextmenu   = None)#menucontextuel
            total=len(listperiod)
            for period in listperiod:
                if period:
                    self.addDir(name      = "%s (%s %s)"%(period,MPDB.countPeriod(self.args.period,period),__language__(30050)), #libellé
                                params    = [("method","date"),("period",nextperiod),("value",period),("viewmode","view")],#paramètres
                                action    = action,#action
                                iconimage = os.path.join(PIC_PATH,"dates.png"),#icone
                                fanart    = os.path.join(PIC_PATH,"fanart-date.png"),
                                contextmenu   = None,#menucontextuel
                                total = total)#nb total d'éléments
                
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE)
        xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="%s : %s"%(__language__(30101),urllib.unquote_plus(self.args.value.encode("utf-8"))) )
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def show_folders(self):
        #on récupère les sous dossiers si il y en a
        if not self.args.folderid: #pas d'id on affiche les dossiers racines
            childrenfolders=[row for row in MPDB.Request("SELECT idFolder,FolderName FROM folders WHERE ParentFolder is null")]
        else:#sinon on affiche les sous dossiers du dossier sélectionné
            childrenfolders=[row for row in MPDB.Request("SELECT idFolder,FolderName FROM folders WHERE ParentFolder='%s'"%self.args.folderid)]
        total = len(childrenfolders)

        #on ajoute les dossiers 
        for idchildren, childrenfolder in childrenfolders:
            #print "%s (%s pics)"%(childrenfolder,MPDB.countPicsFolder(idchildren))
            self.addDir(name      = "%s (%s %s)"%(childrenfolder.decode("utf8"),MPDB.countPicsFolder(idchildren),__language__(30050)), #libellé
                        params    = [("method","folders"),("folderid",str(idchildren)),("onlypics","non"),("viewmode","view")],#paramètres
                        action    = "showfolder",#action
                        iconimage = os.path.join(PIC_PATH,"folders.png"),#icone
                        fanart    = os.path.join(PIC_PATH,"fanart-folder.png"),
                        contextmenu   = None,#menucontextuel
                        total = total)#nb total d'éléments
        
        #maintenant, on liste les photos si il y en a, du dossier en cours
        picsfromfolder = [row for row in MPDB.Request("SELECT p.FullPath,f.strFilename FROM files f,folders p WHERE f.idFolder=p.idFolder AND f.idFolder='%s'"%self.args.folderid)]
        for path,filename in picsfromfolder:
            self.addPic(filename,path,contextmenu=[( __language__(30152),"XBMC.RunPlugin(\"%s?action='addtocollection'&viewmode='view'&path='%s'&filename='%s'\")"%(sys.argv[0],
                                                                                                                         urllib.quote_plus(path),
                                                                                                                         urllib.quote_plus(filename))
                              ),("Don't use this picture","",)],
                        fanart = os.path.join(PIC_PATH,"fanart-folder.png")
                        )
                            #("Add to Collection","XBMC.RunPlugin(%s?method='folders'&folderid='2'&onlypics='non'&action='showfolder'&name='2005-05+%%2823+images%%29')"%sys.argv[0])
            
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE)
        xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="%s : %s"%(__language__(30102),urllib.unquote_plus(self.args.folderid.encode("utf-8"))) )
        #xbmcplugin.setPluginFanart(int(sys.argv[1]), os.path.join(PIC_PATH,"fanart-period.png"))
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def show_keywords(self):
        # affiche les mots clés
        listkw = [u"%s"%k.decode("utf8")  for k in MPDB.list_KW()]
        if MPDB.search_keyword(None): #si il y a des photos sans mots clés
            self.addDir(name      = "%s (%s %s)"%(__language__(30104),MPDB.countKW(None),__language__(30050)), #libellé
                        params    = [("method","keyword"),("kw",""),("viewmode","view")],#paramètres
                        action    = "showpics",#action
                        iconimage = os.path.join(PIC_PATH,"keywords.png"),#icone
                        fanart    = os.path.join(PIC_PATH,"fanart-keyword.png"),
                        contextmenu   = None)#menucontextuel
        total = len(listkw)
        for kw in listkw:
            #on alimente le plugin en mots clés
            self.addDir(name      = "%s (%s %s)"%(kw,MPDB.countKW(kw),__language__(30050)), #libellé
                        params    = [("method","keyword"),("kw",kw),("viewmode","view")],#paramètres
                        action    = "showpics",#action
                        iconimage = os.path.join(PIC_PATH,"keywords.png"),#icone
                        fanart    = os.path.join(PIC_PATH,"fanart-keyword.png"),
                        contextmenu   = [( "Tout ajouter à la collection...","XBMC.RunPlugin(\"%s?action='addfolder'&method='keyword'&kw='%s'&viewmode='scan'\")"%(sys.argv[0],kw))],#menucontextuel
                        total = total)#nb total d'éléments
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE)
        xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="%s : %s"%(__language__(30103),urllib.unquote_plus(self.args.kw.encode("utf-8"))) )
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def show_period(self):
        self.addDir(name      = __language__(30106),
                    params    = [("period","setperiod"),("viewmode","view")],#paramètres
                    action    = "showperiod",#action
                    iconimage = os.path.join(PIC_PATH,"newperiod.png"),#icone
                    fanart    = os.path.join(PIC_PATH,"fanart-period.png"),
                    contextmenu   = None)#menucontextuel
        #If We previously choose to add a new period, this test will ask user for setting the period :
        if self.args.period=="setperiod":
            dateofpics = MPDB.get_pics_dates()#the choice of the date is made with pictures in database (datetime of pics are used)
            dialog = xbmcgui.Dialog()
            rets = dialog.select(__language__(30107),dateofpics)#choose the start date
            if not rets==-1:#is not canceled
                datestart = dateofpics[rets]
                retf = dialog.select(__language__(30108),dateofpics[rets:])#choose the end date (all dates before startdate are ignored to preserve begin/end)
                if not rets==-1:#if end date is not canceled...
                    dateend = dateofpics[rets+retf]
                    #now input the title for the period
                    kb = xbmc.Keyboard(__language__(30109)%(datestart,dateend), __language__(30110), False)
                    kb.doModal()
                    if (kb.isConfirmed()):
                        titreperiode = kb.getText()
                    else:
                        titreperiode = __language__(30109)%(datestart,dateend)
                    #add the new period inside the database
                    MPDB.addPeriode(titreperiode,"datetime('%s')"%datestart,"datetime('%s')"%dateend)
            update=True
        else:
            update=False

        #search for inbase periods and show periods
        for periodname,dbdatestart,dbdateend in MPDB.ListPeriodes():
            datestart,dateend = MPDB.Request("SELECT strftime('%%Y-%%m-%%d',datetime('%s')),strftime('%%Y-%%m-%%d',datetime('%s','+1 day'))"%(dbdatestart,dbdateend))[0]
            self.addDir(name      = "%s (%s)"%(periodname.decode("utf8"),__language__(30113)%(datestart,dateend)), #libellé
                        params    = [("method","date"),("period","period"),("datestart",datestart),("dateend",dateend),("viewmode","view")],#paramètres
                        action    = "showpics",#action
                        iconimage = os.path.join(PIC_PATH,"period.png"),#icone
                        fanart    = os.path.join(PIC_PATH,"fanart-period.png"),
                        contextmenu   = [ ( __language__(30111),"XBMC.RunPlugin(\"%s?action='removeperiod'&viewmode='view'&periodname='%s'&period='period'\")"%(sys.argv[0],periodname) ),
                                          ( __language__(30112),"XBMC.RunPlugin(\"%s?action='renameperiod'&viewmode='view'&periodname='%s'&period='period'\")"%(sys.argv[0],periodname) )
                                        ] )#menucontextuel
            
        xbmcplugin.addSortMethod( int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE )
        xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="%s"%(__language__(30105)))
        xbmcplugin.endOfDirectory( int(sys.argv[1]),updateListing=update )

    def show_collection(self):
        if self.args.method=="setcollection":#ajout d'une collection
            kb = xbmc.Keyboard("",__language__(30155) , False)
            kb.doModal()
            if (kb.isConfirmed()):
                namecollection = kb.getText()
            else:
                #name input for collection has been canceled
                return
            #create the collection in the database
            MPDB.NewCollection(namecollection)
            refresh=True
        else:
            refresh=False
        self.addDir(name      = __language__(30160),
                    params    = [("method","setcollection"),("collect",""),("viewmode","view"),],#paramètres
                    action    = "showcollection",#action
                    iconimage = os.path.join(PIC_PATH,"newcollection.png"),#icone
                    fanart    = os.path.join(PIC_PATH,"fanart-collection.png"),
                    contextmenu   = None)#menucontextuel

        for collection in MPDB.ListCollections():
            self.addDir(name      = collection[0].decode("utf8"),
                        params    = [("method","collection"),("collect",collection[0].decode("utf8")),("viewmode","view")],#paramètres
                        action    = "showpics",#action
                        iconimage = os.path.join(PIC_PATH,"collection.png"),#icone
                        fanart    = os.path.join(PIC_PATH,"fanart-collection.png"),
                        contextmenu   = [(__language__(30158),"XBMC.RunPlugin(\"%s?action='removecollection'&viewmode='view'&collect='%s'\")"%(sys.argv[0],collection[0].decode("utf8")) ),
                                         (__language__(30159),"XBMC.RunPlugin(\"%s?action='renamecollection'&viewmode='view'&collect='%s'\")"%(sys.argv[0],collection[0].decode("utf8")) )
                                         ] )#menucontextuel
            
        xbmcplugin.addSortMethod( int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE )
        xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="%s"%(__language__(30105)))
        xbmcplugin.endOfDirectory( int(sys.argv[1]),updateListing=refresh)

    def global_search(self):
        #récupére la liste des colonnes de la table files
        if not self.args.searchterm:
            kb = xbmc.Keyboard("","Mot à rechercher" , False)
            kb.doModal()
            if (kb.isConfirmed()):
                motrecherche = kb.getText()
            else:
                return
            refresh=False
        else:
            motrecherche = self.args.searchterm
            refresh=True

        filedesc = MPDB.get_fields("files")
        result = False
        for colname,coltype in filedesc:
            compte = MPDB.Searchfiles(colname,motrecherche,count=True)
            if compte:
                result = True
                self.addDir(name      = u"%s résultats pour '%s' dans '%s'"%(compte,motrecherche.decode("utf8"),colname),
                            params    = [("method","search"),("field",u"%s"%colname.decode("utf8")),("searchterm",u"%s"%motrecherche.decode("utf8")),("viewmode","view")],#paramètres
                            action    = "showpics",#action
                            iconimage = os.path.join(PIC_PATH,"search.png"),#icone
                            fanart    = os.path.join(PIC_PATH,"fanart-search.png"),
                            contextmenu   = None)#menucontextuel
        if not result:
            dialog = xbmcgui.Dialog()
            dialog.ok("My Pics Database - Search results", "The search for '%s' did not return any results in the whole database"%motrecherche)
            return
        xbmcplugin.addSortMethod( int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE )
        xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="search")
        xbmcplugin.endOfDirectory( int(sys.argv[1]),updateListing=refresh)

    def show_roots(self):
        "show the root folders"
        refresh=True
        if self.args.do=="addroot":
            dialog = xbmcgui.Dialog()
            newroot = dialog.browse(0, 'Dossier à scanner', 'pictures')
            if not newroot: return
            recursive = dialog.yesno("My Pictures Database","Parcourir ce dossier récursivement") and 1 or 0
            remove = dialog.yesno("My Pictures Database","Remove files from database if pictures does not exists") and 1 or 0
            #ajoute le rootfolder dans la base
            MPDB.AddRoot(newroot,recursive,remove)
            #scan_my_pics(newroot)
            xbmc.executebuiltin( "Notification(MyPictures Database,Folder added !)" )
            if dialog.yesno("My Pictures Database","Do you want to perform a scan now ?"):
                scan_my_pics(newroot)
                xbmc.executebuiltin( "Notification(My Pictures Database,Folder has been scanned)" )
        elif self.args.do=="delroot":
            MPDB.RemoveRoot( urllib.unquote_plus(self.args.delpath) )
            xbmc.executebuiltin( "Notification(deletefolder,%s)"%urllib.unquote_plus(self.args.delpath) )
        elif self.args.do=="rootclic":
            dialog = xbmcgui.Dialog()
            if dialog.yesno("My Pictures Database","Do you want to perform a scan now ?"):
                scan_my_pics(urllib.unquote_plus(self.args.rootpath))
                xbmc.executebuiltin( "Notification(My Pictures Database,Folder has been scanned)" )
        else:
            refresh=False
            
        self.addDir(name      = "Ajouter un chemin",
                    params    = [("do","addroot"),("viewmode","view"),],#paramètres
                    action    = "rootfolders",#action
                    iconimage = os.path.join(PIC_PATH,"search.png"),#icone
                    fanart    = os.path.join(PIC_PATH,"fanart-search.png"),
                    contextmenu   = None)#menucontextuel
        for path in MPDB.RootFolders():
            self.addDir(name      = path[0],
                        params    = [("do","rootclic"),("rootpath",path[0]),("viewmode","view"),],#paramètres
                        action    = "rootfolders",#action
                        iconimage = os.path.join(PIC_PATH,"search.png"),#icone
                        fanart    = os.path.join(PIC_PATH,"fanart-search.png"),
                        contextmenu   = [("Scan this path","Notification(scan folder,scan this folder now !)"),
                                         ("Remove this path from DB","Container.Update(\"%s?action='rootfolders'&do='delroot'&delpath='%s'&viewmode='view'\",replace)"%(sys.argv[0],urllib.quote_plus(path[0].decode("utf8"))))])#menucontextuel
        xbmcplugin.addSortMethod( int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE )
        xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="search")
        xbmcplugin.endOfDirectory( int(sys.argv[1]),updateListing=refresh)
            
    ##################################
    #traitement des menus contextuels
    ##################################
    def remove_period(self):
        MPDB.delPeriode(self.args.periodname)
        xbmc.executebuiltin( "Container.Update(\"%s?action='showperiod'&viewmode='view'&period=''\" , replace)"%sys.argv[0] , )
        
    def rename_period(self):
        datestart,dateend = MPDB.Request( """SELECT DateStart,DateEnd FROM Periodes WHERE PeriodeName='%s'"""%self.args.periodname )[0]
        kb = xbmc.Keyboard(self.args.periodname, __language__(30110), False)
        kb.doModal()
        if (kb.isConfirmed()):
            titreperiode = kb.getText()
        else:
            titreperiode = self.args.periodname
        MPDB.renPeriode(self.args.periodname,titreperiode)
        xbmc.executebuiltin( "Container.Update(\"%s?action='showperiod'&viewmode='view'&period=''\" , replace)"%sys.argv[0] , )

    def addTo_collection(self):
        listcollection = ["[[%s]]"%__language__(30157)]+[col[0] for col in MPDB.ListCollections()]

        dialog = xbmcgui.Dialog()
        rets = dialog.select(__language__(30156),listcollection)
        if rets==-1: #choix de liste annulé
            return
        if rets==0: #premier élément : ajout manuel d'une collection
            kb = xbmc.Keyboard("", __language__(30155), False)
            kb.doModal()
            if (kb.isConfirmed()):
                namecollection = kb.getText()
            else:
                #il faut traiter l'annulation
                return
            #2 créé la collection en base
            MPDB.NewCollection(namecollection)
        else: #dans tous les autres cas, une collection existente choisie
            namecollection = listcollection[rets]
        #3 associe en base l'id du fichier avec l'id de la collection
        MPDB.addPicToCollection( namecollection,urllib.unquote_plus(self.args.path),urllib.unquote_plus(self.args.filename) )
        xbmc.executebuiltin( "Notification(%s,%s %s)"%(__language__(30000).encode("utf8"),
                                                       __language__(30154).encode("utf8"),
                                                       namecollection)
                             )
    def add_folder_to_collection(self):
        listcollection = ["[[%s]]"%__language__(30157)]+[col[0] for col in MPDB.ListCollections()]

        dialog = xbmcgui.Dialog()
        rets = dialog.select(__language__(30156),listcollection)
        if rets==-1: #choix de liste annulé
            return
        if rets==0: #premier élément : ajout manuel d'une collection
            kb = xbmc.Keyboard("", __language__(30155), False)
            kb.doModal()
            if (kb.isConfirmed()):
                namecollection = kb.getText()
            else:
                #il faut traiter l'annulation
                return
            #2 créé la collection en base
            MPDB.NewCollection(namecollection)
        else: #dans tous les autres cas, une collection existente choisie
            namecollection = listcollection[rets]
        #3 associe en base l'id du fichier avec l'id de la collection
        filelist = self.show_pics() #on récupère les photos correspondantes à la vue
        c=0
        for path,filename in filelist: #on les ajoute une par une
            c=c+1
            MPDB.addPicToCollection( namecollection,path,filename )
        xbmc.executebuiltin( "Notification(%s,%s %s)"%(__language__(30000).encode("utf8"),
                                                       "%s photos ajoutées dans :"%c,
                                                       namecollection)
                             )
        
    def remove_collection(self):
        MPDB.delCollection(self.args.collect)
        xbmc.executebuiltin( "Container.Update(\"%s?action='showcollection'&viewmode='view'&collect=''&method='show'\" , replace)"%sys.argv[0] , )

    def rename_collection(self):
        kb = xbmc.Keyboard(self.args.collect, __language__(30153), False)
        kb.doModal()
        if (kb.isConfirmed()):
            newname = kb.getText()
        else:
            newname = self.args.collect
        MPDB.renCollection(self.args.collect,newname)
        xbmc.executebuiltin( "Container.Update(\"%s?action='showcollection'&viewmode='view'&collect=''&method='show'\" , replace)"%sys.argv[0] , )

    def del_pics_from_collection(self):
        MPDB.delPicFromCollection(urllib.unquote_plus(self.args.collect),urllib.unquote_plus(self.args.path),urllib.unquote_plus(self.args.filename))
        xbmc.executebuiltin( "Container.Update(\"%s?action='showpics'&viewmode='view'&collect='%s'&method='collection'\" , replace)"%(sys.argv[0],self.args.collect) , )

    def get_map(self):
        #1- récupère les données GPS de la photo
        #2- si il y a des coordonnées, on valide le menu contextuel
        pass
##>>> gps="[53, 1, 60073/2071]"
##>>> exec("gpslist=%s"%gps)
##>>> gpslist
##[53, 1, 29]
##>>> print "%s° %s' %s\""%tuple(gpslist)
##53° 1' 29"
##print "%s, %s"%(toGPS("[16, 15, 61307/1888]"),toGPS("[145, 23, 170571/3125]"))
##def toGPS(iptcGPS):
##    exec("gpslist=%s"%iptcGPS)
##    return "%s° %s' %s\""%tuple(gpslist)
##html = urllib.urlopen("http://maps.google.fr/mobile?q=-16%C2%B0+15%27+32%22%2C+145%C2%B0+23%27+54%22").read()
##re.findall(r"""<img src="(http://mt0\.google\.com/vt/data=[^"]+)" width="\d+" height="\d+" alt="carte"/>""",html)
##re.findall(r"""<img class=".*?" src="(http://mt0\.google\.com/vt/data=[^"]+)" width="\d+" height="\d+" alt="carte"/>""",html) #celle ci si on utilise un header firefox
##f=open("carte.jpg","wb").write(urllib.urlopen("http://mt0.google.com/vt/data=DGISkzGkvSKtpmptuxGtSlAxye35anR50gV8p99SMBV7lhz5_SO6d2GJtFS6x5v99bmP4fyMNtom1qmOLUz5lAEhA5p2Pag4B-8CXugaRH-y82_kkw").read())
    
    def show_pics(self):
        picfanart = None
        if self.args.method == "folder":#NON UTILISE : l'affichage par dossiers affiche de lui même les photos
            pass

        elif self.args.method == "date":
            #   lister les images pour une date donnée
            picfanart = os.path.join(PIC_PATH,"fanart-date.png")
            format = {"year":"%Y","month":"%Y-%m","date":"%Y-%m-%d","":"%Y","period":"%Y-%m-%d"}[self.args.period]
            if self.args.period=="year" or self.args.period=="":
                if self.args.value:
                    filelist = MPDB.search_between_dates( (self.args.value,format) , ( str( int(self.args.value) +1 ),format) )
                else:
                    filelist = MPDB.search_all_dates()
                    
            elif self.args.period=="month":
                a,m=self.args.value.split("-")
                if m=="12":
                    aa=int(a)+1
                    mm=1
                else:
                    aa=a
                    mm=int(m)+1
                filelist = MPDB.search_between_dates( ("%s-%s"%(a,m),format) , ( "%s-%s"%(aa,mm),format) )
                
            elif self.args.period=="date":
                #BUG CONNU : trouver un moyen de trouver le jour suivant en prenant en compte le nb de jours par mois
                a,m,j=self.args.value.split("-")              
                filelist = MPDB.search_between_dates( ("%s-%s-%s"%(a,m,j),format) , ( "%s-%s-%s"%(a,m,int(j)+1),format) )
                
            elif self.args.period=="period":
                picfanart = os.path.join(PIC_PATH,"fanart-period.png")
                filelist = MPDB.search_between_dates(DateStart=(urllib.unquote_plus(self.args.datestart),format),
                                                     DateEnd=(urllib.unquote_plus(self.args.dateend),format))
                         
            else:
                #pas de periode, alors toutes les photos du 01/01 de la plus petite année, au 31/12 de la plus grande année
                listyears=MPDB.get_years()
                amini=min(listyears)
                amaxi=max(listyears)
                if amini and amaxi:
                    filelist = MPDB.search_between_dates( ("%s"%(amini),format) , ( "%s"%(amaxi),format) )
                else:
                    filelist = []
                    
        elif self.args.method == "keyword":
            #   lister les images correspondant au mot clé
            picfanart = os.path.join(PIC_PATH,"fanart-keyword.png")
            if not self.args.kw: #le mot clé est vide '' --> les photos sans mots clés
                filelist = MPDB.search_keyword(None)
            else:
                filelist = MPDB.search_keyword(urllib.unquote_plus(self.args.kw.encode("utf8")))

        elif self.args.method == "folders":
            #   lister les images du dossier self.args.folderid et ses sous-dossiers
            # BUG CONNU : cette requête ne récupère que les photos du dossier choisi, pas les photos 'filles' des sous dossiers
            #   il faut la modifier pour récupérer les photos filles des sous dossiers
            picfanart = os.path.join(PIC_PATH,"fanart-folder.png")
            listid = MPDB.all_children(self.args.folderid)
            filelist = [row for row in MPDB.Request( "SELECT p.FullPath,f.strFilename FROM files f,folders p WHERE f.idFolder=p.idFolder AND p.ParentFolder in ('%s')"%"','".join([str(i) for i in listid]))]
            
        elif self.args.method == "collection":
            picfanart = os.path.join(PIC_PATH,"fanart-collection.png")
            filelist = MPDB.getCollectionPics(urllib.unquote_plus(self.args.collect))

        elif self.args.method == "search":
            picfanart = os.path.join(PIC_PATH,"fanart-collection.png")
            filelist = MPDB.Searchfiles(urllib.unquote_plus(self.args.field),urllib.unquote_plus(self.args.searchterm),count=False)

        #on teste l'argumen 'viewmode'
            #si viewmode = view : on liste les images
            #si viewmode = scan : on liste les photos qu'on retourne
        if self.args.viewmode=="scan":
            return filelist
        #alimentation de la liste
        for path,filename in filelist:
            #création du menu contextuel selon les situasions
            #1 - add to collection : tous les cas mais pas les collections
            context=[]
            context.append( ( __language__(30152),"XBMC.RunPlugin(\"%s?action='addtocollection'&viewmode='view'&path='%s'&filename='%s'\")"%(sys.argv[0],
                                                                                                                         urllib.quote_plus(path),
                                                                                                                         urllib.quote_plus(filename))
                              )
                            )
            #2 - del pic from collection : seulement les images des collections
            if self.args.method=="collection":
                context.append( ( __language__(30151),"XBMC.RunPlugin(\"%s?action='delfromcollection'&viewmode='view'&collect='%s'&path='%s'&filename='%s'\")"%(sys.argv[0],
                                                                                                                                             self.args.collect,
                                                                                                                                             urllib.quote_plus(path),
                                                                                                                                             urllib.quote_plus(filename))
                                  )
                                )
                
            #3 - montrer où est localisé physiquement la photo
                ## ATTENTION ne fonctionne pas, retourne le message suivant : Unable to locate window with id 126.  Check skin files
            context.append( ( "Localiser sur le disque","XBMC.ActivateWindow(126)" ) )
            #4 - les infos de la photo
            #context.append( ( "paramètres de l'addon","XBMC.ActivateWindow(virtualkeyboard)" ) )
            self.addPic(filename,
                        path,
                        contextmenu = context,
                        fanart = picfanart
                        )
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE)
        xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="photos" )
        xbmcplugin.endOfDirectory(int(sys.argv[1]))           
            



global pDialog
def pupdate(percent, line1="", line2="", line3=""):
    pDialog.update(percent, line1,line2,line3)
    
def scan_my_pics(path=None):
    global pictureDB,pDialog
    #dialog = xbmcgui.Dialog()
    #ok = dialog.ok("scan","scan préalable")
    pDialog = xbmcgui.DialogProgress()
    ret = pDialog.create('MyPicsDB', __language__(30205),pictureDB)

##    # initialisation de la base :
##    MPDB.pictureDB = pictureDB
##    #   - efface les tables et les recréés
##    MPDB.Make_new_base(pictureDB,
##                       ecrase= xbmcplugin.getSetting(int(sys.argv[1]),"initDB") == "true")
    #picpath=[]
    #if xbmcplugin.getSetting(int(sys.argv[1]),'scanfolder'):
    #    picpath.append(xbmcplugin.getSetting(int(sys.argv[1]),'scanfolder'))
    #else:
    #    # A FAIRE : voir ce qu'on peut prendre comme dossier si aucun n'est configuré
    #    dialog = xbmcgui.Dialog()
    #    ok = dialog.ok("MyPicsDB",__language__(30201),__language__(30202))
    #    return False
    
    import time
    t=time.time()
    
    # parcours récursif du dossier 'picpath'
    total = 0
    #n=0
    #for chemin in picpath:
    #pDialog.update(n*100/len(picpath), __language__(30203),chemin)
    MPDB.compte = 0
    #MPDB.browse_folder(chemin,parentfolderID=None,recursive=xbmcplugin.getSetting(int(sys.argv[1]),'recursive')=="true",update=False,updatefunc = pupdate)
    MPDB.browse_folder(path,parentfolderID=None,recursive=xbmcplugin.getSetting(int(sys.argv[1]),'recursive')=="true",update=False,updatefunc = pupdate)
    total = total + MPDB.compte
    #n=n+1

    if xbmcplugin.getSetting(int(sys.argv[1]),'updateDB')=="true":
        # traitement des dossiers supprimés/renommés physiquement --> on supprime toutes les entrées de la base
        lp = MPDB.list_path()
        i = 0
        for path in lp:#on parcours tous les dossiers distinct en base de donnée
            if not os.path.isdir(path): #si le chemin en base n'est pas réellement un dossier,...
                pDialog.update(i*100/len(lp), __language__(30204),path)
                MPDB.DB_del_pic(path)#... on supprime toutes les entrées s'y rapportant
                #print "%s n'est pas un chemin. Les entrées s'y rapportant dans la base sont supprimées."%path 
            i=i+1
    return True
    

if __name__=="__main__":

    m=Main()
    print 
    if not sys.argv[ 2 ]: #pas de paramètres : affichage du menu principal
##        #montage ?
##        smbpath= xbmcplugin.getSetting(int(sys.argv[1]),"sharepath")
##        
##        print smbpath.replace("smb:","")
##        print xbmcplugin.getSetting(int(sys.argv[1]),"sharelogin")
##        print xbmcplugin.getSetting(int(sys.argv[1]),"sharepass")
##        print smbpath.replace("smb:","").replace("/","\\")
##        MPDB.mount(mountpoint="w:",path="\\\\diskstation\\photos",
##                   login=xbmcplugin.getSetting(int(sys.argv[1]),"sharelogin"),
##                   password=xbmcplugin.getSetting(int(sys.argv[1]),"sharepass"))
        # initialisation de la base :
        MPDB.pictureDB = pictureDB
        #   - efface les tables et les recréés
        MPDB.Make_new_base(pictureDB,
                           ecrase= xbmcplugin.getSetting(int(sys.argv[1]),"initDB") == "true")
        MPDB.AddRoot(xbmcplugin.getSetting(int(sys.argv[1]),'scanfolder'),
                     1,#recursive
                     1)#remove
        ok = scan_my_pics(xbmcplugin.getSetting(int(sys.argv[1]),'scanfolder'))#scan lorsque le plugin n'a pas de paramètres
        if not ok: #on peut traiter un retour erroné du scan
            print "erreur lors du scan"
            
            pass
        else:#sinon on affiche le menu d'accueil
            m.args.action=''
            m.show_home()
    #les sélections sur le menu d'accueil :
    #   Tri par dates
    elif m.args.action=='showdate':
        m.show_date()
    #   Tri par dossiers
    elif m.args.action=='showfolder':
        m.show_folders()
    #   Tri par mots clés
    elif m.args.action=='showkeywords':
        m.show_keywords()
    elif m.args.action=='showpics':
        m.show_pics()
    elif m.args.action=='showperiod':
        m.show_period()
    elif m.args.action=='scan':
        #un scan simple est demandé...
        ok = scan_my_pics(xbmcplugin.getSetting(int(sys.argv[1]),'scanfolder'))
    elif m.args.action=='removeperiod':
        m.remove_period()
    elif m.args.action=='renameperiod':
        m.rename_period()
    elif m.args.action=='showcollection':
        m.show_collection()
    elif m.args.action=='addtocollection':
        m.addTo_collection()
    elif m.args.action=='removecollection':
        m.remove_collection()
    elif m.args.action=='delfromcollection':
        m.del_pics_from_collection()
    elif m.args.action=='renamecollection':
        m.rename_collection()
    elif m.args.action=='globalsearch':
        m.global_search()
    elif m.args.action=='addfolder':
        m.add_folder_to_collection()
    elif m.args.action=='rootfolders':
        m.show_roots()
    else:
        m.show_home()
    del MPDB
##    m=Main()
##    m.display()
    
