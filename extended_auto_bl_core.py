from constants import ARENA_BONUS_TYPE, ARENA_PERIOD
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
import json
import os


class SHELL_TYPES(object):
    HOLLOW_CHARGE = 'HOLLOW_CHARGE'
    HIGH_EXPLOSIVE = 'HIGH_EXPLOSIVE'
    ARMOR_PIERCING = 'ARMOR_PIERCING'
    ARMOR_PIERCING_HE = 'ARMOR_PIERCING_HE'
    ARMOR_PIERCING_CR = 'ARMOR_PIERCING_CR'
    SMOKE = 'SMOKE'


class GlobalVars(object):
    def __init__(self):
        self.all_modes = []
        self.active_idx = 0
        self.active_mode = self.all_modes[self.active_idx] if self.all_modes else None
        self.ignored = 1000000
        self.friends = 1000000
        self.extended = False
        self.config_data = {}
        self.check_running = False
        self.id_list = []
        self.enable_clear = False
        self.mode_data = {'mode0': {'name': 'Mod disabled', 'shell_AP': False, 'shell_APCR': False,
                                    'shell_HEAT': False, 'shell_HE': False, 'random': False,
                                    'random_key': False, 'ranked': False, 'ranked_key': False,
                                    'other_modes': False, 'other_modes_key': False,
                                    'light': False, 'light_key': False, 'med': False, 'med_key': False,
                                    'heavy': False, 'heavy_key': False, 'td': False, 'td_key': False,
                                    'spg': False, 'spg_key': False, 'tanklist': [None],
                                    'auto_key_pressed': False, 'wheeled': False, 'wheeled_key': False},
                          'mode1': {'name': 'Only arty', 'shell_AP': False, 'shell_APCR': False,
                                    'shell_HEAT': False, 'shell_HE': False, 'random': True,
                                    'random_key': True, 'ranked': True, 'ranked_key': True,
                                    'other_modes': True, 'other_modes_key': True,
                                    'light': False, 'light_key': False, 'med': False, 'med_key': False,
                                    'heavy': False, 'heavy_key': False, 'td': False, 'td_key': False,
                                    'spg': True, 'spg_key': True, 'tanklist': [None],
                                    'auto_key_pressed': False, 'wheeled': False, 'wheeled_key': False},
                          'mode2': {'name': 'Only HE', 'shell_AP': False, 'shell_APCR': False,
                                    'shell_HEAT': False, 'shell_HE': True, 'random': True,
                                    'random_key': False, 'ranked': True, 'ranked_key': True,
                                    'other_modes': True, 'other_modes_key': False,
                                    'light': False, 'light_key': False, 'med': False, 'med_key': False,
                                    'heavy': False, 'heavy_key': False, 'td': False, 'td_key': False,
                                    'spg': False, 'spg_key': False, 'tanklist': [None],
                                    'auto_key_pressed': False, 'wheeled': False, 'wheeled_key': False},
                          'mode3': {'name': 'HE + blacklist teams', 'shell_AP': False, 'shell_APCR': False,
                                    'shell_HEAT': False, 'shell_HE': True, 'random': True,
                                    'random_key': True, 'ranked': True, 'ranked_key': True,
                                    'other_modes': True, 'other_modes_key': True,
                                    'light': False, 'light_key': False, 'med': False, 'med_key': False,
                                    'heavy': False, 'heavy_key': False, 'td': False, 'td_key': False,
                                    'spg': False, 'spg_key': False, 'tanklist': [None],
                                    'auto_key_pressed': False, 'wheeled': False, 'wheeled_key': False}}

    def convert_to_schematic(self):
        mode_lst = [{}, {}, {}, {}]
        for mode, key in zip(mode_lst, self.mode_data.values()):
            mode['name'] = key['name']
            mode['shell_AP'] = None if not key['shell_AP'] else SHELL_TYPES.ARMOR_PIERCING
            mode['shell_APCR'] = None if not key['shell_APCR'] else SHELL_TYPES.ARMOR_PIERCING_CR
            mode['shell_HEAT'] = None if not key['shell_HEAT'] else SHELL_TYPES.HOLLOW_CHARGE
            mode['shell_HE'] = None if not key['shell_HE'] else SHELL_TYPES.HIGH_EXPLOSIVE
            mode['random'] = None if not key['random'] else ARENA_BONUS_TYPE.REGULAR
            mode['random_key'] = None if not key['random_key'] else ARENA_BONUS_TYPE.REGULAR
            mode['ranked'] = (None,) if not key['ranked'] else (ARENA_BONUS_TYPE.RANKED,)
            mode['ranked_key'] = (None,) if not key['ranked_key'] else (ARENA_BONUS_TYPE.RANKED,)
            mode['other_modes'] = (None,) if not key['other_modes'] else SchematicForMode.other_game_modes
            mode['other_modes_key'] = (None,) if not key['other_modes_key'] else SchematicForMode.other_game_modes
            mode['light'] = None if not key['light'] else VEHICLE_CLASS_NAME.LIGHT_TANK
            mode['light_key'] = None if not key['light_key'] else VEHICLE_CLASS_NAME.LIGHT_TANK
            mode['med'] = None if not key['med'] else VEHICLE_CLASS_NAME.MEDIUM_TANK
            mode['med_key'] = None if not key['med_key'] else VEHICLE_CLASS_NAME.MEDIUM_TANK
            mode['heavy'] = None if not key['heavy'] else VEHICLE_CLASS_NAME.HEAVY_TANK
            mode['heavy_key'] = None if not key['heavy_key'] else VEHICLE_CLASS_NAME.HEAVY_TANK
            mode['td'] = None if not key['td'] else VEHICLE_CLASS_NAME.AT_SPG
            mode['td_key'] = None if not key['td_key'] else VEHICLE_CLASS_NAME.AT_SPG
            mode['spg'] = None if not key['spg'] else VEHICLE_CLASS_NAME.SPG
            mode['spg_key'] = None if not key['spg_key'] else VEHICLE_CLASS_NAME.SPG
            mode['tanklist'] = key['tanklist']
            mode['auto_key_pressed'] = key['auto_key_pressed']
            mode['wheeled'] = None if not key['wheeled'] else 'wheeledVehicle'
            mode['wheeled_key'] = None if not key['wheeled_key'] else 'wheeledVehicle'
        mode0, mode1, mode2, mode3 = mode_lst
        return mode0, mode1, mode2, mode3

    def loadModes(self):
        if os.path.exists('res_mods/configs/extended_auto_bl_modes.json'):
            with open('res_mods/configs/extended_auto_bl_modes.json') as f:
                self.mode_data = json.load(f)
        else:
            try:
                with open('res_mods/configs/extended_auto_bl_modes.json', 'w') as f1:
                    json.dump(self.mode_data, f1, indent=2, sort_keys=True)
            except (IOError, ValueError):
                pass
        mode_0, mode_1, mode_2, mode_3 = self.convert_to_schematic()
        return mode_0, mode_1, mode_2, mode_3

    def increment_mode(self):
        if self.active_mode is not None:
            nr_modes = len(self.all_modes)
            if self.active_idx + 1 == nr_modes:
                self.active_idx = 0
                self.active_mode = self.all_modes[self.active_idx]
            else:
                self.active_idx += 1
                self.active_mode = self.all_modes[self.active_idx]
            self.updateConfigData()
            self.updateJsonWithConfigData()

    def updateConfigData(self):
        self.config_data = {'mode': self.active_idx, 'ignored': self.ignored, 'friends': self.friends, 'extended': self.extended}

    def updateFromConfigData(self):
        self.active_idx = self.config_data['mode']
        self.active_mode = self.all_modes[self.active_idx] if self.all_modes else None
        self.ignored = self.config_data['ignored']
        self.friends = self.config_data['friends']
        self.extended = self.config_data['extended']

    def updateJsonWithConfigData(self):
        try:
            with open('res_mods/configs/extended_auto_bl.json', 'w') as f1:
                json.dump(self.config_data, f1, indent=2)
        except (IOError, ValueError):
            pass

    def loadJson(self):
        if os.path.exists('res_mods/configs/extended_auto_bl.json'):
            with open('res_mods/configs/extended_auto_bl.json') as f:
                self.config_data = json.load(f)
                self.updateFromConfigData()
        else:
            self.updateConfigData()
            self.updateJsonWithConfigData()

    def toggle_extended(self):
        if not self.extended:
            self.extended = True
        elif self.extended:
            self.extended = False
        self.updateConfigData()
        self.updateJsonWithConfigData()

    def toggle_enable_clear(self):
        if not self.enable_clear:
            self.enable_clear = True
        elif self.enable_clear:
            self.enable_clear = False


