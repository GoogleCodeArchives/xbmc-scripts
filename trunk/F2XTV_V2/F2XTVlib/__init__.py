"""init file"""
import enregistreur, programmateur, parseur
import utils
import os


#HOMEDIR = os.getcwd()[:-1]+"\\" #XBMC
HOMEDIR = os.getcwd()+"\\" #PC
DATAS = HOMEDIR+"datas\\"
MEDIAS = HOMEDIR+"medias\\"

SETTINGSini = HOMEDIR+"F2XTV.ini"
PROGRAMMESini = DATAS + "programmation.ini"
