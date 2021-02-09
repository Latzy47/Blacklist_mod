# -*- coding: utf-8 -*-
import BigWorld
import Keys
import Vehicle
import traceback
from PYmodsCore import Sound, PYmodsConfigInterface, pickRandomPart, sendChatMessage, checkKeys, Analytics
from functools import partial
from gui.battle_control import avatar_getter
from PYmodsCore.delayed.support import ConfigInterface as CI
from PYmodsCore.config.interfaces.PyMods import PYmodsSettingContainer, PYmodsConfBlockInterface
from gui.modsListApi import g_modsListApi


class ConfigInterface(PYmodsConfigInterface):
    def __init__(self):
        self.lastRandID = {'ally': -1, 'enemy': -1, 'default': -1}
        self.hornSoundEvent = None
        self.soundCallback = None
        super(ConfigInterface, self).__init__()

    def init(self):
        self.ID = 'X_Auto_BL'
        self.version = '1.31 (%(file_compile_date)s)'
        self.defaultKeys = {'hotkey': [Keys.KEY_G]}
        self.data = {'enabled': True,
                     'mode': 3,
                     'ignored': 1000000,
                     'extended': True,
                     'friends': 1000000}
        self.i18n = {
            'UI_description': 'Extended automated blacklist',
            'UI_setting_mode_text': 'Current mode',
            'UI_setting_mode_tooltip': 'This selects and shows the current mode.',
            'UI_setting_ignored_text': 'Number blacklist',
            'UI_setting_ignored_tooltip': 'This number shows how big your blacklist is.',
            'UI_setting_extended_text': 'Extend lists',
            'UI_setting_extended_tooltip': 'This enables/disables the extention of the blacklist and friendlist.\n'
                                           'Restarting the game is required to take effect.',
            'UI_setting_friends_text': 'Number friendlist',
            'UI_setting_friends_tooltip': 'This number shows how big your friendlist is.'}
        super(ConfigInterface, self).init()
        self.containerClass = MyPYmodsSettingContainer

    def createTemplate(self):
        return {'modDisplayName': self.i18n['UI_description'],
                'enabled': self.data['enabled'],
                'column1': [self.tb.createSlider('ignored', 0, 1000000, 5000), self.tb.createSlider('friends', 0, 1000000, 5000)],
                'column2': [self.tb.createControl('extended'), self.tb.createOptions('mode', [0, 1, 2, 3])]}

    def onButtonPress(self, vName, value):
        pass

    def onMSADestroy(self):
        self.readCurrentSettings()

    def onHotkeyPressed(self, event):
        pass
        # if avatar_getter.isVehicleAlive() and event.isKeyDown() and checkKeys(self.data['hotkey']):


class MyPYmodsSettingContainer(PYmodsSettingContainer):
    def init(self):
        super(MyPYmodsSettingContainer, self).init()
        self.i18n = {
            'modsListApiName': "Blacklist mod",
            'modsListApiDescription': "Extended automated blacklist modification settings",
            'windowTitle': "Blacklist mod settings",
            'enableButtonTooltip': '{HEADER}ON/OFF{/HEADER}{BODY}Enable/disable this mod{/BODY}'}


# disable his patreon
class NewCI(CI):
    def createTemplate(self):
        return {}


# not clickable
g_modsListApi.updateModification('modsSettingsApi', enabled=False)

_config = ConfigInterface()
