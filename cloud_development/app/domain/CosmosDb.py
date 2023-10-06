class CosmosDb():
    def __init__(self,id:str,subscriptionId:str,resourceGroup:str,location:str,name:str, type:str,kind:str,
                 state:str,documentEndpoint:str,enabledApiTypes:str,databaseAccountOfferType:str,minimalTlsVersion:str
                 ):
        self.id = id
        self.subscriptionId = subscriptionId
        self.resourceGroup = resourceGroup
        self.location = location
        self.name = name
        self.type = type
        self.kind = kind

        self.state = state
        self.documentEndpoint = documentEndpoint
        self.enabledApiTypes = enabledApiTypes
        self.databaseAccountOfferType = databaseAccountOfferType
        self.minimalTlsVersion = minimalTlsVersion