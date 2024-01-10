import sys
from cloud_development.app.common.Utils import Utils
from cloud_development.app.RunScopePractice import RunScopePractice
from cloud_development.app.RunModel import RunModel
from cloud_development.app.RunAccountability import RunAccountability

processDate:str = sys.argv[1]

process = RunAccountability(processDate)

process.run()
