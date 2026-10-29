# Migraciones de datos (INSERT / UPDATE / DELETE)

El SQL Project maneja la **estructura** (tablas, vistas, SP). Los cambios de **datos** van aquí.

## Reglas

1. **Un archivo `.sql` por cambio**, con nombre `AAAAMMDD_HHMM_descripcion.sql`
   (ej. `20261029_1730_corrige_saldo_credito_123.sql`). Se ejecutan en orden alfabético.
2. **Cada script se ejecuta una sola vez por base.** El pipeline lo registra en `ctl.SCRIPTS_EJECUTADOS`.
3. **Un script ya ejecutado no se edita.** Si hay que corregirlo, se crea otro script nuevo.
   Si se modifica, el pipeline lo detecta (cambia su huella) y bloquea el PR.
4. **Solo datos.** `CREATE/ALTER/DROP TABLE`, vistas, SP, permisos: PROHIBIDO aquí (la estructura va en el proyecto).
5. **Todo el script corre en una transacción:** si una sentencia falla, no se aplica nada.
6. **Antes de un `UPDATE` o `DELETE`, respaldar las filas** en `ctl.RESPALDO_DATOS` (ver la plantilla).

## Riesgo

| Contenido | Riesgo | Aprobación hacia PROD |
|---|---|---|
| Solo `INSERT` | ESTÁNDAR | Jefe IN |
| `UPDATE`, `DELETE`, `MERGE`, `TRUNCATE` | SENSIBLE | Jefe IN + TI |
| DDL o permisos | PROHIBIDO | No se despliega |

## Flujo

Rama `feature/...` → archivo nuevo aquí → PR a `develop`. El pipeline:
- lo ejecuta en la base efímera de pruebas (valida sintaxis y columnas),
- muestra en el reporte del PR qué scripts quedan **pendientes** en el destino,
- al hacer merge, lo ejecuta en DEV; en el release, en PROD.

Ver la plantilla: `_plantilla.sql.txt` (no se ejecuta porque no termina en `.sql`).

> Un rollback del esquema **no** deshace datos. Para revertir datos se usa el respaldo en `ctl.RESPALDO_DATOS`
> con otra migración nueva.
