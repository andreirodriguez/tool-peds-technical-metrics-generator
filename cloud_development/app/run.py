import sys
from cloud_development.app.common.Utils import Utils
from cloud_development.app.RunScopePractice import RunScopePractice
from cloud_development.app.RunModel import RunModel

processDate:str = sys.argv[1]

process = RunModel(processDate)

process.run()
