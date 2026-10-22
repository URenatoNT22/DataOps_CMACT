# Guía paso a paso: de la configuración al primer pase a producción

Esta guía es para quien configura el repositorio (una sola vez) y para quien hace cambios todos los días.
Al final hay un ejemplo completo: crear una vista nueva y llevarla de DEV a PROD.

---

## Idea central (leer primero)

- **El repositorio es la fuente de verdad.** Lo que está en `database/BI_Analitico/` es lo que debe existir en la base.
- **Nadie edita la base a mano.** Ni en DEV ni en PROD. Se edita el archivo `.sql` en una rama, se abre un Pull Request y el pipeline despliega.
- **No hay que "generar el proyecto" cada vez.** El proyecto se genera una sola vez; después solo se editan sus archivos.
- **El pipeline solo conecta con lo que tú configuras** en GitHub: servidor, usuario, contraseña y nombres de las bases.

---

## Parte 1: configuración (una sola vez)

Todo se configura en GitHub: **Settings → Secrets and variables → Actions**. Nada de esto va dentro del código.

### 1.1 Conexión (pestaña *Secrets*)

| Secret | Qué poner | Ejemplo |
|---|---|---|
| `SQL_SERVER` | Dirección de tu SQL Server **con coma** antes del puerto | `4.tcp.ngrok.io,12345` |
| `SQL_USER` | Login de la cuenta de servicio | `svc_pipeline` |
| `SQL_PASSWORD` | Su contraseña | (la que definiste en `setup/01_crear_bases_y_login.sql`) |

> Con ngrok: ejecutas `ngrok tcp 1433`, copias lo que aparece en *Forwarding* (`tcp://4.tcp.ngrok.io:12345`), quitas `tcp://` y cambias `:` por `,`. Cada vez que reinicies ngrok, actualiza este secret.

### 1.2 Nombres de las bases y roles (pestaña *Variables*)

| Variable | Qué poner | Ejemplo |
|---|---|---|
| `DB_DEV` | **Nombre de la base de desarrollo** | `BI_DEV` |
| `DB_PROD` | **Nombre de la base de producción** | `BI_PROD` |
| `ROL_JEFE_IN` | Usuario(s) de GitHub que aprueban hacia PROD | `URenatoNT22` |
| `ROL_DATA_ENGINEERING` | Usuario(s) que aprueban hacia DEV | `URenatoNT22` |
| `ROL_TI` | Usuario(s) de TI | `cuenta-ti` |

Si `DB_DEV` y `DB_PROD` no se crean, se usan `BI_DEV` y `BI_PROD`. Varios usuarios se separan con coma.

### 1.3 La cuenta de servicio en SQL Server

El login de `SQL_USER` debe existir en la instancia y ser `db_owner` **solo** en las bases de `DB_DEV` y `DB_PROD`. Para las bases de demo ya lo hace `setup/01_crear_bases_y_login.sql`. Para bases con otro nombre, cambia `BI_DEV` / `BI_PROD` en ese script antes de ejecutarlo (sin el `CREATE DATABASE` si la base ya existe).

### 1.4 Probar la conexión

*Actions → Despliegue → Run workflow*, rama **develop**. El primer paso, "Verificar configuración", confirma que los secrets existen. Si falla la conexión, el error aparece en rojo en el resumen de la ejecución.

---

## Parte 2: ¿qué base vas a conectar?

### Escenario A: bases de demo (`BI_DEV` / `BI_PROD` vacías)

**No generas nada.** El proyecto de demo ya está en el repo.

1. *Actions → Despliegue → Run workflow* sobre **develop** → crea las tablas, vistas y procedimientos en `BI_DEV`.
2. Lo mismo sobre **main** → los crea en `BI_PROD` y publica el release `v1.0.0`.
3. *Actions → Datos de demo → Run workflow* → ambiente `ambas`, confirmar con `DEMO` → carga datos ficticios.

### Escenario B: una base real que ya tiene objetos

Aquí **sí** se genera el proyecto, **una sola vez**, a partir de la base:

1. Pon en `DB_DEV` el nombre de tu base de desarrollo real, y en `DB_PROD` el de producción.
2. *Actions → Importar base existente → Run workflow*:
   - `base`: el nombre de la base de la que se toma la estructura (normalmente la de producción).
   - `rama`: dejar `feature/importa-base-existente`.
