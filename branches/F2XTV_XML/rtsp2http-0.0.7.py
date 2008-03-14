# -*- coding: utf-8 -*-
"""
Proxy RTSP 2 HTTP

Ce programme se destine à ceux qui souhaite visionner un flux vidéo
rtsp sur un lecteur qui n'est pas destiné à cela. A la base, ce 
programme est destiné à visionner un flux rtsp sur XBMC.

Pour cela, ce programme crée un proxy qui permet de transformer le 
flux rtsp en un flux http.

Ce script nécessite un fichier de configuration F2XTV.ini devant 
se trouver soit dans le même répertoire que le script (exemple d'utilisation 
sur un pc), soit dans le répertoire userdata d'xbmc (Utilisation du script 
dans xbmc)

Ce script est la reprise du script initié par puyb puis amélioré par alexsolex
et portant le même nom. Ce script est basé sur la même méthode mais la 
programmation est différente
"""

# import des bibliothèques

import socket
import threading
import sys
import os.path
import os
import string
import time
import select
from ConfigParser import ConfigParser

# préparation des variables globales
_version = "0.0.7"
_date = "1177347522"
_info_server = "Proxy RTSP 2 HTTP, version " + _version + ", " + _date


# Fonctions et classes :

#------------------------------------------------------------------

def RecupParamServer ( serv ):
  """
  Fonction permettant de récupérer les paramètres du serveur RTSP serv à partir
  du fichier de configuration F2XTV.ini
  
  Utilisation:
    paramServer = RecupParamServer ( serv )
  avec:
    serv: le nom du serveur RTSP
    paramServer: le dictionnaire contenant les paramètres du serveur RTSP
      - Server: l'adresse IP du serveur RTSP ou son nom DNS
      - Path: le complément d'adresse à fournir au serveur avant 
      d'arriver au fichier partagé
      - Port: le port d'écoute du serveur RTSP
  
  Attention, si les informations du serveur RTSP ne sont pas présentes dans
  le fichier de configuration, paramServer est un dictionnaire vide!
  """
  
  # Récupération du fichier F2XTV.ini
  if os.path.isfile("Q:\\userdata\\F2XTV.ini"):
    mon_fichier = "Q:\\userdata\\F2XTV.ini"
  else:
    homedir = os.getcwd()
    if homedir.endswith(";"): homedir=homedir[:-1]
    mon_fichier = homedir + "\\"+"F2XTV.ini"
  
  # Création du parser
  settings = ConfigParser()
  
  # Lecture du fichier
  settings.read(mon_fichier)
  
  # serv est passé en minuscule
  serv = string.lower(serv)
  
  # Récupération des données si le serveur existe
  serveur = {}
  if settings.has_section("server:" + serv):
    serveur["Server"] = settings.get("server:" + serv, "Server") 
    serveur["Path"] = settings.get("server:" + serv, "Path") 
    serveur["Port"] = settings.getint("server:" + serv, "Port")
    serveur["IP"] = socket.gethostbyname(serveur["Server"])
  
  return serveur

#------------------------------------------------------------------

def RecupOptions ():
  """
  Fonction permettant de récupérer les paramètres du serveur HTTP à partir
  du fichier de configuration F2XTV.ini
  
  Utilisation:
    options = RecupOptions ()
  avec:
    options: le dictionnaire contenant les paramètres du serveur HTTP
  
  Attention, si les informations du serveur RTSP ne sont pas présentes dans
  le fichier de configuration, paramServer est un dictionnaire vide!
  """
  
  # Récupération du fichier F2XTV.ini
  if os.path.isfile("Q:\\userdata\\F2XTV.ini"):
    mon_fichier = "Q:\\userdata\\F2XTV.ini"
  else:
    homedir = os.getcwd()
    if homedir.endswith(";"): homedir=homedir[:-1]
    mon_fichier = homedir + "\\"+"F2XTV.ini"
  
  # Création du parser
  settings = ConfigParser()
  
  # Lecture du fichier
  settings.read(mon_fichier)
  
  # Récupération des données
  options = {}
  options["port"] = settings.getint("general", "port") 
  plagePortsClient = string.split(settings.get("general", "plagePortsClient"), "-")
  options["plagePortsClient"] = [ int(plagePortsClient [0]) , int(plagePortsClient [1]) ] 
  options["showDebug"] = settings.getint("general", "showDebug") 
  
  return options

