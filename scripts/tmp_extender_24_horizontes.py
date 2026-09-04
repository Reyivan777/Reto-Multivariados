from pathlib import Path

path = Path("quarto/xgboost.qmd")
texto = path.read_text(encoding="utf-8")

# Corrige una ecuación duplicada que quedó en una edición previa.
texto = texto.replace(
    '$$\\widehat{O_3}(t+1) = O_3(t)\n$$$$\\widehat{O_3}(t+1) = O_3(t)$$',
    '$$\n\\widehat{O_3}(t+1) = O_3(t)\n$$'
)

conclusion_anterior = '''Este tuning es deliberadamente reducido. Si las mejoras son pequeñas, se conservará una configuración simple y se evitará una búsqueda más costosa. Si algún horizonte muestra una reducción clara del error, esa configuración servirá como referencia para extender el modelado a los 24 horizontes.'''
conclusion_nueva = '''El tuning reducido produjo mejoras muy pequeñas: entre 0.0% y 1.0% en RMSE para los horizontes representativos. Por ello no se justifica utilizar configuraciones distintas por horizonte ni ampliar la búsqueda. Para la extensión a 24 horas se conserva la configuración inicial, que es más simple, uniforme y ya mostró un desempeño prácticamente equivalente.'''

if conclusion_anterior not in texto:
    raise RuntimeError("No se encontró la conclusión del tuning")
texto = texto.replace(conclusion_anterior, conclusion_nueva, 1)

bloque = r'''
## Extensión a los 24 horizontes

El tuning reducido no produjo mejoras suficientes para justificar configuraciones distintas por horizonte. Por ello se conserva la configuración inicial de XGBoost y se extiende el mismo procedimiento a cada horizonte desde 1 hasta 24 horas. Esta decisión permite estudiar la curva completa de desempeño manteniendo constantes los predictores y los hiperparámetros.

Los modelos de `h = 1, 6, 12 y 24` ya fueron entrenados previamente, por lo que se reutilizan sus resultados. Solo se entrenan los veinte horizontes restantes. En todos los casos se utiliza 2021-2023 para entrenamiento, 2024 para validación y 2025 continúa sin utilizarse.

```{r}
#| label: extender-xgboost-24-horizontes
horizontes_pendientes <- setdiff(
  2:24,
  c(6, 12, 24)
)

evaluaciones_horizontes_completos <- map(
  horizontes_pendientes,
  entrenar_y_evaluar_horizonte
)

resultados_24_horizontes <- bind_rows(
  resultado_h1,
  map_dfr(evaluaciones_horizontes, ~ .x$resumen),
  map_dfr(evaluaciones_horizontes_completos, ~ .x$resumen)
) |>
  arrange(Horizonte_h)

resultados_24_horizontes |>
  transmute(
    Horizonte_h,
    Observaciones,
    Mejor_iteracion,
    MAE_Persistencia = round(MAE_Persistencia, 3),
    MAE_XGBoost = round(MAE_XGBoost, 3),
    RMSE_Persistencia = round(RMSE_Persistencia, 3),
    RMSE_XGBoost = round(RMSE_XGBoost, 3),
    Mejora_MAE_pct = round(Mejora_MAE_pct, 1),
    Mejora_RMSE_pct = round(Mejora_RMSE_pct, 1)
  ) |>
  knitr::kable(
    caption = "Desempeño de persistencia y XGBoost para los 24 horizontes en validación 2024"
  )
```

La tabla permite revisar hora por hora cuánto aumenta o disminuye el error y en qué horizontes XGBoost conserva una ventaja clara sobre persistencia. Las métricas continúan calculándose sobre el subconjunto común donde ambos modelos pueden evaluarse de forma justa.

```{r}
#| label: grafica-metricas-24-horizontes
#| fig-cap: "MAE y RMSE de persistencia y XGBoost para horizontes de 1 a 24 horas"
#| fig-width: 8
#| fig-height: 6
resultados_24_horizontes |>
  select(
    Horizonte_h,
    MAE_Persistencia,
    MAE_XGBoost,
    RMSE_Persistencia,
    RMSE_XGBoost
  ) |>
  pivot_longer(
    cols = -Horizonte_h,
    names_to = c("Metrica", "Modelo"),
    names_sep = "_",
    values_to = "Error"
  ) |>
  ggplot(
    aes(
      x = Horizonte_h,
      y = Error,
      group = Modelo,
      linetype = Modelo,
      shape = Modelo
    )
  ) +
  geom_line(linewidth = 0.8) +
  geom_point(size = 2) +
  facet_wrap(~ Metrica, scales = "free_y", ncol = 1) +
  scale_x_continuous(breaks = seq(1, 24, by = 2)) +
  labs(
    x = "Horizonte (horas)",
    y = "Error",
    linetype = "Modelo",
    shape = "Modelo"
  ) +
  theme_minimal()
```

Esta curva completa permitirá identificar con mayor precisión la pérdida de capacidad predictiva a medida que aumenta el horizonte y la recuperación asociada al ciclo diario al acercarse a 24 horas. La evaluación final sobre 2025 se realizará únicamente después de cerrar esta revisión en validación.
'''

marcador = "\n# Evaluación\n"
if "#| label: extender-xgboost-24-horizontes" not in texto:
    if marcador not in texto:
        raise RuntimeError("No se encontró la sección Evaluación")
    texto = texto.replace(
        marcador,
        "\n" + bloque.strip() + "\n\n# Evaluación\n",
        1
    )

texto = texto.replace(
    "La configuración inicial ya se evalúa sobre **2024** en horizontes de 1, 6, 12 y 24 horas. Además, se compara la importancia de variables y se realiza un tuning reducido por horizonte para comprobar si ajustes razonables de los hiperparámetros reducen el error antes de extender el modelo a los 24 horizontes.",
    "La configuración inicial ya se evalúa sobre **2024** en los 24 horizontes de 1 a 24 horas. El tuning reducido mostró mejoras marginales, por lo que se conserva una configuración uniforme y se analiza la curva completa de MAE y RMSE antes de utilizar el conjunto de prueba final."
)

path.write_text(texto, encoding="utf-8")
