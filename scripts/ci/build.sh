#!/usr/bin/env bash
# Compila el SQL Project y genera el DACPAC.  Uso: build.sh <version> [archivo_log] [ruta_proyecto]
# Si falla, publica los errores como anotaciones visibles en el PR / la ejecución.
set -uo pipefail
VERSION="${1:-1.0.0}"; LOG="${2:-build.log}"; PROY="${3:-${PROYECTO:-database/BI_Analitico/BI_Analitico.sqlproj}}"
dotnet build "$PROY" -c Release -nologo -p:DacVersion="${VERSION#v}" 2>&1 | tee "$LOG"
rc=${PIPESTATUS[0]}
if [ "$rc" -ne 0 ]; then
  errores=$(grep -E "error [A-Z]+[0-9]+|: error " "$LOG" | sed 's/\x1b\[[0-9;]*m//g' | sort -u | head -25)
  if [ -n "$errores" ]; then
    while IFS= read -r l; do echo "::error title=Build del SQL Project::$l"; done <<< "$errores"
  else
    echo "::error title=Build del SQL Project::$(tail -25 "$LOG" | sed 's/%/%25/g' | awk '{printf "%s%%0A", $0}')"
  fi
fi
exit "$rc"