#------------------------------------------------------------------

def erreur (client, numErreur, typeErreur, textErreur):
  tabReponse = ['<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">']
  tabReponse.append('<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="fr-FR" lang="fr-FR">')
  tabReponse.append('  <head>')
  tabReponse.append('    <title>%d %s</title>' % (int(numErreur), typeErreur))
  tabReponse.append('  </head>')
  tabReponse.append('  <body>')
  tabReponse.append('    <h1>%s</h1>' % typeErreur)
  # The requested %s %s was not found on this server
  tabReponse.append('    %s<br />' % textErreur)
  tabReponse.append('    <hr>')
  tabReponse.append('    <address>%s</address>'%_info_server)
  tabReponse.append('  </body>')
  tabReponse.append('</html>')
  reponse = string.join(tabReponse, '\n')
  
  tabReponse = ['HTTP/1.0 %d %s' % (int(numErreur), typeErreur)]
  tabReponse.append('Server: %s'%_info_server)
  tabReponse.append('Keep-Alive: timeout=15, max=100')
  tabReponse.append('Connection: close')
  tabReponse.append('Content-Length: %d' % len(reponse))
  tabReponse.append('Content-Type: text/html; charset=utf-8')
  tabReponse.append('')
  tabReponse.append(reponse)
  reponse = string.join(tabReponse, '\r\n')
  
  client.send(reponse)
  
#------------------------------------------------------------------

def showVersion(client):
  tabReponse = ['HTTP/1.0 200 OK']
  tabReponse.append('Server: %s'%_info_server)
  tabReponse.append('Keep-Alive: timeout=15, max=100')
  tabReponse.append('Connection: close')
  tabReponse.append('Content-Length: %d' % len(_date))
  tabReponse.append('Content-Type: text/html; charset=utf-8')
  tabReponse.append('')
  tabReponse.append(_date)
  reponse = string.join(tabReponse, '\r\n')
  
  client.send(reponse)
  
#------------------------------------------------------------------

