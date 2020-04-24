import BigWorld, game
import Keys
import functools
from gui import SystemMessages
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from gui.battle_control.avatar_getter import getPlayerName, getArena
from avatar_helpers import getAvatarDatabaseID
from adisp import async, process
from messenger.proto.events import g_messengerEvents
from messenger.proto.interfaces import IChatError

mod_toggle = {'aus': 0, 'only arty': 1, 'only HE': 2, 'HE + teamBL': 3}
_mod_toggle = mod_toggle['HE + teamBL']  # [0,1,2,3] für [aus, only arty, only HE, HE + teamBL]
# mit Config Datei können Zustände bleiben und sind nicht bei jedem Spielstart wieder auf Default

check_running = False

@proto_getter(PROTO_TYPE.MIGRATION)
def proto():
    return None

@async
def wait(seconds, callback):
    BigWorld.callback(seconds, lambda: callback(None))

class MyError(IChatError):
    def getMessage(self):
        return 'Hello World'

@process
def teambl_key():
    global check_running
    check_running = True

    databID = getAvatarDatabaseID()

    for (vehicleID, vData) in getArena().vehicles.iteritems():
        databaseID = vData['accountDBID']
        acc_name = vData['name']
        if databaseID != databID:
            if databaseID == 0:
                pass
            else:
                proto.contacts.addIgnored(databaseID, acc_name)
                yield wait(1.1)
    check_running = False


def sendMessage(message, types):
    if BigWorld.player():
        SystemMessages.pushMessage(message, types)
    else:
        BigWorld.callback(1, functools.partial(sendMessage, message, types))


def key_events_():
    global mod_toggle
    global _mod_toggle
    old_handler = game.handleKeyEvent

    def new_handler(event):
        global mod_toggle
        global check_running
        global _mod_toggle
        isDown, key, mods, isRepeat = game.convertKeyEvent(event)
        if isDown and mods == 4 and key == Keys.KEY_O:
            _mod_toggle += 1
            if _mod_toggle > 3:
                _mod_toggle = 0
            if _mod_toggle == mod_toggle['aus']:
                sendMessage("Mod disabled", SystemMessages.SM_TYPE.Warning)
            elif _mod_toggle == mod_toggle['only arty']:
                sendMessage("Only Cancer", SystemMessages.SM_TYPE.Warning)
            elif _mod_toggle == mod_toggle['only HE']:
                sendMessage("Only HE", SystemMessages.SM_TYPE.Warning)
            else:
                sendMessage("HE + blacklist Teams", SystemMessages.SM_TYPE.Warning)
        if _mod_toggle == mod_toggle['only arty']:
            pass  # funktion auto arty einfügen
            if isDown and mods == 4 and key == Keys.KEY_B:
                sendMessage("arty mit key", SystemMessages.SM_TYPE.Warning)  # funktion arty mit key
        elif _mod_toggle == mod_toggle['only HE']:
            pass  # funktion auto HE einfügen
        elif _mod_toggle == mod_toggle['HE + teamBL']:
            pass  # funktion auto HE einfügen
            if isDown and mods == 4 and key == Keys.KEY_B:
                g_messengerEvents.onErrorReceived(MyError())
                if check_running == False:
                    teambl_key()
        old_handler(event)
        return

    game.handleKeyEvent = new_handler
    return


key_events_()
