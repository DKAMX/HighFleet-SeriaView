import json
import logging
import seria
from seria_model import ProfileModel

__author__ = 'Max'
__version__ = '0.3.0'

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

        self.seria_node: seria.SeriaNode = None
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

        node = seria.load(filepath)

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

        seria.dump(self.seria_node, filepath)

    def get_gamepath(self):
        self.logger.info('get_gamepath')

        return self.config.get('gamepath', '')

    def set_gamepath(self, gamepath):
        self.logger.info(f'set_gamepath: {gamepath}')

        self.add_config('gamepath', gamepath)
        self.text = _load_text(gamepath)


def _decrypt_seria(filepath):
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


def _load_text(gamepath):
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
