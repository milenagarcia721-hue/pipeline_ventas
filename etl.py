import logging
import sqlite3
from datetime import date
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "ventas.csv"
DB_PATH = BASE_DIR / "ventas.db"
LOG_PATH = BASE_DIR / "pipeline.log"

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def extraer(ruta=DATA_PATH):
    """Lee el archivo CSV y devuelve los registros originales."""
    df = pd.read_csv(ruta)
    logging.info("Extracción completada: %s filas leídas.", len(df))
    return df


def transformar(df, fecha_actual=None):
    """
    Aplica reglas de calidad:
    - Elimina registros sin id_venta, fecha o monto.
    - Conserva una sola fila por id_venta.
    - Convierte fecha y monto a sus tipos correspondientes.
    - Descarta fechas inválidas, fechas futuras y montos no positivos.
    """
    requeridas = {"id_venta", "fecha", "monto"}
    faltantes = requeridas - set(df.columns)
    if faltantes:
        raise ValueError(f"Faltan columnas requeridas: {sorted(faltantes)}")

    fecha_actual = fecha_actual or date.today()
    resultado = df.copy()

    resultado = resultado.dropna(subset=["id_venta", "fecha", "monto"])
    resultado = resultado.drop_duplicates(subset="id_venta", keep="first")

    resultado["fecha"] = pd.to_datetime(resultado["fecha"], errors="coerce")
    resultado["monto"] = pd.to_numeric(resultado["monto"], errors="coerce")
    resultado = resultado.dropna(subset=["fecha", "monto"])

    limite = pd.Timestamp(fecha_actual)
    resultado = resultado[resultado["fecha"].dt.normalize() <= limite]
    resultado = resultado[resultado["monto"] > 0]

    resultado["id_venta"] = pd.to_numeric(
        resultado["id_venta"], errors="coerce"
    )
    resultado = resultado.dropna(subset=["id_venta"])
    resultado["id_venta"] = resultado["id_venta"].astype("int64")
    resultado["monto"] = resultado["monto"].astype(float)

    return resultado.reset_index(drop=True)


def cargar(df, ruta_db=DB_PATH):
    """Reemplaza la tabla ventas; repetir la carga no duplica registros."""
    ruta_db = Path(ruta_db)
    ruta_db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(ruta_db) as conexion:
        df.to_sql("ventas", conexion, if_exists="replace", index=False)
    logging.info("Carga completada: %s filas cargadas en SQLite.", len(df))


def ejecutar_pipeline(ruta_csv=DATA_PATH, ruta_db=DB_PATH, fecha_actual=None):
    """Ejecuta extracción, transformación y carga, y devuelve métricas."""
    datos = extraer(ruta_csv)
    limpios = transformar(datos, fecha_actual=fecha_actual)
    cargar(limpios, ruta_db)
    logging.info(
        "Resumen ETL: %s filas leídas; %s filas cargadas.",
        len(datos),
        len(limpios),
    )
    return {"filas_leidas": len(datos), "filas_cargadas": len(limpios)}


if __name__ == "__main__":
    resultado = ejecutar_pipeline()
    print(
        "Pipeline finalizado. "
        f"Filas leídas: {resultado['filas_leidas']}. "
        f"Filas cargadas: {resultado['filas_cargadas']}."
    )
