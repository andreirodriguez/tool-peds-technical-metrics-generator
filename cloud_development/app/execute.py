import sys
from cloud_development.app.RunProcess import RunProcess

period:str = "202310"
#period:str = sys.argv[1]

runProcess:RunProcess = RunProcess(period)

runProcess.run()
