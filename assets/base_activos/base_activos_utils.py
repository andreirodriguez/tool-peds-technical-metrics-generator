import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

from assets.base_activos.utils import getPathDirectory,getCodeSquadTribe,getStringUpperStrip,isNullOrEmpty,getStringLowerStrip

def getBaseActivos():
    file = "base_activos.xlsx"

    print("Leo base de datos de activos de la CoE: " + file)

    file = getPathDirectory("input\\base_activos\\" + file)

    base = pd.read_excel(file,usecols=["Matricula TM","Nombre","Apellido Paterno","Apellido Materno","Correo","Tribu","Squad","Cod Squad",
                                       "Cod.App.","Rol","Rol Insourcing","Especialidad","Nombre CAL","Matricula CL","Nombre CL",
                                       "Chapter","Tipo_Preper","Empresa","Flag Activo","Fecha actualizado","Tipo","Matriz Roles","Proyecto","Comentarios"],sheet_name=0)
    base = base.astype(object).where(pd.notnull(base),None)

    base = base.rename(columns= {"Matricula TM": "matricula", 
                    "Nombre": "nombre",
                    "Apellido Paterno": "apellido_paterno",
                    "Apellido Materno": "apellido_materno",
                    "Correo": "correo",
                    "Tribu": "tribu",
                    "Squad": "squad",
                    "Cod Squad": "squad_code",
                    "Cod.App.": "cod_app",
                    "Rol": "rol",
                    "Rol Insourcing": "rol_insourcing",
                    "Especialidad": "especialidad",
                    "Nombre CAL": "nombre_cal",
                    "Matricula CL": "matricula_cl",
                    "Nombre CL": "nombre_cl",
                    "Chapter": "chapter",
                    "Tipo_Preper": "tipo_contratacion",
                    "Empresa": "empresa",
                    "Flag Activo": "flag_activo",
                    "Fecha actualizado": "fecha_actualizado",
                    "Tipo" : "tipo",
                    "Matriz Roles" : "matriz_roles",
                    "Proyecto" : "proyecto",
                    "Comentarios": "comentarios"
                    })
    base.fillna("", inplace=True)
    base['matricula'] = base['matricula'].apply(lambda value: getMatriculaWithoutZero(value))
    base['nombre'] = base['nombre'].apply(lambda value: getStringUpperStrip(value))
    base['apellido_paterno'] = base['apellido_paterno'].apply(lambda value: getStringUpperStrip(value))
    base['apellido_materno'] = base['apellido_materno'].apply(lambda value: getStringUpperStrip(value))
    base['correo'] = base['correo'].apply(lambda value: getStringLowerStrip(value))
    base['tribu'] = base['tribu'].apply(lambda value: getStringUpperStrip(value))
    base['squad'] = base.apply(lambda value: getStringUpperStrip(value['squad']) + " [" + str(value['squad_code']) + "]", axis=1)
    base['squad_code'] = base['squad_code'].apply(lambda value: getStringUpperStrip(value))
    base['cod_app'] = base['cod_app'].apply(lambda value: getStringUpperStrip(value))
    base['rol'] = base['rol'].apply(lambda value: getStringUpperStrip(value))
    base['rol_insourcing'] = base['rol_insourcing'].apply(lambda value: getStringUpperStrip(value))
    base['especialidad'] = base['especialidad'].apply(lambda value: getStringUpperStrip(value))
    base['nombre_cal'] = base['nombre_cal'].apply(lambda value: getStringUpperStrip(value))
    base['matricula_cl'] = base['matricula_cl'].apply(lambda value: getMatriculaWithoutZero(value))
    base['nombre_cl'] = base['nombre_cl'].apply(lambda value: getStringUpperStrip(value))
    base['tipo_contratacion'] = base['tipo_contratacion'].apply(lambda value: getStringUpperStrip(value))
    base['empresa'] = base['empresa'].apply(lambda value: getStringUpperStrip(value))
    base['flag_activo'] = base['flag_activo'].apply(lambda value: getStringUpperStrip(value))
    base['fecha_actualizado'] = base['fecha_actualizado'].apply(lambda value: pd.to_datetime(value,format="%d.%m.%Y").date() if value != None else "")

    base["tribu_code"] = base.apply(lambda pr: getCodeSquadTribe(pr["tribu"]),axis=1)

    base = base.sort_values(['matricula','cod_app','fecha_actualizado'], ascending = [True,True,False])
    base = base.drop_duplicates(['matricula','cod_app'],keep='first')

    return base

def getMatriculaWithoutZero(codeTeamMember:str):
    if(isNullOrEmpty(codeTeamMember)): return ""

    codeTeamMember = codeTeamMember.upper().strip()

    firstZero = codeTeamMember[0:1]

    if(firstZero=="0"): codeTeamMember=codeTeamMember[1:len(codeTeamMember)]

    return codeTeamMember.strip()

def setExcelFiltered(base:pd.DataFrame,period:str):
    file = getPathDirectory("output\\base_activos_" + period + ".xlsx")
    columns = ["matricula","nombre","apellido_paterno","apellido_materno","correo","tribu_code","tribu","squad_code","squad","cod_app","rol","rol_insourcing","especialidad","nombre_cal","matricula_cl","nombre_cl","chapter","tipo_contratacion","empresa","flag_activo","fecha_actualizado","tipo","matriz_roles","proyecto","comentarios"]

    print("Exporto archivo de base de activos filtrada para los modelos: " + file)

    base.to_excel(file,sheet_name="Data",columns=columns,index=False)