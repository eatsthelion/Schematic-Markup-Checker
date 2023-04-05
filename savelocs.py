import os

FILEDRIVE   = "G:"
SAVEDRIVE   = r"G:"
OUTPUTLOC   = r'G:\pythonprograms\Database'

ASSETLOC    = r"G:\USERS\Ethan" #change this when working from home
if not os.path.exists(ASSETLOC):
    ASSETLOC = r"G:\My Drive\code\oecworkspace\assets"

# JSON and TXT Files
VERSIONFILE = os.path.join(ASSETLOC,"versionfile.txt")
USERFILE    = os.path.join(ASSETLOC,"oec_users.json")
ASSETSFILE  = os.path.join(ASSETLOC,"oec_assets_and_images.json")
USERJSON    = os.path.join(ASSETLOC,"oec_users.json")
COMPJSON    = os.path.join(ASSETLOC,"oec_comp.json")
ALERTJSON   = os.path.join(ASSETLOC,'oec_notifications_and_alerts.json')

# Images
IMGLOC      = os.path.join(ASSETLOC,'Images')
BACKGROUND  = os.path.join(IMGLOC,"pattern3.jpg")
INFOSYMBOL  = os.path.join(IMGLOC,"infosymbol3.png")
LOGO        = os.path.join(ASSETLOC,"oeclogo2.ico")
LOGOJPG     = os.path.join(ASSETLOC,"oeclogo2.jpg")
TKCOLORS    = r"O:\pythonprograms\Database\Images\tkcolors.png"
SETTINGSYM  = r"O:\pythonprograms\Database\Images\settings_symbol.png"

POPPLER=r"\poppler-21.03.0\Library\bin"

def programSaveOutput(paths,groucho=True):
    if len(paths)<1: return
    if groucho: saveoutput = os.path.join(SAVEDRIVE,paths[0])
    else: saveoutput=""
    for path in paths[1:]:
        saveoutput = os.path.join(saveoutput,path)
        if not os.path.exists(saveoutput):
            os.makedirs(saveoutput)
    return saveoutput