def showInfos (repHTTP, listeClients):
  
  # Récupération du fichier F2XTV.ini
  if os.path.isfile("Q:\\userdata\\F2XTV.ini"):
    mon_fichier = "Q:\\userdata\\F2XTV.ini"
  else:
    mon_fichier = "F2XTV.ini"
  
  # Création du parser
  settings = ConfigParser()
  
  # Lecture du fichier
  settings.read(mon_fichier)
  
  reponse2 = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">\n' \
    + '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="fr-FR" lang="fr-FR">\n' \
    + '   <head>\n' \
    + '      <title>Informations sur le serveur : ' + _info_server + '</title>\n' \
    + '      <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n' \
    + '      <meta http-equiv="Content-Style-Type" content="text/css" />\n' \
    + '      <meta http-equiv="Content-Language" content="fr-FR" />\n' \
    + '      <style type="text/css">\n' \
    + '         ul.partage {margin: 0px ; padding: 0px; list-style-type: none ;}\n' \
    + '         ul.partage li {float: left ; padding-left: 50px ;}\n' \
    + '         div.gen {width: 350px; background-color: #D7E7F2; border: 1px solid #287CB1; padding: 0 10px 10px 10px; margin-left: 15px; margin-bottom: 10px;}\n' \
    + '         div.row {clear: both; padding-top: 10px;}\n' \
    + '         div.row span.title {font-style: oblique; font-size: 110%; font-weight: bold;}\n' \
    + '         div.row span.label {float: left; width: 140px; text-align: right; margin-right: 15px;}\n' \
    + '         div.row span.labelserv {float: left; width: 80px; text-align: right; margin-right: 15px;}\n' \
    + '      </style>\n' \
    + '   </head>\n' \
    + '   \n' \
    + '   <body>\n' \
    + '      <center><h1>' + _info_server + '</h1></center>\n' \
    + '      <hr />\n' \
    + '      <br />\n' \
    + '      <ul class="partage">\n' \
    + '         <li>\n' \
    + '            <h2>Serveur HTTP:</h2>\n' \
    + '            <div class="gen">\n' \
    + '               <div class="row">\n' \
    + '                  <span class="label">host:</span>\n' \
    + '                  <span class="infos">' + settings.get("general", "host") + '&nbsp;</span>\n' \
    + '               </div>\n' \
    + '               <div class="row">\n' \
    + '                  <span class="label">port:</span>\n' \
    + '                  <span class="infos">' + settings.get("general", "port") + '&nbsp;</span>\n' \
    + '               </div>\n' \
    + '               <div class="row">\n' \
    + '                  <span class="label">queueSize:</span>\n' \
    + '                  <span class="infos">' + settings.get("general", "queueSize") + '&nbsp;</span>\n' \
    + '               </div>\n' \
    + '               <div class="row">\n' \
    + '                  <span class="label">plagePortsClient:</span>\n' \
    + '                  <span class="infos">' + settings.get("general", "plagePortsClient") + '&nbsp;</span>\n' \
    + '               </div>\n' \
    + '               <div class="row">\n' \
    + '                  <span class="label">showDebug:</span>\n' \
    + '                  <span class="infos">' + settings.get("general", "showDebug") + '&nbsp;</span>\n' \
    + '               </div>\n' \
    + '            </div>\n' \
    + '            <br />\n' \
    + '            <h2>Clients HTTP:</h2>\n' \
    + '            <div class="gen">\n'
  
  for client in listeClients:
    etatThread = string.split(str(client), ", ") [1]
    etatThread = string.split(etatThread, ")") [0]
    (ipClient, portClient) = client.address
    reponse2 += '               <div class="row">\n' \
      + '                  <span class="label">' + ipClient + ':' + str(portClient) + '&nbsp;</span>\n' \
      + '                  <span class="infos">(' + str(etatThread) + ') - ' + str(client.temp_url) + '&nbsp;</span>\n' \
      + '               </div>\n'
  
  reponse2 += '            </div>\n' \
    + '            <br />\n' \
    + '         </li>\n' \
    + '         <li>\n' \
    + '            <h2>Serveurs RTSP:</h2>\n' \
  
  for section in settings.sections():
    if section.startswith("server:"):
      reponse2 += '            <div class="gen">\n' \
        + '               <div class="row">\n' \
        + '                  <span class="title">' + section.split(":")[1] + '&nbsp;</span>\n' \
        + '               </div>' \
        + '               <div class="row">\n' \
        + '                  <span class="labelserv">Server:</span>\n' \
        + '                  <span class="infos">' + settings.get(section, "Server") + ' (' + socket.gethostbyname(settings.get(section, "Server")) + ')&nbsp;</span>\n' \
        + '               </div>\n' \
        + '               <div class="row">\n' \
        + '                  <span class="labelserv">Path:</span>\n' \
        + '                  <span class="infos">' + settings.get(section, "Path") + '&nbsp;</span>\n' \
        + '               </div>\n' \
        + '               <div class="row">\n' \
        + '                  <span class="labelserv">Port:</span>\n' \
        + '                  <span class="infos">' + settings.get(section, "Port") + '&nbsp;</span>\n' \
        + '               </div>\n' \
        + '            </div>\n'
  
  reponse2 += '         </li>\n' \
    + '      </ul>\n' \
    + '   </body>\n' \
    + '</html>\n'
  
  reponse1 = "HTTP/1.0 200 OK\r\nServer: " + _info_server \
  + "\r\nKeep-Alive: timeout=15, max=100\r\nConnection: close\r\n" \
  + "Content-Length: " + str(len(reponse2)) + "\r\n"\
  + "Content-Type: text/html; charset=utf-8\r\n\r\n" \
  + reponse2
  
  # print "\n---\n", reponse1, "\n---\n"
  repHTTP.send(reponse1)
  

## ------------------------------------------------------ ##
## -------------       RTSP Client        --------------- ##
## ------------------------------------------------------ ##

