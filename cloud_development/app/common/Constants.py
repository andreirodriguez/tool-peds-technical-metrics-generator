PATH_OUTPUT_BASE_ACTIVOS:str = "cloud_development\\resources\\input\\base_activos\\base_activos_{period}.xlsx"



BASE_ACTIVOS_FLAGS_ACTIVE_COE:list[str] = ["ACTIVO COE"]

ASSESMENT_PATH_AZURE_SQL:str = "cloud_development\\resources\\input\\assesments\\azure_sql\\"
ASSESMENT_PATH_CACHE_REDIS:str = "cloud_development\\resources\\input\\assesments\\cache_redis\\"
ASSESMENT_PATH_COSMOS_DB:str = "cloud_development\\resources\\input\\assesments\\cosmos_db\\"

ASSESMENT_METRICS_AZURE_SQL:list[str] = ["normalizacion","performance","querys","transactional","poolConexion","estandarConexion"]
ASSESMENT_METRICS_CACHE_REDIS:list[str] = ["estructura","performance","casosUso","reactividad","estandarConexion","poolConexion"]
ASSESMENT_METRICS_COSMOS_DB:list[str] = ["desnormalizacion","performance","querys","insertions","estandarConexion"]