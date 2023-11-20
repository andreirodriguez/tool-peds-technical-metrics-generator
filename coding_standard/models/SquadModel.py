from config.PropertyInterface import PropertyInterface
from models.ModelInterface import ModelInterface
from queries.SquadQuery import SquadQuery
from typing import List
import pandas as pd

from utils.MaturityCalc import MaturityCalc

class SquadModel(ModelInterface, SquadQuery):
    def __init__(self, squad_df: pd.DataFrame, report_fields: List[PropertyInterface], *args, **kwargs):
        super().__init__(squad_df, *args, **kwargs)        
        self.squad_df = squad_df
        self.maturity = MaturityCalc()
        self.__report_fields = report_fields

    
    @property
    def squad_code(self)->str:
        return self.squad_df['squad_code']
    
    @property
    def tribe_code(self)->str:
        return self.squad_df['tribe_code']

    @property
    def squad(self)->str:
        return self.squad_df['squad']

    @property
    def tribe(self)->str:
        return self.squad_df['tribe']

    @property
    def group(self)->int:
        return self.squad_df['group']
    
    @property
    def cmt(self)->str:
        return self.squad_df['cmt']
    
    @property
    def c_smells_total_info_severity(self)->float:
        return self.sumMetric('c_smells_total_info_severity')
    
    @property
    def c_smells_total_minor_severity(self)->float:
        return self.sumMetric('c_smells_total_minor_severity')
    
    @property
    def c_smells_total_major_severity(self)->float:
        return self.sumMetric('c_smells_total_major_severity')
    
    @property
    def c_smells_total_critical_severity(self)->float:
        return self.sumMetric('c_smells_total_critical_severity')
    
    @property
    def c_smells_total_blocker_severity(self)->float:
        return self.sumMetric('c_smells_total_blocker_severity')
    
    @property  
    def code_smells_severity_penalty(self)->float:
        if self.uniqueRepoCountMetric('c_smells_total_blocker_severity') > 0 or self.uniqueRepoCountMetric('c_smells_total_critical_severity') > 0:
            return -0.5
        
        return 0.0
    
    @property
    def code_smells_diff_points(self)->float:
        return self.avgMetric('code_smells_diff_points')

    @property
    def total_code_smells_overall(self)->float:
        return self.uniqueRepoSumMetric('total_code_smells_overall')

    @property  
    def code_smells_overall_points(self)->float:
        return self.avgMetric('code_smells_overall_points')

    @property      
    def code_smells_severity_points(self)->float:
        return self.avgMetric('code_smells_severity_points')
    
    @property
    def bug_total_info_severity(self)->float:
        return self.sumMetric('bug_total_info_severity')

    @property
    def bug_total_minor_severity(self)->float:
        return self.sumMetric('bug_total_minor_severity')

    @property
    def bug_total_major_severity(self)->float:
        return self.sumMetric('bug_total_major_severity')

    @property
    def bug_total_critical_severity(self)->float:
        return self.sumMetric('bug_total_critical_severity')

    @property
    def bug_total_blocker_severity(self)->float:
        return self.sumMetric('bug_total_blocker_severity')
    
    @property  
    def bugs_severity_penalty(self)->float:
        if self.uniqueRepoCountMetric('bug_total_blocker_severity') > 0 or self.uniqueRepoCountMetric('bug_total_critical_severity') > 0:
            return -0.5

        return 0.0

    @property
    def total_bugs(self)->float:
        return self.sumMetric('total_bugs')
    
    @property
    def bugs_diff_points(self)->float:
        return self.avgMetric('bugs_diff_points')
    
    @property
    def bugs_overall(self)->float:
        return self.uniqueRepoSumMetric('bugs_overall')

    @property    
    def bugs_overall_points(self)->float:
        return self.avgMetric('bugs_overall_points')
        
    @property        
    def bugs_severity_points(self)->float:
        # return  round(self.avgMetric('bugs_severity_points') + self.bugs_severity_penalty, 2)
        return self.avgMetric('bugs_severity_points')
        
    @property
    def comment_lines_density(self):
        return self.uniqueRepoAverageMetric('comment_lines_density')
    
    @property    
    def comment_line_density_points(self)->float:
        return self.avgMetric('comment_line_density_points')
    
    @property        
    def cognitive_diff_complexity_points(self)->float:
        return self.avgMetric('cognitive_diff_complexity_points')
    
    @property        
    def cyclomatic_diff_complexity_points(self)->float:
        return self.avgMetric('cyclomatic_diff_complexity_points')
    
    @property
    def duplicated_lines_density(self):
        return self.uniqueRepoAverageMetric('duplicated_lines_density')
    
    @property        
    def duplicated_lines_density_points(self)->float:
        return self.uniqueRepoAverageMetric('duplicated_lines_density_points')
    
    @property
    def total_high_security_hostpots(self):
        return self.uniqueRepoSumMetric('total_high_security_hostpots')

    @property
    def total_medium_hostpots(self):
        return self.uniqueRepoSumMetric('total_medium_hostpots')

    @property
    def total_low_hostpots(self):
        return self.uniqueRepoSumMetric('total_low_hostpots')
    
    @property  
    def hostpots_severity_penalty(self)->float:
        if self.uniqueRepoCountMetric('total_high_security_hostpots') > 0 or self.uniqueRepoCountMetric('total_medium_hostpots') > 0:
            return -0.5

        return 0.0
    
    @property
    def security_hostp_total_points(self):
        return self.avgMetric('security_hostp_total_points')

    @property
    def total_security_hostspots(self):
        return self.uniqueRepoSumMetric('total_security_hostspots')
    
    @property        
    def security_hostp_severity_points(self)->float:
        return  self.uniqueRepoAverageMetric('security_hostp_severity_points')

    @property    
    def critical_fortify_bugs(self)->int:
        return self.uniqueRepoSumMetric('critical_fortify_bugs')

    @property        
    def high_fortify_bugs(self)->int:
        return self.uniqueRepoSumMetric('high_fortify_bugs')

    @property        
    def medium_fortify_bugs(self)->int:
        return self.uniqueRepoSumMetric('medium_fortify_bugs')

    @property        
    def low_fortify_bugs(self)->int:
        return self.uniqueRepoSumMetric('low_fortify_bugs')

    @property        
    def total_fortify_bugs(self)->int:
        return self.uniqueRepoSumMetric('total_fortify_bugs')
    
    @property  
    def fortify_severity_penalty(self)->float:
        if self.uniqueRepoCountMetric('critical_fortify_bugs') > 0 or self.uniqueRepoCountMetric('high_fortify_bugs') > 0:
            return -0.5

        return 0.0
    
    @property
    def fortify_severity_points(self)->float:
        return self.avgMetric('fortify_severity_points')
        # return  round(self.avgMetric('fortify_severity_points') + self.fortify_severity_penalty, 2)
    
    @property
    def fortify_total_points(self)->float:
        return self.avgMetric('fortify_total_points')
    
    @property
    def functions(self)->float:
        return self.uniqueRepoSumMetric('functions')

    @property
    def complexity(self)->float:
        return self.uniqueRepoSumMetric('complexity')

    @property        
    def complexity_points(self)->float:
        return self.uniqueRepoAverageMetric('complexity_points')
    
    @property
    def cyclomatic_LOW(self)->int:
        return self.uniqueRepoSumMetric('cyclomatic_LOW')

    @property
    def cyclomatic_MEDIUM(self)->int:
        return self.uniqueRepoSumMetric('cyclomatic_MEDIUM')

    @property
    def cyclomatic_HIGH(self)->int:
        return self.uniqueRepoSumMetric('cyclomatic_HIGH')    
    
    @property
    def sonar_projects_penalty_in_complexity(self):
        return self.uniqueRepoCountMetric('severity_complexity_penalty')
    
    @property
    def final_complexity_points(self):
        return self.uniqueRepoAverageMetric('final_complexity_points')
    
    @property
    def cognitive_complexity(self)->int:
        return self.uniqueRepoSumMetric('cognitive_complexity')

    @property
    def cognitive_complexity_points(self)->float:
        return self.uniqueRepoAverageMetric('cognitive_complexity_points')

    @property    
    def cognitive_LOW(self)->int:
        return self.sumMetric('cognitive_LOW')

    @property
    def cognitive_MEDIUM(self)->int:
        return self.sumMetric('cognitive_MEDIUM')

    @property
    def cognitive_HIGH(self)->int:
        return self.sumMetric('cognitive_HIGH')
    
    @property
    def sonar_projects_penalty_in_cogn_complexity(self):
        return self.uniqueRepoCountMetric('severity_cogn_complexity_penalty')
    
    @property
    def final_cogn_complexity_points(self)->float:
        return self.avgMetric('final_cogn_complexity_points')

    @property        
    def technical_maturity_level(self)->float:
        return round(self.avgMetric('technical_maturity_level'), 2)
    
    @property
    def estandares_lineamientos_points(self)->float:
        return round(self.quizAverageMetric('estandares_lineamientos_int_points'), 2)
    
    @property
    def patrones_principios_points(self)->float:
        return round(self.quizAverageMetric('patrones_principios_int_points'), 2)
    
    @property
    def knoledge_maturity_level(self)->float:
        return round(self.maturity.adoptionKnowledgeCalculate(self.estandares_lineamientos_points, self.patrones_principios_points), 2)
    
    @property
    def sonar_execution_ratio(self)->float:
        all_registers           = self.countAllRegisters()
        pr_with_sonar_execution = self.registersWithSonarExecution()
        if pr_with_sonar_execution > 0:
            return round((pr_with_sonar_execution / all_registers) * 100, 1)
        
        return 0.0

    @property
    def sonar_execution_penalty(self)->float:
        return -0.5 if self.sonar_execution_ratio < 50 else 0.0

    @property
    def maturity_level(self)->float:        
        maturity = sum([self.knoledge_maturity_level * self.maturity.ADOCTION_KNOWLEDGE_WEIGHT,
                    self.technical_maturity_level * self.maturity.TECNICAL_MATURITY_WEIGTH,
                    self.code_smells_severity_penalty,
                    self.bugs_severity_penalty,
                    self.hostpots_severity_penalty,
                    self.fortify_severity_penalty ,
                    self.sonar_execution_penalty])
        
        return 0.0 if maturity < 0 else round(maturity, 2)

    @property
    def analysis_date(self):
        return self.metricFirstValue('analysis_date')
    
    @property
    def execution_date(self):
        return self.metricFirstValue('execution_date')
    
    def toDataFrame(self)->pd.DataFrame:
        data = {}

        for conf in self.__report_fields:                              
            data[conf.header_report_name] = getattr(self, conf.property_report)
        
        return pd.DataFrame([data])


    




    



