from config.allowed_variables_by_pr_report import AllowedVariablesByPr
from config.PropertyInterface import PropertyInterface


class PropertyModel(PropertyInterface):
    
    def __init__(self, property_report: AllowedVariablesByPr, header_report_name: AllowedVariablesByPr, property_type: str) -> None:        
        self.__property_report = property_report
        self.__header_report_name = header_report_name
        self.__type = property_type

    @property
    def property_report(self)->str:        
        return self.__property_report.value
    
    @property
    def header_report_name(self)->str:
        return self.__header_report_name
    
    @property
    def property_type(self)->str:
        return self.__type