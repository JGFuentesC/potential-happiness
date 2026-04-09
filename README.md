# Potential Happiness: Polyglot Statistical Processor

Este repositorio contiene una implementación académica de un procesador de señales estadísticas implementado en tres lenguajes de programación: **C**, **Go** y **Python**. El objetivo es comparar el rendimiento, la sintaxis y las capacidades de procesamiento de datos de cada stack tecnológico.

## 🚀 Arquitectura del Proyecto

El sistema está diseñado para ingerir datos crudos desde un archivo CSV y generar reportes estadísticos de alta precisión sobre valores de señal y latencias.

```text
.
├── data/               # Conjunto de datos de muestra (samples.csv)
├── docs/               # Documentación pedagógica
├── scripts/            # Scripts de automatización y benchmarking
└── src/                # Código fuente
    ├── c/              # Implementación de alto rendimiento (Low-level)
    ├── go/             # Implementación concurrente (Systems)
    └── python/         # Implementación de prototipado rápido (Data)
```

## 🛠️ Tecnologías y Requisitos

- **C:** Compilador GCC/Clang y `make`.
- **Go:** Go 1.20 o superior.
- **Python:** Python 3.13 y gestor de paquetes `uv`.

## 📊 Métricas Procesadas

Cada implementación calcula de forma independiente las siguientes métricas para las columnas de `value` y `latency`:
- **Media (Mean):** Promedio aritmético de los registros.
- **Máximo (Max):** Valor pico detectado.
- **Mínimo (Min):** Valor base detectado.

## 📖 Instrucciones de Ejecución

### Núcleo C
```bash
cd src/c
make
./processor
```

### Núcleo Go
```bash
cd src/go
go run main.go
```

### Núcleo Python
```bash
cd src/python
uv run main.py
```

## 📝 Análisis Técnico
Para una revisión profunda de la arquitectura y la deuda técnica, consulte el archivo [research.md](./research.md) generado por nuestro equipo de arquitectura.

---
**Autor:** Dr. José G. Fuentes  
**Instituto:** CADIT Universidad Anáhuac
