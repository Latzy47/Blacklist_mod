import BigWorld, game
import Keys
import functools
from gui import SystemMessages
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from gui.battle_control.avatar_getter import getPlayerName, getArena
from avatar_helpers import getAvatarDatabaseID
from adisp import async, process


mod_toggle = 3 #[0,1,2,3] fьr [aus, only arty, only HE, HE + teamBL]
#mit Config Datei kцnnen Zustдnde bleiben und sind nicht bei jedem Spielstart wieder auf Default

check_running = False

@async
@process
def wait(seconds, callback=None):
    BigWorld.callback(seconds, callback)

def teambl_key():
    global check_running
    check_running = True
    
    @proto_getter(PROTO_TYPE.MIGRATION)
    def proto():
        return None
    
    databID = getAvatarDatabaseID()
    
    @process
    def it_func():
        for (vehicleID, vData) in getArena().vehicles.iteritems():
            databaseID = vData['accountDBID']
            acc_name = vData['name']
            if databaseID != databID:
                proto.contacts.addIgnored(databaseID, acc_name)
                yield wait(1.1)

    it_func()
    
    return

def sendMessage(message, types):
    if BigWorld.player():  
        SystemMessages.pushMessage(message, types) 
    else: 
        BigWorld.callback(1, functools.partial(sendMessage, message, types)) 

def key_events_():
    global mod_toggle
    old_handler = game.handleKeyEvent
    def new_handler(event):
        global mod_toggle
        global check_running
        isDown, key, mods, isRepeat = game.convertKeyEvent(event)
        if isDown and mods == 4 and key == Keys.KEY_O:
            mod_toggle += 1
            if mod_toggle > 3:
                mod_toggle = 0
            if mod_toggle == 0:
                sendMessage("Mod disabled",SystemMessages.SM_TYPE.Warning)
            elif mod_toggle == 1:
                sendMessage("Only Cancer",SystemMessages.SM_TYPE.Warning)
            elif mod_toggle == 2:
                sendMessage("Only HE",SystemMessages.SM_TYPE.Warning)
            else:
                sendMessage("HE + blacklist Teams",SystemMessages.SM_TYPE.Warning)
        if mod_toggle == 1:
            pass #funktion auto arty einfьgen
            if isDown and mods == 4 and key == Keys.KEY_B:
                sendMessage("arty mit key",SystemMessages.SM_TYPE.Warning) #funktion arty mit key
        elif mod_toggle == 2:
            pass #funktion auto HE einfьgen
        elif mod_toggle == 3:
            pass #funktion auto HE einfьgen
            if isDown and mods == 4 and key == Keys.KEY_B:
                sendMessage("TeamBL mit key",SystemMessages.SM_TYPE.Warning)
                if check_running == False:
                    teambl_key()
                    check_running = False
        old_handler(event)
        return
    game.handleKeyEvent = new_handler
    return
key_events_()
