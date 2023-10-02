import os
import sys

class PathManage():
    allowed_extensions = ('csv', 'xlsx')

    @staticmethod
    def getFirstFilePath(path_directory: str)->str:
        try:
            files = os.listdir(path_directory)
            for file in files:
                if PathManage.validateExtension(PathManage, file): 
                    path = path_directory + file                    
                    break

            return path.replace('\\', '/')
        except ValueError:
            print("No se pudo seleccionar el archivo correctamente")
            sys.exit()

    @staticmethod
    def getAllFilesPath(path_directory: str)->dict:
        try:
            paths: dict = []

            files = os.listdir(path_directory)

            for file in files:  
                if PathManage.validateExtension(PathManage, file):
                    data = {'name': file, 'extension': PathManage.getExtension(PathManage, file), 'full_path': path_directory + file}
                    paths.append(data)

            return paths
            
        except ValueError:
            print("No se pudo seleccionar el archivo correctamente")
            sys.exit()

    def deleteDirFiles(self, DIR_PATH: str)->None:        
        for f in os.listdir(DIR_PATH):
            os.remove(os.path.join(DIR_PATH, f))

    
    def validateExtension(self, file: str)->bool:
        extension = self.getExtension(self, file)
        if len(extension) < 2:
            return False
        
        if extension in self.allowed_extensions:            
            return True
        
        return False     
    
    def getExtension(self, file):
        return file.split('.')[-1]
        