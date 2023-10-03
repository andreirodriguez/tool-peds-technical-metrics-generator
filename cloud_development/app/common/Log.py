from os import getcwd

def getLog() -> str:
    dir = getcwd()
    
    return dir + "\\cloud_development\\resources\\log\\metrics-model-cloud-development.log"

def getLogFormat() -> str:
    return "%(asctime)s - %(levelname)s - %(message)s"

def getLogDateFormat() -> str:
    return "%Y-%m-%d %H:%M:%S"   