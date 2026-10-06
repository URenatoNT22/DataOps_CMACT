# Guion de la demo (20-25 minutos)

Requisitos: instalación completa ([03_INSTALACION.md](03_INSTALACION.md)), ngrok activo y tres cuentas:
**Analista** (abre PR), **Jefe IN** (`URenatoNT22`, aprueba DEV y PROD) y **TI** (visto en sensibles, auditoría y rollback).

Hay tres ramas de ejemplo ya preparadas:

| Rama | Caso | Resultado esperado |
|---|---|---|
| `feature/bi-101-rango-atraso` | Columna nueva en un tablón + SP + vista | 🟢 ESTÁNDAR |
| `feature/bi-102-elimina-zona` | Eliminar una columna con datos | 🟠 SENSIBLE + posible pérdida de datos |
| `feature/bi-103-permisos` | Un `GRANT` dentro del proyecto | 🔴 PROHIBIDO |

---

## Acto 1: el problema (2 min)
Hoy un cambio viaja como un script por correo y depende de que TI lo ejecute. No se sabe qué versión está en PROD ni cómo volver atrás.

## Acto 2: un cambio estándar de DEV a DEV (6 min)

1. **Analista**: mostrar el diff de `feature/bi-101-rango-atraso` (agrega `RANGO_ATRASO`). Abrir el PR hacia `develop` con la plantilla.
2. Mostrar los checks corriendo en el PR:
   - **Build**: si se comete un error de sintaxis o se referencia una columna que no existe, falla aquí.
   - **Pruebas en base efímera**: SQL Server se levanta en el runner, se instala la versión actual, se cargan datos ficticios, se actualiza con datos y se corren las pruebas de negocio.
3. Abrir el **comentario automático** del bot: riesgo 🟢, qué cambia, diagrama de impacto (la vista y el job dependen del SP), script exacto y pruebas. En *Actions → la ejecución → Artifacts → reporte-cambio* está el HTML completo.
4. Mostrar el check **Aprobaciones requeridas** en rojo: falta Data Engineering. Intentar aprobar con la cuenta del **autor**: no cuenta.
5. **Jefe IN** (como Data Engineering) aprueba → el gate pasa a verde → *Squash and merge*.
6. Mostrar *Actions → Despliegue* sobre `develop` y luego, en SSMS:
   ```sql
   SELECT TOP 5 * FROM BI_DEV.ctl.HISTORIAL_DESPLIEGUE ORDER BY 1 DESC;
   SELECT TOP 10 RANGO_ATRASO, * FROM BI_DEV.rpt.vw_CARTERA_CREDITOS;
   ```

## Acto 3: de DEV a PROD sin TI (5 min)

1. Abrir el PR `develop → main` con el título `feat: release cartera por tramos de atraso`.
2. El reporte ahora se evalúa contra **BI_PROD** y el gate pide al **Jefe IN**.
3. **Jefe IN** aprueba → *Create a merge commit*.
4. Mostrar:
   - **Release v1.1.0** con el DACPAC, el script ejecutado, el deploy report y la foto previa (punto de rollback).
   - **Issue "🔎 Auditoría post-PROD v1.1.0"** asignado a TI con plazo.
   - **Diccionario de datos** actualizado en GitHub Pages (la nueva columna con su descripción e historial).
5. **TI** agrega la etiqueta `auditoria/conforme`: el issue se cierra y el release queda "certificado por TI".

> TI no ejecutó nada, pero tiene toda la evidencia y la última palabra.

## Acto 4: un cambio sensible (5 min)

1. **Analista** abre el PR de `feature/bi-102-elimina-zona` hacia `develop` → riesgo 🟠, alerta de **pérdida de datos** y el impacto (`vw_CARTERA_CREDITOS` deja de exponer `ZONA`).
2. Aprobar y hacer merge a develop. Luego abrir el PR `develop → main`.
3. El gate exige **Jefe IN + TI**. Aprueba el Jefe IN: sigue en rojo.
4. **TI** revisa y aprueba. Como hay pérdida de datos, agrega `ti/autoriza-perdida-datos` (si la agrega otra cuenta, el pipeline la ignora).
5. Merge → release **v2.0.0** (MAJOR por el `!` del título: rompe compatibilidad para los reportes).

## Acto 5: lo que el pipeline no deja pasar (2 min)

1. Abrir el PR de `feature/bi-103-permisos` → 🔴 **PROHIBIDO**: los permisos los gestiona TI. El PR no se puede fusionar.
2. Romper una prueba a propósito (por ejemplo, cambiar en el SP el cálculo de `SALDO_CAPITAL`): la prueba `04_cronograma_cuadra_con_credito` falla y el PR se bloquea.

## Acto 6: observación, rollback y drift (3 min)

1. En la auditoría de un release, **TI** pone `auditoria/observado` con un comentario → el bot da plazo a IN.
2. **TI** ejecuta *Actions → Rollback* (versión anterior, motivo, issue, `ROLLBACK`). Mostrar que otra cuenta no puede ejecutarlo.
3. **Drift**: en SSMS, hacer un cambio manual en `BI_PROD` (ej. `ALTER VIEW` o crear una tabla) y ejecutar *Actions → Control de drift* → se abre el issue 🧭 con la diferencia.

## Cierre: preguntas que ahora se responden solas
¿Quién hizo el cambio? ¿Quién lo aprobó? ¿Qué versión está en PROD? ¿Qué se ejecutó exactamente? ¿Qué pruebas pasó? ¿Hubo rollback y por qué? Todo está en el PR, el release, el issue de auditoría y `ctl.HISTORIAL_DESPLIEGUE`.
