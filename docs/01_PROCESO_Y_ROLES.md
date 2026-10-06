# Proceso DataOps y roles

## Principios

1. **Un solo camino a producción:** todo cambio entra por Pull Request y lo despliega el pipeline con una cuenta de servicio. Nadie ejecuta scripts a mano en PROD.
2. **Se promueve lo mismo que se probó:** el DACPAC compilado es el artefacto que se instala. El mismo archivo queda adjunto en el release.
3. **El riesgo decide quién aprueba,** no el rol de quien hace el cambio. Lo calcula el pipeline con reglas que define TI.
4. **TI gobierna, no opera:** fija las reglas, da su visto previo en lo sensible, audita después y es el único que puede hacer rollback.
5. **La evidencia se genera sola:** PR, reporte, script, pruebas, release y auditoría quedan enlazados.

## Clasificación de riesgo

| Nivel | Ejemplos | Hacia PROD aprueba |
|---|---|---|
| 🟢 **ESTÁNDAR** (preaprobado por política de TI) | vistas, SP, funciones, tablas nuevas, columnas nuevas nullable | Jefe IN → despliegue → auditoría posterior de TI |
| 🟠 **SENSIBLE** | DROP de objetos o columnas, cambio de tipo, renombres, rebuild de tablas, posible pérdida de datos, esquema nuevo, cambios a pipelines o reglas | Jefe IN **+ visto previo de TI** |
| 🔴 **PROHIBIDO** | permisos, usuarios, roles, logins, `xp_cmdshell`, `OPENROWSET`, configuración de servidor | Nadie: el pipeline lo bloquea. Lo gestiona TI por su canal |

Las reglas están en [`deployment/reglas_riesgo.yml`](../deployment/reglas_riesgo.yml). Si un PR modifica ese archivo, el cambio es SENSIBLE.

**Pérdida de datos:** el perfil de despliegue bloquea cualquier operación que pueda perder datos. Solo se permite si un usuario de TI agrega la etiqueta `ti/autoriza-perdida-datos` al PR. El pipeline verifica quién puso la etiqueta.

## Flujo 1: DEV → DEV

| # | Quién | Qué pasa |
|---|---|---|
| 1 | Analista / Data Scientist / Data Engineering | Crea `feature/<ticket>-<descripcion>` desde `develop` y hace commits. |
| 2 | Analista | Abre el PR hacia `develop` con la plantilla. |
| 3 | Pipeline | **Convenciones:** título, rama y plantilla. |
| 4 | Pipeline | **Build:** compila el DACPAC propuesto y el actual. Los errores de compilación y referencias rotas aparecen aquí. |
| 5 | Pipeline | **Base efímera:** instala la versión actual, carga datos ficticios, actualiza a la propuesta **con datos**, re-ejecuta las cargas y corre pruebas de datos y de humo. |
| 6 | Pipeline | **Destino real:** Deploy Report y script contra `BI_DEV`, y jobs de SQL Agent que usan lo modificado. |
| 7 | Pipeline | **Reporte:** riesgo, qué cambia, impacto, diagrama de dependencias, script y pruebas, como comentario en el PR más un HTML completo. Etiqueta `riesgo/*`. |
| 8 | Data Engineering | Aprueba o solicita cambios. El **Gate de aprobaciones** verifica que el aprobador tenga el rol y no sea el autor. |
| 9 | Data Engineering | Merge (squash). |
| 10 | Pipeline | Despliega a `BI_DEV`, registra en `ctl.HISTORIAL_DESPLIEGUE`, valida y comenta el resultado en el PR. |

Ya no se bloquea la base DEV por usuario: cada PR se prueba en su propia base efímera, y `BI_DEV` solo recibe lo que pasó las pruebas. Los PR sin actividad se cierran por convención y se pueden reabrir.

## Flujo 2: DEV → PROD

