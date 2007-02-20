
import os , os.path
from sys import exc_info
from xml.dom.minidom import parse
from traceback import print_exception
try:
    from xbmcgui import Dialog
except ImportError: pass

ignoreNodeName = ['#cdata-section', '#comment', '#document', '#document-fragment', '#text']

def toPrintOut(m1=None, m2=None, m3=None, m4=None):
    if m1: print str(m1)
    if m2: print str(m2)
    if m3: print str(m3)
    if m4: print str(m4)

class keyboardLayout:
    def __init__(self):
        #List IKB is based wiki, For infos keyboard layout
        #url = http://en.wikipedia.org/wiki/Keyboard_layout
        self.IKB = {
            #Keyboard layouts for Roman script
            #QWERTY
            1 : "Canadian French",
            2 : "Canadian Multilingual Standard",
            3 : "Portuguese (Portugal)",
            4 : "Portuguese (Brazil)",
            5 : "Norwegian",
            6 : "Danish",
            7 : "Italian",
            8 : "UK and Ireland",
            9 : "US",
            10 : "US-International",
            #QWERTZ
            11 : "Germany and Austria (but not Switzerland)",
            12 : "Swiss German, Swiss French, Liechtenstein, Luxembourg",
            13 : "Romanian in Romania and Moldova",
            14 : "Hungary",
            15 : "Poland",
            #AZERTY
            16 : "French",
            17 : "Belgian",
            #QZERTY
            #The QZERTY layout is used mostly, if not exclusively, in Italy, where it is very common on typewriters.
            18 : "QZERTY",
            #Dvorak and others
            19 : "QWERTY-based",
            #Turkish
            20 : "QWERTY and Dvorak-based",
            21 : "Dvorak-based",
            22 : "Original",
            #Keyboard layouts for non-Roman alphabetic scripts
            23 : "Arabic",
            24 : "Armenian",
            25 : "Greek",
            26 : "Hebrew",
            27 : "Russian",
            28 : "Bulgarian",
            29 : "Devanagari",
            30 : "Thai",
            31 : "Khmer",
            #East Asian languages
            #Chinese
            32 : "Chinese (traditional)",
            33 : "Chinese (simpified)",
            #Hangul (for Korean)
            34 : "Dubeolsik",
            35 : "Sebeolsik 390",
            36 : "Sebeolsik Final",
            37 : "Sebeolsik Noshift",
            #Japanese
            38 : "Japanese"
            }
        self.inKeymap = []

