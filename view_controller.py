import json
import logging
import seria
from seria_model import ProfileModel

_CFG_PATH = 'config.json'
_CFG_SET = set(['gamepath'])


class SeriaController:
    def __init__(self):
        self.logger = logging.getLogger("SeriaController")

        self.config: dict = self.load_config()
        self.text: dict = _load_text(self.config.get('gamepath', ''))

        self.seria: seria.SeriaNode = None
        self.profile_model: ProfileModel = ProfileModel()  # empty model for callback use

    def load_config(self) -> dict:
        try:
            with open(_CFG_PATH) as file:
                config = json.load(file)

                if set(config.keys()) != _CFG_SET:
                    raise ValueError('Invalid config file')

                return config
        except:
            return dict()

    def set_config(self, key, value):
        self.config[key] = value
        with open(_CFG_PATH, 'w') as file:
            json.dump(self.config, file)

    def set_gamepath(self, gamepath):
        self.set_config('gamepath', gamepath)
        self.text = _load_text(gamepath)

    def load_seria(self, gamepath):
        self.seria = seria.load(gamepath)

        if self.seria.get_attribute('m_classname') == 'Profile':
            self.profile_model.load(self.seria)

    def load_profile(self, index: int):
        self.load_seria(
            f'{self.config["gamepath"]}/Saves/Profile_{index}/profile.seria')

    def save_seria(self, filepath):
        seria.dump(self.seria, filepath)


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
