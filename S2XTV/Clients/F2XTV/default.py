
import sys, os, traceback
sys.path.append(os.path.join(sys.path[0], 'lib'))
import gui

if __name__ == '__main__':
    try:
        ui = gui.S2XTVGUI()
        if ui.SUCCEEDED:
            ui.doModal()
            del ui
    except:
        traceback.print_exc()
