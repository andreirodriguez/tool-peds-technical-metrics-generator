class RedisCache():
    def __init__(self,id:str,subscriptionId:str,resourceGroup:str,location:str,name:str, type:str,
                 state:str,version:str,hostName:str
                 ):
        self.id = id
        self.subscriptionId = subscriptionId
        self.resourceGroup = resourceGroup
        self.location = location
        self.name = name
        self.type = type

        self.state = state
        self.version = version
        self.hostName = hostName