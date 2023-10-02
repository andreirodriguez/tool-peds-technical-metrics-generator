import abc
from enum import Enum

from config.allowed_variables_by_pr_report import AllowedVariablesByPr

class PropertyInterface(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __init__(self, property_report: Enum, header_report_name: str, property_type: str): pass

    @abc.abstractproperty
    @property
    def property_report(self)->AllowedVariablesByPr: pass

    @abc.abstractproperty
    @property
    def header_report_name(self)->str: pass        

    @abc.abstractproperty
    @property
    def property_type(self)->str: pass
