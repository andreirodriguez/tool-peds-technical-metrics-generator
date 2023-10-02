import pandas as pd
from repo.RepoInterface import RepoInterface

from repo.QuizRepo import QuizRepo
from repo.FortifyRepo import FortifyRepo
from repo.MaturityLevelRepo import MaturityLevelRepo
from repo.PullRequestRepo import PullRequestRepo
from repo.SonarRepo import SonarRepo
from repo.BaseActivosRepo import BaseActivosRepo
from repo.BaseActivos_QuizRepo import BaseActivosQuizRepo
from repo.DetailRepo import DetailRepo

class Storage:
    def base_activos(self, *args, **kwargs)->RepoInterface:
        return self.__parser(BaseActivosRepo(*args, **kwargs))        

    def activos_and_quiz(self, *args, **kwargs)->RepoInterface:
        return self.__parser(BaseActivosQuizRepo(*args, **kwargs))
    
    def sonar(self, *args, **kwargs)->RepoInterface:
        return self.__parser(SonarRepo(*args, **kwargs))
    
    def maturity_level(self, *args, **kwargs)->RepoInterface:
        return MaturityLevelRepo(*args, **kwargs)
    
    def pull_request(self, *args, **kwargs)->RepoInterface:
        return self.__parser(PullRequestRepo(*args, **kwargs))
    
    def fortify(self, *args, **kwargs)->RepoInterface:
        return self.__parser(FortifyRepo(*args, **kwargs))
    
    def quiz(self, *args, **kwargs)->RepoInterface:
        return self.__parser(QuizRepo(*args, **kwargs))    
    
    def pr_detail(self, *args, **kwargs)->RepoInterface:
        return self.__parser(DetailRepo(*args, **kwargs))

    def __parser(self, cls: RepoInterface)->RepoInterface:
        return cls
    