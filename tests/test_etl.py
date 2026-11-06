from datetime import date
import sqlite3

import pandas as pd

from etl import transformar, ejecutar_pipeline


def datos_crudos():
    return pd.DataFrame({
        "id_venta": [1, 2, 2, 3, 4, 5, 6],
        "fecha": [
            "2026-01-05", "2026-01-06", "2026-01-06",
            "2026-01-07", "2026-01-08", "2026-12-01", "2026-01-10"
        ],
        "monto": ["100.5", "-20", "-20", None, "75", "250", "0"],
    })


def test_sin_duplicados_ni_nulos():
    df = transformar(datos_crudos(), fecha_actual=date(2026, 11, 6))
    assert df["id_venta"].is_unique
    assert df[["id_venta", "fecha", "monto"]].notna().all().all()


def test_montos_positivos():
    df = transformar(datos_crudos(), fecha_actual=date(2026, 11, 6))
    assert (df["monto"] > 0).all()


def test_rechaza_fechas_futuras():
    df = transformar(datos_crudos(), fecha_actual=date(2026, 11, 6))
    assert not (df["fecha"].dt.date > date(2026, 11, 6)).any()


def test_solo_conserva_ventas_validas():
    df = transformar(datos_crudos(), fecha_actual=date(2026, 11, 6))
    assert df["id_venta"].tolist() == [1, 4]


def test_pipeline_carga_en_sqlite_y_es_repetible(tmp_path):
    csv = tmp_path / "ventas.csv"
    db = tmp_path / "ventas.db"
    datos_crudos().to_csv(csv, index=False)

    primera = ejecutar_pipeline(csv, db, fecha_actual=date(2026, 11, 6))
    segunda = ejecutar_pipeline(csv, db, fecha_actual=date(2026, 11, 6))

    assert primera == segunda
    assert primera["filas_leidas"] == 7
    assert primera["filas_cargadas"] == 2

    with sqlite3.connect(db) as conexion:
        cantidad = conexion.execute("SELECT COUNT(*) FROM ventas").fetchone()[0]
    assert cantidad == 2
