from pathlib import Path
import re

qmd = Path("quarto/xgboost.qmd")
text = qmd.read_text(encoding="utf-8")

station_marker = "A partir de este punto quedan congelados objetivo, predictores, hiperparámetros e iteraciones.\n\n# Prueba final en 2025"
if text.count(station_marker) != 1:
    raise SystemExit("No se encontró de forma única el punto para insertar la importancia por estación.")

station_section = r'''A partir de este punto quedan congelados objetivo, predictores, hiperparámetros e iteraciones.

# Importancia de variables por estación

El `Gain` anterior describe la importancia de las variables en el modelo global, donde las cuatro estaciones se ajustan de manera conjunta. Sin embargo, esa medida no puede separarse directamente por estación dentro del mismo modelo. Para comparar qué variables resultan más útiles en cada zona se entrenan **cuatro modelos auxiliares**, uno para cada estación, manteniendo exactamente los hiperparámetros y el número de iteraciones seleccionados previamente.

Estos modelos se ajustan únicamente con 2021-2024 y no utilizan 2025. Su propósito es exclusivamente diagnóstico: permiten comparar patrones de `Gain` entre estaciones, pero no sustituyen al modelo global utilizado para la evaluación final.

```{r}
#| label: importancia-modelos-estacion
crear_matriz_xgb_sin_estacion <- function(datos) {
  matriz <- datos |>
    select(all_of(predictores_numericos)) |>
    as.matrix()

  storage.mode(matriz) <- "double"
  matriz
}

datos_importancia_estacion <- base_h24 |>
  filter(Año_objetivo %in% 2021:2024)

importancia_por_estacion <- map_dfr(
  c("NTE", "NTE2", "NO", "NE"),
  function(estacion_actual) {
    datos_estacion <- datos_importancia_estacion |>
      filter(Estacion == estacion_actual)

    dmat_estacion <- xgb.DMatrix(
      data = crear_matriz_xgb_sin_estacion(datos_estacion),
      label = datos_estacion$O3_objetivo,
      missing = NA
    )

    set.seed(123)

    modelo_estacion <- xgb.train(
      params = parametros_finales,
      data = dmat_estacion,
      nrounds = iteraciones_finales,
      verbose = 0
    )

    xgb.importance(model = modelo_estacion) |>
      as_tibble() |>
      mutate(Estacion = estacion_actual)
  }
)

top_gain_estacion <- importancia_por_estacion |>
  group_by(Estacion) |>
  slice_max(Gain, n = 10, with_ties = FALSE) |>
  arrange(Estacion, desc(Gain)) |>
  ungroup()
```

```{r}
#| label: tabla-gain-estacion
top_gain_estacion |>
  group_by(Estacion) |>
  slice_head(n = 5) |>
  ungroup() |>
  select(Estacion, Feature, Gain) |>
  mutate(Gain = round(Gain, 4)) |>
  knitr::kable(
    caption = "Cinco variables con mayor Gain en cada modelo auxiliar por estación"
  )
```

```{r}
#| label: grafica-gain-estacion
#| fig-cap: "Variables con mayor Gain por estación. Cada panel corresponde a un modelo auxiliar ajustado por separado."
#| fig-width: 10
#| fig-height: 8
datos_gain_grafica <- top_gain_estacion |>
  mutate(
    Feature_estacion = paste(Feature, Estacion, sep = "___"),
    Feature_estacion = forcats::fct_reorder(Feature_estacion, Gain)
  )

ggplot(
  datos_gain_grafica,
  aes(x = Gain, y = Feature_estacion)
) +
  geom_col() +
  facet_wrap(
    ~Estacion,
    ncol = 2,
    scales = "free_y"
  ) +
  scale_y_discrete(
    labels = function(x) sub("___.*$", "", x)
  ) +
  labs(
    x = "Gain",
    y = NULL
  ) +
  theme_minimal()
```

La comparación debe centrarse en qué predictores aparecen de forma consistente entre estaciones y cuáles cambian de posición. Como los cuatro paneles provienen de modelos auxiliares diferentes, el `Gain` se interpreta dentro de cada estación y no como una descomposición exacta del `Gain` del modelo global.

# Prueba final en 2025'''

text = text.replace(station_marker, station_section, 1)

