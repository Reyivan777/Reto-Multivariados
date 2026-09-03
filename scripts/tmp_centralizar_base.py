from pathlib import Path

reporte_path = Path("quarto/reporte.qmd")
reporte = reporte_path.read_text(encoding="utf-8")

exportacion = r'''
### Exportación de la base para los modelos

La preparación de datos termina con una única base de origen para el modelado. Para evitar repetir la homologación, limpieza, construcción de la cuadrícula horaria y creación de rezagos en cada archivo de modelo, este objeto se guarda en formato RDS. El formato conserva directamente los tipos de las columnas, los factores, las fechas `POSIXct` y los valores `NA`.

A partir de este punto, los archivos dedicados a cada modelo cargan esta base y se concentran únicamente en construir el objetivo para cada horizonte, ajustar el modelo y evaluarlo. De esta manera, `reporte.qmd` queda como la única fuente de verdad para la preparación de los datos.

```{r}
#| label: exportar-base-modelado
ruta_base_modelado <- here("data", "base_modelado_o3.rds")

saveRDS(
  base_origen_modelado,
  ruta_base_modelado
)

resumen_exportacion_modelado <- tibble(
  Archivo = "data/base_modelado_o3.rds",
  Registros = nrow(base_origen_modelado),
  Estaciones = n_distinct(base_origen_modelado$Estacion),
  Desde = min(base_origen_modelado$fecha_hora),
  Hasta = max(base_origen_modelado$fecha_hora),
  O3_t_disponible_pct = round(
    mean(!is.na(base_origen_modelado$O3_t)) * 100,
    1
  )
)

knitr::kable(
  resumen_exportacion_modelado,
  caption = "Base exportada para los archivos de modelado"
)
```

El archivo `data/base_modelado_o3.rds` es un producto derivado y reproducible. Se genera al renderizar este reporte después de cualquier cambio en la preparación de datos. Por ello no es necesario reconstruir la limpieza ni los rezagos dentro de cada archivo de modelado.
'''

marker = "\n# Modelado\n"
if "#| label: exportar-base-modelado" not in reporte:
    if marker not in reporte:
        raise RuntimeError("No se encontró el marcador # Modelado en reporte.qmd")
    reporte = reporte.replace(
        marker,
        "\n" + exportacion.strip() + "\n\n# Modelado\n",
        1,
    )
    reporte_path.write_text(reporte, encoding="utf-8")

xgb_path = Path("quarto/xgboost.qmd")
xgb = xgb_path.read_text(encoding="utf-8")

old_intro = "Para evitar repetir el procesamiento de los seis archivos de Excel, aquí se parte de `data/datos_etapa2_limpios.csv`, que contiene la base previamente homologada y depurada. A partir de ella se cargan únicamente las cuatro estaciones y las variables necesarias para el modelado de O3."
new_intro = "Para evitar repetir el procesamiento ya documentado en el reporte principal, este archivo parte directamente de `data/base_modelado_o3.rds`. Esa base se genera al final de `reporte.qmd` y ya contiene la cuadrícula horaria, las variables limpias y los rezagos seleccionados. Aquí no se vuelven a homologar fechas, limpiar mediciones ni reconstruir la historia temporal."
xgb = xgb.replace(old_intro, new_intro)

start_marker = "# Carga de la base limpia\n"
end_marker = "# Modelo de persistencia\n"
start = xgb.find(start_marker)
end = xgb.find(end_marker)
if start == -1 or end == -1 or end <= start:
    raise RuntimeError("No se pudieron localizar las secciones iniciales de xgboost.qmd")

