import sys
from unittest.mock import MagicMock

pseudonym_values_db = {}

class gPAS_Client_Mock():
    def __init__(self, access_token, settings):
        pass

    def pseudonymize(self, value):
        pseudo = f'str_{value}'
        pseudonym_values_db[pseudo] = value
        return pseudo

    def de_pseudonymize(self, value):
        de_pseudo = pseudonym_values_db[value]
        return de_pseudo

sys.modules['users'].pseudonymize_utils.gPAS_Client = gPAS_Client_Mock
print('MagicMock')