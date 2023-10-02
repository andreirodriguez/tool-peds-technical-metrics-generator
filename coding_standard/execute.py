import sys
from config.headers_detail_report import DETAIL_HEADERS
from config.headers_squad_report import SQUAD_HEADERS
from repo.Storage import Storage
from utils.constants import OUTPUT_BY_SQUAD_FILE, OUTPUT_BY_SQUAD_FILE_ANDROID, OUTPUT_BY_SQUAD_FILE_BACKEND, OUTPUT_BY_SQUAD_FILE_IOS, OUTPUT_BY_SQUAD_FILE_WEB, OUTPUT_DETAIL_FILE
from reports.PullRequestReport import PullRequestReport
from reports.SquadReport import SquadReport
from utils.GlobalTypes import Especialty
from utils.TimestampsCalc import TimestampsCalc

if __name__ == '__main__':    

    print('CARGANDO DATA....')

    period = sys.argv[1]
    tmp = TimestampsCalc()
    tmp.set_period(period)
    period = f"{tmp.get_year}{tmp.get_month}"

    storage = Storage()

    reports = [
        PullRequestReport(OUTPUT_DETAIL_FILE.format(period), storage, tmp, DETAIL_HEADERS),
        SquadReport(OUTPUT_BY_SQUAD_FILE.format(period), storage, Especialty.ALL, SQUAD_HEADERS),
        SquadReport(OUTPUT_BY_SQUAD_FILE_ANDROID.format(period), storage, Especialty.FRONTEND_ANDROID, SQUAD_HEADERS),
        SquadReport(OUTPUT_BY_SQUAD_FILE_IOS.format(period), storage, Especialty.FRONEND_IOS, SQUAD_HEADERS),
        SquadReport(OUTPUT_BY_SQUAD_FILE_WEB.format(period), storage, Especialty.FRONTEND_WEB, SQUAD_HEADERS),
        SquadReport(OUTPUT_BY_SQUAD_FILE_BACKEND.format(period), storage, Especialty.BACKEND_JAVA, SQUAD_HEADERS)
    ]

    for report in reports:        
        df = report.toDataframe()
        report.to_csv(df)