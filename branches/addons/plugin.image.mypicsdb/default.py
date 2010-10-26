#!/usr/bin/python
# -*- coding: utf8 -*-
"""
TODO :
  - upgrade iptcinfo library (need some unicode improvement)
  - work to make better use of dates inside sqlite and python
  - 'add to collections' context menu from any folder in sort by date view
  - 'add to collections' context menu from any folder in sort by folders view
  - test if a 'collection' or 'period' or 'keyword' view doesn't contain any pictures : remove these from the database when deleting pictures
  - update in scan from library is not good : 2 options : 1- update to remove not found pictures ; 2- update to rescan exif/iptc datas and update files database with new metas
  - Scan : need to fix parameters sending. Right now, recursive or update things are not handled (everything is recursive and updating for new/deleted pics)
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
import urllib2
import re
import xbmcplugin,xbmcgui,xbmc,xbmcaddon
import os.path
import tarfile
import time

from traceback import print_exc

Addon = xbmcaddon.Addon(id='plugin.image.mypicsdb')
__language__ = Addon.getLocalizedString
sys_enc = sys.getfilesystemencoding()
   
if sys.modules.has_key("MypicsDB"):
    del sys.modules["MypicsDB"]
import MypicsDB as MPDB
    
global pictureDB
pictureDB = os.path.join(DB_PATH,"MyPictures.db")
                               
files_fields_description={"strFilename":__language__(30300),
                          "strPath":__language__(30301),
                          "Thumb":__language__(30302)
                          }

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
    def __setitem__(self,key,value):
        self.__dict__[key]=value

class Main:
    def __init__(self):
        self.get_args()

    def get_args(self):
        exec "self.args = _Info(%s)" % ( sys.argv[ 2 ][ 1 : ].replace( "&", ", " ), )

    def Title(self,title):
        xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=urllib.unquote_plus(title.encode("utf-8")) )
        
    def addDir(self,name,params,action,iconimage,fanart=None,contextmenu=None,total=0,info="*",replacemenu=True):
        #params est une liste de tuples [(nomparametre,valeurparametre),]
        #contitution des paramètres
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
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)#,totalItems=total)
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
        # last month
        self.addDir("last month (betatest)",[("method","lastmonth"),("period",""),("value",""),("viewmode","view")],
                    "showpics",os.path.join(PIC_PATH,"dates.png"),
                    fanart=os.path.join(PIC_PATH,"fanart-date.png"))
        # last year
        self.addDir("last 100 (betatest)",[("method","last100"),("period",""),("value",""),("viewmode","view")],
                    "showpics",os.path.join(PIC_PATH,"dates.png"),
                    fanart=os.path.join(PIC_PATH,"fanart-date.png"))
        
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
        self.addDir(unescape(__language__(30098)),[("searchterm",""),("viewmode","view")],"globalsearch",
                    os.path.join(PIC_PATH,"search.png"),
                    fanart=os.path.join(PIC_PATH,"fanart-search.png"))
        # chemin scannés
        self.addDir(unescape(__language__(30099)),[("do","showroots"),("viewmode","view")],"rootfolders",
                    os.path.join(PIC_PATH,"settings.png"),
                    fanart=os.path.join(PIC_PATH,"fanart-setting.png"))
        
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE)
        xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=urllib.unquote_plus("My Pictures Library".encode("utf-8")) )
        xbmcplugin.endOfDirectory(int(sys.argv[1]),cacheToDisc=True)

    def show_date(self):
        #period = year|month|date
        #value  = "2009"|"12/2009"|"25/12/2009"
        action="showdate"
        weekdayname = __language__(30005).split("|")
        monthname = __language__(30006).split("|")
        fullweekdayname = __language__(30007).split("|")
        fullmonthname = __language__(30008).split("|")
        if self.args.period=="year":
            listperiod=MPDB.get_years()
            nextperiod="month"
            allperiod =""
            action="showdate"
            periodformat="%Y"
            displaydate=__language__(30004)#%Y
            thisdateformat=""
            displaythisdate=""
        elif self.args.period=="month":
            listperiod=MPDB.get_months(self.args.value)
            nextperiod="date"
            allperiod="year"
            action="showdate"
            periodformat="%Y-%m"
            displaydate=__language__(30003)#%b %Y
            thisdateformat="%Y"
            displaythisdate=__language__(30004)#%Y
        elif self.args.period=="date":
            listperiod=MPDB.get_dates(self.args.value)
            nextperiod="date"
            allperiod = "month"
            action="showpics"
            periodformat="%Y-%m-%d"
            displaydate=__language__(30002)#"%a %d %b %Y"
            thisdateformat="%Y-%m"
            displaythisdate=__language__(30003)#"%b %Y"
        else:
            listperiod=[]
            nextperiod=None
        
        if not None in listperiod:
            #print self.args.value
            #print time.strftime("%d/%m/%Y",time.strptime(self.args.value,"%Y-%m-%d"))
            dptd = displaythisdate
            dptd = dptd.replace("%b",monthname[time.strptime(self.args.value,thisdateformat).tm_mon - 1])    #replace %b marker by short month name
            dptd = dptd.replace("%B",fullmonthname[time.strptime(self.args.value,thisdateformat).tm_mon - 1])#replace %B marker by long month name
            nameperiode = time.strftime(dptd.encode("utf8"),time.strptime(self.args.value,thisdateformat))
            self.addDir(name      = __language__(30100)%(nameperiode.decode("utf8"),MPDB.countPeriod(allperiod,self.args.value)), #libellé#"All the period %s (%s pics)"%(self.args.value,MPDB.countPeriod(allperiod,self.args.value)), #libellé
                        params    = [("method","date"),("period",allperiod),("value",self.args.value),("viewmode","view")],#paramètres
                        action    = "showpics",#action
                        iconimage = os.path.join(PIC_PATH,"dates.png"),#icone
                        fanart    = os.path.join(PIC_PATH,"fanart-date.png"),
                        contextmenu   = [(__language__(30152),"XBMC.RunPlugin(\"%s?action='addfolder'&method='date'&period='%s'&value='%s'&viewmode='scan'\")"%(sys.argv[0],allperiod,self.args.value))])#menucontextuel
            total=len(listperiod)
            for period in listperiod:
                if period:
                    if action=="showpics":
                        context = [(__language__(30152),"XBMC.RunPlugin(\"%s?action='addfolder'&method='date'&period='%s'&value='%s'&viewmode='scan'\")"%(sys.argv[0],nextperiod,period))]
                    else:
                        context = [(__language__(30152),"XBMC.RunPlugin(\"%s?action='addfolder'&method='date'&period='%s'&value='%s'&viewmode='scan'\")"%(sys.argv[0],self.args.period,period))]
                    
                    self.addDir(name      = "%s (%s %s)"%(time.strftime(self.prettydate(displaydate,time.strptime(period,periodformat)).encode("utf8"),time.strptime(period,periodformat)).decode("utf8"),
                                                          MPDB.countPeriod(self.args.period,period),
                                                          __language__(30050).encode("utf8")), #libellé
                                params    = [("method","date"),("period",nextperiod),("value",period),("viewmode","view")],#paramètres
                                action    = action,#action
                                iconimage = os.path.join(PIC_PATH,"dates.png"),#icone
                                fanart    = os.path.join(PIC_PATH,"fanart-date.png"),
                                contextmenu   = context,#menucontextuel
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
            self.addDir(name      = "%s (%s %s)"%(childrenfolder.decode("utf8"),MPDB.countPicsFolder(idchildren),__language__(30050)), #libellé
                        params    = [("method","folders"),("folderid",str(idchildren)),("onlypics","non"),("viewmode","view")],#paramètres
                        action    = "showfolder",#action
                        iconimage = os.path.join(PIC_PATH,"folders.png"),#icone
                        fanart    = os.path.join(PIC_PATH,"fanart-folder.png"),
                        contextmenu   = None, #menucontextuel
                        total = total)#nb total d'éléments
        
        #maintenant, on liste les photos si il y en a, du dossier en cours
        picsfromfolder = [row for row in MPDB.Request("SELECT p.FullPath,f.strFilename FROM files f,folders p WHERE f.idFolder=p.idFolder AND f.idFolder='%s'"%self.args.folderid)]
        for path,filename in picsfromfolder:
            context = [( __language__(30152),"XBMC.RunPlugin(\"%s?action='addtocollection'&viewmode='view'&path='%s'&filename='%s'\")"%(sys.argv[0],
                                                                                                                         urllib.quote_plus(path),
                                                                                                                         urllib.quote_plus(filename))  ) ]
            #context.append( ("Don't use this picture","") )
            coords = MPDB.getGPS(path,filename)
            if coords:
                #géolocalisation
                context.append( (__language__(30220),"XBMC.RunPlugin(\"%s?action='geolocate'&place='%s'&path='%s'&filename='%s'&viewmode='view'\" ,)"%(sys.argv[0],"%0.6f,%0.6f"%(coords),
                                                                                                                                                       urllib.quote_plus(path),
                                                                                                                                                       urllib.quote_plus(filename))))
            self.addPic(filename,path,contextmenu=context,
                        fanart = os.path.join(PIC_PATH,"fanart-folder.png")
                        )
                            #(__language__(30152),"XBMC.RunPlugin(%s?method='folders'&folderid='2'&onlypics='non'&action='showfolder'&name='2005-05+%%2823+images%%29')"%sys.argv[0])
            
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
            nb = MPDB.countKW(kw)
            if nb:
                self.addDir(name      = "%s (%s %s)"%(kw,nb,__language__(30050)), #libellé
                            params    = [("method","keyword"),("kw",kw),("viewmode","view")],#paramètres
                            action    = "showpics",#action
                            iconimage = os.path.join(PIC_PATH,"keywords.png"),#icone
                            fanart    = os.path.join(PIC_PATH,"fanart-keyword.png"),
                            contextmenu   = [( __language__(30152),"XBMC.RunPlugin(\"%s?action='addfolder'&method='keyword'&kw='%s'&viewmode='scan'\")"%(sys.argv[0],kw)),
                                             ( __language__(30161),"XBMC.RunPlugin(\"%s?action='showpics'&method='keyword'&viewmode='zip'&name='%s'&kw='%s'\")"%(sys.argv[0],kw,kw) ),
                                             ( __language__(30162),"XBMC.RunPlugin(\"%s?action='showpics'&method='keyword'&viewmode='export'&name='%s'&kw='%s'\")"%(sys.argv[0],kw,kw) )
                                             ],#menucontextuel
                            total = total)#nb total d'éléments
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE)
        xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="%s : %s"%(__language__(30103),urllib.unquote_plus(self.args.kw.encode("utf-8"))) )
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

    def show_period(self): #TODO finished the datestart and dateend editing
        self.addDir(name      = __language__(30106),
                    params    = [("period","setperiod"),("viewmode","view")],#paramètres
                    action    = "showperiod",#action
                    iconimage = os.path.join(PIC_PATH,"newperiod.png"),#icone
                    fanart    = os.path.join(PIC_PATH,"fanart-period.png"),
                    contextmenu   = None)#menucontextuel
        #If We previously choose to add a new period, this test will ask user for setting the period :
        if self.args.period=="setperiod":
            dateofpics = MPDB.get_pics_dates()#the choice of the date is made with pictures in database (datetime of pics are used)
            nameddates = [time.strftime(self.prettydate(__language__(30002),time.strptime(date,"%Y-%m-%d")).encode("utf8"),time.strptime(date,"%Y-%m-%d")) for date in dateofpics]
            dialog = xbmcgui.Dialog()
            rets = dialog.select(__language__(30107),["[[%s]]"%__language__(30114)] + nameddates)#dateofpics)#choose the start date
            if not rets==-1:#is not canceled
                if rets==0: #input manually the date
                    d = dialog.numeric(1, __language__(30117) ,time.strftime("%d/%m/%Y",time.strptime(dateofpics[0],"%Y-%m-%d")) )
                    datestart = time.strftime("%Y-%m-%d",time.strptime(d.replace(" ","0"),"%d/%m/%Y"))
                    deb=0
                else:
                    datestart = dateofpics[rets-1]
                    deb=rets-1
            
                retf = dialog.select(__language__(30108),["[[%s]]"%__language__(30114)] + nameddates[deb:])#dateofpics[deb:])#choose the end date (all dates before startdate are ignored to preserve begin/end)
                if not retf==-1:#if end date is not canceled...
                    if retf==0:#choix d'un date de fin manuelle ou choix précédent de la date de début manuelle
                        d = dialog.numeric(1, __language__(30118) ,time.strftime("%d/%m/%Y",time.strptime(dateofpics[-1],"%Y-%m-%d")) )
                        dateend = time.strftime("%Y-%m-%d",time.strptime(d.replace(" ","0"),"%d/%m/%Y"))
                        deb=0
                    else:
                        dateend = dateofpics[deb+retf-1]
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
            datestart,dateend = MPDB.Request("SELECT strftime('%%Y-%%m-%%d',datetime('%s')),strftime('%%Y-%%m-%%d',datetime('%s','+1 days','-1.0 seconds'))"%(dbdatestart,dbdateend))[0]
            self.addDir(name      = "%s (%s)"%(periodname.decode("utf8"),
                                               __language__(30113)%(time.strftime(self.prettydate(__language__(30002),time.strptime(datestart,"%Y-%m-%d")).encode("utf8"),time.strptime(datestart,"%Y-%m-%d")).decode("utf8"),
                                                                    time.strftime(self.prettydate(__language__(30002),time.strptime(dateend  ,"%Y-%m-%d")).encode("utf8"),time.strptime(dateend  ,"%Y-%m-%d")).decode("utf8")
                                                                    )), #libellé
                        params    = [("method","date"),("period","period"),("datestart",datestart),("dateend",dateend),("viewmode","view")],#paramètres
                        action    = "showpics",#action
                        iconimage = os.path.join(PIC_PATH,"period.png"),#icone
                        fanart    = os.path.join(PIC_PATH,"fanart-period.png"),
                        contextmenu   = [ ( __language__(30111),"XBMC.RunPlugin(\"%s?action='removeperiod'&viewmode='view'&periodname='%s'&period='period'\")"%(sys.argv[0],periodname) ),
                                          ( __language__(30112),"XBMC.RunPlugin(\"%s?action='renameperiod'&viewmode='view'&periodname='%s'&period='period'\")"%(sys.argv[0],periodname) ),
                                          ( __language__(30152),"XBMC.RunPlugin(\"%s?action='addfolder'&method='date'&period='period'&datestart='%s'&dateend='%s'&viewmode='scan'\")"%(sys.argv[0],datestart,dateend))
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
                                         (__language__(30159),"XBMC.RunPlugin(\"%s?action='renamecollection'&viewmode='view'&collect='%s'\")"%(sys.argv[0],collection[0].decode("utf8")) ),
                                         (__language__(30061),"XBMC.RunPlugin(\"%s?action='showpics'&method='collection'&viewmode='zip'&name='%s'&collect='%s'\")"%(sys.argv[0],collection[0].decode("utf8"),collection[0].decode("utf8")) ),
                                         (__language__(30062),"XBMC.RunPlugin(\"%s?action='showpics'&method='collection'&viewmode='export'&name='%s'&collect='%s'\")"%(sys.argv[0],collection[0].decode("utf8"),collection[0].decode("utf8")) ) 
                                         ] )#menucontextuel 
            
        xbmcplugin.addSortMethod( int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE )
        xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="%s"%(__language__(30105)))
        xbmcplugin.endOfDirectory( int(sys.argv[1]),updateListing=refresh)

    def global_search(self):
        #récupére la liste des colonnes de la table files
        if not self.args.searchterm:
            kb = xbmc.Keyboard("",__language__(30115) , False)
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
                self.addDir(name      = __language__(30116)%(compte,motrecherche.decode("utf8"),files_fields_description.has_key(colname) and files_fields_description[colname] or colname),
                            params    = [("method","search"),("field",u"%s"%colname.decode("utf8")),("searchterm",u"%s"%motrecherche.decode("utf8")),("viewmode","view")],#paramètres
                            action    = "showpics",#action
                            iconimage = os.path.join(PIC_PATH,"search.png"),#icone
                            fanart    = os.path.join(PIC_PATH,"fanart-search.png"),
                            contextmenu   = [(__language__(30152),"XBMC.RunPlugin(\"%s?action='addfolder'&method='search'&field='%s'&searchterm='%s'&viewmode='scan'\")"%(sys.argv[0],colname,motrecherche))])#menucontextuel
        if not result:
            dialog = xbmcgui.Dialog()
            dialog.ok(__language__(30000), __language__(30116)%motrecherche)
            return
        xbmcplugin.addSortMethod( int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE )
        xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="search")
        xbmcplugin.endOfDirectory( int(sys.argv[1]),updateListing=refresh)

    def show_roots(self):
        "show the root folders"
        refresh=True
        if self.args.do=="addroot":
            dialog = xbmcgui.Dialog()
            newroot = dialog.browse(0, __language__(30201), 'pictures')
            if not newroot: return
            recursive = dialog.yesno(__language__(30000),__language__(30202)) and 1 or 0 #browse recursively this folder ?
            update = dialog.yesno(__language__(30000),__language__(30203)) and 1 or 0 # Remove files from database if pictures does not exists?
            #ajoute le rootfolder dans la base
            MPDB.AddRoot(newroot,recursive,update)
            xbmc.executebuiltin( "Notification(%s,%s)"%(__language__(30000).encode("utf8"),__language__(30204).encode("utf8")) )
            if dialog.yesno(__language__(30000),__language__(30206)):#do a scan now ?
##                xbmc.executebuiltin( "RunScript(%s,%s%s--rootpath %s) "%( os.path.join( os.getcwd(), "scanpath.py"),
##                                                                          recursive==1 and "--recursive " or "",
##                                                                          update==1 and "--update " or "",
##                                                                          newroot
##                                                                        )
##                                     )
                xbmc.executebuiltin( "RunScript(%s,--rootpath=%s) "%( os.path.join( os.getcwd(), "scanpath.py"),
                                                                          newroot
                                                                        )
                                     )

                #xbmc.executebuiltin( "Notification(My Pictures Database,Folder has been scanned)" )
        elif self.args.do=="delroot":
            try:
                MPDB.RemoveRoot( urllib.unquote_plus(self.args.delpath) )
            except IndexError:
                pass
            #TODO : this notification does not work with é letters in the string....
            #xbmc.executebuiltin( "Notification(%s,%s)"%(__language__(30000),__language__(30205)))#+":".encode("utf8")+urllib.unquote_plus(self.args.delpath)) )
        elif self.args.do=="rootclic":
            dialog = xbmcgui.Dialog()
            if dialog.yesno(__language__(30000),__language__(30206)):#do a scan now ?
                path,recursive,update = MPDB.getRoot(urllib.unquote_plus(self.args.rootpath))
##                xbmc.executebuiltin( "RunScript(%s,%s%s-p %s) "%( os.path.join( os.getcwd(), "scanpath.py"),
##                                                                          recursive==1 and "-r " or "",
##                                                                          update==1 and "-u " or "",
##                                                                          urllib.quote_plus(path)
##                                                                        )
##                                     )
                xbmc.executebuiltin( "RunScript(%s,--rootpath=%s)"%( os.path.join( os.getcwd(), "scanpath.py"),
                                                                          urllib.quote_plus(path)
                                                                        )
                                     )
                #xbmc.executebuiltin( "Notification(My Pictures Database,Folder has been scanned)" )
        else:
            refresh=False
            
        self.addDir(name      = __language__(30208),#add a root path
                    params    = [("do","addroot"),("viewmode","view"),],#paramètres
                    action    = "rootfolders",#action
                    iconimage = os.path.join(PIC_PATH,"newsettings.png"),#icone
                    fanart    = os.path.join(PIC_PATH,"fanart-setting.png"),
                    contextmenu   = None)#menucontextuel
        for path,recursive,update in MPDB.RootFolders():
            srec = recursive==1 and "ON" or "OFF"
            supd = update==1 and "ON" or "OFF"
        
            self.addDir(name      = path+" [recursive="+srec+" , update="+supd+"]",
                        params    = [("do","rootclic"),("rootpath",path),("viewmode","view"),],#paramètres
                        action    = "rootfolders",#action
                        iconimage = os.path.join(PIC_PATH,"settings.png"),#icone
                        fanart    = os.path.join(PIC_PATH,"fanart-setting.png"),
                        #menucontextuel
                        contextmenu   = [( __language__(30206),"Notification(TODO : scan folder,scan this folder now !)" ),
                                         ( __language__(30207),"Container.Update(\"%s?action='rootfolders'&do='delroot'&delpath='%s'&viewmode='view'\","%(sys.argv[0],urllib.quote_plus(path.decode("utf8"))))
                                         ]
                        )
        xbmcplugin.addSortMethod( int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE )
        xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="search")
        xbmcplugin.endOfDirectory( int(sys.argv[1]),updateListing=refresh)

    def show_map(self):
        """get a google map for the given place (place is a string for an address, or a couple of gps lat/lon datas"""
##        #google geolocalisation 
##        static_url = "http://maps.google.com/maps/api/staticmap?"
##        param_dic = {#location parameters (http://gmaps-samples.googlecode.com/svn/trunk/geocoder/singlegeocode.html)
##                     "center":"",       #(required if markers not present)
##                     "zoom":"12",         # 0 to 21+ (req if no markers
##                     #map parameters
##                     "size":"640x640",  #widthxheight (required)
##                     "format":"png32",    #"png8","png","png32","gif","jpg","jpg-baseline" (opt)
##                     "maptype":"hybrid",      #"roadmap","satellite","hybrid","terrain" (opt)             
##                     "language":"",
##                     #Feature Parameters:
##                     "markers" :"color:red|label:P|%s",#(opt)
##                                        #markers=color:red|label:P|lyon|12%20rue%20madiraa|marseille|Lille
##                                        #&markers=color:blue|label:P|Australie
##                     "path" : "",       #(opt)
##                     "visible" : "",    #(opt)
##                     #Reporting Parameters:
##                     "sensor" : "false" #is there a gps on system ? (req)
##                     }
##        pDialog = xbmcgui.DialogProgress()
##        ret = pDialog.create(__language__(30000),__language__(30221),self.args.place)
##        pDialog.update(0,"Creating connection...")
##
##        param_dic["markers"]=param_dic["markers"]%self.args.place
##        request_headers = { 'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; fr; rv:1.9.2.10) Gecko/20100914 Firefox/3.6.10' }
##        request = urllib2.Request(static_url+urllib.urlencode(param_dic), None, request_headers)
##        urlfile = urllib2.urlopen(request)
##        print urlfile.info()
##        #DATA_PATH = "c:\\Users\\alexsolex\\Pictures\\"
##        extension = urlfile.info().getheader("Content-Type","").split("/")[1]
##        filesize = int(urlfile.info().getheader("Content-Length",""))
##        try:
##            f=open(os.path.join(DATA_PATH,urllib.unquote_plus(self.args.filename).split(".")[0]+"_maps."+extension),"wb")
##        except:
##            print_exc()
##        for i in range(1+(filesize/10)):
##            f.write(urlfile.read(10))
##            pDialog.update(int(100*(float(i*10)/filesize)),__language__(30221),"%0.2f%%"%(100*(float(i*10)/filesize)))
##        urlfile.close()
##        pDialog.close()
##        try:
##            f.close()
##        except:
##            print_exc()
##            pass
##        HTTP_API_url = "http://%s/xbmcCmds/xbmcHttp?command="%xbmc.getIPAddress()
##        html = urllib.urlopen(HTTP_API_url + "ClearSlideshow" )
##        html = urllib.urlopen(HTTP_API_url + "AddToSlideshow(%s)" % urllib.quote_plus(os.path.join(DATA_PATH,urllib.unquote_plus(self.args.filename).split(".")[0]+"_maps."+extension)) )
##        print html.url
##        html = urllib.urlopen(HTTP_API_url + "ExecBuiltIn(ActivateWindow(12007))" )
        import geomaps
        showmap = geomaps.main(DATA_PATH = DATA_PATH, place =self.args.place, picfile = os.path.join(urllib.unquote_plus(self.args.path),urllib.unquote_plus(self.args.filename)))
        #showmap.set_map(os.path.join(DATA_PATH,urllib.unquote_plus(self.args.filename).split(".")[0]+"_maps."+extension))
        #showmap.set_pic( os.path.join(urllib.unquote_plus(self.args.path),urllib.unquote_plus(self.args.filename)) )
        showmap.doModal()
        del showmap

##        response = xbmc.executeJSONRPC('''{ "jsonrpc": "2.0", "method": "XBMC.StartSlideshow", "parameter": "%s", "id": "1" }'''%os.path.join(DATA_PATH,urllib.unquote_plus(self.args.filename).split(".")[0]+"_maps."+extension))
##        
##        print "response"
##        print response
##        html = urllib.urlopen(HTTP_API_url + "ClearSlideshow")
##        html = urllib.urlopen(HTTP_API_url + "AddToSlideshow('%s')" % urllib.quote(os.path.join(DATA_PATH,urllib.unquote_plus(self.args.filename).split(".")[0]+"_maps."+extension)) )
##        print html.read()
        #xbmc.executebuiltin( "ActivateWindow(12007)" )
        #xbmc.executebuiltin( "SlideShow('%s',,notrandom)"% os.path.join(DATA_PATH,urllib.unquote_plus(self.args.filename).split(".")[0]+"_maps."+extension))
        #xbmc.executebuiltin( "Notification(%s,Maps downloaded to %s)"%("MyPictures DB",os.path.join(DATA_PATH,"maps.jpg")))

    def prettydate(self,dateformat,datetuple):
        "Replace %a %A %b %B date string formater (see strftime format) by the day/month names for the given date tuple given"
        dateformat = dateformat.replace("%a",__language__(30005).split("|")[datetuple.tm_wday])      #replace %a marker by short day name
        dateformat = dateformat.replace("%A",__language__(30007).split("|")[datetuple.tm_wday])      #replace %A marker by long day name
        dateformat = dateformat.replace("%b",__language__(30006).split("|")[datetuple.tm_mon - 1])   #replace %b marker by short month name
        dateformat = dateformat.replace("%B",__language__(30008).split("|")[datetuple.tm_mon - 1])   #replace %B marker by long month name
        return dateformat

    
    ##################################
    #traitement des menus contextuels
    ##################################
    def remove_period(self):
        MPDB.delPeriode(self.args.periodname)
        xbmc.executebuiltin( "Container.Update(\"%s?action='showperiod'&viewmode='view'&period=''\" , replace)"%sys.argv[0]  )
        
    def rename_period(self):
        #TODO : test if 'datestart' is before 'dateend'
        datestart,dateend = MPDB.Request( """SELECT DateStart,DateEnd FROM Periodes WHERE PeriodeName='%s'"""%self.args.periodname )[0]

        dialog = xbmcgui.Dialog()
        d = dialog.numeric(1, "Input start date for period" ,time.strftime("%d/%m/%Y",time.strptime(datestart,"%Y-%m-%d %H:%M:%S")) )
        datestart = time.strftime("%Y-%m-%d",time.strptime(d.replace(" ","0"),"%d/%m/%Y"))

        d = dialog.numeric(1, "Input end date for period" ,time.strftime("%d/%m/%Y",time.strptime(dateend,"%Y-%m-%d %H:%M:%S")) )
        dateend = time.strftime("%Y-%m-%d",time.strptime(d.replace(" ","0"),"%d/%m/%Y"))
        
        #change the dateend
        kb = xbmc.Keyboard(self.args.periodname, __language__(30110), False)
        kb.doModal()
        if (kb.isConfirmed()):
            titreperiode = kb.getText()
        else:
            titreperiode = self.args.periodname
        MPDB.renPeriode(self.args.periodname,titreperiode,datestart,dateend)
        xbmc.executebuiltin( "Container.Update(\"%s?action='showperiod'&viewmode='view'&period=''\" , replace)"%sys.argv[0]  )

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
        for path,filename in filelist: #on les ajoute une par une
            MPDB.addPicToCollection( namecollection,path,filename )
        xbmc.executebuiltin( "Notification(%s,%s %s)"%(__language__(30000).encode("utf8"),
                                                       __language__(30161).encode("utf8")%len(filelist),
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

    def get_map(self): # TODO
        #1- récupère les données GPS de la photo
        #2- si il y a des coordonnées, on valide le menu contextuel
        pass
    
    def show_pics(self):
        picfanart = None
        if self.args.method == "folder":#NON UTILISE : l'affichage par dossiers affiche de lui même les photos
            pass

        # we are showing pictures for a DATE selection
        elif self.args.method == "date":
            #   lister les images pour une date donnée
            picfanart = os.path.join(PIC_PATH,"fanart-date.png")
            format = {"year":"%Y","month":"%Y-%m","date":"%Y-%m-%d","":"%Y","period":"%Y-%m-%d"}[self.args.period]
            if self.args.period=="year" or self.args.period=="":
                if self.args.value:
                    filelist = MPDB.pics_for_period('year',self.args.value)
                else:
                    filelist = MPDB.search_all_dates()
                    
            elif self.args.period in ["month","date"]:
                filelist = MPDB.pics_for_period(self.args.period,self.args.value)

            elif self.args.period=="period":
                picfanart = os.path.join(PIC_PATH,"fanart-period.png")
                filelist = MPDB.search_between_dates(DateStart=(urllib.unquote_plus(self.args.datestart),format),
                                                     DateEnd=(urllib.unquote_plus(self.args.dateend),format))
            else:#period not recognized, show whole pics : TODO check if useful and if it can not be optimized for something better
                listyears=MPDB.get_years()
                amini=min(listyears)
                amaxi=max(listyears)
                if amini and amaxi:
                    filelist = MPDB.search_between_dates( ("%s"%(amini),format) , ( "%s"%(amaxi),format) )
                else:
                    filelist = []

        # we are showing pictures for a KEYWORD selection
        elif self.args.method == "keyword":
            #   lister les images correspondant au mot clé
            picfanart = os.path.join(PIC_PATH,"fanart-keyword.png")
            if not self.args.kw: #le mot clé est vide '' --> les photos sans mots clés
                filelist = MPDB.search_keyword(None)
            else:
                filelist = MPDB.search_keyword(urllib.unquote_plus(self.args.kw).decode("utf8"))

        # we are showing pictures for a FOLDER selection
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

        elif self.args.method == "lastmonth":
            picfanart = os.path.join(PIC_PATH,"fanart-date.png")
            filelist = [row for row in MPDB.Request( """SELECT strPath,strFilename FROM files WHERE datetime("EXIF DateTimeOriginal") BETWEEN datetime('now','-1 months') AND datetime('now') ORDER BY "EXIF DateTimeOriginal" ASC""")]
        elif self.args.method == "last100":#TODO
            picfanart = os.path.join(PIC_PATH,"fanart-date.png")
            filelist = [row for row in MPDB.Request( """SELECT strPath,strFilename FROM files WHERE datetime("EXIF DateTimeOriginal") BETWEEN datetime('now','-1 years') AND datetime('now') ORDER BY "EXIF DateTimeOriginal" ASC""")]

        #on teste l'argumen 'viewmode'
            #si viewmode = view : on liste les images
            #si viewmode = scan : on liste les photos qu'on retourne
            #si viewmode = zip  : on liste les photos qu'on zip
        if self.args.viewmode=="scan":
            return filelist
        
        if self.args.viewmode=="zip":
            destination = os.path.join(DATA_PATH,urllib.unquote_plus(self.args.name)+".tar.gz")
            if os.path.isfile(destination):
                dialog = xbmcgui.Dialog()
                ok = dialog.yesno(__language__(30000),"Archive '%s' already exists in"%os.path.basename(destination),os.path.dirname(destination), "Overwrite ?")
                if not ok:
                    #todo, ask for another name and if cancel, cancel the zip process as well
                    xbmc.executebuiltin( "Notification(My Picture Database,Archiving pictures canceled.,File already exists)" )
                    return
                else:
                    pass #user is ok to overwrite, let's go on
            tar = tarfile.open(destination,"w:gz")#open a tar file using gz compression
            error = 0
            pDialog = xbmcgui.DialogProgress()
            ret = pDialog.create(__language__(30000), 'Adding file to archive :','')
            compte=0
            msg=""
            for (path,filename) in filelist:
                compte=compte+1
                picture = os.path.join(path,filename)
                arcroot = path.replace( os.path.dirname( picture ), "" )
                arcname = os.path.join( arcroot, filename ).replace( "\\", "/" )
                if picture == destination: # sert à rien de zipper le zip lui même :D
                    continue
                pDialog.update(int(100*(compte/float(len(filelist)))),"Creating connection...",'Adding file to archive :',picture)
                try:
                    tar.add( picture , arcname)
                    print "Archiving  %s . . ." % picture
                except:
                    print "tar.gz compression error :"
                    error += 1
                    print "Error  %s" % arcname
                    print_exc()
                if pDialog.iscanceled():
                    msg = "Zip file has been canceled !"
                    break
            tar.close()
            if not msg:
                if error: msg = "%s Errors while zipping %s files"%(error,len(filelist))
                else: msg = "%s files successfully Zipped !!"%len(filelist)
            xbmc.executebuiltin( "Notification(%s,%s)"%(__language__(30000),msg) )
            return
        
        if self.args.viewmode=="export":
            #1- ask for destination
            dialog = xbmcgui.Dialog()
            dstpath = dialog.browse(3, "Select the destination","files" ,"", True, False, "")
            #pour créer un dossier dans la destination, on peut utiliser le nom  self.args.name
            if dstpath == "":
                return
            #3- use the  name to export to that folder
            #   a- ask the user if subfolder has to be created
            #   a-1/ yes : show the keyboard for a possible value for a folder name (using m.args.name as base name)
            #               repeat as long as input value is not correct for a folder name or dialog has been canceled
            #   a-2/ no : simply go on with copy ...
            ok = dialog.yesno("MyPictures Database","Do you want to create a subfolder for exported pictures ?","(%s)"%self.args.name)
            if ok:
                dirok=False
                while not dirok:
                    kb = xbmc.Keyboard(self.args.name, 'Input subfolder name', False)
                    kb.doModal()
                    
                    if (kb.isConfirmed()):
                        subfolder = kb.getText()
                        try:
                            os.mkdir(os.path.join(dstpath,subfolder))
                            dstpath = os.path.join(dstpath,subfolder)
                            dirok = True
                        except Exception,msg:
                            print_exc()
                            dialog.ok("MyPictures Database","Error#%s : %s"%msg.args)
                    else:
                        xbmc.executebuiltin( "Notification(%s,Files copy canceled ! )"%__language__(30000) )
                        return

            
            #browse(type, heading, shares[, mask, useThumbs, treatAsFolder, default])
            from shutil import copy
            pDialog = xbmcgui.DialogProgress()
            ret = pDialog.create(__language__(30000), 'Copying files...')
            i=0.0
            cpt=0
            for path,filename in filelist:
                pDialog.update(int(100*i/len(filelist)),"Copying '%s' to :"%os.path.join(path,filename),dstpath)
                i=i+1.0
                #2- does the destination have the file ? shall we overwrite it ?
                #TODO : rename a file if it already exists, rather than asking to overwrite it
                if os.path.isfile(os.path.join(dstpath,filename)):
                    ok = dialog.yesno(__language__(30000),"File %s already exists in"%filename,dstpath,"Overwrite it ?")
                    if not ok:
                        continue
                copy(os.path.join(path.decode("utf8"),filename.decode("utf8")), dstpath.decode("utf8"))
                cpt = cpt+1
            pDialog.update(100,"Copying Finished !",dstpath)
            xbmc.sleep(1000)
            xbmc.executebuiltin( "Notification(%s,%s files copied to %s )"%(__language__(30000),cpt,dstpath) )
            dialog.browse(2, "Pictures exported","files" ,"", True, False, dstpath)
            return
        
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
            context.append( (__language__(30060),"XBMC.RunPlugin(\"%s?action='locate'&filepath='%s'&viewmode='view'\" ,)"%(sys.argv[0],os.path.join(urllib.quote_plus(path),
                                                                                                                                                          urllib.quote_plus(filename)))))

            #4 - si la photo contient des données GPS, la localiser sur une carte
            coords = MPDB.getGPS(path,filename)
            if coords:
                #géolocalisation
                context.append( (__language__(30220),"XBMC.RunPlugin(\"%s?action='geolocate'&place='%s'&path='%s'&filename='%s'&viewmode='view'\" ,)"%(sys.argv[0],"%0.6f,%0.6f"%(coords),
                                                                                                                                                       urllib.quote_plus(path),
                                                                                                                                                       urllib.quote_plus(filename))))
                                 
            #5 - les infos de la photo
            #context.append( ( "paramètres de l'addon","XBMC.ActivateWindow(virtualkeyboard)" ) )
            self.addPic(filename,
                        path,
                        contextmenu = context,
                        fanart = xbmcplugin.getSetting(int(sys.argv[1]),'usepicasfanart')=='true' and os.path.join(path,filename) or picfanart
                        )
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE)
        xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="photos" )
        xbmcplugin.endOfDirectory(int(sys.argv[1]))           
            

    
            

if __name__=="__main__":
    m=Main()
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
        #set the debugging for the library
        MPDB.DEBUGGING = False
        # initialisation de la base :
        MPDB.pictureDB = pictureDB
        #   - efface les tables et les recréés
        MPDB.Make_new_base(pictureDB,
                           ecrase= Addon.getSetting("initDB") == "true")
        if Addon.getSetting("initDB") == "true":
            Addon.setSetting("initDB","false")
        #scan les répertoires lors du démarrage (selon setting)
        if Addon.getSetting('bootscan')=='true':
            if not(xbmc.getInfoLabel( "Window.Property(DialogAddonScan.IsAlive)" ) == "true"):
                #si un scan n'est pas en cours, on lance le scan
                xbmc.executebuiltin( "RunScript(%s,--database) "%os.path.join( os.getcwd(), "scanpath.py") )
                #puis on rafraichi le container sans remplacer le contenu, avec un paramètre pour dire d'afficher le menu
                xbmc.executebuiltin( "Container.Update(\"%s?action='showhome'&viewmode='view'\" ,)"%(sys.argv[0]) , )
                
    elif m.args.action=='showhome':
        #display home menu
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
    #   Affiche les images
    elif m.args.action=='showpics':
        m.show_pics()
    #affiche la sélection de période
    elif m.args.action=='showperiod':
        m.show_period()
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
    elif m.args.action=='locate':
        dialog = xbmcgui.Dialog()
        print urllib.unquote_plus(m.args.filepath)
        dstpath = dialog.browse(2, "The file is located here :","files" ,"", True, False, urllib.unquote_plus(m.args.filepath))
    elif m.args.action=='geolocate':
        m.show_map()
    else:
        m.show_home()
    del MPDB
    
