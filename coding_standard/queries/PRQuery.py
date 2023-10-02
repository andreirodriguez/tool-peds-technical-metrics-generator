import pandas as pd
from utils.GlobalTypes import FortifyBugType, HostsPotsType

class PRQuery:

    def __init__(self, df_pr: pd.DataFrame, sonar_tbl: pd.DataFrame, fortify_df: pd.DataFrame):        
        self.df_pr          = df_pr
        sonar_tbl           = sonar_tbl[(sonar_tbl['repo'] == self.df_pr['repo']) & (sonar_tbl['Código Aplicación'] == self.df_pr['app'])]

        self.__sonar_base_tbl = sonar_tbl
        self.__sonar_tbl    = sonar_tbl[sonar_tbl['branch_name'] == self.df_pr['origin_branch']]

        
        fortify_df = fortify_df[(fortify_df['Aplicación'] == self.df_pr['app']) & (fortify_df['Versión'] == self.df_pr['repo'])]
        self.__fortify_tbl  = fortify_df


    def getIssuesByPullRequest(self, severity, severity_type):        
        df          = self.__sonar_tbl        
        df          = df[(df['Metric'] == severity_type) & (df['Value'] == severity)]

        return len(df)
    
    def getAllIssuesBySeverity(self, severity_type):        
        df          = self.__sonar_tbl
        severities  = ['INFO','MINOR','MAJOR', 'CRITICAL', 'BLOCKER']
        df          = df[df.Value.isin(severities) & (df['Metric'] == severity_type)]
        return df

    def getLastHistoryItemOfAMetricType(self, metric: str, metryc_type = float)->pd.DataFrame:
        df          = self.__sonar_tbl
        df          = df[(df['Metric'] == metric)]
        df          = df.astype({'Value': metryc_type})
        data        = df.tail(1)
        return data
    
    def getMetricByRepo(self, metric: str, metryc_type = float)->pd.DataFrame:
        df          = self.__sonar_base_tbl
        df_pr       = self.df_pr

        df          = df[df['repo'] == df_pr['repo']]
        df          = df[(df['Metric'] == metric)]
        df          = df.astype({'Value': metryc_type})
        data        = df.tail(1)
        return data
    
    @property
    def cognitiveComplexity(self)->int:
        df          = self.__sonar_tbl
        
        df          = df[(df['Metric'] == 'cognitive_complexity_by_issue')]        
        df          = df.astype({'Value': float} )

        if len(df[df['Value'] > 50]) > 0:
            return 1        
        if len(df[(df['Value'] > 30) & (df['Value'] <= 50)]) > 0:
            return 2
        if len(df[(df['Value'] > 20) & (df['Value'] <= 30)]) > 0:
            return 3
        if len(df[(df['Value'] > 15) & (df['Value'] <= 20)]) > 0:
            return 4
        
        return 5
    
    @property
    def cyclomaticComplexity(self)->int:
        df          = self.__sonar_tbl

        df          = df[df['Metric'] == 'cyclomatic_complexity_by_issue']         
        df          = df.astype({'Value': float})

        if len(df[df['Value'] > 50]) > 0:
            return 1        
        if len(df[(df['Value'] > 20) & (df['Value'] <= 50)]) > 0:
            return 2
        if len(df[(df['Value'] > 15) & (df['Value'] <= 20)]) > 0:
            return 3
        if len(df[(df['Value'] > 10) & (df['Value'] <= 15)]) > 0:
            return 4
        
        return 5
    
    def getSecurityHospotByType(self, seg_hostpot_type: HostsPotsType)->int:        
        df          = self.__sonar_base_tbl           
        df          = df[df['Metric'] == 'security_hostpot_level']

        return len(df[df['Value'] == seg_hostpot_type.value])
    
    
    def getLastPRByRepo(self, df_prs_by_squad: pd.DataFrame, repo:str)->pd.DataFrame:
        df_prs_by_squad = df_prs_by_squad[df_prs_by_squad['repo'] == repo]
        df_prs_by_squad = df_prs_by_squad.sort_values(by=['prid'])
        lastPR          = df_prs_by_squad.tail(1)
        return lastPR
    
    def prHasSonar(self)->bool:        
        return True if len(self.__sonar_tbl) > 0 else False 
    
    def getSonarProjectName(self)->str:
        df = self.__sonar_tbl
        df = df.tail(1)
        if df.empty == False:            
            return df['Proyecto Sonar'].values[0]
        
        return ''

    def prHasFortify(self, lastPR: pd.DataFrame)->bool:
        df              = self.__fortify_tbl
        return True if len(df) > 0 else False 


    def fortifyBugs(self, lastPR: pd.DataFrame)->dict:
        df                  = self.__fortify_tbl                         

        criticalBugs        = df['Valor Crítico'].sum()
        notCriticalBugs     = df['Only Not an Issue Critical'].sum()
        realCriticalBugs    = criticalBugs - notCriticalBugs

        hightBugs           = df['Valor Alto'].sum()
        notHigthBugs        = df['Only Not an Issue High'].sum()
        realHightBugs       = hightBugs - notHigthBugs

        mediumBugs          = df['Valor Medio'].sum()
        notMediumBugs       = df['Only Not an Issue Medium'].sum()        
        realMediumBugs      = mediumBugs - notMediumBugs

        lowBugs             = df['Valor Bajo'].sum()
        notLowBugs          = df['Only Not an Issue Low'].sum()        
        realLowBugs         = lowBugs - notLowBugs

        return {
            FortifyBugType.CRITICAL.value : realCriticalBugs,
            FortifyBugType.HIGH.value     : realHightBugs,
            FortifyBugType.MEDIUM.value   : realMediumBugs,
            FortifyBugType.LOW.value      : realLowBugs
        }       

    def getComplexityRanges(self, complex_type: str):
        df          = self.__sonar_base_tbl        
        severities  = [f"{complex_type}_LOW",f"{complex_type}_MEDIUM", f"{complex_type}_HIGH"]        
        df          = df[df.Metric.isin(severities)]
        return df
    
    def setSeverities(self, dfSeverities: pd.DataFrame)->dict:
        return {
                    'blocker':  len(dfSeverities[dfSeverities['Value']== 'BLOCKER']),
                    'critical': len(dfSeverities[dfSeverities['Value'] == 'CRITICAL']),
                    'major':    len(dfSeverities[dfSeverities['Value'] == 'MAJOR']),
                    'minor':    len(dfSeverities[dfSeverities['Value'] == 'MINOR']),
                    'info':     len(dfSeverities[dfSeverities['Value'] =='INFO']) 
                }