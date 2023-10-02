# Metrics project

## Init Project

### Create a virtual environment
```shell
python  -m  venv  ven
```
### Activate venv
```shell
venv\Scripts\activate
```
### Get libs
```shell
pip  install  -r  requirements.txt
```
## Data Required
| Folder  | Source  |
|--|--|
| PR | [Folder](https://confluence.lima.bcp.com.pe/display/DB/Reporte+de+Pull+Request+en+Bitbucket) 										|
| Commits | [Folder](https://confluence.lima.bcp.com.pe/display/DB/Reporte+de+Commits+en+Bitbucket) 										|
| Base Activos | [Folder](https://credicorponline.sharepoint.com/:f:/s/IndicadoresCoEIngSW/Eii6cbB30aVEnCAOJeXxFuwBYDdgslExD-AqNctInBORPw?e=CE7wo4) 										|
| Exclusiones | [Folder](https://credicorponline.sharepoint.com/:f:/s/Equipodata/Er3NERWlG_dCkHWvvY8j0GIB9v1vNAYoBOKbAavJpg_73A?e=2uE1vC)				|
| Squads Priorizados | [Folder](https://credicorponline.sharepoint.com/:f:/s/Equipodata/Eiv6cHIqsF1DoPuEk-OMCUEBqM8HZaKyp01fJTBQX2uJlA?e=gcw7Cy) |
| Quiz | [Folder](https://credicorponline.sharepoint.com/:f:/s/Equipodata/EvWSSVyBrmlCjHnoxpSZbagBgR3IR_EpBcfCIU9cd-J-rw?e=reXHtf) 																		|

## Steps to execute
| Name  | Params  |  Execute as  | Sample  | 
|--|--| --|--|
| metrics_v3 | YYYYMM | Script | python -m codereview.metrics_v3 202304 |