conclusion_marker = "\n# Conclusión\n"
if text.count(conclusion_marker) != 1:
    raise SystemExit("No se encontró de forma única el punto para insertar el análisis de residuos.")

residual_section = r'''
# Análisis de residuos

El MAE y el RMSE resumen la magnitud del error, pero no muestran si el modelo se equivoca de manera sistemática. Para complementar esas métricas se analizan los residuos de la prueba final de 2025. Se define:

$$
e_i = O3_i - \widehat{O3}_i
$$

Por esta convención, un residuo positivo indica que el modelo **subestimó** el O3 observado y un residuo negativo indica que lo **sobreestimó**. Un modelo bien comportado debería producir residuos centrados cerca de cero y sin patrones claros respecto a las predicciones, la estación o la hora del día.

XGBoost no requiere normalidad de los residuos como supuesto para poder ajustarse. Por ello, el histograma y la gráfica Q-Q se utilizan como diagnósticos descriptivos de la forma de los errores, no como una prueba de un supuesto obligatorio del modelo.

```{r}
#| label: residuos-2025
resultados_residuos <- resultados_prueba |>
  mutate(
    Residuo_Persistencia = O3_objetivo - O3_alineado_1d,
    Residuo_XGBoost = O3_objetivo - Pred_XGBoost
  )

resumen_residuos_2025 <- bind_rows(
  resultados_residuos |>
    summarise(
      Modelo = "Persistencia diaria",
      Media_residuo = mean(Residuo_Persistencia),
      Mediana_residuo = median(Residuo_Persistencia),
      Desv_estandar = sd(Residuo_Persistencia),
      P05 = as.numeric(quantile(Residuo_Persistencia, 0.05)),
      P95 = as.numeric(quantile(Residuo_Persistencia, 0.95))
    ),
  resultados_residuos |>
    summarise(
      Modelo = "XGBoost final",
      Media_residuo = mean(Residuo_XGBoost),
      Mediana_residuo = median(Residuo_XGBoost),
      Desv_estandar = sd(Residuo_XGBoost),
      P05 = as.numeric(quantile(Residuo_XGBoost, 0.05)),
      P95 = as.numeric(quantile(Residuo_XGBoost, 0.95))
    )
)

resumen_residuos_2025 |>
  mutate(across(where(is.numeric), ~ round(.x, 3))) |>
  knitr::kable(
    caption = "Resumen global de residuos en la prueba final de 2025"
  )
```

```{r}
#| label: residuos-estacion-2025
resumen_residuos_estacion <- resultados_residuos |>
  group_by(Estacion) |>
  summarise(
    Observaciones = n(),
    Media_residuo = mean(Residuo_XGBoost),
    Mediana_residuo = median(Residuo_XGBoost),
    Desv_estandar = sd(Residuo_XGBoost),
    P05 = as.numeric(quantile(Residuo_XGBoost, 0.05)),
    P95 = as.numeric(quantile(Residuo_XGBoost, 0.95)),
    .groups = "drop"
  )

resumen_residuos_estacion |>
  mutate(across(where(is.numeric) & !matches("Observaciones"), ~ round(.x, 3))) |>
  knitr::kable(
    caption = "Resumen de residuos del XGBoost final por estación en 2025"
  )
```

```{r}
#| label: diagnostico-grafico-residuos
#| fig-cap: "Diagnóstico gráfico de los residuos del XGBoost final en 2025"
#| fig-width: 10
#| fig-height: 8
residuos_hora <- resultados_residuos |>
  group_by(Hora_objetivo) |>
  summarise(
    Media_residuo = mean(Residuo_XGBoost),
    .groups = "drop"
  )

p_resid_pred <- ggplot(
  resultados_residuos,
  aes(x = Pred_XGBoost, y = Residuo_XGBoost)
) +
  geom_point(alpha = 0.15, size = 0.7) +
  geom_hline(yintercept = 0, linewidth = 0.5) +
  geom_smooth(method = "loess", se = FALSE, linewidth = 0.8) +
  labs(
    title = "Residuos vs. predicción",
    x = "O3 predicho",
    y = "Residuo"
  ) +
  theme_minimal()

p_hist_resid <- ggplot(
  resultados_residuos,
  aes(x = Residuo_XGBoost)
) +
  geom_histogram(bins = 40) +
  geom_vline(xintercept = 0, linewidth = 0.5) +
  labs(
    title = "Distribución de residuos",
    x = "Residuo",
    y = "Frecuencia"
  ) +
  theme_minimal()

p_qq_resid <- ggplot(
  resultados_residuos,
  aes(sample = Residuo_XGBoost)
) +
  stat_qq(alpha = 0.25, size = 0.8) +
  stat_qq_line(linewidth = 0.7) +
  labs(
    title = "Gráfica Q-Q",
    x = "Cuantil teórico",
    y = "Cuantil observado"
  ) +
  theme_minimal()

p_hora_resid <- ggplot(
  residuos_hora,
  aes(x = Hora_objetivo, y = Media_residuo)
) +
  geom_hline(yintercept = 0, linewidth = 0.5) +
  geom_line(linewidth = 0.8) +
  geom_point(size = 2) +
  scale_x_continuous(breaks = 10:20) +
  labs(
    title = "Residuo medio por hora objetivo",
    x = "Hora objetivo",
    y = "Residuo medio"
  ) +
  theme_minimal()

grid::grid.newpage()
grid::pushViewport(
  grid::viewport(layout = grid::grid.layout(2, 2))
)
print(
  p_resid_pred,
  vp = grid::viewport(layout.pos.row = 1, layout.pos.col = 1)
)
print(
  p_hist_resid,
  vp = grid::viewport(layout.pos.row = 1, layout.pos.col = 2)
)
print(
  p_qq_resid,
  vp = grid::viewport(layout.pos.row = 2, layout.pos.col = 1)
)
print(
  p_hora_resid,
  vp = grid::viewport(layout.pos.row = 2, layout.pos.col = 2)
)
```

La interpretación conjunta revisa cuatro aspectos: sesgo global cercano a cero, ausencia de estructura marcada en residuos frente a predicciones, comportamiento de las colas de la distribución y posibles diferencias sistemáticas según la hora o la estación. Estos diagnósticos complementan al MAE y RMSE porque muestran **cómo** se distribuye el error, no solamente su magnitud media.
'''

