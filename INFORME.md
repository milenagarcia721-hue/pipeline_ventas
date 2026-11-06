# Informe — Pipeline ETL de ventas

## Objetivo
Automatizar la recepción de un CSV diario de ventas, depurar registros inválidos y cargar la información confiable en SQLite. El proceso se integra con pruebas automáticas y un flujo de integración continua.

## Reglas de calidad
- **Completitud:** se descartan filas sin `id_venta`, `fecha` o `monto`.
- **Unicidad:** se conserva un único registro por identificador de venta.
- **Validez de tipos:** la fecha se convierte a tipo fecha y el monto a valor numérico; los valores que no se pueden convertir se descartan.
- **Dominio del monto:** solo se aceptan montos estrictamente mayores que cero.
- **Validez temporal:** se rechazan ventas cuya fecha sea posterior al día de ejecución.

## Decisiones técnicas
Se utilizó pandas para leer y transformar el CSV, SQLite como destino y pytest para automatizar las verificaciones. La carga reemplaza la tabla `ventas` en cada ejecución, lo que hace que el resultado sea repetible y evita duplicados por reejecución. Se usa `logging` para registrar filas leídas y cargadas. El parámetro `fecha_actual` permite probar de forma determinista la regla de fechas futuras.

## Integración y despliegue
GitHub Actions ejecuta las pruebas en cada `push` y `pull_request`. Si las pruebas pasan, ejecuta el pipeline. El Dockerfile permite construir una imagen reproducible con Python y las dependencias del proyecto.

## Resultado esperado con los datos de ejemplo
El CSV contiene 7 filas. Aplicando las reglas, se cargan 2 ventas válidas (IDs 1 y 4). Las demás se descartan por monto negativo, duplicidad, monto vacío, fecha futura o monto igual a cero.
