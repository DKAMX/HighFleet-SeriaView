import json
import logging
import os
from seria import *
from seria_model import *
from localization import L10N

__author__ = 'Max'

_CFG_PATH = 'config.json'
_CFG_SET = set(['gamepath'])

VIEWMODE_SETTINGS = 0
VIEWMODE_BASIC = 1
VIEWMODE_MAP = 2
VIEWMODE_TREE = 3


class SeriaController:
    def __init__(self):
        self.logger = logging.getLogger("SeriaController")

        self.config: dict = self.load_config()
        self.text: dict = _load_text(self.config.get('gamepath', ''))
        self.ship_designs: dict = _load_ship_designs(
            self.config.get('gamepath', ''))
        self.oid_set: set = _load_part_oid(self.config.get('gamepath', ''))
        self.parts: dict = _load_parts(self.config.get('gamepath', ''),
                                       self.oid_set)

        self.seria_node: SeriaNode = None
        self.profile_model: ProfileModel = ProfileModel()  # empty model for callback use

    def load_config(self) -> dict:
        self.logger.info('load_config')

        try:
            with open(_CFG_PATH) as file:
                config = json.load(file)

                if set(config.keys()) != _CFG_SET:
                    raise ValueError('Invalid config file')

                return config
        except:
            return dict()

    def add_config(self, key, value):
        self.logger.info(f'add_config: {key}={value}')

        self.config[key] = value
        with open(_CFG_PATH, 'w') as file:
            json.dump(self.config, file)

    def load_seria(self, filepath) -> bool:
        '''Load seria file and set it as current seria
        @return: True if success, False if failed'''

        self.logger.info(f'load_seria: {filepath}')

        node = load(filepath)

        if node is None:
            return False

        self.seria_node = node
        if self.seria_node.get_attribute('m_classname') == 'Profile':
            self.profile_model.load(self.seria_node)

        return True

    def load_profile(self, index: int) -> str:
        self.logger.info(f'load_profile: {index}')

        filepath = f'{self.config["gamepath"]}/Saves/Profile_{index}/profile.seria'
        try:
            self.load_seria(filepath)
            return filepath
        except:
            return None

    def save_seria(self, filepath):
        self.logger.info(f'save_seria: {filepath}')

        dump(self.seria_node, filepath)

    def get_gamepath(self):
        self.logger.info('get_gamepath')

        return self.config.get('gamepath', '')

    def set_gamepath(self, gamepath):
        self.logger.info(f'set_gamepath: {gamepath}')

        self.add_config('gamepath', gamepath)
        self.text = _load_text(gamepath)
        self.ship_designs = _load_ship_designs(gamepath)
        self.oid_set = _load_part_oid(gamepath)
        self.parts = _load_parts(gamepath, self.oid_set)

    def get_oid_text(self, oid: str):
        if self.text is None:
            return oid
        return f'{self.text.get(oid, oid)} {self.text.get(oid + "_SDESC", "")}'

    def get_node_text(self, node: SeriaNode):
        classname = node.get_attribute('m_classname')
        name = node.get_attribute('m_name')
        codename = node.get_attribute('m_codename')

        if classname == 'Profile':
            return f'{L10N().text("PROFILE")}'
        if classname == 'Escadra':
            return f'{L10N().text("ESCADRA")} {name}'
        if classname == 'Location':
            return f'{L10N().text("LOCATION")} {name} ({codename})'
        if classname == 'NPC':
            output = 'NPC'
            fullname = node.get_attribute('m_fullname')
            if fullname:
                output += f' {fullname}'
            location = node.get_attribute('m_location')
            if location:
                output += f' {location}'
            return output
        if classname == 'Node':
            ship_name = get_ship_name(node)
            return 'Node' if ship_name is None else f'Node {ship_name}'
        if classname == 'Body':
            oid = node.get_attribute('m_oid')
            return f'Body {self.get_oid_text(oid)}' if oid else 'Body'
        if classname == 'Item':
            return f'{L10N().text("ITEM")}'
        return classname

    def is_profile(self):
        self.logger.info('is_profile')

        return self.seria_node.get_attribute('m_classname') == 'Profile'


def _decrypt_seria(filepath: str):
    '''Decrypt seria_enc file and return as a list of lines
    reference: https://gist.github.com/blluv/3c72b9e85a190a63da384488d4e28ee9
    @param filepath: path to the seria_enc file
    @return: list of lines'''

    try:
        file = open(filepath, 'rb')
        data = list(file.read())
        a = 0
        b = 2531011
        while a < len(data):
            data[a] = (b ^ (b >> 15) ^ data[a]) & 0xff
            b += 214013
            b &= 0xffffffff
            a += 1
        return bytes(data).decode('cp1251').split('\n')
    except:
        return None


def _load_text(gamepath: str):
    '''Load in-game text from resource file, return as a dictionary
    @return: key(oid), value(text)'''

    lines = _decrypt_seria(gamepath + '/Data/Dialogs/english.seria_enc')

    if lines is None:
        return None

    text_map = dict()
    for line in lines:
        if line.startswith('#ITEM') or line.startswith('#CRAFT') or line.startswith('#MDL'):
            key, value = line.split('\t', 1)
            text_map[key[1:]] = value
    return text_map


def _load_ship_designs(gamepath: str):
    '''Load ship designs from resource file, return as a dictionary
    @return: key(ship name), value(path to design file)'''

    vanilla_path = gamepath + '/Objects/Designs'
    player_path = gamepath + '/Ships'

    designs = dict()
    try:
        for filename in os.listdir(vanilla_path):
            filepath = vanilla_path + '/' + filename
            if os.path.isfile(filepath) and filename.endswith('.seria'):
                designs[filename] = filepath

        for filename in os.listdir(player_path):
            filepath = player_path + '/' + filename
            if os.path.isfile(filepath) and filename.endswith('.seria'):
                designs[filename] = filepath

        return designs
    except:
        return None


def _load_part_oid(gamepath: str):
    filepath = gamepath + '/Libraries/OL.seria'
    return get_part_oid_set(load(filepath))


def _load_parts(gamepath: str, oid_set: set):
    '''Load parts from resource file, return as a dictionary
    @return: key(oid), value(part name)'''

    filepath = gamepath + '/Libraries/parts.seria'
    parts_node = load(filepath)

    parts_map = dict()
    for node in parts_node.get_nodes():
        oid = node.get_attribute('m_oid')
        if oid in oid_set:
            parts_map[oid] = node
    return parts_map
