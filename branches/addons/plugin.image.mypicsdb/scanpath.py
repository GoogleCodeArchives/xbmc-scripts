usagestr = """
requires : MyPictures Database library
requires : XBMC mediacenter (at least Dharma version)

Scans silently folders for feeding the database with IPTC/EXIF pictures metadatas

usage :
    scan_path (--database|--rootpath) [--recursive] [--update] %database_path% [%folder to scan%]
        --database 
            Use the database given as first argument. Browse all root path found in the database
      OR
        --rootpath
            Scan a path for pictures (does not create the root folder in the database)
        --recursive
            If given, in addition to -p, indicates a recursive scan
        --update
            if given, remove pictures that does not exists anymore in the given path

        -h or --help : show the usage info

      arguments :
          1- full path to the database
          2- if --rootpath, the path to scan for pictures
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



import xbmc,xbmcgui
import urllib
from traceback import print_exc,format_tb
if sys.modules.has_key("MypicsDB"):
    del sys.modules["MypicsDB"]
import MypicsDB as MPDB
    
global pictureDB
pictureDB = os.path.join(DB_PATH,"MyPictures.db")

import time 
from traceback import print_exc
 
from DialogAddonScan import AddonScan
from file_item import Thumbnails  

listext = [".JPG",".TIF",".PNG",".GIF",".BMP",".JPEG"]

def main2():
    #get active window
    import optparse
    parser = optparse.OptionParser()
    parser.enable_interspersed_args()  
    parser.add_option("--database","-d",action="store_true", dest="database",default=False)
    #parser.add_option("--help","-h")
    parser.add_option("-p","--rootpath",action="store", type="string", dest="rootpath")
    parser.add_option("-r","--recursive",action="store_true", dest="recursive", default=True)
    parser.add_option("-u","--update",action="store_true", dest="update", default=True)
    (options, args) = parser.parse_args()
    print "option,args"
    print options
    print args
    print dir(parser)
    
    if options.rootpath:
        print urllib.unquote_plus(options.rootpath)
        scan = AddonScan()#xbmcgui.getCurrentWindowId()
        scan.create( "MyPicture Database " )
        print options.recursive
        print options.update
        scan.update(0,0,"MyPicture Database [Preparing]","please wait...")
        count_files(urllib.unquote_plus(options.rootpath))
        try:
            #browse_folder(dirname,parentfolderID=None,recursive=True,updatecontent=False,rescan=False,updatefunc=None)
            browse_folder(urllib.unquote_plus(options.rootpath),parentfolderID=None,recursive=options.recursive,updatecontent=options.update,rescan=True,updatefunc=scan)
        except:
            print_exc()
        scan.close()
        
        
    if options.database:
        listofpaths = MPDB.RootFolders()
        if listofpaths:
            scan = AddonScan()#xbmcgui.getCurrentWindowId()
            scan.create( "MyPicture Database " )
            scan.update(0,0,"MyPicture Database [Preparing]","please wait...")
            for path,recursive,update in listofpaths:
                count_files(urllib.unquote_plus(path))
                try:
                    #browse_folder(dirname,parentfolderID=None,recursive=True,updatecontent=False,rescan=False,updatefunc=None)
                    browse_folder(urllib.unquote_plus(path),parentfolderID=None,recursive=recursive==1,updatecontent=update==1,rescan=False,updatefunc=scan)
                except:
                    print_exc()
            scan.close()
            



global compte,comptenew,cptscanned,cptdelete
compte=comptenew=cptscanned=cptdelete=0
global totalfiles,totalfolders
totalfiles=totalfolders=0

def processDirectory ( args, dirname, filenames ):
    global totalfolders,totalfiles
    totalfolders=totalfolders+1
    for filename in filenames:
        if os.path.splitext(filename)[1].upper() in listext:
            totalfiles=totalfiles+1

def count_files ( path ):
    global totalfiles,totalfolders
    totalfiles=totalfolders=0
    os.path.walk(path, processDirectory, None )
    print totalfiles,totalfolders
    
def browse_folder(dirname,parentfolderID=None,recursive=True,updatecontent=False,rescan=False,updatefunc=None):
    """parcours le dossier racine 'dirname'
    - 'recursive' pour traverser récursivement les sous dossiers de 'dirname'
    - 'update' pour forcer le scan des images qu'elles soient déjà en base ou pas
    - 'updatefunc' est une fonction appelée pour indiquer la progression. Les paramètres sont (pourcentage(int),[ line1(str),line2(str),line3(str) ] )
