import pandas as pd
from config.PropertyInterface import PropertyInterface
from models.ModelInterface import ModelInterface
from queries.PRQuery import PRQuery
from utils.GlobalTypes import HostsPotsType, IssueSeverityType, SeverityType
from utils.MaturityCalc import MaturityCalc
from utils.MetricCalculate import MetricCalculate
from utils.TimestampsCalc import TimestampsCalc

class PullRequestModel(ModelInterface, PRQuery):        
    __default_points = 0

    def __init__(self, maturity: MaturityCalc, timestapms: TimestampsCalc, df_prs_by_squad:pd.DataFrame, report_fields: tuple[PropertyInterface], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.maturity = maturity
        self.timestapms = timestapms
        self.pr = kwargs['df_pr']
        self.df_prs_by_squad = df_prs_by_squad
        self.__fields_to_print = report_fields
        self.__global_setter()
    
    @property
    def has_sonar(self)->bool:
        return self.__has_sonar

    @property
    def has_fortify(self)->bool:
        return self.__has_fortify
    
    @property
    def app(self)->str:
        return self.pr.app

    @property        
    def repo(self)->str:
        return self.pr.repo
    
    @property
    def sonar_project_name(self)->str:
        return self.getSonarProjectName()

    @property    
    def squad(self)->str:
        return self.pr.squad
    
    @property
    def squad_code(self)->int:
        return self.pr.squad_code
    
    @property
    def tribe_code(self)->int:
        return self.pr.tribe_code
    
    @property
    def tribe(self)->str:
        return self.pr.tribe
    
    @property
    def prid(self)->int:
        return self.pr.prid
    
    @property
    def specialty(self)->str:
        return self.pr.specialty
    
    @property
    def technology(self)->str:
        return self.pr.technology
    
    @property
    def author(self)->str:
        return self.pr.author
    
    @property
    def author_name(self)->str:
        return self.pr.author_name
    
    @property
    def origin_branch(self)->str:
        return self.pr.origin_branch
    
    @property
    def close_date(self)->str:
        return self.pr.close_date
    
    @property    
    def c_smells_total_info_severity(self):
        result = self.getIssuesByPullRequest(IssueSeverityType.INFO.value, SeverityType.CODE_SMELL.value)
        self.total_code_smells += result
        return result            
    
    @property    
    def c_smells_total_minor_severity(self):
        result = self.getIssuesByPullRequest(IssueSeverityType.MINOR.value, SeverityType.CODE_SMELL.value)            
        self.total_code_smells += result
        return result
    
    @property    
    def c_smells_total_major_severity(self):
        result = self.getIssuesByPullRequest(IssueSeverityType.MAJOR.value, SeverityType.CODE_SMELL.value)
        self.total_code_smells += result
        return result
    
    @property    
    def c_smells_total_critical_severity(self):
        result = self.getIssuesByPullRequest(IssueSeverityType.CRITICAL.value, SeverityType.CODE_SMELL.value)
        self.total_code_smells += result
        return result
    
    @property    
    def c_smells_total_blocker_severity(self):
        result = self.getIssuesByPullRequest(IssueSeverityType.BLOCKER.value, SeverityType.CODE_SMELL.value)
        self.total_code_smells += result
        return result
    
    @property
    def code_smells_diff_points(self):
        if not self.__has_sonar: return self.__default_points
        return MetricCalculate.bugAnscodeSmellsAveragePoints(self.total_code_smells)
    
    @property
    def total_code_smells_overall(self):
        dfLastRegister  = self.getLastHistoryItemOfAMetricType('code_smells')
        return (0 if not len(dfLastRegister) else float(dfLastRegister['Value']))
    
    @property
    def code_smells_overall_penalty(self)->float:
        return MetricCalculate.penaltyCalc(self.total_code_smells_overall, 20)
    
    @property
    def code_smells_overall_points(self):
        if not self.__has_sonar: return self.__default_points
        return MetricCalculate.bugAnscodeSmellsAveragePoints(self.total_code_smells_overall)

    
    @property    
    def code_smells_severity_points(self)->int:
        if not self.__has_sonar: return self.__default_points
        dfSeverities   = self.getAllIssuesBySeverity(SeverityType.CODE_SMELL.value)
        severities     = self.setSeverities(dfSeverities)
        return MetricCalculate.severityPoints(severities)      

    @property    
    def bug_total_info_severity(self):
        return self.getIssuesByPullRequest(IssueSeverityType.INFO.value, SeverityType.BUG.value)            
    
    @property
    def bug_total_minor_severity(self):
        return self.getIssuesByPullRequest(IssueSeverityType.MINOR.value, SeverityType.BUG.value)            
    
    @property        
    def bug_total_major_severity(self):
        return self.getIssuesByPullRequest(IssueSeverityType.MAJOR.value, SeverityType.BUG.value)            
    
    @property        
    def bug_total_critical_severity(self):
        return self.getIssuesByPullRequest(IssueSeverityType.CRITICAL.value, SeverityType.BUG.value)            
    
    @property        
    def bug_total_blocker_severity(self):
        return self.getIssuesByPullRequest(IssueSeverityType.BLOCKER.value, SeverityType.BUG.value)            

    @property
    def total_bugs(self):
        return self.bug_total_info_severity + self.bug_total_minor_severity + self.bug_total_major_severity + self.bug_total_critical_severity + self.bug_total_blocker_severity
    
    @property
    def bugs_diff_points(self):
        if not self.__has_sonar: return self.__default_points
        return MetricCalculate.bugAnscodeSmellsAveragePoints(self.total_bugs)
    
    @property
    def bugs_overall(self):
        dfLastRegister = self.getLastHistoryItemOfAMetricType('bugs')
        return 0 if not len(dfLastRegister) else float(dfLastRegister['Value'])
    
    @property
    def bugs_overall_penalty(self)->float:
        return MetricCalculate.penaltyCalc(self.bugs_overall, 20)
    
    @property
    def bugs_overall_points(self):
        if not self.__has_sonar: return self.__default_points
        return MetricCalculate.bugAnscodeSmellsAveragePoints(self.bugs_overall)

    @property
    def bugs_severity_points(self):
        if not self.__has_sonar: return self.__default_points
        dfSeverities    = self.getAllIssuesBySeverity(SeverityType.BUG.value)
        severities      = self.setSeverities(dfSeverities)
        return MetricCalculate.severityPoints(severities)

    @property
    def comment_lines_density(self):
        dfLastRegister = self.getLastHistoryItemOfAMetricType('comment_lines_density')
        return 0 if not len(dfLastRegister) else float(dfLastRegister['Value'])
    
    @property
    def comment_line_density_points(self):
        if not self.__has_sonar: return self.__default_points
        dfLastRegister = self.getLastHistoryItemOfAMetricType('comment_lines_density')
        return MetricCalculate.commentsDensityPoints(
            0 if not len(dfLastRegister) else float(dfLastRegister['Value'])
        )    

    @property
    def cognitive_diff_complexity_points(self):   
        if not self.__has_sonar: return self.__default_points
        return self.cognitiveComplexity
    
    @property
    def cyclomatic_diff_complexity_points(self):
        if not self.__has_sonar: return self.__default_points
        return self.cyclomaticComplexity
    
    @property
    def duplicated_lines_density(self):
        dfLastRegister = self.getLastHistoryItemOfAMetricType('duplicated_lines_density')
        return 0 if not len(dfLastRegister) else float(dfLastRegister['Value'])

    @property
    def duplicated_lines_density_points(self):
        if not self.__has_sonar: return self.__default_points
        return MetricCalculate.duplicatedLinesDensityPoints(self.duplicated_lines_density)
    
    @property
    def total_high_security_hostpots(self):
        return self.getSecurityHospotByType(HostsPotsType.HIGHT)

    @property        
    def total_medium_hostpots(self):
        return self.getSecurityHospotByType(HostsPotsType.MEDIUM)

    @property        
    def total_low_hostpots(self):
        return self.getSecurityHospotByType(HostsPotsType.LOW)

    @property
    def security_hostp_severity_points(self)->float:
        if not self.__has_sonar: return self.__default_points
        return MetricCalculate.hostsPotsSeverityPoints(self.total_low_hostpots, self.total_medium_hostpots, self.total_high_security_hostpots)
    
    @property
    def total_security_hostspots(self)->float:
        if not self.__has_sonar: return self.__default_points
        return self.total_high_security_hostpots + self.total_medium_hostpots + self.total_low_hostpots
    
    @property
    def security_hostpots_total_penalty(self)->float:
        return MetricCalculate.penaltyCalc(self.total_security_hostspots, 4)

    @property
    def security_hostp_total_points(self):
        if not self.__has_sonar: return self.__default_points
        return MetricCalculate.hostsPotsTotalPoints(self.total_security_hostspots)

    # FORTIFY
    
    @property
    def critical_fortify_bugs(self):          
        return self.__fortify_bugs['critical']
    
    @property
    def high_fortify_bugs(self):              
        return self.__fortify_bugs['high']
    
    @property
    def medium_fortify_bugs(self):            
        return self.__fortify_bugs['medium']
    
    @property
    def low_fortify_bugs(self):               
        return self.__fortify_bugs['low']
    
    @property
    def total_fortify_bugs(self):             
        return self.__fortify_bugs['critical'] + self.__fortify_bugs['high'] + self.__fortify_bugs['medium'] + self.__fortify_bugs['low']            
    
    @property
    def fortify_severity_points(self):        
        if not self.__has_fortify: return self.__default_points
        return MetricCalculate.fortifySeverityPoints(self.__fortify_bugs)
    
    @property
    def fortify_total_bugs_penalty(self)->float:
        return MetricCalculate.penaltyCalc(self.total_fortify_bugs, 20)
    
    @property
    def fortify_total_points(self):           
        if not self.__has_fortify: return self.__default_points
        return MetricCalculate.fortifyTotalPoints(self.total_fortify_bugs)
    
    @property
    def functions(self):
        dfLastRegister = self.getLastHistoryItemOfAMetricType('functions')
        return (0 if not len(dfLastRegister) else float(dfLastRegister['Value']))

    @property
    def complexity(self):
        dfLastRegister = self.getLastHistoryItemOfAMetricType('complexity')
        return (0 if not len(dfLastRegister) else float(dfLastRegister['Value']))  

    @property
    def complexity_points(self):
        if not self.__has_sonar: return self.__default_points
        complex_calc = self.complexity / self.functions if self.complexity and self.functions else 0
        return MetricCalculate.complexityPoints(complex_calc)    
    
    @property
    def cyclomatic_LOW(self):
        dfLastRegister = self.getMetricByRepo('cyclomatic_LOW')
        return (0 if not len(dfLastRegister) else float(dfLastRegister['Value']))
    
    @property
    def cyclomatic_MEDIUM(self):
        dfLastRegister = self.getMetricByRepo('cyclomatic_MEDIUM')
        return (0 if not len(dfLastRegister) else float(dfLastRegister['Value']))
    
    @property
    def cyclomatic_HIGH(self):
        dfLastRegister = self.getMetricByRepo('cyclomatic_HIGH')
        return (0 if not len(dfLastRegister) else float(dfLastRegister['Value']))

    @property
    def severity_complexity_penalty(self):
        dfComplexity = self.getComplexityRanges('cyclomatic')
        return MetricCalculate.severityComplexityPenalty(dfComplexity, 'cyclomatic')

    @property
    def final_complexity_points(self):
        if not self.__has_sonar: return self.__default_points
        return 0 if (self.complexity_points - self.severity_complexity_penalty) < 0 else self.complexity_points - self.severity_complexity_penalty

    @property
    def cognitive_complexity(self):    
        dfLastRegister = self.getLastHistoryItemOfAMetricType('cognitive_complexity')
        return (0 if not len(dfLastRegister) else float(dfLastRegister['Value']))

    @property
    def cognitive_complexity_points(self):
        if not self.__has_sonar: return self.__default_points
        complex_calc = self.cognitive_complexity / self.functions if self.cognitive_complexity and self.functions else 0
        return MetricCalculate.cognitiveComplexityPoints(complex_calc)

    @property
    def cognitive_LOW(self):
        dfLastRegister = self.getMetricByRepo('cognitive_LOW')
        return (0 if not len(dfLastRegister) else float(dfLastRegister['Value']))

    @property
    def cognitive_MEDIUM(self):    
        dfLastRegister = self.getMetricByRepo('cognitive_MEDIUM')
        return (0 if not len(dfLastRegister) else float(dfLastRegister['Value']))

    @property
    def cognitive_HIGH(self):    
        dfLastRegister = self.getMetricByRepo('cognitive_HIGH')
        return (0 if not len(dfLastRegister) else float(dfLastRegister['Value']))            

    @property
    def severity_cogn_complexity_penalty(self):
        dfComplexity   = self.getComplexityRanges('cognitive')            
        return MetricCalculate.severityComplexityPenalty(dfComplexity, 'cognitive')
    
    @property
    def final_cogn_complexity_points(self):
        if not self.__has_sonar: return self.__default_points
        return 0 if (self.cognitive_complexity_points - self.severity_cogn_complexity_penalty) < 0 else self.cognitive_complexity_points - self.severity_cogn_complexity_penalty
    
    @property        
    def maturity_clean_code(self):
        return self.maturity.cleanCodeCal(
                                            self.code_smells_diff_points,
                                            self.code_smells_overall_points, 
                                            self.code_smells_severity_points,
                                            self.bugs_diff_points,
                                            self.bugs_overall_points,
                                            self.bugs_severity_points
                                        )
    
    @property    
    def maturity_maintenaibily(self)->float:
        return self.maturity.maintainabilityAndResilience(
                                                            self.comment_line_density_points,
                                                            self.duplicated_lines_density_points,
                                                            self.cognitive_diff_complexity_points,
                                                            self.cyclomatic_diff_complexity_points,
                                                            self.final_complexity_points,
                                                            self.final_cogn_complexity_points
                                                        )            
    
    @property        
    def maturity_security(self)->float:
        return self.maturity.securityCalc(
                                            self.security_hostp_severity_points,
                                            self.security_hostp_total_points,
                                            self.fortify_severity_points,
                                            self.fortify_total_points
                                        )
    
    @property 
    def technical_maturity_level(self)->float:            
        tecnical_metric = self.maturity_clean_code + self.maturity_maintenaibily + self.maturity_security
        tecnical_metric += self.code_smells_overall_penalty + self.bugs_overall_penalty + self.security_hostpots_total_penalty  + self.fortify_total_bugs_penalty
        return round((tecnical_metric) * (100 / 85), 2)
    
    @property
    def analysis_date(self):
        return self.timestapms.first_day_custom_date


    @property
    def execution_date(self):
        return self.timestapms.current_date_formated


    def __global_setter(self)->None:
        self.total_code_smells  = 0
        self.__EMPTY_STRING     = ''
        self.__EMPTY_QUALIFICATION = 0

        # SONAR
        self.__has_sonar        = self.prHasSonar()        
        # FORTIFY
        last_pr                 = self.getLastPRByRepo(self.df_prs_by_squad, self.pr['repo'])
        self.__has_fortify      = self.prHasFortify(last_pr)
        self.__fortify_bugs     = self.fortifyBugs(last_pr)

    def toDataFrame(self)->pd.DataFrame:
        data = {}

        for conf in self.__fields_to_print:      
            if conf.property_type == 'SONAR' and not self.__has_sonar:
                data[conf.header_report_name] = self.__EMPTY_STRING
                continue            

            if conf.property_type == 'FORTIFY' and not self.__has_fortify:
                data[conf.header_report_name] = self.__EMPTY_STRING
                continue

            data[conf.header_report_name] = getattr(self, conf.property_report)
        
        return pd.DataFrame([data])        