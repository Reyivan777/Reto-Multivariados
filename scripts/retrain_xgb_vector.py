from pathlib import Path
import re

QMD = Path("quarto/xgboost.qmd")
text = QMD.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: se esperaba 1 coincidencia y se encontraron {count}")
    text = text.replace(old, new, 1)


replace_once(
    "  ungroup() |>\n  mutate(\n    fecha_objetivo = fecha_hora + hours(24),",
    "  ungroup() |>\n  mutate(\n    WS_sin = WS * WD_sin,\n    WS_cos = WS * WD_cos,\n    fecha_objetivo = fecha_hora + hours(24),",
    "componentes de viento",
)

replace_once(
    "- radiación solar, temperatura, humedad relativa y velocidad del viento en `t`;\n- dirección del viento mediante seno y coseno;",
    "- radiación solar, temperatura y humedad relativa en `t`;\n- viento en `t` mediante dos componentes que combinan rapidez y dirección: `WS_sin` y `WS_cos`;",
    "descripción de predictores",
)

replace_once(
    "No se utilizan condiciones meteorológicas reales de `t+24`, porque no estarían disponibles al generar el pronóstico.",
    """La versión anterior representaba el viento con tres variables: `WS`, `WD_sin` y `WD_cos`. En esta versión se integran rapidez y dirección en dos componentes:\n\n$$\nWS_{sin}=WS\\,WD_{sin}, \\qquad WS_{cos}=WS\\,WD_{cos}\n$$\n\nComo `WD_sin` y `WD_cos` ya codifican circularmente la dirección, multiplicarlas por `WS` incorpora también la magnitud del viento. Las dos componentes conservan conjuntamente la información de rapidez y dirección.\n\nNo se utilizan condiciones meteorológicas reales de `t+24`, porque no estarían disponibles al generar el pronóstico.""",
    "explicación vectorial",
)

replace_once(
    '  "SR", "TEMP", "RH", "WS", "WD_sin", "WD_cos",',
    '  "SR", "TEMP", "RH", "WS_sin", "WS_cos",',
    "lista de predictores",
)

replace_once(
    """En 2024, la persistencia diaria obtiene MAE de **11.444** y RMSE de **15.749**, mientras que el XGBoost reformulado obtiene MAE de **10.055** y RMSE de **13.611**. Esto representa reducciones aproximadas de **12.1% en MAE** y **13.6% en RMSE**.""",
    """En 2024, la persistencia diaria obtiene MAE de **`r round(metricas_persistencia_h24$MAE[[1]], 3)`** y RMSE de **`r round(metricas_persistencia_h24$RMSE[[1]], 3)`**, mientras que el XGBoost con viento vectorial obtiene MAE de **`r round(metricas_xgb_h24$MAE[[1]], 3)`** y RMSE de **`r round(metricas_xgb_h24$RMSE[[1]], 3)`**. Esto representa reducciones de **`r round(100 * (metricas_persistencia_h24$MAE[[1]] - metricas_xgb_h24$MAE[[1]]) / metricas_persistencia_h24$MAE[[1]], 1)`% en MAE** y **`r round(100 * (metricas_persistencia_h24$RMSE[[1]] - metricas_xgb_h24$RMSE[[1]]) / metricas_persistencia_h24$RMSE[[1]], 1)`% en RMSE**.""",
    "texto de validación",
)

replace_once(
    """importancia_h24 <- xgb.importance(\n  model = modelo_xgb_h24\n) |>\n  as_tibble() |>\n  arrange(desc(Gain))\n\nimportancia_h24 |>""",
    """importancia_h24 <- xgb.importance(\n  model = modelo_xgb_h24\n) |>\n  as_tibble() |>\n  arrange(desc(Gain))\n\ngain_o3_1d_h24 <- importancia_h24 |>\n  filter(Feature == \"O3_alineado_1d\") |>\n  summarise(Gain = sum(Gain)) |>\n  pull(Gain)\n\ngain_o3_diario_h24 <- importancia_h24 |>\n  filter(Feature %in% c(\n    \"O3_alineado_1d\", \"O3_alineado_2d\",\n    \"O3_alineado_3d\", \"O3_alineado_4d\"\n  )) |>\n  summarise(Gain = sum(Gain)) |>\n  pull(Gain)\n\ngain_ws_sin_h24 <- importancia_h24 |>\n  filter(Feature == \"WS_sin\") |>\n  summarise(Gain = sum(Gain)) |>\n  pull(Gain)\n\ngain_ws_cos_h24 <- importancia_h24 |>\n  filter(Feature == \"WS_cos\") |>\n  summarise(Gain = sum(Gain)) |>\n  pull(Gain)\n\ngain_viento_h24 <- gain_ws_sin_h24 + gain_ws_cos_h24\n\nimportancia_h24 |>""",
    "cálculo de Gain",
)

