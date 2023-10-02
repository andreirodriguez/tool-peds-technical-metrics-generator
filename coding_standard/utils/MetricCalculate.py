from utils.GlobalTypes import FortifyBugType

class MetricCalculate:

    @staticmethod
    def complexityPenaltyRange(dfComplexity, complexity_type: str):
        df = dfComplexity
        if len(df[df['Metric'] == f"{complexity_type}_HIGH"]) > 0:
            return f"{complexity_type}_HIGH"
        if len(df[df['Metric'] == f"{complexity_type}_MEDIUM"]) > 0:
            return f"{complexity_type}_MEDIUM"
        if len(df[df['Metric'] == f"{complexity_type}_LOW"]) > 0:
            return f"{complexity_type}_LOW"
        
        return 0

    @staticmethod
    def severityComplexityPenalty(dfComplexity, complexity_type: str):
        df = dfComplexity
        if len(df[df['Metric'] == f"{complexity_type}_HIGH"]) > 0:
            return 2
        if len(df[df['Metric'] == f"{complexity_type}_MEDIUM"]) > 0:
            return 1.5
        if len(df[df['Metric'] == f"{complexity_type}_LOW"]) > 0:
            return 0.5
        
        return 0
    
    @staticmethod
    def hostsPotsTotalPoints(total_security_hostpots:int)->int:
        ranges = [
            {"from": -0.9, "to": 0, "qualification": 5},
            {"from": 0, "to": 1, "qualification": 4},
            {"from": 1, "to": 4, "qualification": 3},
            {"from": 4, "to": 10, "qualification": 2},
            {"from": 10, "to": float('inf'), "qualification": 1},
        ]

        return MetricCalculate.__calculer(total_security_hostpots, ranges)
    
    @staticmethod
    def quizPoints(qualification:int)->int:
        ranges = [
            {"from": 80, "to": 100, "qualification": 5},
            {"from": 65, "to": 80, "qualification": 4},
            {"from": 50, "to": 65, "qualification": 3},
            {"from": 20, "to": 50, "qualification": 2},
            {"from": -0.9, "to": 20, "qualification": 1}
        ]

        return MetricCalculate.__calculer(qualification, ranges)

    @staticmethod
    def hostsPotsSeverityPoints(hpot_low:int, hpot_medium:int, hpot_high:int)->int:
        if hpot_high > 0:
            return 1
        
        if hpot_medium > 0:
            return 2
        
        if hpot_low > 0:
            return 3
        
        return 5

    @staticmethod
    def cognitiveComplexityPoints(complex: float)->int:
        ranges = [
            {"from": -0.9, "to": 0.5, "qualification": 5},
            {"from": 0.5, "to": 0.75, "qualification": 4},
            {"from": 0.75, "to": 1, "qualification": 3},
            {"from": 1, "to": 1.25, "qualification": 2},
            {"from": 1.25, "to": float('inf'), "qualification": 1},
        ]

        return MetricCalculate.__calculer(complex, ranges)

    @staticmethod
    def complexityPoints(complex: float)->int:
        ranges = [
            {"from": -0.1, "to": 1.5, "qualification": 5},
            {"from": 1.5, "to": 2, "qualification": 4},
            {"from": 2, "to": 2.5, "qualification": 3},
            {"from": 2.5, "to": 3, "qualification": 2},
            {"from": 3, "to": float('inf'), "qualification": 1},
        ]

        return MetricCalculate.__calculer(complex, ranges)
    
    def __calculer(value, ranges: dict)->int:        
        for range in ranges:
            if value > range['from'] and value <= range['to']:
                return range['qualification']                
    
    @staticmethod
    def commentsDensityPoints(value: float)->int:  #verificar métricas

        ranges = [
            {"from": -0.9, "to": 10, "qualification": 5},
            {"from": 10, "to": 20, "qualification": 4},
            {"from": 20, "to": 25, "qualification": 3},
            {"from": 25, "to": 35, "qualification": 2},
            {"from": 35, "to": float('inf'), "qualification": 1},
        ]

        return MetricCalculate.__calculer(value, ranges)        

    @staticmethod        
    def severityPoints(bugs):
        if bugs['blocker'] > 0:
            return 1
        if bugs['critical'] > 0:
            return 2
        if bugs['major'] > 0:
            return 3
        if bugs['minor'] > 0:
            return 4
        
        return 5
    

    @staticmethod
    def bugAnscodeSmellsAveragePoints(value: float)->int:
        ranges = [
            {"from": -0.9, "to": 0, "qualification": 5},
            {"from": 0, "to": 1, "qualification": 4},
            {"from": 1, "to": 4, "qualification": 3},
            {"from": 4, "to": 10, "qualification": 2},
            {"from": 10, "to": float('inf'), "qualification": 1},
        ]

        return MetricCalculate.__calculer(value, ranges)    
    
    @staticmethod        
    def duplicatedLinesDensityPoints(value: int): #verificar métricas

        ranges = [
            {"from": -0.9, "to": 0, "qualification": 5},
            {"from": 0, "to": 2, "qualification": 4},
            {"from": 2, "to": 3, "qualification": 3},
            {"from": 3, "to": 6, "qualification": 2},
            {"from": 6, "to": float('inf'), "qualification": 1},
        ]

        return MetricCalculate.__calculer(value, ranges)
    
    @staticmethod        
    def fortifySeverityPoints(bugs):
        if bugs[FortifyBugType.CRITICAL.value] > 0:
            return 1
        if bugs[FortifyBugType.HIGH.value] > 0:
            return 2
        if bugs[FortifyBugType.MEDIUM.value] > 0:
            return 3
        if bugs[FortifyBugType.LOW.value] > 0:
            return 4
        
        return 5
    
    @staticmethod
    def fortifyTotalPoints(total_bugs: int)->int:
        ranges = [
            {"from": -0.9, "to": 0, "qualification": 5},
            {"from": 0, "to": 2, "qualification": 4},
            {"from": 2, "to": 5, "qualification": 3},
            {"from": 5, "to": 10, "qualification": 2},
            {"from": 10, "to": float('inf'), "qualification": 1},
        ]

        return MetricCalculate.__calculer(total_bugs, ranges)

    @staticmethod
    def penaltyCalc(metric_value: float, metric_limit)->float:
        return -0.5 if metric_value >= metric_limit else 0.0
