PATH_INPUT_BASE_ACTIVOS:str = "cloud_development\\resources\\input\\base_activos\\base_activos_{period}.xlsx"
PATH_INPUT_SONAR:str = "cloud_development\\resources\\input\\sonar\\"
PATH_INPUT_AZURE_MONITOR:str = "cloud_development\\resources\\input\\azure_monitor\\"

PATH_INPUT_ASSESMENT_AZURE_SQL:str = "cloud_development\\resources\\input\\assesments\\azure_sql\\"
PATH_INPUT_ASSESMENT_CACHE_REDIS:str = "cloud_development\\resources\\input\\assesments\\cache_redis\\"
PATH_INPUT_ASSESMENT_COSMOS_DB:str = "cloud_development\\resources\\input\\assesments\\cosmos_db\\"

AZURE_MONITOR_FILE_AZURE_SQL:str = "sql-databases.csv"
AZURE_MONITOR_FILE_REDIS_CACHE:str = "redis-caches.csv"
AZURE_MONITOR_FILE_COSMOS_DB:str = "cosmos-dbs.csv"

BASE_ACTIVOS_FLAGS_ACTIVE_COE:list[str] = ["ACTIVO COE"]

ASSESMENT_METRICS_AZURE_SQL:list[str] = ["normalizacion","performance","querys","transactional","poolConexion","estandarConexion"]
ASSESMENT_METRICS_CACHE_REDIS:list[str] = ["estructura","performance","casosUso","reactividad","estandarConexion","poolConexion"]
ASSESMENT_METRICS_COSMOS_DB:list[str] = ["desnormalizacion","performance","querys","insertions","estandarConexion"]

FORMAT_DATETIME_SONAR:str = "%Y-%m-%dT%H:%M:%S-%f"


URL_BASE_BITBUCKET_REPO:str = "https://bitbucket.lima.bcp.com.pe/scm/"

SERVICE_CLOUD_AZURE_SQL:str = "azureSql"
SERVICE_CLOUD_CACHE_REDIS:str = "cacheRedis"
SERVICE_CLOUD_COSMOS_DB:str = "cosmosDb"

METRIC_SONAR_CONNECTION_POOL:str = "connectionPool"