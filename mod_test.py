# coding=utf-8
import BigWorld, game
import Keys
import functools
from gui import SystemMessages
from gui.battle_control.avatar_getter import getArena
from avatar_helpers import getAvatarDatabaseID
from adisp import async, process
from gui.battle_control.controllers import anonymizer_fakes_ctrl
from gui.battle_control.controllers import repositories
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
import BattleReplay
from messenger.m_constants import UserEntityScope
import logging
from messenger import MessengerEntry

_logger = logging.getLogger(__name__)
gui = MessengerEntry.g_instance.gui

mod_toggle = {'aus': 0, 'only arty': 1, 'only HE': 2, 'HE + teamBL': 3}
_mod_toggle = mod_toggle['HE + teamBL']  # [0,1,2,3] für [aus, only arty, only HE, HE + teamBL]
# mit Config Datei können Zustände bleiben und sind nicht bei jedem Spielstart wieder auf Default

check_running = False

@async
def wait(seconds, callback):
    BigWorld.callback(seconds, lambda: callback(None))

@process
def teambl_key():
    global check_running
    prebID = 0
    check_running = True
    arena = getattr(BigWorld.player(), 'arena', None)
    if arena is not None:
        sessionProvider = dependency.instance(IBattleSessionProvider)
        setup = repositories.BattleSessionSetup(avatar=BigWorld.player(), sessionProvider=sessionProvider)
        adding = anonymizer_fakes_ctrl.AnonymizerFakesController(setup)
        databID = getAvatarDatabaseID()

        vehID = getattr(BigWorld.player(), 'playerVehicleID', None)
        if vehID is not None and vehID in arena.vehicles:
            prebID = arena.vehicles[vehID]['prebattleID']

        for (vehicleID, vData) in getArena().vehicles.iteritems():
            databaseID = vData['accountDBID']
            av_ses_id = vData['avatarSessionID']
            _prebattleID = vData['prebattleID']
            user = adding.usersStorage.getUser(av_ses_id, scope=UserEntityScope.BATTLE)
            if user is not None:
                if databaseID != databID and not user.isFriend():
                    if prebID > 0 and prebID != _prebattleID:
                        adding.addBattleIgnored(av_ses_id)
                        yield wait(1.1)
                    elif prebID == 0:
                        adding.addBattleIgnored(av_ses_id)
                        yield wait(1.1)
            else:
                if databaseID != databID:
                    if prebID > 0 and prebID != _prebattleID:
                        adding.addBattleIgnored(av_ses_id)
                        yield wait(1.1)
                    elif prebID == 0:
                        adding.addBattleIgnored(av_ses_id)
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
                arena = getattr(BigWorld.player(), 'arena', None)
                if arena is not None:
                    gui.addClientMessage('Mod disabled', True)
                elif BigWorld.player():
                    sendMessage("Mod disabled", SystemMessages.SM_TYPE.Warning)
            elif _mod_toggle == mod_toggle['only arty']:
                arena = getattr(BigWorld.player(), 'arena', None)
                if arena is not None:
                    gui.addClientMessage('Only Cancer', True)
                elif BigWorld.player():
                    sendMessage("Only Cancer", SystemMessages.SM_TYPE.Warning)
            elif _mod_toggle == mod_toggle['only HE']:
                arena = getattr(BigWorld.player(), 'arena', None)
                if arena is not None:
                    gui.addClientMessage('Only HE', True)
                elif BigWorld.player():
                    sendMessage("Only HE", SystemMessages.SM_TYPE.Warning)
            else:
                arena = getattr(BigWorld.player(), 'arena', None)
                if arena is not None:
                    gui.addClientMessage('HE + blacklist Teams', True)
                elif BigWorld.player():
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
                if check_running == False:
                    teambl_key()
        old_handler(event)
        return

    game.handleKeyEvent = new_handler
    return

if not BattleReplay.isPlaying():
    key_events_()
