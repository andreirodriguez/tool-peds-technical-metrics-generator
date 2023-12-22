import sys
from cloud_development.app.common.Utils import Utils
from cloud_development.app.RunScopePractice import RunScopePractice
from cloud_development.app.RunModel import RunModel

period:str = sys.argv[1]

process = RunScopePractice(period)

process.run()
