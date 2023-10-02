import abc
import pandas as pd

class ModelInterface(metaclass=abc.ABCMeta):    
    
    @abc.abstractmethod
    def toDataFrame()->pd.DataFrame:
        pass