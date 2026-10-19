Instrucciones
Para el examen podrás usar Posit Cloud (antes RStudio Cloud). Podrás apoyarte en un formulario personal de código que tú mismo(a) elaborarás. Este formulario es tu “hoja de ruta” para ejecutar los análisis del curso sin tener que memorizar comandos. Ajústate a los siguientes puntos para elaborarlo.

1. ¿Qué es un formulario?
Es un archivo personal de apoyo que reúne los comandos principales de los temas del curso, organizado para localizar y adaptar rápidamente el procedimiento que necesites durante el examen. Debe cumplir:

estar elaborado en Quarto (.qmd) o R Markdown (.Rmd)
estar organizado mediante títulos y subtítulos (#, ##, ###) para que puedas utilizar el outline y comprimir, desplegar o localizar rápidamente sus secciones.
contener únicamente texto: no deberá incluir chunks ejecutables;
usar un formato sencillo, como encabezados, viñetas y código escrito como texto;
ser breve, funcional y elaborado por ti;
incluir solamente código que hayas probado previamente con ejercicios o conjuntos de datos del curso;
tener una extensión máxima de 10 páginas en la versión PDF.
Deberás entregar los dos archivos: el formulario original en formato .qmd o .Rmd y su versión compilada en .pdf.

2. ¿Qué no es un formulario?
Un formulario no es:

Un manual o resumen teórico del curso.
No debe contener definiciones extensas, demostraciones ni explicaciones desarrolladas de los temas.
Una colecciones exhaustivas código.
Evita ejemplos completos, procedimientos redundantes, bases de datos, simulaciones y resultados de ejercicios anteriores.
Un archivo que deba ejecutarse completo.
Contiene bloques independientes que podrás copiar y adaptar según el problema de tu examen y que probaste antes de incluirlo en el formulario.
Un conjunto de ejemplos completos.
No incluyas bases de datos, simulaciones, resultados extensos, salidas de consola ni gráficas de ejercicios anteriores.
Una solución automática.
Durante el examen tendrás que sustituir los nombres de los datos, seleccionar las variables pertinentes y establecer los parámetros adecuados.
En síntesis, es una guía breve para recordar y adaptar procedimientos que ya conoces, no una fuente de soluciones o respuestas prefabricadas.

3. Estructura mínima requerida.

Organiza el formulario mediante encabezados que permitan localizar rápidamente cada procedimiento desde el outline:
Por ejemplo:

- '# 0. Preparación de los datos'
- '# 1. Normal Multivariada'
- '## Calculo de probabilidades'
- '## Evaluación de la Normalidad'
- '# 2. Regresión Múltiple'
- '## Ajuste y pruebas de significancia'
- '## Diagnóstico y validación'
- '# 3. Análisis de componentes principales'
- '#... Otros  temas del curso'

Antes de cada bloque de código, incluye una indicación breve sobre su propósito, cuándo utilizarlo y qué elementos deberás adaptar. Evita explicaciones extensas. Algo tan breve como esto sería suficiente:
Para ajustar el modelo: sustituir y por la variable respuesta y x1, x2 por las variables explicativas.

4. Uso de IA
Puedes usar Gemini u otra herramienta de IA para preparar tu formulario antes del examen. Durante el examen no estará permitida la consulta a IA. Si utilizas IA para elaborar tu formulario:

Revisa, comprende y prueba personalmente cada bloque de código antes de incluirlo. No copies instrucciones cuyo funcionamiento desconozcas.
Elimina ejemplos de datos, simulaciones, resultados y objetos creados únicamente para construir la respuesta.
Puedes conservar plantillas generales, siempre que indiques claramente qué elementos deberás sustituir. Por ejemplo:
Sustituye X por las variables cuantitativas seleccionadas y k por el número de conglomerados: grupos <- cluster::pam(X, k = k)
Conserva únicamente el código necesario. Evita procedimientos redundantes, simulaciones, gráficas innecesarias u operaciones que generen objetos excesivamente grandes, pues Posit Cloud dispone de memoria limitada.
La IA puede ayudarte a construir el formulario, pero tú eres responsable de comprender, adaptar y verificar todo su contenido.

5. Librerías y paquetes.
NO debes colocar una lista grande de librerías al inicio de tu formulario. En lugar de eso coloca la librería dentro de cada sección específica. Ejemplo:

- '# Análisis de componentes principales'
pca <- FactoMineR :: PCA(datos, scale.unit = TRUE, graph=FALSE)
- '# Análisis factorial'
af <- psych :: fa(datos, nfactors = 3, rotate = "varimax")
- '# Clustering1'
cl <- cluster :: pam(datos, k = 3)
Beneficio: Solo se cargan paquetes cuando los necesites, esto implica menos RAM consumida.

6. Preparación de Posit Cloud

Crear tu cuenta en Posit Cloud
Entra a Posit Cloud desde tu navegador (https://posit.cloud/)
Regístrate con tu correo institucional o personal (no uses tu usuario de Google porque no estará disponible dentro de LockDown Browser)
Confirma tu cuenta desde el mensaje que recibirás por correo e inicia sesión.
Crear tu proyecto para el examen
Dentro de Posit Cloud, selecciona: New Project y crea un proyecto de RStudio.
Asígnale el nombre: Examen_Multivariado
Abre el proyecto.
Incorpora tu formulario
Puedes hacerlo de dos maneras:
Opción 1: crea tu formulario dentro de Posit Cloud.
Selecciona: File → New File → Quarto o RMarkdown y guárdalo como "FormularioMultivariado.qmd" o "FormularioMultivariado.Rmd"
Edita o elabora tu archivo para convertirlo en tu formulario.
Opción 2: subirlo desde tu computadora
Elabora tu formulario en tu RStudio local.
Entra a tu proyecto Examen_Multivariado de Posit Cloud
En el panel "Files", selecciona Upload (flecha amarilla hacia arriba)
Sigue las instrucciones que aparecen a continuación y caga el archivo .qmd o .Rmd.
Abre el formulario dentro del proyecto y verifica que esté completo y que puedas navegar por sus secciones mediante el outline.
Instalar previamente los paquetes necesarios
Instala en el mismo proyecto todos los paquetes utilizados en tu formulario. Hazlo previamente desde la consola; por ejemplo:
install.packages(c("psych", "FactoMineR", "factoextra", "cluster"))
Las instrucciones install.packages() no deben aparecer en el formulario. Dentro de este solo deberás indicar library() (o llamar la librería con ::) en la sección donde se utilice el paquete correspondiente.
Después de instalar los paquetes:
Selecciona Session → Restart R.
Carga cada paquete mediante library().
Comprueba que no se produzcan errores.
Verifica el acceso. Antes del examen:
cierra y vuelve a abrir el proyecto;
comprueba que puedes iniciar sesión con tu correo y contraseña (sin acceder a Posit por tus contraseñas guardadas en tu navegador);
verifica que el formulario se abre correctamente;
confirma que los paquetes continúan instalados;
realiza la prueba de acceso mediante LockDown Browser indicada por los profesores.
No esperes hasta un día antes del examen para crear la cuenta, instalar paquetes o comprobar el acceso.

7. Lista de verificación final.
Antes del examen, confirma lo siguiente:

Formulario

☐ Está organizado mediante encabezados.
☐ Está en formato .qmd o .Rmd y no contiene chunks ejecutables.
☐ Está organizado por temas mediante encabezados visibles en el outline.
☐ Cada tarea contiene pocas líneas y evita procedimientos redundantes.
☐ Comprendo y he probado todo el código incluido.
☐ Señalé claramente los nombres, variables y parámetros que deberé sustituir.
☐ No contiene instalaciones de paquetes, ejemplos completos ni resultados innecesarios.
☐ El PDF tiene un máximo de 10 páginas.
☐ Entregué los archivos .qmd o .Rmd y .pdf solicitados.

Preparación técnica
☐ Completé el examen de prueba técnica antes de su cierre.
☐ Puedo entrar a Posit Cloud escribiendo personalmente mi correo y contraseña, sin depender de Google ni de contraseñas guardadas en el navegador.
☐ El proyecto Examen_Multivariado contiene mi formulario y se abre correctamente.
☐ Después de reiniciar R, puedo cargar sin errores todos los paquetes que utilizaré.
