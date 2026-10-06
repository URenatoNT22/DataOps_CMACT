#!/usr/bin/env python3
"""
Clasifica el riesgo de un cambio: ESTANDAR | SENSIBLE | PROHIBIDO.

Fuentes (todas opcionales salvo las reglas):
  --deploy-report  XML generado por `sqlpackage /Action:DeployReport` contra la base destino
  --script         SQL generado por `sqlpackage /Action:Script` (lo que realmente se ejecutaría)
  --archivos       archivo de texto con la lista de archivos modificados en el PR (git diff --name-only)
  --proyecto       carpeta del SQL Project (se revisa todo el código en busca de sentencias prohibidas)

Salida: JSON con nivel, motivos y operaciones; además imprime un resumen.
"""
import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

NIVELES = ["ESTANDAR", "SENSIBLE", "PROHIBIDO"]


def leer_deploy_report(ruta):
    """Devuelve (operaciones, alertas). operaciones = {Nombre: [{objeto, tipo}]}."""
    operaciones, alertas = {}, []
    if not ruta or not Path(ruta).exists() or Path(ruta).stat().st_size == 0:
        return None, []
    raiz = ET.parse(ruta).getroot()
    quitar_ns = lambda t: t.split("}", 1)[-1]
    for nodo in raiz.iter():
        etiqueta = quitar_ns(nodo.tag)
        if etiqueta == "Operation":
            nombre = nodo.get("Name")
            for item in nodo:
                if quitar_ns(item.tag) == "Item":
                    operaciones.setdefault(nombre, []).append({
                        "objeto": item.get("Value"), "tipo": item.get("Type"),
                        "avisos": [i.get("Value") for i in item if quitar_ns(i.tag) == "Issue"],
                    })
        elif etiqueta == "Alert":
            for issue in nodo:
                if quitar_ns(issue.tag) == "Issue":
                    alertas.append({"alerta": nodo.get("Name"), "detalle": issue.get("Value"),
                                    "id": issue.get("Id")})
    return operaciones, alertas


def esquema_de(objeto):
    m = re.match(r"\[([^\]]+)\]", objeto or "")
    return m.group(1) if m else ""


def clasificar(reglas, operaciones, alertas, script, archivos, proyecto):
    motivos = []  # (nivel, texto)

    def subir(nivel, texto):
        motivos.append({"nivel": nivel, "motivo": texto})

    if operaciones is not None:
        for op in reglas.get("operaciones_sensibles", []):
            for it in operaciones.get(op, []):
                subir("SENSIBLE", f"Operación {op} sobre {it['objeto']} ({it['tipo']})")
        for nombre, items in operaciones.items():
            for it in items:
                if it["tipo"] in reglas.get("tipos_prohibidos", []):
                    subir("PROHIBIDO", f"{nombre} de objeto de seguridad {it['objeto']} ({it['tipo']})")
                esq = esquema_de(it["objeto"])
                if it["tipo"] == "SqlSchema" and nombre == "Create":
                    subir("SENSIBLE", f"Creación de esquema nuevo {it['objeto']}")
                elif esq and it["tipo"] not in ("SqlSchema",) and esq not in reglas.get("esquemas_permitidos", []) \
                        and it["tipo"] not in reglas.get("tipos_prohibidos", []):
                    subir("SENSIBLE", f"Objeto fuera de los esquemas permitidos: {it['objeto']}")
        for a in alertas:
            if a["alerta"] in reglas.get("alertas_sensibles", []):
                subir("SENSIBLE", f"Alerta {a['alerta']}: {a['detalle']}")

    if script:
        cuerpo = re.sub(r"/\*.*?\*/", "", script, flags=re.S)
        cuerpo = re.sub(r"--[^\n]*", "", cuerpo)
        for regla in reglas.get("patrones_script_sensibles", []):
            for m in re.finditer(regla["pattern"], cuerpo, flags=re.I):
                linea = cuerpo[max(0, cuerpo.rfind("\n", 0, m.start()) + 1): cuerpo.find("\n", m.end())].strip()
                if "tmp_ms_xx" in linea:  # renombres internos de un TableRebuild (ya reportado como operación)
                    continue
                subir("SENSIBLE", f"{regla['motivo']}: `{linea[:160]}`")

    for archivo in archivos:
        for prefijo in reglas.get("archivos_gobierno", []):
            if archivo.startswith(prefijo):
                subir("SENSIBLE", f"Modifica archivo de gobierno del proceso: {archivo}")
                break

    if proyecto and Path(proyecto).exists():
        for sql in Path(proyecto).rglob("*.sql"):
            if "bin" in sql.parts or "obj" in sql.parts:
                continue
            texto = re.sub(r"/\*.*?\*/", "", sql.read_text(encoding="utf-8-sig"), flags=re.S)
            texto = re.sub(r"--[^\n]*", "", texto)
            for regla in reglas.get("patrones_codigo_prohibidos", []):
                if re.search(regla["pattern"], texto, flags=re.I | re.M):
                    subir("PROHIBIDO", f"{regla['motivo']} en {sql.as_posix()}")

    nivel = "ESTANDAR"
    for m in motivos:
        if NIVELES.index(m["nivel"]) > NIVELES.index(nivel):
            nivel = m["nivel"]
    # quitar duplicados conservando orden
    vistos, unicos = set(), []
    for m in motivos:
        k = (m["nivel"], m["motivo"])
        if k not in vistos:
            vistos.add(k)
            unicos.append(m)
    return nivel, unicos


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--reglas", default="deployment/reglas_riesgo.yml")
    p.add_argument("--deploy-report")
    p.add_argument("--script")
    p.add_argument("--archivos")
    p.add_argument("--proyecto", default="database")
    p.add_argument("--destino", default="", help="Etiqueta del destino evaluado (ej. BI_PROD)")
    p.add_argument("--salida", required=True)
    a = p.parse_args()

    reglas = yaml.safe_load(Path(a.reglas).read_text(encoding="utf-8"))
    operaciones, alertas = leer_deploy_report(a.deploy_report)
    script = Path(a.script).read_text(encoding="utf-8-sig") if a.script and Path(a.script).exists() else ""
    archivos = []
    if a.archivos and Path(a.archivos).exists():
        archivos = [l.strip() for l in Path(a.archivos).read_text().splitlines() if l.strip()]

    nivel, motivos = clasificar(reglas, operaciones, alertas, script, archivos, a.proyecto)
    resumen = {k: len(v) for k, v in (operaciones or {}).items()}
    salida = {
        "nivel": nivel,
        "destino": a.destino,
        "evaluado_contra_destino": operaciones is not None,
        "motivos": motivos,
        "resumen_operaciones": resumen,
        "operaciones": operaciones or {},
        "alertas": alertas,
        "perdida_datos_posible": any(x["alerta"] == "DataIssue" for x in alertas),
        "archivos_modificados": archivos,
    }
    Path(a.salida).parent.mkdir(parents=True, exist_ok=True)
    Path(a.salida).write_text(json.dumps(salida, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Riesgo: {nivel}")
    for m in motivos:
        print(f"  - [{m['nivel']}] {m['motivo']}")
    print(f"Operaciones: {resumen or 'sin cambios'}")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        import traceback
        tb = traceback.format_exc()
        print(tb, file=sys.stderr)
        print("::error title=Clasificación de riesgo::" + tb.replace("%", "%25").replace("\n", "%0A")[-3000:])
        sys.exit(1)
