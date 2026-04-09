# Research Report: Polyglot Statistical Signal Processor

## 1. Arquitectura del Sistema
El proyecto es un procesador estadístico multilingüe diseñado para comparar la eficiencia y sintaxis de tres lenguajes (C, Go y Python) en tareas de procesamiento de datos por lotes (Batch Processing). Todos los componentes consumen una fuente de datos común en `data/samples.csv`.

### 1.1 Componentes por Lenguaje
- **Núcleo C (`src/c`):**
  - Implementación de bajo nivel enfocada en el rendimiento.
  - Tokenización manual mediante `strtok` y conversión de tipos con `atof`.
  - Gestión manual de memoria (aunque mínima para este caso).
- **Núcleo Go (`src/go`):**
  - Implementación concurrente y tipada.
  - Utiliza `encoding/csv` para un parseo robusto.
  - Enfoque en legibilidad y seguridad de tipos.
- **Núcleo Python (`src/python`):**
  - Prototipado rápido y alta abstracción.
  - Utiliza `csv.DictReader` para acceso nominal a columnas.
  - Gestión de entorno mediante `uv`.

## 2. Flujo de Datos y Stack Tecnológico
- **Entrada:** Archivo CSV con columnas `id`, `value`, `latency`.
- **Procesamiento:** Cálculo de métricas estadísticas (Media, Máximo, Mínimo) para valores y latencias.
- **Salida:** Reporte formateado en consola (estandarizado en los tres lenguajes).

## 3. Hallazgos Técnicos y Deuda
- **Acoplamiento de Rutas:** Los tres núcleos utilizan rutas relativas `../../data/samples.csv`, lo que requiere que se ejecuten desde sus respectivos directorios `src/<lang>`.
- **Gestión de Errores:** 
  - C: Muy básica (solo apertura de archivo).
  - Go: Sigue el patrón idiomático de error checking.
  - Python: Manejo de excepciones limitado.
- **Escalabilidad:** Go y Python cargan los registros en memoria (`ReadAll` y `DictReader` convertido a lista), mientras que C procesa línea por línea, siendo más eficiente en el uso de memoria para datasets masivos.