replace_once(
    """`O3_alineado_1d` concentra **55.64% del Gain** y es el predictor principal. Los cuatro valores diarios alineados suman aproximadamente **70.4% del Gain**, lo que confirma que la historia del O3 a la misma hora de días anteriores concentra la mayor parte de la señal predictiva.\n\nTambién aparecen `O3_lag_1`, `TEMP`, `SR`, `RH`, `WS`, la hora objetivo y el mes, por lo que el modelo utiliza información complementaria para corregir la referencia del día anterior. Estas importancias describen uso predictivo dentro del modelo y no causalidad física.""",
    """`O3_alineado_1d` concentra **`r round(100 * gain_o3_1d_h24, 2)`% del Gain**. Los cuatro valores diarios alineados suman **`r round(100 * gain_o3_diario_h24, 2)`%**, por lo que la historia del O3 a la misma hora de días anteriores continúa concentrando una parte importante de la señal predictiva.\n\nLas nuevas componentes `WS_sin` y `WS_cos` suman conjuntamente **`r round(100 * gain_viento_h24, 2)`% del Gain** (`WS_sin`: `r round(100 * gain_ws_sin_h24, 2)`%; `WS_cos`: `r round(100 * gain_ws_cos_h24, 2)`%). Esta suma permite evaluar el viento como un solo fenómeno representado mediante dos componentes. El `Gain` describe utilidad predictiva dentro del modelo y no importancia causal o física.""",
    "interpretación de Gain",
)

replace_once(
    ") |>\n  bind_rows(resultado_inicial) |>\n  arrange(RMSE_validacion)\n\nresultados_tuning_h24 |>",
    ") |>\n  bind_rows(resultado_inicial) |>\n  arrange(RMSE_validacion)\n\nmejor_configuracion_h24 <- resultados_tuning_h24 |>\n  slice(1)\n\nresultados_tuning_h24 |>",
    "selección de tuning",
)

replace_once(
    """La mejor configuración es **T1**, con `eta = 0.05`, `max_depth = 4`, `min_child_weight = 5`, `subsample = 0.8` y `colsample_bytree = 0.8`. Su mejor iteración es 119. Sobre el subconjunto común obtiene MAE de **10.035** y RMSE de **13.560**.\n\nLa mejora frente a la configuración inicial es pequeña, pero T1 utiliza árboles menos profundos y obtiene un desempeño ligeramente mejor. Por ello se adopta como configuración definitiva.""",
    """La mejor configuración es **`r mejor_configuracion_h24$Configuracion[[1]]`**, con `eta = `r mejor_configuracion_h24$eta[[1]]``, `max_depth = `r mejor_configuracion_h24$max_depth[[1]]``, `min_child_weight = `r mejor_configuracion_h24$min_child_weight[[1]]``, `subsample = `r mejor_configuracion_h24$subsample[[1]]`` y `colsample_bytree = `r mejor_configuracion_h24$colsample_bytree[[1]]``. Su mejor iteración es **`r mejor_configuracion_h24$Mejor_iteracion[[1]]`**. Sobre el subconjunto común obtiene MAE de **`r round(mejor_configuracion_h24$MAE_comun[[1]], 3)`** y RMSE de **`r round(mejor_configuracion_h24$RMSE_comun[[1]], 3)`**.\n\nEsta configuración se selecciona únicamente con la validación de 2024 y se adopta para el reentrenamiento con 2021-2024.""",
    "texto de tuning",
)

replace_once(
    """parametros_finales <- list(\n  objective = \"reg:squarederror\",\n  eval_metric = \"rmse\",\n  eta = 0.05,\n  max_depth = 4,\n  min_child_weight = 5,\n  subsample = 0.8,\n  colsample_bytree = 0.8,\n  lambda = 1\n)\n\niteraciones_finales <- 119""",
    """parametros_finales <- list(\n  objective = \"reg:squarederror\",\n  eval_metric = \"rmse\",\n  eta = mejor_configuracion_h24$eta[[1]],\n  max_depth = mejor_configuracion_h24$max_depth[[1]],\n  min_child_weight = mejor_configuracion_h24$min_child_weight[[1]],\n  subsample = mejor_configuracion_h24$subsample[[1]],\n  colsample_bytree = mejor_configuracion_h24$colsample_bytree[[1]],\n  lambda = 1\n)\n\niteraciones_finales <- mejor_configuracion_h24$Mejor_iteracion[[1]]""",
    "parámetros finales",
)

