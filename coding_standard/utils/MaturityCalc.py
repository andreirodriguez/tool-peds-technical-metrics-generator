class MaturityCalc:
    #PRINCIPAL METRICS
    TECNICAL_MATURITY_WEIGTH            = 0.85
    ADOCTION_KNOWLEDGE_WEIGHT           = 0.15

    #SUB METRICS
    CLEAN_CODE_WEIGHT                   = 0.45
    MAINTAINABILITY_RESILIENCE_WEIGHT   = 0.10
    SECURITY_WEIGHT                     = 0.30

    def cleanCodeCal(self, c_smell_diff_points, c_smell_overall_points, c_smell_severity_points, bug_diff_points, bug_overall_points, bug_severity_points):
        # PRINCIPAL WEIGHTS
        CODE_SMELL_TOTAL_WEIGHT     = 0.40
        CODE_SMELL_SEVERITY_WEIGHT  = 0.10
        BUGS_TOTAL_WEIGHT           = 0.40
        BUGS_SEVERITY_WEIGHT        = 0.10

        # SUB WEIGHTS
        CODE_SMELL_DIFF_WEIGHT      = 1
        CODE_SMELL_OVERALL_WEIGHT   = 0

        BUG_DIFF_WEIGHT             = 1
        BUG_OVERALL_WEIGHT          = 0

        c_smell_diff_maturity       = CODE_SMELL_DIFF_WEIGHT * c_smell_diff_points
        c_smell_overall_maturity    = CODE_SMELL_OVERALL_WEIGHT * c_smell_overall_points
        c_smells_total_maturity     = (c_smell_diff_maturity + c_smell_overall_maturity) * CODE_SMELL_TOTAL_WEIGHT

        c_smell_severity_maturity   = CODE_SMELL_SEVERITY_WEIGHT * c_smell_severity_points

        bug_diff_maturity           = BUG_DIFF_WEIGHT * bug_diff_points
        bug_overall_maturity        = BUG_OVERALL_WEIGHT * bug_overall_points
        bug_total_maturity          = (bug_diff_maturity + bug_overall_maturity) * BUGS_TOTAL_WEIGHT

        bugs_severity_maturity      = BUGS_SEVERITY_WEIGHT * bug_severity_points

        return (c_smells_total_maturity + c_smell_severity_maturity + bug_total_maturity + bugs_severity_maturity) * self.CLEAN_CODE_WEIGHT

    def maintainabilityAndResilience(self, comment_lines_dens_points, duplicate_lines_density_points, cyclomatic_diff_complex_points, cognitive_diff_complex_points, cyclomatic_overall_points, cognitive_overall_points):
        COMMENT_LINES_DENSITY_WEIGHT        = 0.05
        DUPLICATE_LINES_WEIGHT              = 0.15
        CYCLOMATIC_COMPLEXITY_WEIGHT        = 0.40
        COGNITIVE_COMPLEXITY_WEIGHT         = 0.40

        # SUB WEIGHTS
        CYCLOMATIC_COMPLEXITY_DIFF_WEIGHT   = 0
        CYCLOMATIC_COMPLEXITY_OVERALL_WEIGHT= 1

        COGNITIVE_COMPLEXITY_DIFF_WEIGHT    = 0
        COGNITIVE_COMPLEXITY_OVERALL_WEIGHT = 1

        comment_lines_maturity              = COMMENT_LINES_DENSITY_WEIGHT * comment_lines_dens_points
        duplicate_lines_maturity            = DUPLICATE_LINES_WEIGHT * duplicate_lines_density_points

        diff_cyclomatic_complex_maturity    = CYCLOMATIC_COMPLEXITY_DIFF_WEIGHT * cyclomatic_diff_complex_points
        diff_cognitive_complex_maturity     = COGNITIVE_COMPLEXITY_DIFF_WEIGHT * cognitive_diff_complex_points
        
        overall_cyclomatic_points           = CYCLOMATIC_COMPLEXITY_OVERALL_WEIGHT * cyclomatic_overall_points
        overall_cognitive_points            = COGNITIVE_COMPLEXITY_OVERALL_WEIGHT * cognitive_overall_points

        final_cyclomatic_maturity           = CYCLOMATIC_COMPLEXITY_WEIGHT * (diff_cyclomatic_complex_maturity + overall_cyclomatic_points)
        final_cognitive_maturity            = COGNITIVE_COMPLEXITY_WEIGHT * (diff_cognitive_complex_maturity + overall_cognitive_points)

        return (comment_lines_maturity + duplicate_lines_maturity + final_cyclomatic_maturity + final_cognitive_maturity) * self.MAINTAINABILITY_RESILIENCE_WEIGHT

    def securityCalc(self, sec_hostpot_severity_points, sec_hostpot_total_points, fortify_severity_points, fortify_total_bugs_points):
        SECURITY_HOSTPOT_TOTAL_WEIGHT       = 0.20
        SECURITY_HOSTPOT_SEVERITY_WEIGHT    = 0.20
        FORTIFY_TOTAL_BUGS                  = 0.35
        FORTIFY_SEVERITY_BUGS               = 0.25
        
        security_hostpot_severity_maturity  = SECURITY_HOSTPOT_SEVERITY_WEIGHT * sec_hostpot_severity_points
        security_hostpot_issues_maturity    = SECURITY_HOSTPOT_TOTAL_WEIGHT * sec_hostpot_total_points

        fortify_severity_maturity           = FORTIFY_SEVERITY_BUGS * fortify_severity_points
        fortify_bugs_maturity               = FORTIFY_TOTAL_BUGS * fortify_total_bugs_points

        return (security_hostpot_severity_maturity + security_hostpot_issues_maturity + fortify_severity_maturity + fortify_bugs_maturity) * self.SECURITY_WEIGHT
    
    def tecnicalMaturityCal(self, tecnical_maturity_avg:float)->float:
        return tecnical_maturity_avg * self.TECNICAL_MATURITY_WEIGTH

    def adoptionKnowledgeCalculate(self, standards_points:float, principles_and_patters_points:float)->float:
        STANDARS                    = 0.50
        PRINCIPLES                  = 0.50

        standards_maturity          = standards_points * STANDARS
        principles_and_patters      = principles_and_patters_points * PRINCIPLES

        return (standards_maturity + principles_and_patters)