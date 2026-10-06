# Paso a Gitea (implementación)

La demo corre en GitHub, pero se diseñó para pasarse a Gitea con pocos cambios: la lógica está en scripts propios (`scripts/ci/`), no en funciones exclusivas de GitHub.

| Componente | GitHub (demo) | Gitea (implementación) |
|---|---|---|
| Workflows | `.github/workflows/*.yml` | Gitea Actions también lee `.github/workflows` (o `.gitea/workflows`). La sintaxis es compatible. |
| Runner | Hosted (nube) + ngrok | **act_runner** en un servidor de TI dentro de la red, con Docker. Ya no se necesita ngrok. |
| Base efímera de pruebas | `services: mssql` | Igual (act_runner soporta `services` con Docker). |
| `actions/checkout`, `setup-dotnet`, `upload-artifact` | Marketplace | Se usan igual (Gitea los toma de GitHub o de un espejo interno aprobado por TI). |
| Pasos con `actions/github-script` y `gh` CLI | API de GitHub | **Reemplazar** por llamadas a la API de Gitea (`curl` con token o `tea` CLI): comentarios, etiquetas, issues y releases. Son ~6 pasos. |
| Gate de aprobaciones | Workflow propio | Gitea lo trae **nativo** en la protección de ramas: aprobaciones requeridas, *approvals whitelist* por usuarios o equipos y checks obligatorios. El workflow solo se mantiene para la regla "SENSIBLE requiere TI". |
| Roles | Variables `ROL_*` | Equipos de la organización (`IN-Desarrollo`, `IN-DataEngineering`, `IN-Jefatura`, `TI-DBA`). |
| CODEOWNERS | Soportado | Soportado (Gitea 1.21+). |
| Etiquetas `riesgo/*`, `auditoria/*` | Etiquetas normales | Gitea tiene **scoped labels**: `riesgo/...` es excluyente (un PR solo puede tener un riesgo). |
| Environments (`produccion`) | Historial de despliegues | No existen en Gitea. Se ignoran; el historial queda en releases y en `ctl.HISTORIAL_DESPLIEGUE`. |
| Releases con DACPAC adjunto | Releases | Releases de Gitea (o el registro de paquetes genérico). |
| Diccionario de datos | GitHub Pages | Publicarlo en un servidor web interno, adjuntarlo al release o servirlo desde el registro de paquetes. |
| Secretos | Secrets de Actions | Secrets de Actions de Gitea (por repo u organización). TI administra la cuenta de servicio. |

## Checklist de migración

1. TI instala Gitea y act_runner (con Docker) en la red interna, con acceso a la instancia SQL.
2. Crear la organización, los equipos y el repositorio. Hacer push del repo (`git push --mirror`).
3. Configurar secretos, variables y protección de ramas con *approvals whitelist* por equipo.
4. Reemplazar los pasos `github-script` / `gh` por llamadas a la API de Gitea.
5. Cambiar `SQL_SERVER` a la instancia real y crear `svc_pipeline` con el script de setup.
6. Probar el flujo completo con un PR de prueba (el guion de la demo sirve tal cual).
