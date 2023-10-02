import math

from unittesting.models.RangeCoveragePoint import RangeCoveragePoint
from unittesting.models.RangeQuizPoint import RangeQuizPoint
from unittesting.models.MetricTechnicalPoint import MetricTechnicalPoint
from unittesting.utils import isNotNumber

def get_coverage_points(coverage_percentage: float):
    ranges = [RangeCoveragePoint(0,30,1),
              RangeCoveragePoint(30,40,2), 
              RangeCoveragePoint(40,70,3),
              RangeCoveragePoint(70,90,4),
              RangeCoveragePoint(90,100,5)]

    return get_coverage_range_points(ranges,coverage_percentage)

def get_new_coverage_points(coverage_percentage: float):  
    ranges = [RangeCoveragePoint(0,40,1),
              RangeCoveragePoint(40,70,2), 
              RangeCoveragePoint(70,80,3),
              RangeCoveragePoint(80,90,4),
              RangeCoveragePoint(90,100,5)]

    return get_coverage_range_points(ranges,coverage_percentage)

def get_quiz_test_points(quiz: float):  
    ranges = [RangeQuizPoint(0,20,1),
              RangeQuizPoint(20,50,2), 
              RangeQuizPoint(50,65,3),
              RangeQuizPoint(65,80,4),
              RangeQuizPoint(80,100,5)]

    return get_quiz_test_range_points(ranges,quiz)

def get_survey_points(squad, df_survey):
    try:
        return df_survey[df_survey['SQUAD'] == squad].values[0][1]
    except:
        return 0
    
def get_coverage_range_points(ranges,coverage:float):
    if coverage is None or math.isnan(coverage): return None

    point = 0
    count = 1
    length = len(ranges)

    for range in ranges:
        if(count<length):
            if(range.rangeLower <= coverage < range.rangeUpper):
                point = range.point
                point += (coverage - range.rangeLower) * (100/(range.rangeUpper - range.rangeLower)/100)
                point = round(point, 2) 

                break
        else:
            if(range.rangeLower <= coverage <= range.rangeUpper):
                point = range.point

        count += 1

    return point

def get_quiz_test_range_points(ranges,quiz:float):
    if quiz is None or math.isnan(quiz): return None

    point = 0
    count = 1
    length = len(ranges)

    for range in ranges:
        if(count<length):
            if(range.rangeLower <= quiz < range.rangeUpper):
                point = range.point
                point += (quiz - range.rangeLower) * (100/(range.rangeUpper - range.rangeLower)/100)
                point = round(point, 2) 

                break
        else:
            if(range.rangeLower <= quiz <= range.rangeUpper):
                point = range.point

        count += 1

    return point

def get_coverage_metric_technical(overall_coverage_point,new_coverage_point,isLegacy:bool):
    if new_coverage_point is None or math.isnan(new_coverage_point): return overall_coverage_point

    if isLegacy:
        return round(overall_coverage_point * 0.1 + new_coverage_point * 0.9, 2)
    else:
        return round(overall_coverage_point * 0.5 + new_coverage_point * 0.5, 2)
    
def get_metric_technical_weighing(metrics)->float:
    metric_technical:float = 0
    metric_technical_minimum:float = 1

    for metric in metrics:
        if(metric.value==None):
            metric_technical += metric_technical_minimum * metric.weighing
        else:
            metric_technical += metric.value * metric.weighing

    return round(metric_technical,2)

def setMaturityLevel(squads):
    squads["patrones_principios_metric"] =  squads.apply(lambda squad: getMetricPatronesPrincipios(squad["patrones_points"],squad["principios_points"]),axis=1)
    squads["asserts_restricciones_metric"] =  squads.apply(lambda squad: getMetricAssertsRestricciones(squad["asserts_points"],squad["restricciones_points"]),axis=1)
    squads["mocks_stubs_metric"] =  squads.apply(lambda squad: getMetricMocksStubs(squad["mocks_points"],squad["stubs_points"]),axis=1)
    squads["naming_convention_metric"] =  squads.apply(lambda squad: getMetricNamingConvention(squad["naming_convention_points"]),axis=1)
    squads["coverage_metric"] =  squads.apply(lambda squad: getMetricCoverage(squad["coverage_points"],squad["coverage_valor_points"]),axis=1)

    squads["maturity_level"] =  squads.apply(lambda squad: getMaturityLevel(squad["patrones_principios_metric"],squad["asserts_restricciones_metric"],squad["mocks_stubs_metric"],squad["naming_convention_metric"],squad["coverage_metric"],squad["coverage_points"],squad["penalty_prs_executions_sonar"]),axis=1)

