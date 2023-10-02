import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

from unittesting.utils import getPathDirectory,getCodeSquadTribe,setAnalysisExecutionDate
from unittesting.sonar_utils import getValueMetricSonar
from unittesting.maturity_points import get_coverage_points,get_new_coverage_points,get_coverage_metric_technical
from unittesting.constants import YES

def getPrsCodeReview(year,month):
    file = str(year) + str(month).zfill(2) + "-prs-with-commit-info.csv"

    print("Leo prs de Code Review: " + file)

    file = getPathDirectory("input\\pull_requests\\" + file)

    xlsPR = pd.read_csv(file,usecols=['app','repo','prid','squad','tribe','technology','specialty','application_type','author','origin_branch','author_name','close_date', 'mod_functionality_for_UT'],encoding="utf-8")
    xlsPR["specialty"] = xlsPR.apply(lambda pr: str(pr["specialty"]).upper(),axis=1)

    xlsPR = xlsPR.astype(object).where(pd.notnull(xlsPR),None)

    xlsPR["squad_code"] = xlsPR.apply(lambda pr: getCodeSquadTribe(pr["squad"]),axis=1)

    xlsPR = xlsPR[xlsPR["mod_functionality_for_UT"] == YES]

    return xlsPR

def getPrsSonarExecutions(prsCodeReview,sonarExecutions):
    prsCodeReview["overall_coverage"] = prsCodeReview.apply(lambda pr: getValueMetricSonar(pr,"coverage",sonarExecutions),axis=1)
    prsCodeReview["new_coverage"] = prsCodeReview.apply(lambda pr: getValueMetricSonar(pr,"new_coverage",sonarExecutions),axis=1)

    print("Leo prs de Code Review con ejecuciones de Sonar")

    return prsCodeReview

def getPrsSonarExecutionsWithMaturityLevel(period:str,prsSonarExecutions:pd.DataFrame)->pd.DataFrame:
    prsSonarExecutions["overall_coverage_points"] = prsSonarExecutions.apply(lambda pr: get_coverage_points(pr["overall_coverage"]),axis=1)
    prsSonarExecutions["new_coverage_points"] = prsSonarExecutions.apply(lambda pr: get_new_coverage_points(pr["new_coverage"]),axis=1)
    prsSonarExecutions["coverage_points"] = prsSonarExecutions.apply(lambda pr: get_coverage_metric_technical(pr["overall_coverage_points"],pr["new_coverage_points"],pr["application_type"]=="LEGACY"),axis=1)

    setAnalysisExecutionDate(period,prsSonarExecutions)

    print("Leo prs de Code Review con ejecuciones de Sonar y su metrica tecnica")

    return prsSonarExecutions