import sys
from cloud_development.app.RunProcess import RunProcess
from cloud_development.app.RunAssesment import RunAssesment

#period:str = sys.argv[1]
period:str = "202309"

process = RunAssesment(period)

process.run()