replace_once(
    """En la prueba final se evaluaron **7,333 observaciones** de 2025. La persistencia diaria obtiene MAE de **13.787** y RMSE de **18.975**, mientras que XGBoost obtiene MAE de **11.864** y RMSE de **16.229**.\n\nEsto equivale a una reducción de **13.9% en MAE** y **14.5% en RMSE** respecto a la persistencia diaria. Por tanto, la ventaja observada durante la validación de 2024 se mantiene en datos completamente fuera de muestra.\n\nLos errores absolutos son mayores en 2025 que en 2024. El RMSE del XGBoost pasa de aproximadamente **13.56** en validación a **16.23** en prueba final, pero la persistencia diaria también empeora de **15.75** a **18.98**. Esto indica que 2025 fue un periodo más difícil de predecir en términos absolutos, sin que desaparezca la ventaja relativa de XGBoost.\n\nDe hecho, la reducción relativa del RMSE se mantiene muy estable: alrededor de **13.9% en validación** y **14.5% en prueba final**. Esta consistencia es una señal favorable de generalización.""",
    """En la prueba final se evaluaron **`r format(nrow(resultados_prueba), big.mark = ",")` observaciones** de 2025. La persistencia diaria obtiene MAE de **`r round(metricas_persistencia_2025$MAE[[1]], 3)`** y RMSE de **`r round(metricas_persistencia_2025$RMSE[[1]], 3)`**, mientras que XGBoost obtiene MAE de **`r round(metricas_xgb_2025$MAE[[1]], 3)`** y RMSE de **`r round(metricas_xgb_2025$RMSE[[1]], 3)`**.\n\nEsto equivale a una reducción de **`r round(mejora_final$Mejora_MAE_pct[[1]], 1)`% en MAE** y **`r round(mejora_final$Mejora_RMSE_pct[[1]], 1)`% en RMSE** respecto a la persistencia diaria. El RMSE del XGBoost pasa de **`r round(mejor_configuracion_h24$RMSE_comun[[1]], 3)`** en validación 2024 a **`r round(metricas_xgb_2025$RMSE[[1]], 3)`** en prueba final.""",
    "texto de prueba 2025",
)

replace_once(
    "metricas_estacion_2025 |>\n  mutate(",
    """mejor_estacion_rmse <- metricas_estacion_2025 |>\n  slice_max(Mejora_RMSE_pct, n = 1, with_ties = FALSE)\n\nmenor_estacion_rmse <- metricas_estacion_2025 |>\n  slice_min(Mejora_RMSE_pct, n = 1, with_ties = FALSE)\n\nmetricas_estacion_2025 |>\n  mutate(""",
    "resumen por estación",
)

replace_once(
    """XGBoost supera a persistencia en las cuatro estaciones:\n\n- **NTE:** el RMSE baja de 17.977 a 15.387, una mejora de **14.4%**.\n- **NTE2:** el RMSE baja de 18.854 a 16.003, una mejora de **15.1%**.\n- **NO:** el RMSE baja de 19.635 a 17.052, una mejora de **13.2%**.\n- **NE:** el RMSE baja de 19.486 a 16.486, una mejora de **15.4%**.\n\nLa mejora no depende de una sola estación. `NO` es la estación con la menor reducción relativa del error, aunque XGBoost también supera claramente a persistencia. `NE` presenta la mayor reducción porcentual tanto en MAE como en RMSE.""",
    """XGBoost obtiene menor RMSE que la persistencia en **`r sum(metricas_estacion_2025$RMSE_XGBoost < metricas_estacion_2025$RMSE_Persistencia)` de `r nrow(metricas_estacion_2025)` estaciones**. La mayor reducción relativa del RMSE aparece en **`r mejor_estacion_rmse$Estacion[[1]]`**, con **`r round(mejor_estacion_rmse$Mejora_RMSE_pct[[1]], 1)`%**, y la menor en **`r menor_estacion_rmse$Estacion[[1]]`**, con **`r round(menor_estacion_rmse$Mejora_RMSE_pct[[1]], 1)`%**.""",
    "texto por estación",
)

