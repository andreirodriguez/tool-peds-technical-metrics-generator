import json
import numpy as np
from utils.constants import EXTENSIONS_ADD_FUNTIONALITY

from enum import Enum
class TargetTechnology(Enum):
    JAVA = 'JAVA'
    IOS = 'IOS'
    ANDROID = 'ANDROID'
    WEB = 'WEB'
    ALL = 'ALL'

class ExtensionProcessor:
    def __init__(self) -> None:
        with open(EXTENSIONS_ADD_FUNTIONALITY, 'r') as json_file:
            self.data = json.load(json_file)

    def get_extensions(self, technology: TargetTechnology)->list:
        if technology == TargetTechnology.ALL:
            all_technologies = []
            for technology_key in self.data:
                all_technologies += self.data[technology_key]
            
            return np.unique(all_technologies)

        return self.data[technology.value]