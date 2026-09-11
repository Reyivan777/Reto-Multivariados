# Guion sugerido — XGBoost (~3 minutos)

Usa **estaciones de monitoreo** en lugar de “plantas”: NTE, NTE2, NO y NE.

## Diapositiva 1 — Cómo construimos el XGBoost (~50 s)

**Título sugerido:** `XGBoost: un modelo global, validado por estación`

**Visual:** `01_estructura_modelo.svg`

**Mensaje principal:** se construyó un modelo global con las cuatro estaciones para predecir O3 a 24 horas. Además se entrenaron cuatro modelos auxiliares, uno por estación, únicamente para revisar si la importancia de las variables cambiaba espacialmente.

**Qué decir:**

> Para XGBoost trabajamos con cuatro estaciones: NTE, NTE2, NO y NE. El modelo final se entrenó de forma conjunta con las cuatro estaciones para predecir el O3 con 24 horas de anticipación. Después entrenamos cuatro modelos auxiliares, uno por estación, no para sustituir al modelo final, sino para entender qué variables eran más importantes en cada zona. El resultado fue muy consistente: en las cuatro estaciones dominaron el O3 del día anterior a la misma hora, el O3 reciente y el O3 de dos días antes. Esto nos indica que la historia reciente del ozono es la señal predictiva más estable.

**No explicar:** profundidad de árboles, eta, early stopping, matrices de XGBoost o fórmulas de Gain, salvo que pregunten.

---

## Diapositiva 2 — Resultados de predicción (~70 s)

**Título sugerido:** `¿XGBoost mejora una predicción simple?`

**Visual:** `02_resultados_error.svg`

**Mensaje principal:** comparar contra persistencia diaria, porque es el punto de referencia más natural: asumir que mañana a la misma hora habrá el mismo O3 que hoy.

**Qué decir:**

> Para saber si el modelo realmente aportaba valor, lo comparamos contra persistencia diaria, que simplemente usa el O3 de hoy como pronóstico para mañana a la misma hora. En 2025, XGBoost redujo el MAE de 13.787 a 11.797 y el RMSE de 18.975 a 16.111; son mejoras aproximadas de 14.4% y 15.1%. Además, la mejora aparece en las cuatro estaciones. NE tuvo la mayor mejora relativa y NO la menor, pero incluso en NO XGBoost siguió superando a la persistencia. Por eso la mejora no depende de una sola estación.

**Idea de cierre:** `XGBoost mejora el baseline en 4 de 4 estaciones.`

---

## Diapositiva 3 — Qué nos dicen los residuos (~55 s)

**Título sugerido:** `Dónde funciona bien y dónde todavía falla`

**Visual:** `03_residuos.svg`

**Mensaje principal:** los errores están razonablemente centrados y son menos dispersos que con persistencia, pero el modelo tiende a subestimar episodios altos, especialmente alrededor de 14:00–15:00.

**Qué decir:**

> Finalmente analizamos los residuos para no quedarnos únicamente con MAE y RMSE. El residuo medio fue 1.205, bastante cercano a cero, aunque positivo, lo que indica una ligera tendencia a subestimar el O3. La dispersión de los residuos bajó de 18.976 con persistencia a 16.067 con XGBoost. La principal limitación aparece en concentraciones altas y alrededor de las 14:00 a 15:00, donde la subestimación aumenta. Entonces el modelo mejora de manera consistente el pronóstico general, pero los episodios altos siguen siendo el reto principal.

## Distribución del tiempo

- Diapositiva 1: ~50 s
- Diapositiva 2: ~70 s
- Diapositiva 3: ~55 s
- Transiciones: ~5–10 s

Total: aproximadamente 3 minutos.

## Frase para entregar la palabra

> En resumen, XGBoost mejoró de forma consistente la referencia simple en las cuatro estaciones y el análisis de residuos nos permitió identificar con claridad dónde todavía puede mejorar el pronóstico.
