#!/usr/bin/env python3
"""
Reemplaza los objetos de DEMO del SQL Project por los objetos extraídos de una base existente.

Uso: importar.py <carpeta_extraida> <carpeta_proyecto> [--resumen resumen.md]

- Conserva el .sqlproj y lo que necesita el pipeline (esquema ctl + ctl.HISTORIAL_DESPLIEGUE).
- Descarta del repositorio lo que el proceso prohíbe (usuarios, roles, permisos): lo gestiona TI.
- Mueve el contenido de demo (pruebas y datos ficticios) a carpetas *_demo para que no se ejecuten.
"""
import argparse
import re
import shutil
from pathlib import Path

PROHIBIDO = re.compile(
    r"^\s*(GRANT|DENY|REVOKE)\b|\bCREATE\s+(USER|LOGIN|ROLE|APPLICATION\s+ROLE)\b|\bALTER\s+(ROLE|SERVER\s+ROLE)\b.*\bADD\s+MEMBER\b",
    re.I | re.M)
CONSERVAR = {"ctl/Tables/HISTORIAL_DESPLIEGUE.sql"}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("extraido")
    p.add_argument("proyecto")
    p.add_argument("--resumen", default="resumen_importacion.md")
    a = p.parse_args()
    ext, proy = Path(a.extraido), Path(a.proyecto)
    raiz = proy.parent.parent  # raíz del repositorio

    # 1. guardar lo que necesita el pipeline
    guardados = {r: (proy / r).read_text(encoding="utf-8") for r in CONSERVAR if (proy / r).exists()}

    # 2. borrar objetos de demo (todo menos el .sqlproj)
    for item in proy.iterdir():
        if item.suffix == ".sqlproj":
            continue
        shutil.rmtree(item) if item.is_dir() else item.unlink()

    # 3. copiar lo extraído, filtrando lo prohibido
    copiados, descartados, por_tipo = [], [], {}
    for f in sorted(ext.rglob("*.sql")):
        rel = f.relative_to(ext)
        texto = f.read_text(encoding="utf-8-sig", errors="replace")
        if PROHIBIDO.search(re.sub(r"--[^\n]*", "", texto)):
            descartados.append(str(rel))
            continue
        destino = proy / rel
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(texto, encoding="utf-8")
        copiados.append(str(rel))
        tipo = rel.parts[1] if len(rel.parts) > 2 else rel.parts[0]
        por_tipo[tipo] = por_tipo.get(tipo, 0) + 1

    # 4. restaurar objetos del pipeline (y su esquema si la base no lo tiene)
    textos = "\n".join((proy / c).read_text(encoding="utf-8") for c in copiados)
    if not re.search(r"CREATE\s+SCHEMA\s+\[?ctl\]?", textos, re.I):
        (proy / "Security").mkdir(exist_ok=True)
        (proy / "Security" / "ctl.sql").write_text(
            "-- Esquema de control usado por el pipeline (historial de despliegues).\n"
            "CREATE SCHEMA [ctl] AUTHORIZATION [dbo];\nGO\n", encoding="utf-8")
    for rel, contenido in guardados.items():
        if not (proy / rel).exists():
            (proy / rel).parent.mkdir(parents=True, exist_ok=True)
            (proy / rel).write_text(contenido, encoding="utf-8")

    # 5. contenido de demo fuera del circuito
    movidos = []
    for origen, destino in [("tests/datos", "tests/datos_demo"), ("setup/02_datos_ficticios.sql", "setup/demo/02_datos_ficticios.sql"),
                            ("setup/03_job_carga_diaria.sql", "setup/demo/03_job_carga_diaria.sql")]:
        o, d = raiz / origen, raiz / destino
        if o.exists():
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(o), str(d))
            movidos.append(f"{origen} → {destino}")
    (raiz / "tests" / "datos").mkdir(parents=True, exist_ok=True)
    (raiz / "tests" / "datos" / "README.md").write_text(
        "# Pruebas de datos\n\nAgregar aquí las pruebas de la base real: un `.sql` por prueba que devuelve filas "
        "solo cuando hay un problema. Ver ejemplos en `tests/datos_demo/` y `docs/02_CONVENCIONES.md`.\n", encoding="utf-8")

    r = ["## Importación de base existente", "",
         f"Objetos importados: **{len(copiados)}**", ""]
    r += [f"- {t}: {n}" for t, n in sorted(por_tipo.items())]
    if descartados:
        r += ["", f"**Descartados por ser de seguridad ({len(descartados)})**: los gestiona TI, no el repositorio."]
        r += [f"- `{d}`" for d in descartados[:50]]
    if movidos:
        r += ["", "**Contenido de demo retirado del circuito:**"] + [f"- {m}" for m in movidos]
    r += ["", "Revisar en el PR: que el build compile (referencias a otras bases requieren variables SQLCMD) "
          "y agregar descripciones (MS_Description) y pruebas de datos propias."]
    Path(a.resumen).write_text("\n".join(r), encoding="utf-8")
    print("\n".join(r))


if __name__ == "__main__":
    main()
