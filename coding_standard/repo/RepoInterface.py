import abc
import pandas as pd

class RepoInterface(metaclass=abc.ABCMeta):    
    
    @abc.abstractmethod
    def table()->pd.DataFrame:
        pass