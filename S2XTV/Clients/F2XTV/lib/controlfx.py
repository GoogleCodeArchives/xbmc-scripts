
import glob
import random , time
import xbmc, xbmcgui

glob.FX_IsAlive = False

class ControlFX:
    def __init__(self, win, control, keeplayout=False, replacelayout=(False, 0)):
        if not glob.FX_IsAlive:
            self.win = win
            self.win.control = control
            self.widthLayout = self.heightLayout = self.posxyLayout = None
            self.replaceLayout = replacelayout
            if keeplayout:
                self.widthLayout = self.win.control.getWidth()
                self.heightLayout = self.win.control.getHeight()
                self.posxyLayout = self.win.control.getPosition()

    def setDefaultLayout(self, xy=0, w=0, h=0):
        if self.replaceLayout[0]:
            xbmc.sleep(int(self.replaceLayout[1]*1000))
        if self.widthLayout and self.heightLayout and self.posxyLayout:
            if xy: self.win.control.setPosition(self.posxyLayout[0], self.posxyLayout[1])
            if w: self.win.control.setWidth(self.widthLayout)
            if h: self.win.control.setHeight(self.heightLayout)

    def slide(self, start, end, tm=max(1, 10), img=None, img2=None):
        if glob.FX_IsAlive: return
        glob.FX_IsAlive = True
        endx, endy = end
        startx, starty = start
        diffX = (startx - endx)
        diffY = (starty - endy)
        if img2: self.win.control.setImage(img2)
        for pos in range(tm, -1, -1):
            elmt_stepX = float(diffX)/float(tm)
            elmt_stepY = float(diffY)/float(tm)
            deltaX     = int(pos*elmt_stepX)
            deltaY     = int(pos*elmt_stepY)
            self.win.control.setPosition(endx + deltaX, endy + deltaY)
            time.sleep(0.01)
        if img: self.win.control.setImage(img)
        glob.FX_IsAlive = False

    def slideRandom(self, offset=0, tm=max(10, 100)):
        if glob.FX_IsAlive: return
        glob.FX_IsAlive = True
        ctr = {"w": int(self.win.getWidth())/2, "h": int(self.win.getHeight())/2}
        posx, posy = (random.choice(range(offset, ctr["w"]-offset)), random.choice(range(offset, ctr["h"]-offset)))
        startposx, startposy = self.win.control.getPosition()
        diffX = (startposx - posx)
        diffY = (startposy - posy)
        for pos in range(tm, -1, -1):
            elmt_stepX = float(diffX)/float(tm)
            elmt_stepY = float(diffY)/float(tm)
            deltaX     = int(pos*elmt_stepX)
            deltaY     = int(pos*elmt_stepY)
            self.win.control.setPosition(posx + deltaX, posy + deltaY)
            time.sleep(0.01)
        glob.FX_IsAlive = False

    def zoomOutPCT(self, pct=10, replace=False):
        if glob.FX_IsAlive: return
        glob.FX_IsAlive = True
        width = self.win.control.getWidth()
        height = self.win.control.getHeight()
        zwidth = width * (1 + (float(pct) / 100))
        zheight = height * (1 + (float(pct) / 100))
        widthOffset = int((zwidth - width) / 2)
        heightOffset = int((zheight - height) / 2)
        x, y = self.win.control.getPosition()
        x -= widthOffset
        y -= heightOffset
        self.win.control.setPosition(x, y)
        self.win.control.setWidth(int(zwidth))
        self.win.control.setHeight(int(zheight))
        if replace: self.setDefaultLayout(1,1,1)
        glob.FX_IsAlive = False

    def zoomInPCT(self, pct=10, replace=False):
        if glob.FX_IsAlive: return
        glob.FX_IsAlive = True
        width = self.win.control.getWidth()
        height = self.win.control.getHeight()
        zwidth = width * (1 + (float(-pct) / 100))
        zheight = height * (1 + (float(-pct) / 100))
        widthOffset = int((zwidth - width) / 2)
        heightOffset = int((zheight - height) / 2)
        x, y = self.win.control.getPosition()
        x -= widthOffset
        y -= heightOffset
        self.win.control.setPosition(x, y)
        self.win.control.setWidth(int(zwidth))
        self.win.control.setHeight(int(zheight))
        if replace: self.setDefaultLayout(1,1,1)
        glob.FX_IsAlive = False