# cette classe correspond au client RTSP, cette partie discutera 
# directement avec le serveur RTSP 
class RTSPClient (threading.Thread):
  
  #------------------------------------------------------------------
  # Intégration dans le __init_des paramètres du serveur
  def __init__ ( self, socketHTTP, paramServer, url, PortsClient, showDebug ):
    self.paramServer = paramServer
    self.socketClientHTTP = socketHTTP
    self.url = url
    self.numSeq = 1
    self.size = 1024
    self.PortsClient = PortsClient
    self.showDebug = showDebug
    
    self.demande = "rtsp://" + self.paramServer["IP"] + "/" + \
      self.paramServer["Path"] + self.url
    if self.showDebug: print self.demande
  
  #------------------------------------------------------------------
  # Définition du socket correspondant au serveur RTSP
  def open_socket ( self ):
    print "ouverture socket serveur RTSP (" + self.paramServer["IP"] + ":" + str(self.paramServer["Port"]) + ")"
    try:
      self.SocketRTSP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.SocketRTSP.connect ( ( self.paramServer["IP"], self.paramServer["Port"] ) )
    except socket.error, (value,message):
      if self.SocketRTSP:
        self.SocketRTSP.close()
      sys.exit("Ouverture Socket impossible : " + message)
  
  #------------------------------------------------------------------
  def request_Options ( self ):
    
    print "demande d'options - serveur: " + self.paramServer["Server"]
    requete = "OPTIONS " + self.demande + " RTSP/1.0\r\n" + \
      "CSeq: " + str(self.numSeq) + "\r\n" + \
      "User-Agent: " + _info_server + "\r\n\r\n"
    if self.showDebug: print "----\n", requete, "----\n"
    
    self.SocketRTSP.send (requete)
    self.numSeq += 1
    
    data = self.SocketRTSP.recv(self.size)
    if self.showDebug: print "----\n", data, "----\n"
    
    # Analyse et récupération des fonctions disponibles pour le serveur
    lines = string.split (data, "\n")
    verif = 1
    for line in lines:
      if verif:
        (proto, code, error) = string.split (line, " ", 2)
        verif = 0
        if proto[0:4] != "RTSP":
          print "ATTENTION : ce n'est pas une requête RTSP"
          return 1
        if code != "200":
          print "ATTENTION : flux RTSP non valide"
          print "ERREUR :", error
          return 1
      else:
        if string.find (line, ":") > 0:
          (header, infos) = string.split (line, ":", 1)
          if header == 'Public':
            infos = string.replace (infos, ",", " ")
            self.fonctionsServeurRTSP = string.split (infos)
    return 0
  
  #------------------------------------------------------------------
  def request_Describe ( self ):
    
    print "demande de description - video: " + self.url + " - serveur: " + self.paramServer["Server"]
    requete = "DESCRIBE " + self.demande + " RTSP/1.0\r\n" + \
      "CSeq: " + str(self.numSeq) + "\r\n" + \
      "Accept: application/sdp\r\n" + \
      "User-Agent: " + _info_server + "\r\n\r\n"
    if self.showDebug: print "----\n", requete, "----\n"
    
    self.SocketRTSP.send (requete)
    self.numSeq += 1
    
    data = self.SocketRTSP.recv(self.size)
    limite = string.find(data, '\r\n\r\n')
    
    data1 = data[:limite+4]
    if self.showDebug: print "----\n", data1, "----\n"
    data2 = data[limite+4:]
    
    # Analyse et récupération du nombre de caractères correspondant aux 
    # informations du flux
    lines = string.split (data1, "\r\n")
    verif = 1
    infosSup = 0
    self.nomFlux = '*'
    nomFluxRecu = False
    for line in lines:
      if verif:
        (proto, code, error) = string.split (line, " ", 2)
        if proto[0:4] != "RTSP":
          print "ATTENTION : ce n'est pas une requête RTSP"
          return 1
        if code == "500" or code == "404":
          print "ATTENTION : flux RTSP inaccessible :", code
          erreur (self.socketClientHTTP, code, error, "The requested file %s was not found on this server" % self.url)
          return 2
        if code != "200":
          print "ATTENTION : flux RTSP non valide"
          print "ERREUR :", error
          return 1
        verif = 0
      else:
        if string.find (line, "=") > 0:
          (header, infos) = string.split (line, "=", 1)
          if header == 'a':
            (header_, infosSup) = string.split (infos, ":", 1)
            if header_ == 'control':
              self.nomFlux = string.split(infosSup)[0]
              nomFluxRecu = True
        elif string.find (line, ":") > 0:
          (header, infos) = string.split (line, ":", 1)
          if header.lower() == 'content-length':
            infosSup = int(infos)
    if self.showDebug: print "nb de caractères :", infosSup
    
    longueur = infosSup - len(data2)
    
    if not nomFluxRecu:
      if longueur > 0:
        data3 = self.SocketRTSP.recv(longueur)
        data = data2 + data3
      else:
        data = data2
      if self.showDebug: print "----\n", data, "----\n"
      
      TrouveControl = False
      
      lines = string.split (data, "\n")
      self.nomFlux = '*'
      for line in lines:
        if string.find (line, "=") > 0:
          (header, infos) = string.split (line, "=", 1)
          if header == 'a':
            (header_, infosSup) = string.split (infos, ":", 1)
            if header_ == 'control':
              if not TrouveControl :
                self.nomFlux = string.split(infosSup)[0]
                TrouveControl = True
              else:
                print "Plus d'un flux de control! non géré par le proxy!"
                erreur (self.socketClientHTTP, code, error, "The requested file %s was not found on this server" % self.url)
                return 2
    if self.showDebug: print self.nomFlux
    
    if self.nomFlux == '*':
      self.nomFlux = self.demande
    
    return 0
  
  #------------------------------------------------------------------
  def request_Setup ( self ):
    
    print "demande de setup - video: " + self.url + " - serveur: " + \
      self.paramServer["Server"] + " - port: " + str(self.PortsClient) + \
      "-" + str(self.PortsClient+1)
    requete = "SETUP " + self.nomFlux + " RTSP/1.0\r\n" + \
      "CSeq: " + str(self.numSeq) + "\r\n" + \
      "Transport: RTP/AVP;unicast;client_port=" + str(self.PortsClient) + \
      "-" + str(self.PortsClient+1) + "\r\n" + \
      "User-Agent: " + _info_server + "\r\n\r\n"
    if self.showDebug: print "----\n", requete, "----\n"
    
    self.SocketRTSP.send (requete)
    self.numSeq += 1
    
    data = self.SocketRTSP.recv(self.size)
    if self.showDebug: print "----\n", data, "----\n"
    
    # Analyse et récupération du numéro de session et des numéros de port
    # du serveur si nécessaire
    lines = string.split (data, "\n")
    verif = 1
    self.paramServer["Life_Line"] = False
    self.paramServer["LL_Server_Port"] = 0
    self.numSession = ""
    for line in lines:
      if verif:
        (proto, code, error) = string.split (line, " ", 2)
        if proto[0:4] != "RTSP":
          print "ATTENTION : ce n'est pas une requête RTSP : " + proto[0:4]
          return 1
        if code == "500" or code == "404" or code == "453":
          print "ATTENTION : flux RTSP inaccessible :", code
          erreur (self.socketClientHTTP, code, error, "The requested file %s (error %d) was not found on this server" % (self.url, int(code)))
          return 2
        if code != "200":
          print "ATTENTION : flux RTSP non valide"
          print "ERREUR :", code , ":", error
          return 1
        verif = 0
      else:
        if string.find (line, ":") > 0:
          (header, infos) = string.split (line, ":", 1)
          if header == 'Transport':
            infosSup = string.split (infos, ";")
            for infoSup in infosSup:
              if string.find (infoSup, "=") > 0:
                (nom_port, ports) = string.split (infoSup, "=")
                if nom_port == 'server_port':
                  self.paramServer["Life_Line"] = True
                  self.paramServer["LL_Server_Port"] = int(string.split (ports, "-") [1])
          elif header == 'Session':
            self.numSession = string.split(infos)[0]
    
    reponse="HTTP/1.0 200 OK\nContent-type: application/octet-stream\n" \
                + "Cache-Control: no-cache\n\n"
    self.socketClientHTTP.send(reponse)
    
    if self.showDebug: print str(self.paramServer["Life_Line"]) + " : " + str(self.paramServer["LL_Server_Port"])
    if self.showDebug: print self.numSession
    
    return 0
  
  #------------------------------------------------------------------
  def request_Play ( self ):
    print "demande de lecture - video: " + self.url + " - serveur: " + \
      self.paramServer["Server"] + " - port: " + str(self.PortsClient) + \
      "-" + str(self.PortsClient+1) + " - Client: " + str(self.socketClientHTTP.getpeername())
    
    # Création du socket permettant la réception des données UDP
    try:
      self.SocketUDP = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
      self.SocketUDP.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      self.SocketUDP.bind ( ( '', self.PortsClient ) )
      self.SocketUDP.settimeout ( 5 )
    except socket.error, (value,message):
      if self.SocketUDP:
        self.SocketUDP.close()
      print "Ouverture Socket UDP impossible :", message
      return 0
    
    # Création du socket de controle de flux si nécessaire
    if self.paramServer["Life_Line"]:
      try:
        self.SocketControl = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.SocketControl.bind ( ( '', self.PortsClient+1))
        self.SocketControl.connect ( ( self.paramServer["IP"], self.paramServer["LL_Server_Port"]))
      except socket.error, (value,message):
        if self.SocketControl:
          self.SocketControl.close()
        if self.SocketUDP:
          self.SocketUDP.close()
        print "Ouverture Socket de controle impossible :", message
        return 0
    
    # Préparation de la requête
    requete = "PLAY " + self.demande + " RTSP/1.0\r\n" + \
      "CSeq: " + str(self.numSeq) + "\r\n" + \
      "Session: " + str(self.numSession) + "\r\n" + \
      "Range: npt=0.000-\r\n" + \
      "User-Agent: " + _info_server + "\r\n\r\n"
    if self.showDebug: print "----\n", requete, "----\n"
    self.SocketRTSP.send (requete)
    self.numSeq += 1
    
    data = self.SocketRTSP.recv(self.size)
    if self.showDebug: print "----\n", data, "----\n"
    
    running = True
    t = time.clock()
    
    sheader = "Session: " + str(self.numSession) + "\n\n"
    
    while running:
      if self.paramServer["Life_Line"]:
        if time.clock()-t > 5:
          self.SocketControl.send(sheader)
          t=time.clock()
      
      # on lit 2k... Si le datagram est plus petit, on aura moins de données (FIXME : lire la MTU d'un paquet UDP)
      try:
        data, addr = self.SocketUDP.recvfrom(2048)
      except Exception, err:
        running = False
        print err
        print "RTSP TimeOut"
      else:
        if addr[0] == self.paramServer["IP"]:
          try:
            self.socketClientHTTP.sendall(data[12:])
            # on envoie la paylaod... C'est a dire, le datgram moins les 12 octets d'entête
          except Exception, err:
            running = False # une exception... on arrete tout !
            if type(err) == tuple:
              (num, descr) = err
              if num != 10054: # le client a coupé la communication
                print "Exception lors de l'envoi des données en http"
                print err
                import traceback
                traceback.print_exc()
            else:
              print "Exception lors de l'envoi des données en http"
              print type(err)
              print err
              import traceback
              traceback.print_exc()
              

    self.request_Teardown ()
  
  #------------------------------------------------------------------
  def request_Teardown ( self ):
    requete = "TEARDOWN " + self.demande + " RTSP/1.0\n" + \
      "CSeq: " + str(self.numSeq) + "\n" + \
      "Session: " + str(self.numSession) + "\n" + \
      "User-Agent: " + _info_server + "\n\n\n"
    if self.showDebug: print "----\n", requete, "----\n"
    self.SocketRTSP.send (requete)
    self.numSeq += 1
    
    try:
      data = self.SocketRTSP.recv(self.size)
      if self.showDebug: print "----\n", data, "----\n"
    except Exception, error:
      print error
    
    self.SocketUDP.close ()
    if self.paramServer["Life_Line"]:
      self.SocketControl.close ()
  
  #------------------------------------------------------------------
  # Action effectuée par ce thread
  def run ( self ):
    
    self.open_socket ()
    
    # ajout de la variable self.fonctionsServeurRTSP indiquant les fonctions
    # acceptées par le serveur
    boucle = 0
    bouclage = 1
    while bouclage == 1 and boucle < 5:
      bouclage = self.request_Options ()
      boucle += 1
    
    # ajout de la variable self.nomFlux donnant l'adresse réelle du flux
    if bouclage == 0:
      if self.fonctionsServeurRTSP.index('DESCRIBE') >= 0:
        bouclage = 1
        boucle = 0
        while bouclage == 1 and boucle < 5:
          bouclage = self.request_Describe ()
          boucle += 1
      else:
        print "demande de description impossible"
        self.nomFlux = self.demande
    
    # le dictionnaire self.paramServer est complété par le booléen Life_Line et 
    # la valeur du port du serveur servant à la ligne de vie. Ajout de la variable
    # self.session donnant la valeur de la session en cours.
    if bouclage == 0:
      if self.fonctionsServeurRTSP.index('SETUP') >= 0:
        bouclage = 1
        boucle = 0
        while bouclage == 1 and boucle < 5:
          bouclage = self.request_Setup ()
          boucle += 1
      else:
        print "demande de setup impossible"
    
    if bouclage == 0 :
      if self.fonctionsServeurRTSP.index('PLAY') >= 0:
        self.request_Play ()
      else:
        print "demande de lecture impossible"
    
    if bouclage == 1 :
      erreur (self.socketClientHTTP, 404, "Not Found", "The requested file %s was not found on this server" % self.url)
    
    print "fermeture socket serveur RTSP"
    self.SocketRTSP.close ()


