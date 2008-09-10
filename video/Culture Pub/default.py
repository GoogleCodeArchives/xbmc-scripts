"""
    Plugin for downloading scripts/plugins/skins from http://code.google.com/p/xbmc-addons/
"""

# main imports
import sys

# plugin constants
__plugin__ = "Culture Pub"
__author__ = "alexsolex"
__url__ = ""
__svn_url__ = ""
__credits__ = "Team XBMC"
__version__ = "1.0"


if ( __name__ == "__main__" ):
    if ( "download_url=" in sys.argv[ 2 ] ):
        from installerAPI import xbmcplugin_downloader as plugin
    else:
        from installerAPI import xbmcplugin_list as plugin
    plugin.Main()
