import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

from cloud_development.app.common.Utils import Utils
import cloud_development.app.common.Constants as Constants

class BaseActivosRepository():

    def getBaseByPeriod(self,period:str)->pd.DataFrame:
        file:str = Utils.getPathDirectory(Constants.PATH_OUTPUT_BASE_ACTIVOS.format(period=period))

        usecols:list[str]=["matricula","nombre","apellido_paterno","apellido_materno","correo",
                             "tribu_code","tribu","squad_code","squad","cod_app","especialidad","flag_activo"]

        data:pd.DataFrame = pd.read_excel(file,usecols=usecols)
        data = data.astype(object).where(pd.notnull(data),None)

        data = data.rename(columns={
            "matricula":"employeeCode",
            "nombre":"name",
            "apellido_paterno":"fatherLastName",
            "apellido_materno":"motherLastName",
            "correo":"email",
            "tribu_code":"tribeCode",
            "tribu":"tribe",
            "squad_code":"squadCode",
            "squad":"squad",
            "cod_app":"appCode",
            "especialidad":"specialty",
            "flag_activo":"flagActive"
        })

        data = data[(data['flagActive'].isin(Constants.BASE_ACTIVOS_FLAGS_ACTIVE_COE))]

        data = data.sort_values(["employeeCode","squadCode"], ascending = [True, False])

        return data