nueva_carga = r'''# Carga de la base de modelado

Este archivo comienza donde termina la preparación del reporte principal. Primero se cargan las librerías necesarias y se fija la semilla para que los resultados del entrenamiento sean reproducibles. `xgboost` debe estar registrado en `renv.lock` para que cualquier integrante pueda restaurar el entorno con `renv::restore()`.

```{r}
#| label: configuracion
library(tidyverse)
library(here)
library(lubridate)
library(xgboost)

options(scipen = 999)
set.seed(123)
```

La base se lee directamente desde el RDS generado por `reporte.qmd`. Si el archivo no existe, primero debe renderizarse el reporte principal. No se realiza ninguna conversión adicional de fechas ni se vuelven a crear los rezagos.

```{r}
#| label: carga-base-modelado
ruta_base_modelado <- here("data", "base_modelado_o3.rds")

if (!file.exists(ruta_base_modelado)) {
  stop(
    "No se encontró data/base_modelado_o3.rds. ",
    "Renderiza primero quarto/reporte.qmd para generar la base de modelado."
  )
}

base_origen_modelado <- readRDS(ruta_base_modelado)
```

Antes de entrenar se comprueba que la base conserve la estructura esperada. Esta verificación permite detectar inmediatamente si el archivo de modelado quedó desactualizado o incompleto.

```{r}
#| label: verificacion-base-modelado
columnas_requeridas <- c(
  "Estacion", "fecha_hora",
  "O3_t", "O3_lag_1", "O3_lag_2", "O3_lag_3", "O3_lag_24",
  "SR", "TEMP", "RH", "WS", "WD_sin", "WD_cos", "NOX"
)

faltantes_estructura <- setdiff(
  columnas_requeridas,
  names(base_origen_modelado)
)

if (length(faltantes_estructura) > 0) {
  stop(
    "La base de modelado no contiene: ",
    paste(faltantes_estructura, collapse = ", ")
  )
}

resumen_base_xgboost <- tibble(
  Registros = nrow(base_origen_modelado),
  Desde = min(base_origen_modelado$fecha_hora),
  Hasta = max(base_origen_modelado$fecha_hora),
  Estaciones = n_distinct(base_origen_modelado$Estacion),
  O3_t_disponible_pct = round(
    mean(!is.na(base_origen_modelado$O3_t)) * 100,
    1
  )
)

knitr::kable(
  resumen_base_xgboost,
  caption = "Verificación de la base recibida desde reporte.qmd"
)
```

# Construcción del horizonte

La única transformación temporal que corresponde a este archivo es definir **qué hora futura se desea predecir**. La base de origen ya contiene toda la información disponible en el momento `t`; la función siguiente agrega `O3(t+h)`, las variables cíclicas de la hora y el mes objetivo y la separación cronológica de entrenamiento, validación y prueba.

```{r}
#| label: funcion-base-horizonte
construir_base_horizonte <- function(h) {
  base_origen_modelado |>
    group_by(Estacion) |>
    mutate(
      O3_objetivo = lead(O3_t, h)
    ) |>
    ungroup() |>
    mutate(
      Horizonte_h = h,
      fecha_objetivo = fecha_hora + hours(h),
      Año_objetivo = year(fecha_objetivo),
      Hora_objetivo = hour(fecha_objetivo),
      Mes_objetivo = month(fecha_objetivo),
      Hora_sin_obj = sin(2 * pi * Hora_objetivo / 24),
      Hora_cos_obj = cos(2 * pi * Hora_objetivo / 24),
      Mes_sin_obj = sin(2 * pi * (Mes_objetivo - 1) / 12),
      Mes_cos_obj = cos(2 * pi * (Mes_objetivo - 1) / 12),
      Periodo = case_when(
        Año_objetivo %in% 2021:2023 ~ "Entrenamiento",
        Año_objetivo == 2024 ~ "Validacion",
        Año_objetivo == 2025 ~ "Prueba",
        TRUE ~ NA_character_
      )
    ) |>
    filter(
      !is.na(Periodo),
      between(Hora_objetivo, 10, 20)
    )
}
```

## Primer horizonte: una hora

Por ahora se mantiene `h = 1` para comprobar el flujo completo antes de extender el entrenamiento a los 24 horizontes. Solo se eliminan filas sin `O3_objetivo`; los valores faltantes de los predictores permanecen disponibles para que XGBoost los maneje de forma nativa.

```{r}
#| label: base-h1
base_h1 <- construir_base_horizonte(1) |>
  filter(!is.na(O3_objetivo))

resumen_h1 <- base_h1 |>
  count(Periodo, name = "Observaciones_con_objetivo") |>
  arrange(factor(
    Periodo,
    levels = c("Entrenamiento", "Validacion", "Prueba")
  ))

knitr::kable(
  resumen_h1,
  caption = "Observaciones disponibles para predecir O3 con una hora de anticipación"
)
```

La cantidad de objetivos debe coincidir con la obtenida en `reporte.qmd` para el mismo horizonte. Esta comprobación asegura que el modelo utiliza exactamente la misma base que sustentó las decisiones metodológicas anteriores.
'''

xgb = xgb[:start] + nueva_carga.strip() + "\n\n" + xgb[end:]
xgb_path.write_text(xgb, encoding="utf-8")

gitignore_path = Path(".gitignore")
gitignore = gitignore_path.read_text(encoding="utf-8") if gitignore_path.exists() else ""
rds_line = "data/base_modelado_o3.rds"
if rds_line not in gitignore.splitlines():
    if gitignore and not gitignore.endswith("\n"):
        gitignore += "\n"
    gitignore += rds_line + "\n"
    gitignore_path.write_text(gitignore, encoding="utf-8")

Path("scripts/tmp_centralizar_base.py").unlink()
Path(".github/workflows/tmp_centralizar_base.yml").unlink()
