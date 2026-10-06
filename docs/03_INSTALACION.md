# Instalación de la demo

Tiempo estimado: 30 a 45 minutos. Solo se instala en tu máquina SQL Server y ngrok. El resto corre en GitHub Actions; no hace falta un runner propio.

## 1. SQL Server 2022 Developer

1. Instalar **SQL Server 2022 Developer** (gratuito) y SSMS.
2. Habilitar TCP/IP: *SQL Server Configuration Manager → SQL Server Network Configuration → Protocols for MSSQLSERVER → TCP/IP → Enabled*. En *IP Addresses → IPAll*, poner `TCP Port = 1433`.
3. Habilitar autenticación mixta: SSMS → clic derecho en el servidor → *Properties → Security → SQL Server and Windows Authentication mode*.
4. Reiniciar el servicio de SQL Server. Opcional: iniciar **SQL Server Agent** para el job de ejemplo.
5. En SSMS, abrir [`setup/01_crear_bases_y_login.sql`](../setup/01_crear_bases_y_login.sql), **cambiar la contraseña** y ejecutar. Crea `BI_DEV`, `BI_PROD` y el login `svc_pipeline` (db_owner solo en esas dos bases).

## 2. ngrok (exponer la instancia a GitHub Actions)

1. Crear cuenta en ngrok e instalarlo. Ejecutar `ngrok config add-authtoken <token>`.
2. ngrok pide **verificar la cuenta con tarjeta** para los túneles TCP; no se cobra en el plan gratuito.
3. Ejecutar:
   ```
   ngrok tcp 1433
   ```
4. Copiar la dirección `Forwarding`, ej. `tcp://4.tcp.ngrok.io:12345`. El secreto se escribe con **coma**: `4.tcp.ngrok.io,12345`.

> Cada vez que se reinicia ngrok la dirección cambia: actualizar el secreto `SQL_SERVER`. Mientras ngrok esté apagado, los PR siguen funcionando (se evalúan contra la base efímera), pero no se puede desplegar.

## 3. Secretos y variables en GitHub

*Settings → Secrets and variables → Actions*

**Secrets**

| Nombre | Valor |
|---|---|
| `SQL_SERVER` | `4.tcp.ngrok.io,12345` |
| `SQL_USER` | `svc_pipeline` |
| `SQL_PASSWORD` | la contraseña del paso 1.5 |

**Variables**

| Nombre | Valor demo | Uso |
|---|---|---|
| `ROL_JEFE_IN` | `URenatoNT22` | Aprueba hacia PROD |
| `ROL_DATA_ENGINEERING` | `URenatoNT22` | Aprueba hacia DEV |
| `ROL_TI` | `<cuenta-ti>` | Visto en sensibles, auditoría, rollback |
| `DB_DEV` / `DB_PROD` | `BI_DEV` / `BI_PROD` | Opcional (esos son los valores por defecto) |
| `SLA_AUDITORIA_HORAS` | `48` | Opcional |
| `SLA_CORRECCION_HORAS` | `24` | Opcional |

Pasar a otra instancia o a otras bases es solo cambiar estos valores.

## 4. Cuentas y colaboradores

*Settings → Collaborators → Add people*: invitar la cuenta del **analista** y la de **TI**. Cada una acepta la invitación desde su correo.

## 5. Protección de ramas

*Settings → Branches → Add classic branch protection rule*. Crear una regla para `main` y otra para `develop`:

- ✅ Require a pull request before merging
  - Required approvals: **1**
  - ✅ Dismiss stale pull request approvals when new commits are pushed
- ✅ Require status checks to pass before merging. Agregar:
  - `Convenciones del PR`
  - `Build y análisis de código`
  - `Pruebas en base efímera`
  - `Reporte y clasificación de riesgo`
  - `Aprobaciones requeridas`
- ✅ Require conversation resolution before merging
- ✅ Do not allow bypassing the above settings (aplica también al administrador)
- ❌ Allow force pushes / ❌ Allow deletions

> Los checks aparecen en el buscador después de que corrieron al menos una vez (ya corrieron en el PR #1).

*Settings → General → Pull Requests*: dejar habilitados **squash** (feature → develop) y **merge commit** (develop → main).

## 6. GitHub Pages (diccionario de datos)

*Settings → Pages → Build and deployment → Source: **GitHub Actions***.

Después de cada despliegue a PROD, el diccionario queda en `https://urenatont22.github.io/DataOps_CMACT/`.

## 7. Primer despliegue y datos

1. *Actions → Despliegue → Run workflow* sobre **develop**: crea el esquema en `BI_DEV`.
2. *Actions → Despliegue → Run workflow* sobre **main**: crea el esquema en `BI_PROD` y el release **v1.0.0**.
3. *Actions → Datos de demo → Run workflow → ambas*: genera datos ficticios y carga los tablones.
4. Opcional, en SSMS: [`setup/03_job_carga_diaria.sql`](../setup/03_job_carga_diaria.sql) crea el job de SQL Agent (sirve para mostrar el análisis de impacto sobre jobs).

Verificación en SSMS:
```sql
SELECT * FROM BI_PROD.ctl.HISTORIAL_DESPLIEGUE;
SELECT TOP 20 * FROM BI_PROD.rpt.vw_RESUMEN_CARTERA_AGENCIA ORDER BY FECHA_CORTE DESC;
```
