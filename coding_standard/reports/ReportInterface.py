import abc
import pandas as pd

class ReportInterface(metaclass=abc.ABCMeta):    
    
    @abc.abstractmethod
    def toDataframe()->pd.DataFrame:
        pass    

    @abc.abstractmethod
    def to_csv(path_directory: str)->None:
        pass