# Pipeline ETL de ventas — Taller práctico DevOps

## Objetivo
Construir un pipeline que extrae ventas desde CSV, aplica reglas de calidad y carga los registros válidos en SQLite. Las pruebas automatizadas y GitHub Actions verifican el proceso en cada `push` y `pull_request`.

## Estructura
```text
pipeline-ventas/
├── data/ventas.csv
├── etl.py
├── tests/test_etl.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── README.md
├── INFORME.md
└── .github/workflows/ci.yml
```

## Requisitos
Python 3.12 recomendado. También se necesita Git para publicar el proyecto en GitHub. Docker es opcional para ejecutar el contenedor.

## Ejecutar localmente
Desde la carpeta raíz del proyecto:

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python -m pytest -v
python etl.py
```

El resultado se guarda en `ventas.db`, en la tabla `ventas`. El archivo `pipeline.log` registra las filas leídas y cargadas.

## Reglas de calidad implementadas
1. Se requieren las columnas `id_venta`, `fecha` y `monto`.
2. Se eliminan registros con valores nulos en esos campos.
3. Se conserva una sola fila por `id_venta`.
4. La fecha debe ser válida y no puede estar en el futuro.
5. El monto debe ser numérico y mayor que cero.

## Idempotencia
La carga usa `if_exists="replace"` para reconstruir la tabla `ventas` en cada ejecución. Así, ejecutar el mismo pipeline varias veces no agrega duplicados.

## Docker
```bash
docker build -t pipeline-ventas .
docker run --rm pipeline-ventas
```

## GitHub Actions
El workflow `.github/workflows/ci.yml` se ejecuta en cada `push` o `pull_request`. Instala dependencias, corre pytest y ejecuta el pipeline. Si una prueba falla, el workflow se marca como fallido y no continúa con el paso de ejecución del ETL.

Para publicarlo: crea un repositorio vacío en GitHub y, desde esta carpeta, ejecuta:
```bash
git init
git add .
git commit -m "Implementa pipeline ETL de ventas con pruebas y CI"
git branch -M main
git remote add origin https://github.com/TU-USUARIO/TU-REPOSITORIO.git
git push -u origin main
```
Reemplaza la URL de ejemplo por la URL real de tu repositorio.

## Evidencias de entrega
- Enlace al repositorio de GitHub después de publicarlo.
- Captura del workflow exitoso (verde), en la pestaña **Actions**.
- `INFORME.md` como informe de reglas de calidad y decisiones.
- Para demostrar una falla de CI, modifica temporalmente una expectativa de prueba para que sea incorrecta, haz `git commit` y `git push`, y verifica el workflow rojo. Después restaura la expectativa, crea otro commit y vuelve a subirlo para obtener el workflow verde.
