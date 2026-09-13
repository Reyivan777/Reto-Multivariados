# Reto Multivariados — SIMA

Proyecto del Equipo 4 para analizar y predecir la concentración de ozono troposférico (O3) en la Zona Metropolitana de Monterrey con 24 horas de anticipación, utilizando datos del Sistema Integral de Monitoreo Ambiental (SIMA) de Nuevo León.

## Estructura del repositorio

- `data/`: bases originales de 2020 a 2025 y `datos_etapa2_limpios.csv`.
- `quarto/reporte.qmd`: preparación de datos, análisis exploratorio y generación local de `data/base_modelado_o3.rds`.
- `quarto/PCA_etapa_4.qmd`: análisis de componentes principales (PCA), técnica de interdependencia.
- `quarto/GAM_h24_final.qmd`: modelo GAM Gamma final para O3 a 24 horas.
- `quarto/xgboost.qmd`: desarrollo y modelo XGBoost final.
- `quarto/comparacion_final_modelos.qmd`: comparación GAM vs. XGBoost y generación de resultados locales en `output/`.
- `quarto/entrega_etapa_4.qmd`: reporte final del reto.
- `quarto/entrega_etapa_2.qmd` y `quarto/entrega_etapa_3.qmd`: entregas previas del proyecto.
- `quarto/GAM.qmd` y `quarto/reg_lineal_o3*.qmd`: análisis exploratorios conservados como parte del procedimiento.
- `quarto/presentacion_xgboost/`: materiales de apoyo utilizados durante el desarrollo del modelo.
- `docs/quarto/`: PDF oficiales de las etapas entregadas.
- `renv.lock` y `renv/`: entorno reproducible de R.

## Reproducción

1. Restaurar las dependencias de R:

```r
renv::restore()
```

2. Renderizar `quarto/reporte.qmd` para generar `data/base_modelado_o3.rds`.
3. Renderizar `quarto/PCA_etapa_4.qmd`, `quarto/GAM_h24_final.qmd` y `quarto/xgboost.qmd` cuando se quieran revisar los análisis individuales.
4. Renderizar `quarto/comparacion_final_modelos.qmd`. Este archivo genera localmente los CSV de `output/`, incluido `predicciones_comunes_2025.csv`.
5. Renderizar `quarto/entrega_etapa_4.qmd` para producir el reporte final en PDF.

Los archivos de salida intermedios, cachés y carpetas `*_files` no se versionan porque pueden regenerarse desde los archivos fuente `.qmd`.
