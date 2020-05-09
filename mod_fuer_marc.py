# coding=utf-8

import BigWorld

import BattleReplay
from adisp import async, process
from avatar_helpers import getAvatarDatabaseID
from gui.battle_control.avatar_getter import getArena
from gui.battle_control.controllers import anonymizer_fakes_ctrl
from gui.battle_control.controllers import repositories
from helpers import dependency
from messenger.m_constants import UserEntityScope
from skeletons.gui.battle_session import IBattleSessionProvider


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
        if arena.bonusType != 1:
            return
        yield wait(30)
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
                if databaseID != databID and not (user.isFriend() or user.isIgnored()):
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



if not BattleReplay.isPlaying() and not check_running:
    teambl_key()
