#!/usr/bin/env python3
"""Valida las convenciones del Pull Request: título, nombre de rama y plantilla completa.
Lee TITULO, RAMA, BASE y CUERPO del entorno. Emite anotaciones ::error:: de GitHub Actions."""
import os
import re
import sys

titulo = os.environ.get("TITULO", "")
rama = os.environ.get("RAMA", "")
base = os.environ.get("BASE", "")
cuerpo = os.environ.get("CUERPO", "") or ""
errores = []

TIPOS = "feat|fix|perf|refactor|docs|test|chore|revert"
if not re.match(rf"^({TIPOS})(\([a-z0-9_.\-]+\))?!?: .{{5,}}", titulo):
    errores.append(("Título del PR", "Debe seguir Conventional Commits: '<tipo>(<ámbito>): <descripción>'. "
                    "Ej: 'feat(tab): agrega columna SEGMENTO_RIESGO a TB_CREDITO'. Tipos: " + TIPOS.replace("|", ", ")))

if base == "main":
    if not re.match(r"^(develop|hotfix/[a-z0-9._\-]+)$", rama):
        errores.append(("Rama de origen", f"A main solo se llega desde develop (release) o hotfix/*. Rama actual: {rama}"))
elif base == "develop":
    if not re.match(r"^(feature|fix|hotfix|docs|chore|demo)/[a-z0-9._\-]+$", rama):
        errores.append(("Nombre de rama", f"Use feature/<ticket>-<descripcion>, fix/..., docs/... en minúsculas. Rama actual: {rama}"))

sin_comentarios = re.sub(r"<!--.*?-->", "", cuerpo, flags=re.S)
m = re.search(r"##\s*Motivo[^\n]*\n(.*?)(?=\n##\s|\Z)", sin_comentarios, flags=re.S | re.I)
if not m or len(m.group(1).strip()) < 10:
    errores.append(("Descripción del PR", "Complete la sección '## Motivo' de la plantilla (qué necesidad de negocio atiende)."))

for titulo_err, msg in errores:
    print(f"::error title={titulo_err}::{msg}")
if errores:
    sys.exit(1)
print("Convenciones OK")