text = text.replace(conclusion_marker, residual_section + conclusion_marker, 1)

# Añadir una mención breve al cierre sin fijar conclusiones numéricas antes de ver los resultados.
old_end = "En 2025, XGBoost obtiene MAE de **`r round(metricas_xgb_2025$MAE[[1]], 3)`** y RMSE de **`r round(metricas_xgb_2025$RMSE[[1]], 3)`**, equivalentes a mejoras de **`r round(mejora_final$Mejora_MAE_pct[[1]], 1)`%** y **`r round(mejora_final$Mejora_RMSE_pct[[1]], 1)`%** frente a persistencia."
new_end = old_end + " El análisis de residuos y la comparación de `Gain` por estación complementan estas métricas al revisar posibles sesgos, patrones de error y diferencias espaciales en la importancia de los predictores."
if text.count(old_end) != 1:
    raise SystemExit("No se encontró el cierre esperado del documento.")
text = text.replace(old_end, new_end, 1)

qmd.write_text(text, encoding="utf-8")

# Preparar scripts de validación para GitHub Actions.
def extract_r_chunks(path: Path, stop_after=None):
    source = path.read_text(encoding="utf-8")
    chunks = re.findall(r"```\{r[^}]*\}\s*\n(.*?)\n```", source, flags=re.S)
    selected = []
    for chunk in chunks:
        if re.search(r"^\s*#\|\s*eval:\s*false\s*$", chunk, flags=re.M | re.I):
            continue
        selected.append(chunk)
        if stop_after and stop_after in chunk:
            break
    return selected

report_chunks = extract_r_chunks(Path("quarto/reporte.qmd"), stop_after="base_modelado_o3.rds")
if not any("saveRDS" in chunk and "base_modelado_o3.rds" in chunk for chunk in report_chunks):
    raise SystemExit("No se encontró el chunk que exporta base_modelado_o3.rds en reporte.qmd")
Path("/tmp/reporte_base.R").write_text("\n\n".join(report_chunks), encoding="utf-8")

xgb_chunks = extract_r_chunks(qmd)
Path("/tmp/xgboost_diagnosticos.R").write_text("\n\n".join(xgb_chunks), encoding="utf-8")