| # | Quién | Qué pasa |
|---|---|---|
| 1 | Jefe IN / Data Engineering | Abre el PR `develop → main` (release). |
| 2 | Pipeline | Pasos 3 a 7 del flujo anterior, contra **`BI_PROD`**. |
| 3 | Jefe IN | Aprueba. Si es **SENSIBLE**, TI también debe aprobar (visto previo). |
| 4 | Jefe IN | Merge con **merge commit** (no squash, para conservar la historia). |
| 5 | Pipeline | Calcula la versión semántica, toma una foto previa de `BI_PROD`, **recalcula el riesgo contra PROD** y se detiene si subió a SENSIBLE sin visto de TI. |
| 6 | Pipeline | Despliega, registra y ejecuta la validación post-deploy (humo + pruebas de datos). |
| 7 | Pipeline | Crea el **release `vX.Y.Z`** con el DACPAC, el script ejecutado, el deploy report, la foto previa y los resultados. |
| 8 | Pipeline | Abre el issue **"🔎 Auditoría post-PROD vX.Y.Z"** asignado a TI, con plazo, y actualiza el **diccionario de datos**. |
| 9 | TI | Audita: etiqueta `auditoria/conforme` (certifica y cierra) o `auditoria/observado` (comenta la observación). |
| 10 | IN | Si fue observado: corrige con un nuevo PR (`fix:`) dentro del plazo, o justifica. |
| 11 | TI | Si vence el plazo sin corrección: el issue recibe `rollback/habilitado` y TI ejecuta **Actions → Rollback** hacia la versión anterior. |
| 12 | IN | Tras un rollback, revierte el cambio en `main` (`revert:`) para que el repositorio vuelva a coincidir con PROD. |

**Jobs, SP y ETL:** el impacto se conoce **antes** del despliegue (dependencias en el modelo y jobs que usan los objetos), y la base efímera re-ejecuta la carga con el código nuevo. El rollback usa `BlockOnPossibleDataLoss`: si volver atrás implica perder datos, se detiene y TI decide.

**Drift:** cada noche se compara cada base con lo que debería tener. Si alguien cambió algo a mano, se abre un issue `drift`.

## Roles

| Macro rol | Rol | Puede | Mecanismo |
|---|---|---|---|
| Desarrollador | Data Analyst / Data Scientist | Commit en `feature/*`, abrir PR | Colaborador del repo; ramas protegidas impiden push directo |
| Desarrollador | Data Engineering | Commit, abrir PR | Colaborador del repo |
| Revisor DEV | Data Engineering | Aprobar PR hacia `develop` | Variable `ROL_DATA_ENGINEERING` + Gate |
| Aprobador PROD | Jefe IN (+ suplente) | Aprobar PR hacia `main` | Variable `ROL_JEFE_IN` + Gate + CODEOWNERS |
| Aprobador sensible | TI / DBA | Visto previo en cambios SENSIBLES, autorizar pérdida de datos | Variable `ROL_TI` + Gate |
| Funcional | Usuario de negocio | Leer, comentar y dar conformidad del indicador (UAT) | Lectura + comentarios en el PR o issue |
| Auditor post-PROD | TI / DBA | Dictamen, observaciones, rollback, atender drift | `ROL_TI` en Auditoría y Rollback |
| Ejecutor | Pipeline (`svc_pipeline`) | Build, pruebas, despliegue | Única identidad con permisos de DDL en las bases |

**Segregación de funciones:** quien desarrolla ≠ quien aprueba ≠ quien despliega ≠ quien audita. El autor de un PR nunca cuenta como aprobador de su propio cambio.

## Plazos (configurables)

| Variable | Por defecto | Significado |
|---|---|---|
| `SLA_AUDITORIA_HORAS` | 48 | Tiempo de TI para emitir el dictamen después del despliegue |
| `SLA_CORRECCION_HORAS` | 24 | Tiempo de IN para corregir una observación antes de habilitar el rollback |

## Matriz RACI

| Actividad | IN Dev | Data Eng. | Jefe IN | TI / DBA | Pipeline |
|---|---|---|---|---|---|
| Desarrollo del cambio | R | R | | | |
| Abrir PR | R | R | | | |
| Build, pruebas, riesgo, documentación | | | | | R |
| Aprobación DEV | | A | | | |
| Aprobación PROD (estándar) | | C | A | I | |
| Aprobación PROD (sensible) | | C | A | A | |
| Despliegue | | | | I | R |
| Auditoría posterior | I | I | I | A/R | |
| Corrección de observaciones | R | R | A | C | |
| Rollback | I | I | I | A/R | R |
| Reglas de riesgo y perfil de despliegue | C | C | C | A/R | |
