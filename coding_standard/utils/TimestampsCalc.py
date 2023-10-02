from datetime import datetime

class TimestampsCalc:
    
    __year    : int
    __month   : int  
    __day     : int    
    __period  : str  
    
    def set_period(self, period)->None:
        self.__period  = period

    @property
    def current_date_formated(self)->str:
        current_date = datetime.now()
        month        = '0' + str(current_date.month) if current_date.month < 10 else str(current_date.month)
        return str(current_date.day) + '/' + month + '/' + str(current_date.year)
    
    @property
    def first_day_custom_date(self)->str:
        self.__set_period()        
        return '01/' + self.__month + '/' + str(self.__year)

    def __set_period(self)->None:
        self.__year  = self.__period[:4]
        self.__month  = self.__period[-4:-2]
        self.__day  = self.__period[-2:]
    
    @property
    def get_month(self)->str:
        self.__set_period()
        return self.__month
    
    @property
    def get_year(self)->str:
        self.__set_period()
        return self.__year
    
    @property
    def get_day(self)->str:
        self.__set_period()
        return self.__day
    
    @staticmethod
    def set_dataframe_date(date: str, separator: str)->datetime.date:       
        date_str = str(date).rsplit(separator)
        year_str = date_str[2].split(' ')
        time_str = year_str[1].split(':')        

        return datetime(int(year_str[0]), int(date_str[1]), int(date_str[0]), int(time_str[0]), int(time_str[1]))