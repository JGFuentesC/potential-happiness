# Statistical Signal Processor (Python)

Sistema de procesamiento y análisis descriptivo de señales capturadas en formato tabular (CSV). Este componente forma parte del ecosistema de análisis de datos para sistemas de alta disponibilidad.

## Descripción Técnica

El procesador realiza la ingesta de datos de rendimiento y valores de señal, ejecutando una reducción estadística en tiempo real para determinar métricas fundamentales:
- **Media Aritmética:** Cálculo del valor promedio de señal y latencia.
- **Valores Extremos:** Identificación de máximos y mínimos para la detección de anomalías.

## Stack Tecnológico

- **Python 3.13+**
- **uv:** Gestor de paquetes y entornos virtuales de alto rendimiento.
- **CSV Engine:** Procesamiento nativo para mínima latencia de parsing.

## Instalación y Uso

Asegúrese de contar con `uv` instalado en su sistema.

1. **Sincronizar el entorno:**
   ```bash
   uv sync
   ```

2. **Ejecución del procesador:**
   ```bash
   uv run main.py
   ```

## Estructura de Datos Requerida

El sistema espera un archivo en `../../data/samples.csv` con el siguiente esquema:
- `id`: Identificador único (int)
- `value`: Magnitud de la señal (float)
- `latency`: Tiempo de respuesta en milisegundos (float)

---
**Dr. José G. Fuentes**  
*CADIT Universidad Anáhuac*