"""
    #######
    # STEP 1 : list all files in directory
    #######
    try:
        listdir = os.listdir(dirname)
    except:
        tb = sys.exc_info()[2]
        tbinfo = format_tb(tb)[0]
        pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n    " + \
                str(sys.exc_type)+ ": " + str(sys.exc_value) + "\n"
        MPDB.log( pymsg )
        listdir=[]
        
    global compte,comptenew,cptscanned,cptdelete
    cpt=0
    #on liste les fichiers jpg du dossier
    listfolderfiles=[]

    #######
    # STEP 2 : Keep only the files with extension...
    #######
    for f in listdir:
        if os.path.splitext(f)[1].upper() in listext:
            listfolderfiles.append(f)

   
    #on récupère la liste des fichiers entrées en BDD pour le dossier en cours
    listDBdir = MPDB.DB_listdir(dirname)# --> une requête pour tout le dossier

    #######
    # STEP 3 : If folder contains pictures, create folder in database
    #######
    #on ajoute dans la table des chemins le chemin en cours
    PFid = MPDB.DB_folder_insert(os.path.basename(dirname) or os.path.dirname(dirname).split(os.path.sep)[-1],
                            dirname,
                            parentfolderID,
                            listfolderfiles and "1" or "0"#i
                            )
    if listfolderfiles:#si le dossier contient des fichiers jpg...
##        #on ajoute dans la table des chemins le chemin en cours
##        PFid = DB_folder_insert(os.path.basename(dirname) or os.path.dirname(dirname).split(os.path.sep)[-1],
##                                dirname,
##                                parentfolderID,
##                                i#"1" if listfolderfiles else "0"
##                                )
        #######
        # STEP 4 : browse all pictures
        #######
        #puis on parcours toutes les images du dossier en cours
        for picfile in listfolderfiles:#... on parcours tous les jpg
            cptscanned = cptscanned+1
            cpt = cpt + 1
            ###if updatefunc and updatefunc.iscanceled(): return#dialog progress has been canceled
            #on enlève l'image traitée de listdir
            listdir.pop(listdir.index(picfile))
            #picture is not yet inside database
            if not (picfile in listDBdir) or rescan:
                #if updatefunc: updatefunc.update(int(100 * float(cpt)%len(listfolderfiles)),"Adding from %s to Database :"%dirname,picfile)
                if updatefunc:
                    #updatefunc.update(int(100 * float(cpt)%len(listfolderfiles)),
                    updatefunc.update(int(100*float(cptscanned)/float(totalfiles)),#cptscanned-(cptscanned/100)*100,
                                      cptscanned/100,#TODO : compter les dossiers parcourus pour la 2ieme barre
                                      "MyPicture Database [Adding] (%0.2f%%)"%(100*float(cptscanned)/float(totalfiles)),
                                      picfile)
                #préparation d'un dictionnaire pour les champs et les valeurs
                # c'est ce dictionnaire qui servira à  remplir la table fichiers
                ##picentry = { "strPath":dirname, "strFilename":picfile }
                picentry = { "idFolder":PFid, "strPath":dirname.decode("utf8"),"strFilename":picfile.decode("utf8"),"UseIt":1,"sha":MPDB.fileSHA(os.path.join(dirname,picfile)),"DateAdded":time.strftime("%Y-%m-%d %H:%M:%S") }

                ### chemin de la miniature
                thumbnails = Thumbnails()
                picentry["Thumb"]=thumbnails.get_cached_picture_thumb( os.path.join(dirname,picfile) ).decode("utf8")

                ###############################
                #    getting  EXIF  infos     #
                ###############################
                #reading EXIF infos
                #   (file fields are creating if needed)
                try:
                    exif = MPDB.get_exif(os.path.join(dirname,picfile).encode('utf8'))
                except UnicodeDecodeError:
                    exif = MPDB.get_exif(os.path.join(dirname,picfile))
                #EXIF infos are added to a dictionnary
                picentry.update(exif)

                ###############################
                #    getting  IPTC  infos     #
                ###############################
                iptc = MPDB.get_iptc(dirname,picfile)
                #IPTC infos are added to a dictionnary
                picentry.update(iptc)

                ###############################
                #  Insert infos in database   #
                ###############################

                #insertion des données dans la table
                MPDB.DB_file_insert(dirname,picfile,picentry,rescan)

                #comptage
                comptenew=comptenew+1
            else: # the file is already in DB, we are passing it
                #if updatefunc: updatefunc.update(int(100 * float(cpt)%len(listfolderfiles)),"Already in Database :",picfile)
                if updatefunc:
                    #updatefunc.update(int(100 * float(cpt)/len(listfolderfiles)),
                    updatefunc.update(int(100*float(cptscanned)/float(totalfiles)),#cptscanned-(cptscanned/100)*100,
                                      cptscanned/100,
                                      "MyPicture Database [Passing] (%0.2f%%)"%(100*float(cptscanned)/float(totalfiles)),
                                      picfile)
                pass
            if picfile in listDBdir:
                listDBdir.pop(listDBdir.index(picfile))
                
        #Now if the database contain some more pictures assign for this folder, we need to delete them if 'update' setting is true
        if listDBdir and updatecontent: #à l'issu si listdir contient encore des fichiers, c'est qu'ils sont en base mais que le fichier n'existe plus physiquement.
            for f in listDBdir: #on parcours les images en DB orphelines
                cptdelete=cptdelete+1
                if updatefunc:
                    updatefunc.update(int(100*float(cptscanned)/float(totalfiles)),#cptscanned-(cptscanned/100)*100,
                                      cptscanned/100,
                                      "MyPicture Database [Removing]",
                                      f)
                MPDB.DB_del_pic(dirname,f)
                MPDB.log( "\t%s has been deleted from database because the file does not exists in this folder. "%f)#f.decode(sys_enc))
            MPDB.log("")

            
    else:
        MPDB.log( "Ce dossier ne contient pas d'images :")
        MPDB.log( dirname )
        MPDB.log( "" )
    
    if cpt:
        MPDB.log( "%s nouvelles images trouvees dans %s"%(str(cpt),dirname) )
        #unicode(info.data[k].encode("utf8").__str__(),"utf8")
        compte=compte+cpt
        cpt=0
    if recursive: #gestion de la recursivité. On rappel cette même fonction pour chaque dossier rencontré
        MPDB.log( "traitement des sous dossiers de :")
        MPDB.log( dirname )
        for item in listdir:
            if os.path.isdir(os.path.join(dirname,item)):#un directory
                #browse_folder(dirname,parentfolderID=None,recursive=True,updatecontent=False,rescan=False,updatefunc=None)
                browse_folder(os.path.join(dirname,item),PFid,recursive,updatecontent,rescan,updatefunc)
            else:
                #listdir contenait un fichier mais pas un dossier
                # inutilisé... on passe pour le moment
                pass
    
def usage():
    print usagestr

if __name__=="__main__":
    #commande dos de test :
    #F:\Apps\Python24>python scanpath.py --rootpath --recursive --update 'c:\path to database\db.db' 'path to scan'

    #1- récupérer le paramètre
    main2()
    xbmc.executebuiltin( "Notification(MyPictures Database,%s scanned / %s added / %s removed)"%(cptscanned,comptenew,cptdelete) )
