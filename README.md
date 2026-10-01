# Money Manager App

Este repositorio contiene una suite de aplicaciones para gestionar finanzas personales, con una base común en SQLite y múltiples interfaces:

- Tkinter: aplicación de escritorio
- Flask: aplicación web
- Kivy: versión móvil / multitouch
- Login y base de datos completa
- Registro de ingresos, gastos, presupuestos y resúmenes financieros

## Estructura

- `database.py` : capa común de base de datos SQLite
- `tkinter_app.py` : aplicación de escritorio (Tkinter)
- `flask_app.py` : aplicación web con Flask
- `kivy_app.py` : versión móvil con Kivy
- `requirements.txt` : dependencias de Python

## Requisitos

Python 3.10+

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecutar escritorio

```bash
python tkinter_app.py
```

## Ejecutar web

```bash
python flask_app.py
```

Abrir en el navegador:

```text
http://127.0.0.1:5000
```

## Ejecutar móvil

```bash
python kivy_app.py
```

## Funcionalidades principales

- Registro de usuarios con login
- Agregar ingresos y gastos
- Clasificar por categoría
- Definir presupuestos por categoría
- Ver historial de transacciones
- Ver balance general
- Ver gastos por categoría
- Dashboard financiero simple

## Base de datos

Se usa SQLite con archivo local:

```text
money_manager.db
```

## Autor

Proyecto de ejemplo para manejo de dinero personal en Python.