def getMetricPatronesPrincipios(patrones_points:float,principios_points:float)->float:
    metrics = []

    if(math.isnan(patrones_points) and math.isnan(principios_points)): return None

    metrics.append(MetricTechnicalPoint(0.6,patrones_points))
    metrics.append(MetricTechnicalPoint(0.4,principios_points))

    return get_metric_technical_weighing(metrics)

def getMetricAssertsRestricciones(asserts_points:float,restricciones_points:float)->float:
    metrics = []

    if(math.isnan(asserts_points) and math.isnan(restricciones_points)): return None

    metrics.append(MetricTechnicalPoint(0.7,asserts_points))
    metrics.append(MetricTechnicalPoint(0.3,restricciones_points))

    return get_metric_technical_weighing(metrics)

def getMetricMocksStubs(mocks_points:float,stubs_points:float)->float:
    metrics = []

    if(math.isnan(mocks_points) and math.isnan(stubs_points)): return None

    metrics.append(MetricTechnicalPoint(0.4,mocks_points))
    metrics.append(MetricTechnicalPoint(0.6,stubs_points))

    return get_metric_technical_weighing(metrics)

def getMetricNamingConvention(naming_convention_points:float)->float:
    metrics = []

    if(math.isnan(naming_convention_points)): return None

    metrics.append(MetricTechnicalPoint(1,naming_convention_points))

    return get_metric_technical_weighing(metrics)

def getMetricCoverage(coverage_points:float,coverage_valor_points:float)->float:
    metrics = []

    if(isNotNumber(coverage_points) and isNotNumber(coverage_valor_points)): return None

    if(not isNotNumber(coverage_points) and not isNotNumber(coverage_valor_points)): 
        metrics.append(MetricTechnicalPoint(0.9,coverage_points))
        metrics.append(MetricTechnicalPoint(0.1,coverage_valor_points))

        return get_metric_technical_weighing(metrics)
    else:
        if(isNotNumber(coverage_points)): return coverage_valor_points
        else: return coverage_points

def getMaturityLevel(metric_patrones_principios:float,metric_asserts_restricciones:float,metric_mocks_stubs:float,metric_naming_convention:float,metric_coverage:float,coverage_points:float,penalty_prs_executions_sonar:float)->float:
    metrics = []

    if(isNotNumber(coverage_points)): return None

    if(math.isnan(metric_patrones_principios) and math.isnan(metric_asserts_restricciones) and math.isnan(metric_mocks_stubs)and math.isnan(metric_naming_convention) and math.isnan(metric_coverage)): return None

    maturity_level = None

    if(not math.isnan(metric_patrones_principios) and not math.isnan(metric_asserts_restricciones) and not math.isnan(metric_mocks_stubs)and not math.isnan(metric_naming_convention) and not math.isnan(metric_coverage)): 
        metrics.append(MetricTechnicalPoint(0.05,metric_patrones_principios))
        metrics.append(MetricTechnicalPoint(0.25,metric_asserts_restricciones))
        metrics.append(MetricTechnicalPoint(0.15,metric_mocks_stubs))
        metrics.append(MetricTechnicalPoint(0.05,metric_naming_convention))
        metrics.append(MetricTechnicalPoint(0.50,metric_coverage))

        maturity_level = get_metric_technical_weighing(metrics)
    else:
        maturity_level = metric_coverage

    maturity_level += penalty_prs_executions_sonar

    return maturity_level