from constants import ARENA_BONUS_TYPE
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
            self.updateJsonWithConfigData()

    def toggle_extended(self):
        if not self.extended:
            self.extended = True
        elif self.extended:
            self.extended = False
        self.updateConfigData()
        self.updateJsonWithConfigData()


class SchematicForMode(object):
    other_game_modes = (0, 2, 4, 5, 6, 7, 9, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25,
                        26, 27, 28, 29, 30, 31, 33)

    def __init__(self, name='', shell_AP=None, shell_APCR=None, shell_HEAT=None,
                 shell_HE=None, random=ARENA_BONUS_TYPE.REGULAR, random_key=ARENA_BONUS_TYPE.REGULAR,
                 other_modes=None, other_modes_key=None, light=None, light_key=None,
                 med=None, med_key=None, heavy=None, heavy_key=None, td=None, td_key=None, spg=None,
                 spg_key=None, tanklist=None):
        self.name = name
        self.shell_list = {shell_AP, shell_APCR, shell_HEAT, shell_HE}
        self.auto_mode = {random, other_modes}  # other_modes must be tuple
        self.key_mode = {random_key, other_modes_key}
        self.tank_cls = {light, med, heavy, td, spg}
        self.tank_cls_key = {light_key, med_key, heavy_key, td_key, spg_key}
        self.tanklist = tanklist


def std_name(all_modes):
    if all_modes:
        all_modes_names = [modes.name for modes in all_modes]
        start_nr = 1
        basic_name = 'Mode '
        start_name = basic_name + str(start_nr)
        while start_name in all_modes_names:
            start_nr += 1
            start_name = basic_name + str(start_nr)
        return start_name


global_vars = GlobalVars()
disabled_mode = SchematicForMode(name='Mod disabled', random=None, random_key=None)
arty_mode = SchematicForMode(name='Only arty', other_modes=SchematicForMode.other_game_modes,
                             other_modes_key=SchematicForMode.other_game_modes, spg=VEHICLE_CLASS_NAME.SPG,
                             spg_key=VEHICLE_CLASS_NAME.SPG)
he_mode = SchematicForMode(name='Only HE', shell_HE=SHELL_TYPES.HIGH_EXPLOSIVE, random_key=None,
                           other_modes=SchematicForMode.other_game_modes)
he_bl_mode = SchematicForMode(name='HE + blacklist teams', shell_HE=SHELL_TYPES.HIGH_EXPLOSIVE,
                              other_modes=SchematicForMode.other_game_modes,
                              other_modes_key=SchematicForMode.other_game_modes)
