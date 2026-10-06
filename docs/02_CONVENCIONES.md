# Convenciones

## Ramas

| Rama | Propósito | Protegida | Se despliega en |
|---|---|---|---|
| `main` | Versión aprobada en producción | Sí | `BI_PROD` |
| `develop` | Integración | Sí | `BI_DEV` |
| `feature/<ticket>-<descripcion>` | Un cambio = una rama, nace de `develop` | No | Base efímera del PR |
| `fix/<ticket>-<descripcion>` | Corrección, nace de `develop` | No | Base efímera del PR |
| `hotfix/<descripcion>` | Urgencia en PROD, nace de `main` y vuelve a `main` y a `develop` | No | Base efímera del PR |

Nombres en minúsculas, con guiones: `feature/bi-101-rango-atraso`.

## Commits y título del PR: Conventional Commits

```
<tipo>(<ámbito>): <descripción en imperativo>
```

| Tipo | Uso | Efecto en la versión |
|---|---|---|
| `feat` | Objeto o columna nueva, nuevo indicador | MINOR (1.**2**.0) |
| `fix` | Corrección | PATCH (1.2.**1**) |
| `perf`, `refactor` | Optimización o reorganización sin cambio funcional | PATCH |
| `docs`, `test`, `chore` | Documentación, pruebas, mantenimiento | PATCH |
| `revert` | Revertir un cambio (ej. después de un rollback) | PATCH |
| `feat!:` o `BREAKING CHANGE` | Rompe compatibilidad para los consumidores (columna eliminada, vista renombrada) | MAJOR (**2**.0.0) |

Ámbito sugerido: el esquema (`tab`, `rpt`, `src`, `ctl`) o `pipeline`.

Ejemplos:
- `feat(tab): agrega RANGO_ATRASO a TB_CREDITO`
- `fix(rpt): corrige ratio de mora cuando el saldo es cero`
- `feat(tab)!: elimina ZONA de TB_CREDITO`

## Estrategia de merge

- `feature/*` → `develop`: **Squash and merge** (un commit por cambio, con el título del PR).
- `develop` → `main`: **Create a merge commit** (conserva los commits y permite calcular la versión).

## Objetos SQL

| Regla | Ejemplo |
|---|---|
| Un archivo por objeto, en `<esquema>/<Tipo>/<OBJETO>.sql` | `tab/Tables/TB_CREDITO.sql` |
| Tablones: prefijo `TB_`, en el esquema `tab`, un registro por entidad y fecha de corte | `tab.TB_CRONOGRAMA` |
| Vistas de consumo: prefijo `vw_`, en `rpt`. Los reportes nunca leen tablones directamente | `rpt.vw_CARTERA_CREDITOS` |
| Procedimientos de carga: `usp_CARGA_<TABLON>`, idempotentes por fecha de corte, registran en `ctl.BITACORA_CARGA` | `tab.usp_CARGA_TB_CREDITO` |
| Columnas en MAYÚSCULAS_CON_GUION_BAJO | `SALDO_CAPITAL` |
| Toda tabla, vista, SP y columna lleva `MS_Description`: alimenta el diccionario de datos | `sp_addextendedproperty` al final del archivo |
| Columnas nuevas en tablas con datos: `NULL` o con `DEFAULT` | Evita cambios SENSIBLES innecesarios |
| Nada de permisos, usuarios ni roles en el proyecto | Es PROHIBIDO: lo gestiona TI |
| Cambios de estructura (renombrar, cambiar tipo) | Usar el refactor del proyecto; se clasifican como SENSIBLES |

## Pruebas de datos

Archivo `.sql` en `tests/datos/` que **devuelve filas solo cuando hay problema**:

```sql
-- severidad: ERROR            (ERROR bloquea el PR · ADVERTENCIA solo informa)
-- descripcion: Qué valida, en lenguaje de negocio.
SELECT ... WHERE <condición de falla>;
```

Tres niveles: técnico (el SP compila y corre), datos (saldos, claves, huérfanos) y negocio (el indicador cuadra y está en rango).

## Versionado

- PROD: `vMAYOR.MENOR.PARCHE`, calculado automáticamente desde los commits. Cada versión es un **release** con su DACPAC (punto de rollback).
- DEV: `MAYOR.MENOR.PARCHE.<ejecución>`.
- La versión instalada en cada base se consulta en `ctl.HISTORIAL_DESPLIEGUE`.