class setKeymap:
    def __init__(self, path=""):
        self.xml = path
        self.doc = self.xml
        self.hasNoBuild = False
        self.printingList = None
        self.actionsList = {}
        self.infokeyboard = None
        self.ikbLayout = keyboardLayout()

    def getActionsList(self, category="", printList=False):
        self.printingList = printList
        try: self.getActions(category)
        except:
            ei = exc_info()
            print_exception(ei[0], ei[1], ei[2])
            self.hasNoBuild = True
        if self.hasNoBuild:
            # Is real error or User called hasNoBuild
            self.actionsList = {}
        if self.printingList: toPrintOut(self.actionsList)

    def has_Attribute(self, name, attr="ikb"):
        if name.hasAttribute(attr):
            value = name.getAttribute(attr)
            if not value in self.ikbLayout.inKeymap:
                self.ikbLayout.inKeymap.append(value)
            if value == self.infokeyboard:
                if self.printingList: toPrintOut(name.nodeName+" has condition "+value)
                return True
            else: return False
        else: return True

    def getActions(self, category):
        self.doc = parse(self.xml)
        for child in self.doc.childNodes:
            if (child.nodeName != "keymap")&(child.nodeName not in ignoreNodeName):
                print "Invalid Tag Name:", child.nodeName
        self.doc = child
        for child in self.doc.childNodes:
            if child.nodeName == "infokeyboard":
                self.infokeyboard = [info.data for info in child.childNodes][0]
                if self.printingList: toPrintOut("infokeyboard = "+self.ikbLayout.IKB[int(self.infokeyboard)])
            if child.nodeName == category:
                if self.has_Attribute(child):
                    self.categoryList = {}
                    for action in child.childNodes:
                        if not action.nodeName in ignoreNodeName:
                            if self.has_Attribute(action):
                                self.readActions(action, category)
                                if self.printingList: toPrintOut("Category list "+child.nodeName)

    def readActions(self, action, category):
        list = {}
        for item in action.childNodes:
            if not item.nodeName in ignoreNodeName:
                if self.has_Attribute(item):
                    code, type, desc = (item.getAttribute("code"), item.getAttribute("type"), [node.data for node in item.childNodes][0])
                    list[int(code)] = desc
                    if self.printingList: toPrintOut("Action ID "+code+" "+type+" "+desc)
        if list != {}:
            self.categoryList[action.nodeName] = list
            self.actionsList[category] = self.categoryList

    def changeKeyboard(self, value=None):
        try:
            if not value:
                list = []
                [list.append(self.ikbLayout.IKB[int(ikb)]) for ikb in self.ikbLayout.inKeymap]
                selected = Dialog().select("Availability of keyboard:", list)
                if selected != -1:
                    for k in self.ikbLayout.IKB.items():
                        if k[1] == list[selected]: value = str(k[0])
            if value:
                for node in self.doc.getElementsByTagName("infokeyboard")[0].childNodes:
                    if (node.nodeValue != value)&(self.ikbLayout.IKB.has_key(int(value))):
                        node.nodeValue = value
                    else: value = None
            if value:
                #if os.path.exists(self.xml): os.unlink(self.xml)
                f = open(self.xml, "w")
                self.doc.writexml(f)
                f.close()
                if self.printingList: toPrintOut("Keyboard changed: "+self.ikbLayout.IKB[int(value)])
                return True
            else: return False
        except:
            ei = exc_info()
            print_exception(ei[0], ei[1], ei[2])
            return False

# TEST YOUR KEYMAP.XML
if __name__ == "__main__":
    PATH = "Keymap.xml" #""" PC """
    if not os.path.exists(PATH):
        PATH = os.path.join(os.getcwd()[:-1], "Keymap.xml") #""" XBox """
    actionKey = setKeymap(PATH)
    # getActionsList( category[, printList=False])
    # category : Tag for group actions
    # printList : [OPT] Infos for testing Keymap.xml
    list = ["general", "extra", "extra2"]
    [actionKey.getActionsList(category) for category in list]
    # if you want test or fake error for build and import in default.py set True at variable.hasNoBuild
    # actionKey.hasNoBuild = True
    # Call or print  your full List actions
    if actionKey.hasNoBuild: print "No build of Keymap.xml!!!"
    else:
        print "Availability of keyboard:"
        for ikb in actionKey.ikbLayout.inKeymap:
            print "-", str(actionKey.ikbLayout.IKB[int(ikb)])
        # changeKeyboard([value]) and this funtion return True or False
        # value, [OPT] example: ( "1" or '1' ) and not 1.
        # NOTE: value not set a default xbmcgui.Dialog().select( ... ) is apply.
        if actionKey.changeKeyboard():
            # reload your actions in Keymap.xml
            print "Keyboard changed: "
            [actionKey.getActionsList(category, True) for category in list]
        else:
            print "Full List =", str(actionKey.actionsList)
            print "Unpacked Full List"
            for category in actionKey.actionsList:
                print "-", category
                for actions in actionKey.actionsList[category]:
                    print "--", actions
                    for button in actionKey.actionsList[category][actions]:
                        print "---", button

        # Test code of function getButtonCode() in def onAction(self, action):
        fakeCode = 275
        exitscripts = actionKey.actionsList["general"]["exitscripts"]
        replay = actionKey.actionsList["extra"]["replay"]
        if exitscripts.has_key(fakeCode): print "code: %d = exit scripts" % fakeCode
        elif replay.has_key(fakeCode): print "code: %d = replay" % fakeCode
        else: print "code: %d not in Keymap.xml" % fakeCode