3. El workflow **solo lee** la base. Genera un `.sql` por objeto en `database/BI_Analitico/` (carpetas por esquema y tipo) y los deja en esa rama. Descarta usuarios, roles y permisos (los gestiona TI) y retira el contenido de demo.
4. Abre un Pull Request de esa rama hacia `develop` y revisa el reporte. Si algo no compila (por ejemplo, referencias a otras bases), se corrige en la misma rama.
5. Merge. Desde ese momento el repositorio representa tu base, y se trabaja como en la Parte 3.

> **Protección incluida:** si por error apuntas el pipeline a una base real **sin** haberla importado, el despliegue se detiene con el mensaje *"Base no administrada por el pipeline"*. Así no se borra ningún objeto que no esté en el repositorio.

---

## Parte 3: cómo hace cambios el equipo (siempre igual)

```
develop ──┬──────────────────────────────── merge ──→ se despliega en DEV
          └── feature/bi-104-...  (tu cambio) ┘
```

1. Crear una rama desde `develop` con el nombre `feature/<ticket>-<descripcion>`.
2. Editar o crear archivos `.sql` dentro de `database/BI_Analitico/`.
3. Abrir un Pull Request hacia `develop`.
4. El pipeline valida y comenta; Data Engineering aprueba y hace merge; se despliega en DEV.
5. Para producción: un PR de `develop` hacia `main`. El Jefe IN aprueba (y TI, si es sensible), se hace merge y se despliega en PROD.

Se puede trabajar desde el navegador (sin instalar nada) o desde la PC con Git. El ejemplo muestra las dos formas.

---

## Parte 4: ejemplo completo, una vista de mora por analista

**Pedido:** Cobranzas quiere ver, por analista, cuánto saldo tiene en mora.

### Paso 1: crear la rama y el archivo

**Opción navegador:**
1. En GitHub, selector de ramas → `develop`.
2. Entrar a `database/BI_Analitico/rpt/Views/` → **Add file → Create new file**.
3. Nombre: `vw_MORA_POR_ANALISTA.sql`.
4. Pegar el contenido de abajo.
5. **Commit changes…** → elegir **Create a new branch** → nombre `feature/bi-104-mora-por-analista` → **Propose changes**.

**Opción PC (Git):**
```bash
git checkout develop
git pull
git checkout -b feature/bi-104-mora-por-analista
# crear el archivo database/BI_Analitico/rpt/Views/vw_MORA_POR_ANALISTA.sql
git add .
git commit -m "feat(rpt): agrega vista de mora por analista"
git push -u origin feature/bi-104-mora-por-analista
```

**Contenido del archivo:**
```sql
-- Vista de consumo: saldo y saldo en mora por analista y fecha de corte.
CREATE VIEW [rpt].[vw_MORA_POR_ANALISTA]
AS
SELECT
    [t].[FECHA_CORTE],
    [t].[ANALISTA],
    COUNT_BIG(*)                                                              AS [NRO_CREDITOS],
    SUM([t].[SALDO_CAPITAL])                                                  AS [SALDO_CARTERA],
    SUM(CASE WHEN [t].[DIAS_ATRASO] > 30 THEN [t].[SALDO_CAPITAL] ELSE 0 END) AS [SALDO_EN_MORA]
FROM [tab].[TB_CREDITO] AS [t]
GROUP BY [t].[FECHA_CORTE], [t].[ANALISTA];
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description',
    @value = N'Saldo de cartera y saldo en mora (más de 30 días) por analista y fecha de corte. Para gestión de cobranza.',
    @level0type = N'SCHEMA', @level0name = N'rpt', @level1type = N'VIEW', @level1name = N'vw_MORA_POR_ANALISTA';
GO
```

El bloque `sp_addextendedproperty` es la descripción que aparecerá en el diccionario de datos.

### Paso 2: abrir el Pull Request
- **Base:** `develop` · **Compare:** `feature/bi-104-mora-por-analista`
- **Título:** `feat(rpt): agrega vista de mora por analista`
- **Descripción:** completar la plantilla; como mínimo, la sección **Motivo**.

### Paso 3: lo que hace el pipeline solo (3 a 5 minutos)

