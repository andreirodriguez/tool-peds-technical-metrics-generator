from enum import Enum

class Especialty(Enum):
    ALL              = 'ALL'
    BACKEND_JAVA     = 'BACKEND JAVA'
    FRONTEND_WEB     = 'FRONTEND WEB'
    FRONTEND_ANDROID = 'FRONTEND ANDROID'
    FRONEND_IOS      = 'FRONTEND IOS'

class IssueSeverityType(Enum):
    INFO     = 'INFO'
    MAJOR    = 'MAJOR'
    MINOR    = 'MINOR'
    CRITICAL = 'CRITICAL'
    BLOCKER  = 'BLOCKER'

class SeverityType(Enum):
    BUG         = 'bug_severity'
    CODE_SMELL  = 'code_smell_severity'

class HostsPotsType(Enum):
    HIGHT   = 'HIGH'
    MEDIUM  = 'MEDIUM'
    LOW     = 'LOW'

class FortifyBugType(Enum):
    CRITICAL = 'critical'
    HIGH     = 'high'
    MEDIUM   = 'medium'
    LOW      = 'low'