## ------------------------------------------------------ ##
## -------------       HTTP Server        --------------- ##
## ------------------------------------------------------ ##

# cette classe correspond au serveur HTTP qui reçoit et gère les demande
# de clients (lecteur vidéo)
class HTTPServer (threading.Thread):
  
  #------------------------------------------------------------------
  # Intégration dans le __init__ des paramètres du serveur
  def __init__ ( self, host='', port=8083 , queueSize=1, plagePortsClient=[31330, 31340], showDebug=0):
    self.host = host
    self.port = port
    self.queueSize = queueSize
    self.plagePortsClient = plagePortsClient
    self.threads = []
    self.PortsClient = self.plagePortsClient [0]
    self.showDebug = showDebug
  
  #------------------------------------------------------------------
  # Définition des sockets correspondant à chacun des clients HTTP
  def open_socket ( self ):
    try:
      self.SocketServeur = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
      self.SocketServeur.setsockopt ( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
      self.SocketServeur.bind ( ( self.host, self.port ) )
      self.SocketServeur.listen ( self.queueSize )
    except socket.error, (value,message):
      if self.SocketServeur:
        self.SocketServeur.close()
      print "Ouverture Socket impossible :", message
      sys.exit(1)
  
  #------------------------------------------------------------------
  # Action effectuée par ce thread
  def run ( self ):
    self.open_socket ()
    ServeurHTTPrunning = True
    print "proxy démarré"
    print "version: %s" % _info_server
    print "en attente de client ..."
    
    try:
      while ServeurHTTPrunning:
        r, s, e = select.select([self.SocketServeur], [], [], 1.0)
        if r:
          client = HTTPClient ( self.threads, self.SocketServeur.accept (), self.PortsClient, self.showDebug )
          print "demande client recue"
          client.start ()
          self.PortsClient += 2
          if self.PortsClient >= self.plagePortsClient [1]:
            self.PortsClient = self.plagePortsClient [0]
          self.threads.append ( client )
    except socket.error:
      pass
    else :
      
      # Lors de la coupure de la boucle while (à définir), on arrête
      # le serveur
      print "fermeture du serveur et des clients"
      self.stop ()
  
  #------------------------------------------------------------------
  def stop ( self ):
    # on coupe le serveur et tous les threads
    print "fermeture serveur"
    self.SocketServeur.close ()
    for client in self.threads:
      print "fermeture client: %s" % client
      client.join ()
    print "fin serveur HTTP"

## ------------------------------------------------------ ##
## -------------       HTTP Client        --------------- ##
## ------------------------------------------------------ ##

# cette classe correspond à un client HTTP désirant recevoir un flux vidéo
class HTTPClient (threading.Thread):
  
  #------------------------------------------------------------------
  # Intégration dans le __init__ du thread des paramètres du socket
  def __init__ ( self, clients, ( client, address ), PortsClient, showDebug ):
    threading.Thread.__init__ ( self )
    self.clients = clients
    self.client = client
    self.address = address
    self.size = 1024
    self.PortsClient = PortsClient
    self.showDebug = showDebug
  
  #------------------------------------------------------------------
  # Action effectuée lorsque le proxy reçoit une demande
  def run ( self ):
    print 'Nouvelle connexion:', self.address [ 0 ] + ':' + str(self.address [ 1 ])
    try:
      data = self.client.recv(self.size)
    except Exception, err:
      if self.showDebug: print "erreur dans le client.recv"
      if self.showDebug: print err
      self.client.close()
    else:
      if self.showDebug: print "----\n", data, "----\n"
      if data:
        ligne0 = data.split ("\n") [ 0 ]
        (request, self.temp_url, proto) = ligne0.split (" ") [0:3]
        if request!="GET":
          print "ATTENTION : le player n'a pas envoyé de GET"
          erreur (self.client, 404, "Not Found", "The requested URL %s was not found on this server" % request)
        if proto[0:4]!="HTTP":
          print "ATTENTION : Ce n'est pas une requête HTTP"
        # on récupère l'information concernant le serveur désiré
        url_split = self.temp_url.split("/")
        if len(url_split) > 2:
          (serv, url) = url_split[1:3]
          if self.showDebug: print "Serveur:", serv
          if self.showDebug: print "Vidéo demandée:", url
          paramServer = RecupParamServer (serv)
          if paramServer:
            if self.showDebug: print "Fichier de configuration trouvé"
            if self.showDebug: print paramServer
            
            print "Lancement de la connection RTSP"
            clientRTSP = RTSPClient ( self.client, paramServer, url, self.PortsClient, self.showDebug )
            clientRTSP.run()
          else:
            print "Serveur inconnu :", serv
            erreur (self.client, 404, "Not Found", "The requested Server %s was not found on this server" % serv)
        else:
          if url_split[1] == 'showInfos':
            print "demande d'infos"
            showInfos (self.client, self.clients)
          elif url_split[1] == 'version':
            print "demande de version"
            showVersion (self.client)
          else:
            print "demande non gérée :", url_split
            erreur (self.client, 404, "Not Found", "The requested URL %s was not found on this server" % self.temp_url)
      else:
        self.client.close()
    print 'Connexion', self.address [ 0 ] + ':' + str(self.address [ 1 ]), 'terminée' + '\n'

#------------------------------------------------------------------

class principal:
  
  #------------------------------------------------------------------
  
  def arretAtexit (self):
    print "\n\n-----\nfermeture par atexit"
    try:
      self.ServeurHTTP.stop()
    except NameError:
      print "Serveur déjà arrêté"
    print "-----\n\n"
  
  #------------------------------------------------------------------
  
  def run(self):
    
    import atexit
    atexit.register(self.arretAtexit)
    
    options = RecupOptions()
    self.ServeurHTTP = HTTPServer (port = options['port'], \
      plagePortsClient = options['plagePortsClient'], \
      showDebug = options['showDebug'])
    try:
      self.ServeurHTTP.run ()
    except Exception, Excp:
      print "une exception a arrêté le serveur HTTP"
      print Excp


#------------------------------------------------------------------
# Ici, nous utilisons le nom "__main__" de l'expace de nommage global afin
# de déterminer si ce programme a été exécuté directement. En plaçant ce 
# code ici, nous pouvons facilement importer ce programme comme module. 

if __name__ == "__main__":
  M = principal()
  M.run()