| Check | Qué verás |
|---|---|
| Convenciones del PR | ✅ si el título y la rama siguen el formato |
| Build y análisis de código | ✅ compila. Un error de sintaxis o una columna mal escrita aparece aquí, con el archivo y la línea |
| Pruebas en base efímera | ✅ se instala sobre una copia con datos y pasan las pruebas |
| Reporte y clasificación de riesgo | Comentario en el PR: 🟢 **ESTÁNDAR**, "🆕 Agregado `rpt.vw_MORA_POR_ANALISTA`", dependencia de `tab.TB_CREDITO` y el script que se ejecutará en `BI_DEV` |
| Aprobaciones requeridas | ⏳ en rojo hasta que apruebe Data Engineering |

### Paso 4: aprobar y fusionar (Data Engineering)
**Files changed → Review changes → Approve**. Cuando todo esté en verde: **Squash and merge**.

### Paso 5: verificar en DEV
En *Actions → Despliegue* aparece la ejecución sobre `develop`. En el PR, el bot comenta "✅ Desplegado en `BI_DEV`". En SSMS:
```sql
SELECT TOP 10 * FROM BI_DEV.rpt.vw_MORA_POR_ANALISTA ORDER BY SALDO_EN_MORA DESC;
SELECT TOP 5 * FROM BI_DEV.ctl.HISTORIAL_DESPLIEGUE ORDER BY ID_DESPLIEGUE DESC;
```

### Paso 6: pasar a producción
1. **Pull requests → New** → base `main`, compare `develop`.
2. Título: `feat: release vista de mora por analista`.
3. El reporte ahora se calcula contra `BI_PROD`. Aprueba el **Jefe IN**. Si fuera SENSIBLE, también TI.
4. **Create a merge commit** (no squash).
5. Resultado automático:
   - Despliegue en `BI_PROD`.
   - Release `v1.1.0` con el DACPAC, el script ejecutado y las evidencias.
   - Issue **🔎 Auditoría post-PROD v1.1.0** para TI.
   - Diccionario de datos actualizado (si GitHub Pages está activado).

### Paso 7: auditoría de TI
TI abre el issue y agrega la etiqueta `auditoria/conforme`: el issue se cierra y el release queda certificado. Si encuentra algo, usa `auditoria/observado` y comenta; IN tiene plazo para corregir.

---

## Parte 5: si algo falla

| Mensaje | Causa | Qué hacer |
|---|---|---|
| "Secretos SQL_* no configurados" | Faltan secrets | Parte 1.1 |
| "No hay conexión con BI_DEV (¿ngrok activo?)" | ngrok apagado o dirección cambiada | Reiniciar ngrok y actualizar `SQL_SERVER` |
| Build en rojo con `SQL71501` u otro código | Error en el `.sql` (objeto o columna inexistente, sintaxis) | Corregir el archivo en la misma rama: el PR se re-valida solo |
| Pruebas en rojo | Una prueba de datos detectó un problema | Abrir el reporte del PR: dice qué prueba falló y muestra filas de ejemplo |
| "Aprobaciones requeridas" en rojo | Falta la aprobación del rol correcto, o aprobó el mismo autor | Debe aprobar alguien del rol (variables `ROL_*`) distinto del autor |
| "Base no administrada por el pipeline" | La base tiene objetos que no están en el repo | Escenario B: importar la base primero |
| "Falta visto de TI" al desplegar | El cambio resultó SENSIBLE contra PROD | TI aprueba el PR de `develop → main` |
| Despliegue bloqueado por pérdida de datos | El cambio elimina o recorta columnas con datos | TI agrega `ti/autoriza-perdida-datos` en el PR, si lo acepta |

## Preguntas frecuentes

**¿Puedo seguir creando objetos desde SSMS?** Para probar en tu PC, sí. Pero lo que debe llegar a DEV o PROD se agrega como archivo en el repo. Lo que se cree a mano en las bases lo detecta el control de drift cada noche.

**¿Dónde veo la documentación?** En el comentario de cada PR, en *Actions → ejecución → Artifacts → reporte-cambio* (HTML), en cada release y en el diccionario publicado en GitHub Pages.

**¿Cómo vuelvo atrás un cambio en PROD?** Solo TI: *Actions → Rollback*, indicando la versión anterior (por ejemplo `v1.0.0`), el motivo y `ROLLBACK` para confirmar.