class SchematicForMode(object):
    other_game_modes = (0, 2, 4, 5, 6, 7, 9, 13, 14, 15, 16, 17, 18, 19, 20, 21, 23, 24, 25,
                        26, 27, 28, 29, 30, 31, 33)

    def __init__(self, name='', shell_AP=None, shell_APCR=None, shell_HEAT=None,
                 shell_HE=None, random=ARENA_BONUS_TYPE.REGULAR, random_key=ARENA_BONUS_TYPE.REGULAR,
                 ranked=(None,), ranked_key=(None,),
                 other_modes=(None,), other_modes_key=(None,), light=None, light_key=None,
                 med=None, med_key=None, heavy=None, heavy_key=None, td=None, td_key=None, spg=None,
                 spg_key=None, tanklist=[None], auto_key_pressed=False, wheeled=None, wheeled_key=None):
        self.name = name
        self.shell_list = {shell_AP, shell_APCR, shell_HEAT, shell_HE}
        self.auto_mode = {random}
        self.auto_mode.update(ranked)
        self.auto_mode.update(other_modes)
        self.key_mode = {random_key}
        self.key_mode.update(ranked_key)
        self.key_mode.update(other_modes_key)
        self.tank_cls = {light, med, heavy, td, spg, wheeled}
        self.tank_cls_key = {light_key, med_key, heavy_key, td_key, spg_key, wheeled_key}
        self.tanklist = tanklist
        self.auto_key_pressed = auto_key_pressed

    def removeNone(self):
        self.shell_list.discard(None)
        self.auto_mode.discard(None)
        self.key_mode.discard(None)
        self.tank_cls.discard(None)
        self.tank_cls_key.discard(None)


global_vars = GlobalVars()
