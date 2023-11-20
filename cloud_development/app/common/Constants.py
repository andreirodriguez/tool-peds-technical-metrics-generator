PATH_INPUT_BASE_ACTIVOS:str = "cloud_development\\resources\\input\\base_activos\\base_activos_{period}.xlsx"
PATH_INPUT_SONAR:str = "cloud_development\\resources\\input\\sonar\\"
PATH_INPUT_AZURE_MONITOR:str = "cloud_development\\resources\\input\\azure_monitor\\"

PATH_INPUT_ASSESMENT_AZURE_SQL:str = "cloud_development\\resources\\input\\assesments\\azure_sql\\"
PATH_INPUT_ASSESMENT_CACHE_REDIS:str = "cloud_development\\resources\\input\\assesments\\cache_redis\\"
PATH_INPUT_ASSESMENT_COSMOS_DB:str = "cloud_development\\resources\\input\\assesments\\cosmos_db\\"

PATH_INPUT_METRIC_AZURE_SQL_TABLE_COLUMNS:str = "cloud_development\\resources\\input\\azure_monitor\\{tenantId}\\{subscriptionId}\\{resourceGroup}\\azure-sql\\{sqlServer}({sqlDatabase})\\table-columns-azure-sql.csv"
PATH_INPUT_METRIC_AZURE_SQL_ADVISOR_RECOMMENDEDS:str = "cloud_development\\resources\\input\\azure_monitor\\{tenantId}\\{subscriptionId}\\{resourceGroup}\\azure-sql\\{sqlServer}({sqlDatabase})\\advisor-recommendeds-azure-sql.csv"
PATH_INPUT_METRIC_AZURE_SQL_TOP_QUERIES:str = "cloud_development\\resources\\input\\azure_monitor\\{tenantId}\\{subscriptionId}\\{resourceGroup}\\azure-sql\\{sqlServer}({sqlDatabase})\\top-queries-azure-sql.csv"
PATH_INPUT_METRIC_AZURE_SQL_MONITOR_METRICS:str = "cloud_development\\resources\\input\\azure_monitor\\{tenantId}\\{subscriptionId}\\{resourceGroup}\\azure-sql\\{sqlServer}({sqlDatabase})\\monitor-metrics-azure-sql.csv"

PATH_INPUT_METRIC_REDIS_CACHE_MONITOR_METRICS:str = "cloud_development\\resources\\input\\azure_monitor\\{tenantId}\\{subscriptionId}\\{resourceGroup}\\redis-cache\\{redisCache}\\monitor-metrics-redis-cache.csv"

PATH_INPUT_METRIC_COSMOS_DB_MONITOR_METRICS:str = "cloud_development\\resources\\input\\azure_monitor\\{tenantId}\\{subscriptionId}\\{resourceGroup}\\cosmos-db\\{cosmosDb}\\monitor-metrics-cosmos-db.csv"

PATH_INPUT_SQUADS_PRIORIZADOS:str = "cloud_development\\resources\\input\\squads_priorizados\\squads_priorizados.xlsx"
PATH_INPUT_SQUADS_PRIORIZADOS_HOJA_AZURE_SQL:str = "CLOUD SQL"
PATH_INPUT_SQUADS_PRIORIZADOS_HOJA_AZURE_REDIS:str = "CLOUD REDIS"
PATH_INPUT_SQUADS_PRIORIZADOS_HOJA_AZURE_COSMOS:str = "CLOUD COSMOS"
PATH_INPUT_SQUADS_PRIORIZADOS_HOJA_AZURE_GENERAL:str = "GENERAL"

AZURE_MONITOR_FILE_AZURE_SQL:str = "sql-databases.csv"
AZURE_MONITOR_FILE_REDIS_CACHE:str = "redis-caches.csv"
AZURE_MONITOR_FILE_COSMOS_DB:str = "cosmos-dbs.csv"

PATH_OUTPUT_FILE_SUMMARY:str = "cloud_development\\resources\\output\\{period}-cloud-development-maturity-level-by-squad-summary.xlsx"

AZURE_MONITOR_AZURE_SQL_METRICS:list[str] = ["tablesDenormalized","topConsumptionQueries","advisorsRecommended","deadlock","connectionFailed"]
AZURE_MONITOR_AZURE_SQL_ADVISORS_RECOMMENDED_STATES:list[str] = ["Active","Pending"]
AZURE_MONITOR_AZURE_SQL_METRIC_DEADLOCK:str = "deadlock"
AZURE_MONITOR_AZURE_SQL_METRIC_CONNECTION_SUCCESSFUL:str = "connection_successful"
AZURE_MONITOR_AZURE_SQL_METRIC_CONNECTION_FAILED:str = "connection_failed"

AZURE_MONITOR_AZURE_REDIS_METRICS:list[str] = ["cacheMissRate","maximumProcessorConsumption","maximumMemoryConsumption"]
AZURE_MONITOR_AZURE_REDIS_METRIC_CACHE_MISS_RATE:str = "cachemissrate"
AZURE_MONITOR_AZURE_REDIS_METRIC_CACHE_HITS:str = "cachehits"
AZURE_MONITOR_AZURE_REDIS_METRIC_CACHE_MISSES:str = "cachemisses"
AZURE_MONITOR_AZURE_REDIS_METRIC_PERCENT_PROCESSOR:str = "percentProcessorTime"
AZURE_MONITOR_AZURE_REDIS_METRIC_MEMORY_PERCENTAGE:str = "usedmemorypercentage"

AZURE_MONITOR_AZURE_COSMOS_METRICS:list[str] = ["maximumRusConsumption"]
AZURE_MONITOR_AZURE_COSMOS_METRIC_RU_CONSUMPTION:str = "NormalizedRUConsumption"

BASE_ACTIVOS_FLAGS_ACTIVE_COE:list[str] = ["ACTIVO COE"]

ASSESMENT_METRICS_AZURE_SQL:list[str] = ["normalizedAssesment","performanceAssesment","querysAssesment","transactionalAssesment","connectionPoolAssesment","standardConnectionAssesment"]
ASSESMENT_METRICS_CACHE_REDIS:list[str] = ["structureAssesment","performanceAssesment","useCaseAssesment","reactivityAssesment","standardConnectionAssesment","connectionPoolAssesment"]
ASSESMENT_METRICS_COSMOS_DB:list[str] = ["denormalizationAssesment","performanceAssesment","querysAssesment","insertionsAssesment","standardConnectionAssesment"]

FORMAT_DATETIME_SONAR:str = "%Y-%m-%dT%H:%M:%S-%f"

URL_BASE_BITBUCKET_REPO:str = "https://bitbucket.lima.bcp.com.pe/scm/"

SERVICE_CLOUD_AZURE_SQL:str = "azureSql"
SERVICE_CLOUD_CACHE_REDIS:str = "cacheRedis"
SERVICE_CLOUD_COSMOS_DB:str = "cosmosDb"

METRIC_SONAR_CONNECTION_POOL:str = "connectionPool"

METRIC_SONAR_POINTS_MAXIMUM:float = 5.00
METRIC_SONAR_POINTS_MINIMUM:float = 1.00