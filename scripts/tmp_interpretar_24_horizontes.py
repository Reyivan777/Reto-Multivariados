from pathlib import Path

path = Path("quarto/xgboost.qmd")
texto = path.read_text(encoding="utf-8")

viejo = """Esta curva completa permitirá identificar con mayor precisión la pérdida de capacidad predictiva a medida que aumenta el horizonte y la recuperación asociada al ciclo diario al acercarse a 24 horas. La evaluación final sobre 2025 se realizará únicamente después de cerrar esta revisión en validación.

# Evaluación

La configuración inicial ya se evalúa sobre **2024** en los 24 horizontes de 1 a 24 horas. El tuning reducido mostró mejoras marginales, por lo que se conserva una configuración uniforme y se analiza la curva completa de MAE y RMSE antes de utilizar el conjunto de prueba final.

El conjunto de **2025 permanece reservado** para la prueba final y no debe utilizarse para decidir parámetros, variables ni arquitectura del modelo.
"""

nuevo = """Los resultados muestran que XGBoost supera a persistencia en los 24 horizontes de validación. A una hora obtiene un MAE de 4.248 y un RMSE de 6.027. Conforme aumenta la anticipación, ambos errores crecen hasta alcanzar su zona más alta alrededor de 12-13 horas; en `h = 13`, el MAE es 10.863 y el RMSE 14.741. Después el error disminuye gradualmente y en `h = 24` termina con MAE de 10.043 y RMSE de 13.651.

La forma de la curva es consistente con el ciclo diario observado previamente. Los horizontes intermedios separan al origen y al objetivo en fases distintas del día, por lo que el valor actual de O3 pierde capacidad predictiva y cobran mayor importancia la hora objetivo y las variables meteorológicas. Al acercarse a 24 horas, el origen y el objetivo vuelven a corresponder aproximadamente a la misma hora del día, lo que recupera parte de la estructura temporal.

Persistencia presenta este efecto de manera todavía más marcada: su RMSE aumenta desde 9.416 en `h = 1` hasta valores superiores a 31 alrededor de 7-11 horas y después desciende a 15.749 en `h = 24`. XGBoost controla mucho mejor este aumento. La reducción de RMSE respecto a persistencia supera 50% en buena parte de los horizontes intermedios, mientras que en 24 horas baja a 13.3% porque la propia persistencia vuelve a ser una referencia más competitiva.

Las cantidades de observaciones se mantienen estables, aproximadamente entre 14.4 mil y 15.4 mil casos comunes según el horizonte, por lo que la forma de la curva no se explica por cambios drásticos en el tamaño de la muestra. En conjunto, la validación 2024 muestra que el modelo conserva una ventaja sobre persistencia en todo el rango de 1 a 24 horas y que su mayor dificultad aparece alrededor de medio día de anticipación.

# Evaluación

La selección del modelo queda cerrada con **2024**: XGBoost supera a persistencia en los 24 horizontes, el tuning reducido solo produjo mejoras marginales y se conserva una configuración uniforme para todos los horizontes. La evolución de MAE y RMSE también es coherente con la estructura diaria identificada durante el análisis exploratorio.

El conjunto de **2025 permanece reservado** para la prueba final. A partir de este punto no se deben modificar predictores, hiperparámetros ni decisiones de modelado utilizando los resultados de 2025.
"""

if viejo not in texto:
    raise SystemExit("No se encontró el bloque esperado para reemplazar.")

path.write_text(texto.replace(viejo, nuevo, 1), encoding="utf-8")
