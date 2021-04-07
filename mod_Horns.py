# -*- coding: utf-8 -*-
import Keys
from PYmodsCore import PYmodsConfigInterface, checkKeys
from PYmodsCore.delayed.support import ConfigInterface as CI
from PYmodsCore.config.interfaces.PyMods import PYmodsSettingContainer
from gui.modsListApi import g_modsListApi
from messenger.proto.xmpp.xmpp_constants import CONTACT_LIMIT


class ConfigInterface(PYmodsConfigInterface):
    def __init__(self):
        super(ConfigInterface, self).__init__()

    def init(self):
        self.ID = 'X_Auto_BL'
        self.version = '1.31 (01.04.2021)'
        self.defaultKeys = {'hotkey1': [Keys.KEY_O, [Keys.KEY_LALT, Keys.KEY_RALT]],  # switch modes
                            'hotkey2': [Keys.KEY_B, [Keys.KEY_LALT, Keys.KEY_RALT]],  # key function
                            'hotkey3': [Keys.KEY_C, [Keys.KEY_LALT, Keys.KEY_RALT]],  # enable clear
                            'hotkey4': [Keys.KEY_X, [Keys.KEY_LALT, Keys.KEY_RALT]]}  # start clear
        self.data = {'enabled': True,
                     'ignored': 1000000,
                     'extended': True,
                     'friends': 1000000,
                     'hotkey1': self.defaultKeys['hotkey1'],
                     'hotkey2': self.defaultKeys['hotkey2'],
                     'hotkey3': self.defaultKeys['hotkey3'],
                     'hotkey4': self.defaultKeys['hotkey4']}
        self.i18n = {
            'UI_description': 'Extended automated blacklist',
            'UI_setting_ignored_text': 'Number blacklist',
            'UI_setting_ignored_tooltip': 'This number shows the length of your blacklist.',
            'UI_setting_extended_text': 'Extend lists',
            'UI_setting_extended_tooltip': 'This enables/disables the extention of the blacklist'
                                           ' and friendlist.\n'
                                           'Restarting the game is required to take effect.',
            'UI_setting_friends_text': 'Number friendlist',
            'UI_setting_friends_tooltip': 'This number shows the length of your friendlist.',
            'UI_setting_hotkey1_text': 'Switch modes',
            'UI_setting_hotkey1_tooltip': 'Pressing this hotkey will switch between modes.',
            'UI_setting_hotkey2_text': 'Blacklist key',
            'UI_setting_hotkey2_tooltip': 'Pressing this hotkey will blacklist your desired tanks.',
            'UI_setting_hotkey3_text': 'Clear enable',
            'UI_setting_hotkey3_tooltip': 'Pressing this hotkey will enable/disable clearing your blacklist.',
            'UI_setting_hotkey4_text': 'Clear start',
            'UI_setting_hotkey4_tooltip': 'Pressing this hotkey will start clearing your blacklist.'}
        super(ConfigInterface, self).init()
        self.containerClass = MyPYmodsSettingContainer
        self.modSettingsID = 'x_auto_bl'
        self.modsGroup = 'xAutoBl'
        self.author = 'by FvckingLatzyMan'

    def createTemplate(self):
        return {'modDisplayName': self.i18n['UI_description'],
                'enabled': self.data['enabled'],
                'column1': [self.tb.createSlider('ignored', 5000, 1000000, 5000),
                            self.tb.createSlider('friends', 5000, 1000000, 5000),
                            self.tb.createHotKey('hotkey1')],
                'column2': [self.tb.createControl('extended'),
                            self.tb.createHotKey('hotkey2'),
                            self.tb.createHotKey('hotkey3'),
                            self.tb.createHotKey('hotkey4')]}

    def onButtonPress(self, vName, value):
        pass

    def onMSADestroy(self):
        self.readCurrentSettings()

    def onHotkeyPressed(self, event):
        if event.isKeyDown() and checkKeys(self.data['hotkey2']):
            print 'Test mod_Horns.py ###################'


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

config0 = ConfigInterface()


if config0.data['extended']:
    CONTACT_LIMIT.ROSTER_MAX_COUNT = config0.data['friends']
    CONTACT_LIMIT.BLOCK_MAX_COUNT = config0.data['ignored']
