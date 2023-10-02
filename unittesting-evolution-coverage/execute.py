import sys

import pandas as pd
from pandas.tseries.offsets import MonthEnd

from os import listdir,path
import datetime
import numpy as np

pathDir = path.dirname(path.abspath(__file__)) + "\\"

def getPathDirectory(newDir):
    pathDirectory = pathDir + newDir

    return pathDirectory

def getAplications():
    print("Leo excel portafolio")

    xlsApp=pd.read_excel(getPathDirectory("input\\Portafolio\\Portafolio.xlsx"),sheet_name="Aplicaciones",usecols=[0,4],names=['COD_APP','ESTADO'])

    return xlsApp

def getFileDevSecOps(file):
    print("Leo excel DevSecOps: " + file)

    period = file[:6]
    year = int(period[0:4])
    month = int(period[4:6])
    date = datetime.datetime(year, month, 1,23,59,59)
    dateChangeReport = datetime.datetime(2022,10, 1,0,0,0) + MonthEnd(0)

    xlsSonar = None

    if(date > dateChangeReport):
        xlsSonar = pd.read_excel(getPathDirectory("input\\DevSecOps\\" + file),sheet_name=0,header=2,usecols=[0,1,2,3,4,5,6],names=['APPLICATION','PROJECT','REPOSITORY','VERSION','METRIC','VALUE','DATE OF ANALYSIS'])
        xlsSonar['DATE OF ANALYSIS'] = xlsSonar['DATE OF ANALYSIS'].apply(lambda x: pd.to_datetime(x,format="%d/%m/%Y %H:%M:%S").to_datetime64())    
    else:
        xlsSonar = pd.read_excel(getPathDirectory("input\\DevSecOps\\" + file),sheet_name='Sonar Report - Main',usecols=['APPLICATION','PROJECT','REPOSITORY','VERSION','METRIC','VALUE','DATE OF ANALYSIS'])
        xlsSonar['DATE OF ANALYSIS'] = xlsSonar['DATE OF ANALYSIS'].apply(lambda x: pd.to_datetime(x).to_datetime64())    

    xlsSonar['METRIC'] = xlsSonar['METRIC'].apply(lambda x: str(x).upper())

    xlsSonar = xlsSonar[(xlsSonar['METRIC']=='COVERAGE (%) [D]') | (xlsSonar['METRIC']=='COVERAGE')]

    xlsSonar['VALUE'] = xlsSonar['VALUE'].apply(lambda x: float(x))

    fileDate = datetime.datetime(year, month, 1,23,59,59) + MonthEnd(0)

    xlsSonar['FILE_DATE'] = fileDate

    return xlsSonar

def getFileConsolidated():
    print("INICIO a leer excel consolidado de SONAR")

    xlsConsolidated = pd.DataFrame({'APPLICATION': [],'PROJECT': [],'REPOSITORY':[],'VERSION': [],'METRIC': [],'VALUE': [], 'DATE OF ANALYSIS': []})

    files = [x for x in listdir(getPathDirectory("input\\DevSecOps"))]

    for file in files:
        if (file.endswith(".xlsx")==False): continue

        xlsSonar = getFileDevSecOps(file)

        xlsConsolidated = pd.concat([xlsConsolidated, xlsSonar], ignore_index=True)        

    print("FIN a leer excel consolidado de SONAR")

    return xlsConsolidated

def getReportSonarMonthly(xlsPortafolio,xlsConsolidated,date):
    # VALIDANDO CONSISTENCIA DE FECHAS
    xlsReport = xlsConsolidated[xlsConsolidated['DATE OF ANALYSIS']<= xlsConsolidated['FILE_DATE']]

    # ELIMINANDO REGISTROS SIN APP
    xlsReport = xlsReport[~xlsReport['APPLICATION'].isna()]
    xlsReport = xlsReport[~xlsReport['VERSION'].isna()]

    # FILTRANDO REGISTROS DE UN MES
    xlsReport = xlsReport[xlsReport['FILE_DATE']<=date]

    # SOLO REGISTROS DE CERTIFICACION CON RELEASE CANDIDATE
    xlsReport = xlsReport[xlsReport['VERSION'].str.contains("-RC-")]

    # ORDENO POR APLICACION PROYECTO Y FECHA DE ANALISIS, Y ME QUEDO CON LA MAS RECIENTE
    xlsReport = xlsReport.sort_values(['APPLICATION','PROJECT','DATE OF ANALYSIS'], ascending = [True, True, False])
    xlsReport = xlsReport.drop_duplicates(['APPLICATION','PROJECT'],keep='first')

    # ELIMINANDO APP NO VIGENTES
    xlsReport = pd.merge(xlsReport,xlsPortafolio, left_on='APPLICATION', right_on='COD_APP',how='left')
    xlsReport = xlsReport[(~xlsReport['ESTADO'].isna()) & (xlsReport['ESTADO']!='No Vigente')]

    return xlsReport

def executeReportMonthly(xlsPortafolio,xlsConsolidated,date):
    date = datetime.datetime(date.year, date.month, 1,23,59,59) + MonthEnd(0)
    file = getPathDirectory("output\\" + date.strftime('%Y%m') + " .ReporteSonarDevSecOps-QG.xlsx")

    xlsReport = getReportSonarMonthly(xlsPortafolio,xlsConsolidated,date)

    xlsReport.to_excel(file,sheet_name="Report",columns=["APPLICATION","PROJECT","REPOSITORY","VERSION","METRIC","VALUE","DATE OF ANALYSIS","FILE_DATE","ESTADO"],index=False)

    print("Reporte exportado a Excel: " + date.strftime('%Y%m%d') + " en la ruta: " + file)

def execute(periods):
    print("INICIO del proceso para generar los reportes")

    xlsPortafolio = getAplications()       
    xlsConsolidated = getFileConsolidated()

    for period in periods:        
        year = int(period[0:4])
        month = int(period[4:6])
        
        date = datetime.datetime(year,month,1)

        executeReportMonthly(xlsPortafolio,xlsConsolidated,date)

    print("FIN del proceso para generar los reportes")

# RUN PROJECT
#python -m unittesting-evolution-coverage.execute 202201,202202,202203,202204,202205,202206,202207,202208,202209,202210,202211,202212,202301,202302,202303

periods:str = sys.argv[1].split(",")

execute(periods)
