import xbmc,xbmcgui
class main(xbmcgui.Window):
    def __init__(self):
        pass
    def play(self,chaine):
        xbmc.executebuiltin("XBMC.PlayMedia(http://127.0.0.1:8083/freeboxtv/%s)"%chaine)
        
    def onAction(self,action):
        if action == 10:
            self.close()
        elif action == 1:#fleche gauche
            o = overlay()
            o.show()
            del o
        
class overlay(xbmcgui.WindowDialog):
    def __init__(self):
        self.addControl(xbmcgui.ControlImage(50,56,196,26, 'background.png'))
        xbmc.sleep(3000)
        self.close()
        
m = main()
m.play("201")
xbmc.sleep(5000)
m.onAction(1)
m.doModal()
del m

