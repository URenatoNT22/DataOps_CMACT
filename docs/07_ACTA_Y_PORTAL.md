# Acta del pase, Anexo 01 y Portal DataOps

Todo se genera solo, a partir de lo que el pipeline ya sabe. Nadie arma el acta a mano.

## Qué se genera y dónde

| Documento | Cuándo | Dónde |
|---|---|---|
| **Borrador del acta** (sección D en Word + Anexo 01 en Excel) | En cada Pull Request | *Actions → ejecución → Artifacts → `reporte-cambio` → `acta_borrador/`* |
| **Acta definitiva** (sección D en Word y web + Anexo 01 en Excel) | En cada despliegue (DEV y PROD) | Artefacto `evidencias-…` de la ejecución. En PROD, además, **adjunta al release** |
| **Portal DataOps** | Después de cada despliegue, auditoría o control de drift, y cada mañana | GitHub Pages (`Settings → Pages → Source: GitHub Actions`) |

## Sección D: de dónde sale cada dato

| Dato del acta | Fuente |
|---|---|
| Afecta cierre diario / performance, criticidad | Sección 4 de la plantilla del PR (si falta, la criticidad se deduce del riesgo) |
| Nombre de aplicación | Variable `APLICACION` (por defecto `BI_ANALITICO`) |
| Ubicación del script | Release de la versión (DACPAC y script ejecutado adjuntos) |
| Listado de scripts: crear / modificar / eliminar | Plan de despliegue (Deploy Report) contra la base destino |
| Actualización de datos | Migraciones de `migraciones/` ejecutadas en el pase |
| Base y servidor | Variables `DB_DEV` / `DB_PROD`; servidor enmascarado o variable `SERVIDOR_ETIQUETA` |
| Jobs y frecuencia | Sección 3 del PR + jobs del servidor que usan los objetos modificados |
| Fecha, hora, ejecutado por, versión, estado | Ejecución del pipeline |
| Validación post-despliegue y plan de reversión | Resultados de las pruebas y versión anterior |

Las firmas no se generan: el acta es la evidencia técnica y la conformidad se firma aparte.

## Anexo 01: clasificar campos sensibles

En el `.sql` de la tabla, junto a la descripción de la columna, agregar la propiedad `DatoSensible` con una
de las categorías de la hoja "Lista Campos Sensibles":

```sql
EXEC sys.sp_addextendedproperty @name = N'DatoSensible', @value = N'DNI / Documento de identidad',
    @level0type = N'SCHEMA', @level0name = N'dbo', @level1type = N'TABLE', @level1name = N'INT_BfxRep90_Dia',
    @level2type = N'COLUMN', @level2name = N'Doi';
GO
```

Si una columna no está clasificada pero su nombre lo sugiere (`Doi`, `Celular`, `Direccion`, `Correo`,
`CuentaCliente`…), el anexo la incluye con `*` para que el responsable la confirme.

## Portal

| Sección | Contenido |
|---|---|
| Resumen | Versión en PROD, pases del mes, % de despliegues exitosos, PR en curso, auditorías y alertas |
| Pases a producción | Un registro por release con sus documentos (acta web, Word y Excel) |
| Validaciones | Resultado de validación por pase y riesgo de los PR abiertos |
| Inventario de datos sensibles | Todas las tablas del modelo vigente con sus campos sensibles |
| Diccionario de datos | Tablas, columnas, descripciones, dependencias e historial |

> **Confidencialidad:** GitHub Pages de un repositorio público es público. Con datos reales, publicar el
> portal en un servidor interno o usar un repositorio privado.
