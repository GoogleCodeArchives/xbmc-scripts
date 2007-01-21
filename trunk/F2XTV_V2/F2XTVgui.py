import xbmc , xbmcgui
import sys
from os import path


ExtrasPath      =   sys.path[0] +  '\\datas\\'
sys.path.append(sys.path[0] + '\\libs')
ImagePath       = ExtrasPath + 'images'
SkinPath        = ExtrasPath + 'skins\\'

#actions keymap
ACTION_BACK         = [275, #pad : "back button"
                       216] #remote : "back" button
ACTION_B            = [257, #pad : Red B
                       221] #remote : skip-
ACTION_CONTEXT      = [261, #pad : white button
                       247]  #remote 'menu'
ACTION_Y            = [259, #pad : yellow Y
                       260, #pad : black button
                       223]  #remote : skip+
ACTION_EDIT         = [] #not used yet
#   key :       remote code :       pad code:
#   up          166                 210
#   down        167                 211
#   right       168                 213
#   left        169                 212
#   back        216                 275
#   select      11                  /
#   menu        247                 /
#   display     213                 /
#   skip+       223                 /
#   skip-       221                 /
#   forward     227                 /
#   reverse     226                 /
#   play        234                 /
#   stop        224                 /
#   pause       230                 /
#   title       229                 /
#   info        195                 /
#   0           207                 /
#   1           206                 /
#   2           205                 /
#   ...         ...                 /
#   9           198                 /
#   start       /                   274
#   white       /                   261
#   black       /                   260
#   RstickUp    /                   266
#   RstickDwn   /                   267
#   RstickLft   /                   268
#   RstickRght  /                   269
#   Rstickclic  /                   277
#   LstickUp    /                   280
#   LstickDwn   /                   281
#   LstickLft   /                   282
#   LstickRght  /                   283
#   Lstickclic  /                   276
#   Ltrigger    /                   278
#   Rtrigger    /                   279
#   A           /                   256
#   B           /                   257
#   X           /                   258
#   Y           /                   259

class main(xbmcgui.Window):
    def __init__(self):
        import guibuilder
        guibuilder.GUIBuilder(self,  SkinPath + 'F2XTV_PMIII.xml', ImagePath, debug=True)
        if (not self.SUCCEEDED): self.exitScript()
        else:
            for item in range(20):
                l = xbmcgui.ListItem('This is item #%d of 20 items' % (item +1,),
                                     'item# %d' % (item +1,),
                                     '',
                                     'defaultAlbumCover.png')
                self.controls[30].addItem(l)

    def exitScript(self):
        self.close()
        
    def onAction(self,action):
        if action == 1:
            self.close()

    def onControl(self,control):
        if control == self.bouton:
            pass



m = main()
if (m.SUCCEEDED): m.doModal()
del m
