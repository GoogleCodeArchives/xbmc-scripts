# -*- coding: cp1252 -*-
import threading
import urllib
import time
import StringIO
"""
utilisation :
    enregistrement = Recorder(label=self.info,chanid=idchan,channame=nomchan,channum=numchan) #création de l'enregistrement
    enregistrement.start() #lancement de l'enregistrement
    enregistrement.stop() #arrête l'enregistrement
"""
class Recorder(threading.Thread):
    """
    Créé une nouvelle instance d'enregistrement Freebox
        Recorder( label , chanid , channame , channum )
    avec
        label:      un objet xbmc.controlLabel
        chanid:     l'id de la chaine a enregistrer
        channame:   le nom de la chaine
        channum:    le numéro de la chaine
    """
    def __init__(self,label,chanid,channame,channum):
        self.recording = False
        self.chanid = chanid
        self.channum = channum
        self.channame = channame
        self.info = label
        self.caching = False # activation du cache pour générer la preview
        self.preview = False # disponibilité de la preview
        self.filename = "%s_%s.avi"%(utils.FatX(channame,decal=13),time.strftime("%d%m%y_%Hh%M",time.localtime()))
        #print self.filename,str(len(self.filename))
        self.filesize = 0
        self.memfile = StringIO.StringIO() # fichier mémoire recevant les données le temps de la mise en cache

    def run(self):
        try:
            TV = urllib.urlopen("http://127.0.0.1:8083/freeboxtv/%s"%self.chanid)
            self.recording = True
        except IOError:
            print "Impossible d'ouvrir le flux (timeout)"
            self.recording=False
        
        rec = open(RECORDS + self.filename,"wb",32768)
        starttime=time.time()
        while self.recording:
            self.info.setLabel("%.1f Mo en %i sec."%(self.filesize/1024.0,time.time()-starttime))
            datas = TV.read(2048)
            rec.write(datas)
            self.filesize+=2
            if self.caching:
                self.memfile.write(datas)
                if self.memfile.len > CACHESIZE: #si le cache est rempli :
                    print "Fin du caching ! Ecriture de preview.avi"
                    # - on écrit le fichier preview
                    f = open(HOMEDIR + "preview.avi","wb")
                    f.write(self.memfile.getvalue())
                    f.close()
                    #print self.memfile
                    #thread.start_new_thread(self.previewcache,())
                    # - on réinitialise pour la suite
                    self.caching = False #fin de la mise en cache
                    self.preview = True #fichier de preview disponible
                    self.memfile.close()
                    self.memfile = StringIO.StringIO()
                else:
                    pass
            else: #pas de mise en cache demandée
                pass
        #l'enregistrement doit se terminer
        # - fermeture des fichiers
        try:
            TV.close()
            del TV
        except:
            print "impossible de fermer la connection au proxy"

        rec.close()
        self.memfile.close()
        del rec, self.memfile
        #création du thumbnail
        try:
            print LOGODIR+"%s.bmp"%self.chanid
            print RECORDS+self.filename[:-3]+"tbn"
            shutil.copyfile(LOGODIR+"%s.bmp"%self.chanid , RECORDS+self.filename[:-3]+"tbn")
        except:
            print "erreur lors de la création de la miniature"
        #réinitialisation
        self.preview=False

    def previewcache(self):
        self.caching = False #fin de la mise en cache
        f = open(HOMEDIR + "preview.avi","wb",1024)
        f.write(self.memfile.getvalue())
        f.close()
        self.preview = True #fichier de preview disponible
        self.memfile.close()
        self.memfile = StringIO.StringIO()
        print "PREVIEWCACHE TERMINE"

    def stop(self):
        self.recording = False

if __name__ == "__main__":
    print "Lancement du module enregistreur."
    print ""