replace_once(
    """El XGBoost reformulado a 24 horas supera de manera consistente a la persistencia diaria tanto en validación 2024 como en la prueba final 2025. El modelo aprovecha principalmente la periodicidad diaria del O3: aproximadamente 70% del `Gain` proviene de valores de O3 alineados con la misma hora de días anteriores, mientras que el comportamiento reciente, la meteorología y las variables temporales aportan información complementaria.\n\nEn 2025, XGBoost reduce el MAE de 13.787 a 11.864 y el RMSE de 18.975 a 16.229, equivalentes a mejoras de **13.9% y 14.5%**, respectivamente. Además, la mejora se observa en las cuatro estaciones, lo que respalda que el resultado global no está concentrado en una sola zona de monitoreo.\n\nLa prueba final confirma que el modelo conserva su ventaja fuera de muestra. A partir de estos resultados no se deben reajustar variables, hiperparámetros ni iteraciones utilizando 2025; cualquier modificación posterior correspondería a una nueva versión del modelo y requeriría una nueva evaluación independiente.""",
    """El XGBoost a 24 horas utiliza ahora el viento mediante dos componentes, `WS_sin` y `WS_cos`, en lugar de `WS`, `WD_sin` y `WD_cos`. En validación 2024, la configuración seleccionada obtiene MAE de **`r round(mejor_configuracion_h24$MAE_comun[[1]], 3)`** y RMSE de **`r round(mejor_configuracion_h24$RMSE_comun[[1]], 3)`**. Los cuatro valores diarios alineados de O3 concentran **`r round(100 * gain_o3_diario_h24, 2)`% del Gain**, mientras que las dos componentes del viento suman **`r round(100 * gain_viento_h24, 2)`%**.\n\nEn 2025, XGBoost obtiene MAE de **`r round(metricas_xgb_2025$MAE[[1]], 3)`** y RMSE de **`r round(metricas_xgb_2025$RMSE[[1]], 3)`**, equivalentes a mejoras de **`r round(mejora_final$Mejora_MAE_pct[[1]], 1)`%** y **`r round(mejora_final$Mejora_RMSE_pct[[1]], 1)`%** frente a persistencia.""",
    "conclusión",
)

QMD.write_text(text, encoding="utf-8")


def extract_r_chunks(source: Path, stop_when: str | None = None) -> str:
    raw = source.read_text(encoding="utf-8")
    chunks = re.findall(r"```\{r[^}]*\}\s*\n(.*?)\n```", raw, flags=re.S)
    selected = []
    for chunk in chunks:
        if re.search(r"^\s*#\|\s*eval:\s*false\s*$", chunk, flags=re.M | re.I):
            continue
        selected.append(chunk)
        if stop_when and stop_when in chunk:
            break
    if stop_when and not any(stop_when in c for c in selected):
        raise RuntimeError(f"No se encontró el marcador {stop_when}")
    return "\n\n".join(selected)


Path("/tmp/reporte_base.R").write_text(
    extract_r_chunks(Path("quarto/reporte.qmd"), "saveRDS("), encoding="utf-8"
)

summary_r = r'''
writeLines(c(
  sprintf("VAL_INITIAL_MAE=%.6f", metricas_xgb_h24$MAE[[1]]),
  sprintf("VAL_INITIAL_RMSE=%.6f", metricas_xgb_h24$RMSE[[1]]),
  sprintf("BEST_CONFIG=%s", mejor_configuracion_h24$Configuracion[[1]]),
  sprintf("BEST_ITER=%d", as.integer(mejor_configuracion_h24$Mejor_iteracion[[1]])),
  sprintf("VAL_TUNED_MAE=%.6f", mejor_configuracion_h24$MAE_comun[[1]]),
  sprintf("VAL_TUNED_RMSE=%.6f", mejor_configuracion_h24$RMSE_comun[[1]]),
  sprintf("TEST_MAE=%.6f", metricas_xgb_2025$MAE[[1]]),
  sprintf("TEST_RMSE=%.6f", metricas_xgb_2025$RMSE[[1]]),
  sprintf("PERSIST_TEST_MAE=%.6f", metricas_persistencia_2025$MAE[[1]]),
  sprintf("PERSIST_TEST_RMSE=%.6f", metricas_persistencia_2025$RMSE[[1]]),
  sprintf("IMPROVE_TEST_MAE_PCT=%.6f", mejora_final$Mejora_MAE_pct[[1]]),
  sprintf("IMPROVE_TEST_RMSE_PCT=%.6f", mejora_final$Mejora_RMSE_pct[[1]]),
  sprintf("GAIN_WS_SIN=%.8f", gain_ws_sin_h24),
  sprintf("GAIN_WS_COS=%.8f", gain_ws_cos_h24),
  sprintf("GAIN_WIND_TOTAL=%.8f", gain_viento_h24),
  sprintf("GAIN_O3_DAILY_TOTAL=%.8f", gain_o3_diario_h24)
), "/tmp/xgb_resultados.env")
'''

Path("/tmp/xgboost_vector.R").write_text(
    extract_r_chunks(QMD) + "\n\n" + summary_r,
    encoding="utf-8",
)
