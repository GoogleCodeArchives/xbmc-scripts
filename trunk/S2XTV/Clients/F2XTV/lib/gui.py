# -*- coding: utf-8 -*-

import os , os.path
import xbmc , xbmcgui
import sys , traceback
CWD = os.getcwd()[:-1] # DOSSIER RACINE DU SCRIPT, SOIT OU EST LE DEFAULT.PY ( CAR GUI.PY EST EN IMPORTATION )
#sys.path.append(os.path.join(CWD, "lib")) # PAS BESOIN DE LE REINTRODIURE DEJA FAIT PAR LE DEFAULT.PY
import guibuilder
import controlfx as FX
import KeymapBuilder as KB

actionKey = KB.setKeymap(os.path.join(CWD, "Keymap.xml")) # NOTE: actionKey VA DEVENIR PROCHAINEMENT UN ( self )

def printLastError():
    ei = sys.exc_info()
    xbmcgui.Dialog().ok("Error !!!", str(ei[1]))
    traceback.print_exception(ei[0], ei[1], ei[2])

class S2XTVGUI(xbmcgui.Window):
    def __init__(self):
        self.setupGUI()
        if not self.SUCCEEDED: self.close()
        else:
            self.setupKeymap()
            self.setupVariables()
            
            self.curMainList = ["chaine 1","chaine 2","chaine 3"] # POUR EXEMPLE DES CHAINES
            self.fillMainList('chaine(s)')

    def setupGUI(self):
        current_skin = xbmc.getSkinDir()
        if not os.path.exists(os.path.join(CWD, 'skins', current_skin)): current_skin = 'default'
        skin_path = os.path.join(CWD, 'skins', current_skin)
        self.image_path = os.path.join(skin_path, 'media')
        if (self.getResolution() == 0 or self.getResolution() % 2): xml_file = 'skin_16x9.xml'
        else: xml_file = 'skin.xml'
        if not os.path.isfile(os.path.join(skin_path, xml_file)): xml_file = 'skin.xml'
        guibuilder.GUIBuilder(self, os.path.join(skin_path, xml_file), self.image_path, useDescAsKey=True,
            title="Free Multiposte TV", line1="Setting up script:", useLocal=True, debug=False)

    def setupKeymap(self):
        list = ["general"]
        [actionKey.getActionsList(section) for section in list]
        if len(actionKey.actionsList.keys()) == len(list):
            try:
                self.exitscripts = actionKey.actionsList["general"]['exitscripts']
            except: actionKey.hasNoBuild = True
        else: actionKey.hasNoBuild = True
        if actionKey.hasNoBuild:
            xbmcgui.Dialog().ok("Error", "Invalid Keymap.xml or function call", "Look for this error...", "And try again.")

    def setupVariables(self):
        self.toggleListControl()

    def toggleListControl(self):
        try:
            if xbmc.getCondVisibility(self.controls['Liste']['visible']):
                self.controls['Grande Liste']['control'].setEnabled(False)
                self.controls['Grande Liste']['control'].setVisible(False)
                self.controls['Liste']['control'].setEnabled(True)
                self.controls['Liste']['control'].setVisible(True)
                self.controls['Voir grande liste Button']['control'].setLabel("Voir: Liste")
            elif xbmc.getCondVisibility(self.controls['Grande Liste']['visible']):
                self.controls['Liste']['control'].setEnabled(False)
                self.controls['Liste']['control'].setVisible(False)
                self.controls['Grande Liste']['control'].setEnabled(True)
                self.controls['Grande Liste']['control'].setVisible(True)
                self.controls['Voir grande liste Button']['control'].setLabel("Voir: Liste 2")
        except: printLastError()

    def synchroniseList(self):
        if (self.getFocus() == self.controls['Liste']['control'])&(self.controls['Liste']['control'].getSelectedPosition() != -1):
            self.controls['Grande Liste']['control'].selectItem(self.controls['Liste']['control'].getSelectedPosition())
        elif (self.getFocus() == self.controls['Grande Liste']['control'])&(self.controls['Grande Liste']['control'].getSelectedPosition() != -1):
            self.controls['Liste']['control'].selectItem(self.controls['Grande Liste']['control'].getSelectedPosition())

    def fillMainList(self, namecountlabel=""):
        """ Fill the list depending on actual context """
        [self.controls['%s' % x]['control'].reset() for x in ['Liste', 'Grande Liste']]
        list = self.curMainList
        for item in list:
            for x in ['Liste', 'Grande Liste']:
                self.controls['%s' % x]['control'].addItem(
                    xbmcgui.ListItem(
                        label = item,
                        label2 = item,
                        thumbnailImage  = self.isValideTBN("")
                        )
                    )
        self.setCountLabel(namecountlabel)

    def isValideTBN(self, tbn):
        if os.path.isfile(tbn): tbn = tbn
        elif self.getFocus() == self.controls['Parametres Button']['control']: tbn = "DefaultPlaylistBig.png"
        else: tbn = "defaultVideoBig.png"
        return tbn

    def setCountLabel(self, namelabel=""):
        if namelabel != "":
            self.controls['Liste Count Label']['control'].setLabel('%d %s' % (self.controls['Liste']['control'].size(), namelabel))
        else:
            self.controls['Liste Count Label']['control'].setLabel('')

    def onAction(self, action):
        if actionKey.hasNoBuild: self.close()
        else:
            self.synchroniseList()
            BUTTONCODE = action.getButtonCode()
            if self.exitscripts.has_key(BUTTONCODE):
                self.close()

    def onControl(self, control):
        if control == self.controls['Voir grande liste Button']['control']:
            if xbmc.getCondVisibility(self.controls['Liste']['visible']):
                self.controls['Liste']['visible'] = "false"
                self.controls['Grande Liste']['visible'] = "true"
            elif xbmc.getCondVisibility(self.controls['Grande Liste']['visible']):
                self.controls['Liste']['visible'] = "true"
                self.controls['Grande Liste']['visible'] = "false"
            self.toggleListControl()

        elif control == self.controls['Chaines Button']['control']:
            self.controls['Title Label']['control'].setLabel('Chaines TV')
            self.curMainList = ["chaine 1","chaine 2","chaine 3"] # POUR EXEMPLE DES CHAINES
            self.fillMainList('chaine(s)')

        elif control == self.controls['Programmations Button']['control']:
            self.controls['Title Label']['control'].setLabel("Programmations d'enregistrements")
            self.curMainList = ["Programmation 1","Programmation 2","Programmation 3"] # POUR EXEMPLE DES PROGRAMMATIONS
            self.fillMainList('Programmation(s)')

        elif control == self.controls['Enregistrements Button']['control']:
            self.controls['Title Label']['control'].setLabel('Enregistrements')
            self.curMainList = ["Enregistrement 1","Enregistrement 2","Enregistrement 3"] # POUR EXEMPLE DES ENREGISTREMENTS
            self.fillMainList('Enregistrement(s)')

        elif control == self.controls['Parametres Button']['control']:
            self.controls['Title Label']['control'].setLabel('Paramètres')
            self.curMainList = ["Paramètre 1","Paramètre 2","Paramètre 3"] # POUR EXEMPLE DES PARAMÈTRES
            self.fillMainList('Paramètre(s)')

        else:
            controlsLits = ['Liste', 'Grande Liste']
            for ctrl in controlsLits:
                if control == self.controls['%s' % ctrl]['control']:
                    print ctrl
                    print self.controls['%s' % ctrl]['control'].getSelectedItem().getLabel()

if __name__ == "__main__":
    try:
        w = S2XTVGUI()
        if w.SUCCEEDED:
            w.doModal()
            del w
    except: printLastError()
