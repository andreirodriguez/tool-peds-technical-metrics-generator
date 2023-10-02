import sys
import assets.base_activos.base_activos_utils as base_activos_utils
import assets.base_activos.squad_priorizados_utils as squad_priorizados_utils
import assets.base_activos.team_members_utils as team_members_utils
import assets.base_activos.pull_requests_utils as pull_requests_utils
import assets.base_activos.data_process_project_utils as data_process_project_utils
import assets.base_activos.utils as utils

def execute(period):
    base = base_activos_utils.getBaseActivos()
    
    base_activos_utils.setExcelFiltered(base,period)

    squads = squad_priorizados_utils.getValidationSquads(base)

    squad_priorizados_utils.setExcelSummary(squads)

    projects = data_process_project_utils.getProjectsScope()

    team_members_prs = pull_requests_utils.getTeamMembersPullRequests(projects)

    team_members = team_members_utils.getValidationTeamMembers(base,team_members_prs)

    team_members_utils.setExcelReport(team_members)

period:str = sys.argv[1]

execute(period)