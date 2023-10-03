import sys
from cloud_development.app.RunProcess import RunProcess
from cloud_development.app.common.Utils import Utils

period:str = "202310"
#period:str = sys.argv[1]

runProcess:RunProcess = RunProcess(period)

runProcess.run()
