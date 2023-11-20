import sys
from cloud_development.app.RunModel import RunModel

period:str = sys.argv[1]

process = RunModel(period)

process.run()
