#!/usr/bin/env python3
"""
Genera los documentos del Pase a Producción a partir de lo que ya sabe el pipeline:

  actividades.docx / actividades.html   Sección D. Actividades del Pase a Producción
  anexo01_inventario_tablas.xlsx        Anexo 01 - Inventario de tablas (con campos sensibles)
  acta.json                             Datos estructurados (los usa el portal / dashboard)

Fuentes: Deploy Report (riesgo.json), migraciones de datos, jobs afectados, pruebas, DACPAC
(descripciones y clasificación de datos sensibles) y los campos del/los Pull Request.
Las firmas quedan en blanco: el documento es la evidencia técnica; la conformidad se firma aparte.
"""
import argparse
import datetime as dt
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import modelo_dacpac as md  # noqa: E402

TIPOS_OBJETO = {
    "SqlTable": "Tabla", "SqlView": "Vista", "SqlProcedure": "Procedimiento almacenado",
    "SqlScalarFunction": "Función", "SqlInlineTableValuedFunction": "Función",
    "SqlMultiStatementTableValuedFunction": "Función", "SqlSchema": "Esquema", "SqlIndex": "Índice",
    "SqlSequence": "Secuencia", "SqlSynonym": "Sinónimo", "SqlTrigger": "Trigger", "SqlDmlTrigger": "Trigger",
}
OPERACION = {"Create": "crear", "Alter": "modificar", "TableRebuild": "modificar", "Rename": "modificar",
             "Move": "modificar", "Drop": "eliminar"}

# Catálogo de campos sensibles (mismo listado que usa TI en el Anexo 01)
CATEGORIAS = [
    "DNI / Documento de identidad", "Nombre completo (identifica a una persona)", "Dirección", "Teléfono",
    "Fecha de nacimiento", "Correo electrónico", "Número de cuenta", "CCI", "Número de tarjeta", "CVV", "PIN",
    "Fecha de vencimiento", "Contraseñas", "Token", "Ingreso / Sueldo", "Huellas biométricas",
    "Reconocimiento facial", "Firma digital",
]
# Detección por nombre de columna (se marca con * para que el responsable la confirme)
REGLAS_SENSIBLES = [
    (r"(^|_)(doi|dni|ruc)($|_)|nro_?doc|num_?doc|documento", "DNI / Documento de identidad"),
    (r"nombre_?(completo|cliente)|^cliente$|apellido|razon_?social|^nombres?$", "Nombre completo"),
    (r"direcci|domicilio", "Dirección"),
    (r"celular|telefono|tel[eé]f|movil|^fono", "Teléfono"),
    (r"nacimiento|fec_?nac", "Fecha de nacimiento"),
    (r"correo|e?mail", "Correo electrónico"),
    (r"(^|_)cci($|_)", "CCI"),
    (r"cuenta|(^|_)cta|^cta", "Número de cuenta"),
    (r"tarjeta|(^|_)pan($|_)", "Número de tarjeta"),
    (r"(^|_)cvv($|_)", "CVV"),
    (r"(^|_)pin($|_)", "PIN"),
    (r"password|contrase|clave_?acceso", "Contraseñas"),
    (r"(^|_)token", "Token"),
    (r"sueldo|salario|ingreso", "Ingreso / Sueldo"),
]
ROMANOS = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI",
           "XVII", "XVIII", "XIX", "XX", "XXI", "XXII", "XXIII", "XXIV", "XXV", "XXVI", "XXVII", "XXVIII", "XXIX", "XXX"]


def romano(i):
    return ROMANOS[i - 1] if i <= len(ROMANOS) else str(i)


def leer(ruta, defecto=None):
    if ruta and Path(ruta).exists() and Path(ruta).stat().st_size:
        try:
            return json.loads(Path(ruta).read_text(encoding="utf-8"))
        except Exception:
            pass
    return defecto


def simple(nombre):
    return ".".join(md._partes(nombre)) or nombre


# ------------------------------------------------------------------ campos del Pull Request
def _linea(cuerpo, etiqueta):
    m = re.search(rf"^[ \t]*[-*]?[ \t]*\*\*{etiqueta}[^*\n]*\*\*[ \t]*:?[ \t]*([^\n]*)$", cuerpo, flags=re.I | re.M)
    return m.group(1).strip() if m else ""


def _opcion(cuerpo, etiqueta):
    """Devuelve la opción marcada [x] en una línea del tipo: **Etiqueta:** [ ] Sí  [x] No"""
    linea = _linea(cuerpo, etiqueta)
    m = re.search(r"\[[xX]\]\s*([^\[\n]+)", linea)
    return m.group(1).strip().rstrip("·|,;") if m else ""


def campos_pr(cuerpo):
    cuerpo = re.sub(r"<!--.*?-->", "", cuerpo or "", flags=re.S)
    limpio = lambda v: "" if not v or v.startswith("_") or v in ("-", "—") else v
    return {
        "requerimiento": limpio(_linea(cuerpo, "Código de requerimiento")),
        "area": limpio(_linea(cuerpo, "Área solicitante")),
        "modulo": limpio(_linea(cuerpo, "Módulo")),
        "tipo_pase": _opcion(cuerpo, "Tipo de pase"),
        "afecta_cierre": _opcion(cuerpo, "Afecta cierre diario"),
        "afecta_performance": _opcion(cuerpo, "Afecta performance"),
        "criticidad": _opcion(cuerpo, "Criticidad"),
        "jobs": limpio(_linea(cuerpo, "Jobs involucrados")),
        "frecuencia": _opcion(cuerpo, "Frecuencia del job"),
        "ventana": limpio(_linea(cuerpo, "Ventana de ejecución")),
    }


def consolidar(prs, riesgo_nivel):
    """Un release puede traer varios PR: se toma el valor más exigente."""
    campos = [campos_pr(p.get("cuerpo", "")) for p in prs]
    si = lambda clave: "Sí" if any(c[clave].lower().startswith("s") for c in campos) else (
        "No" if any(c[clave] for c in campos) else "")
    orden = {"alta": 3, "media": 2, "baja": 1}
    crit = max((c["criticidad"] for c in campos if c["criticidad"]), key=lambda x: orden.get(x.lower(), 0), default="")
    if not crit:
        crit = {"SENSIBLE": "Alta", "PROHIBIDO": "Alta", "ESTANDAR": "Media"}.get(riesgo_nivel, "Media") + " (según riesgo calculado)"
    jobs = "; ".join(dict.fromkeys(c["jobs"] for c in campos if c["jobs"]))
    frec = ", ".join(dict.fromkeys(c["frecuencia"] for c in campos if c["frecuencia"]))
    return {
        "afecta_cierre": si("afecta_cierre") or "No indicado",
        "afecta_performance": si("afecta_performance") or "No indicado",
        "criticidad": crit,
        "jobs": jobs, "frecuencia": frec,
        "requerimientos": [dict(c, pr=p.get("numero"), titulo=p.get("titulo"), autor=p.get("autor"),
                                aprobadores=p.get("aprobadores", ""), url=p.get("url", "")) for c, p in zip(campos, prs)],
    }


# ------------------------------------------------------------------ objetos y datos
def listado_scripts(riesgo):
    grupos = {"crear": [], "modificar": [], "eliminar": []}
    vistos = set()
    for op, items in (riesgo.get("operaciones") or {}).items():
        accion = OPERACION.get(op)
        if not accion:
            continue
        for it in items:
            if it["tipo"] not in TIPOS_OBJETO or (accion, it["objeto"]) in vistos:
                continue
            vistos.add((accion, it["objeto"]))
            detalle = " (reconstrucción de tabla)" if op == "TableRebuild" else (" (renombre)" if op == "Rename" else "")
            grupos[accion].append({"objeto": simple(it["objeto"]), "tipo": TIPOS_OBJETO[it["tipo"]], "nota": detalle})
    for g in grupos.values():
        g.sort(key=lambda x: (x["tipo"], x["objeto"].lower()))
    return grupos


def sensibles_de_tabla(obj):
    salida, detectados = [], False
    for c in obj.columnas:
        if c.sensible:
            salida.append(f"{c.nombre} ({c.sensible})")
            continue
        nombre = c.nombre.lower()
        if nombre.startswith(("id_", "tipo_", "cod_tipo", "flg_", "ind_")) or nombre.endswith(("_id", "_tipo")):
            continue
        for patron, cat in REGLAS_SENSIBLES:
            if re.search(patron, nombre, flags=re.I):
                salida.append(f"{c.nombre} ({cat})*")
                detectados = True
                break
    return salida, detectados


def inventario(objetos, riesgo, todas=False):
    tablas_afectadas = set()
    for op, items in (riesgo.get("operaciones") or {}).items():
        if op in ("Create", "Alter", "TableRebuild"):
            tablas_afectadas |= {it["objeto"] for it in items if it["tipo"] == "SqlTable"}
    filas = []
    for nombre, o in sorted(objetos.items()):
        if o.tipo_sql != "SqlTable" or (not todas and nombre not in tablas_afectadas):
            continue
        campos, detectados = sensibles_de_tabla(o)
        filas.append({"tabla": f"{o.esquema}.{o.corto}", "descripcion": o.descripcion or "(sin descripción en el proyecto)",
                      "sensible": "Sí" if campos else "No", "campos": ", ".join(campos), "detectado": detectados})
    return filas


# ------------------------------------------------------------------ modelo del acta
def construir(a):
    ctx = leer(a.contexto, {})
    riesgo = leer(a.riesgo, {"nivel": "ESTANDAR", "operaciones": {}})
    migraciones = [r for r in (leer(a.migraciones, {}) or {}).get("resultados", []) if r["estado"] != "OMITIDA"]
    jobs_det = (leer(a.jobs, {}) or {}).get("jobs", [])
    pruebas = (leer(a.pruebas, {}) or {}).get("resultados", []) + (leer(a.smoke, {}) or {}).get("resultados", [])
    prs = leer(a.prs, []) or []
    objetos = md.cargar(a.dacpac) if a.dacpac and Path(a.dacpac).exists() else {}

    ahora = dt.datetime.now(dt.timezone(dt.timedelta(hours=-5)))
    fecha = ctx.get("fecha") or ahora.strftime("%d/%m/%Y")
    hora = ctx.get("hora") or ahora.strftime("%H:%M")
    app = ctx.get("aplicacion") or "BI_ANALITICO"
    version = ctx.get("version", "")
    numero = ctx.get("numero_acta") or f"Acta_{ahora:%Y%m}_{app}_{version}".rstrip("_")
    pr_info = consolidar(prs, riesgo.get("nivel"))
    total_ok = sum(1 for p in pruebas if p["estado"] in ("OK", "OMITIDA"))
    return {
        "numero_acta": numero, "aplicacion": app, "version": version,
        "version_anterior": ctx.get("version_anterior", ""), "ambiente": ctx.get("ambiente", "PROD"),
        "estado": ctx.get("estado", "EXITOSO"), "fecha": fecha, "hora": hora,
        "base": ctx.get("base", ""), "servidor": ctx.get("servidor", "(gestionado por TI)"),
        "ejecutado_por": ctx.get("ejecutado_por", "Pipeline DataOps"),
        "aprobadores": ctx.get("aprobadores", ""), "release_url": ctx.get("release_url", ""),
        "run_url": ctx.get("run_url", ""), "commit": ctx.get("commit", ""), "riesgo": riesgo.get("nivel", ""),
        "perdida_datos": riesgo.get("perdida_datos_posible", False),
        "impacto": pr_info, "scripts": listado_scripts(riesgo),
        "migraciones": [{"script": m["script"], "tipo": {"INSERTA": "INSERT", "MODIFICA": "UPDATE / DELETE"}.get(m["tipo"], m["tipo"]),
                         "estado": m["estado"], "filas": m.get("filas"), "descripcion": m.get("descripcion", "")} for m in migraciones],
        "jobs_detectados": sorted({j["job"] for j in jobs_det}),
        "validacion": {"total": len(pruebas), "ok": total_ok,
                       "fallas": [p["prueba"] for p in pruebas if p["estado"] not in ("OK", "OMITIDA", "ADVERTENCIA")]},
        "inventario": inventario(objetos, riesgo, todas=a.inventario_completo),
        "generado": ahora.strftime("%d/%m/%Y %H:%M"),
    }


# ------------------------------------------------------------------ HTML
CSS = """
@page{size:A4;margin:18mm 14mm}
body{font-family:Calibri,"Segoe UI",Arial,sans-serif;color:#1f2328;margin:0;background:#f4f5f7;font-size:10.5pt}
.hoja{max-width:820px;margin:24px auto;background:#fff;border:1px solid #d0d7de;padding:28px 34px}
.cab{display:grid;grid-template-columns:150px 1fr 150px;border:1px solid #8c959f;align-items:center;text-align:center}
.cab div{padding:10px 8px;font-size:9pt}.cab .t{border-left:1px solid #8c959f;border-right:1px solid #8c959f;font-weight:700;font-size:11pt}
.meta{display:flex;justify-content:space-between;font-size:9pt;color:#57606a;margin:10px 0 18px}
h2{background:#d9d9d9;padding:6px 10px;font-size:12.5pt;margin:18px 0 12px}
table{width:100%;border-collapse:collapse}th,td{border:1px solid #8c959f;padding:6px 8px;vertical-align:top;font-size:9.5pt}
th{background:#eef0f2;font-weight:700;text-align:center}
.det ol{margin:0 0 6px 18px;padding:0}.det li{margin:2px 0}.lbl{font-weight:700}
.sub{font-weight:700;margin:8px 0 3px}.rom{list-style:upper-roman;margin:2px 0 4px 34px}
.chk{font-family:Consolas,monospace}.ok{color:#1a7f37;font-weight:700}.ko{color:#cf222e;font-weight:700}
.nota{font-size:8.5pt;color:#57606a;margin-top:10px}a{color:#0969da}
@media print{body{background:#fff}.hoja{border:0;margin:0;padding:0}}
"""


def _chk(valor, opcion):
    return "[X]" if valor.lower().startswith(opcion.lower()[0]) and valor not in ("No indicado", "") else "[&nbsp;&nbsp;]"


def _lista_html(items):
    if not items:
        return "<div class='nota'>No aplica.</div>"
    return "<ol class='rom'>" + "".join(
        f"<li>{html.escape(i['objeto'])} <span class='nota'>· {html.escape(i['tipo'])}{html.escape(i['nota'])}</span></li>"
        for i in items) + "</ol>"


def render_html(d):
    e = html.escape
    imp, s = d["impacto"], d["scripts"]
    estado_cls = "ok" if d["estado"] in ("EXITOSO", "BORRADOR") else "ko"
    filas = []
    # 1. Ejecución de scripts / jobs
    det = [f"<ol><li><span class='lbl'>Afecta cierre diario:</span> <span class='chk'>Sí {_chk(imp['afecta_cierre'], 'Sí')} &nbsp; No {_chk(imp['afecta_cierre'], 'No')}</span></li>",
           f"<li><span class='lbl'>Afecta performance del sistema:</span> <span class='chk'>Sí {_chk(imp['afecta_performance'], 'Sí')} &nbsp; No {_chk(imp['afecta_performance'], 'No')}</span></li>",
           f"<li><span class='lbl'>Criticidad:</span> {e(imp['criticidad'])}</li></ol>",
           "<div class='sub'>Datos de los scripts</div><ol start='4'>",
           f"<li><span class='lbl'>Nombre de aplicación:</span> {e(d['aplicacion'])}</li>",
           f"<li><span class='lbl'>Ubicación del script:</span> " + (
               f"<a href='{e(d['release_url'])}'>Release {e(d['version'])}</a> (DACPAC y script ejecutado adjuntos)" if d["release_url"]
               else f"Repositorio, versión {e(d['version'])} · commit {e(d['commit'][:8])}") + "</li>",
           "<li><span class='lbl'>Listado de scripts:</span>",
           "<div class='sub'>- Crear:</div>" + _lista_html(s["crear"]),
           "<div class='sub'>- Modificar:</div>" + _lista_html(s["modificar"]),
           "<div class='sub'>- Eliminar:</div>" + _lista_html(s["eliminar"]), "</li>",
           f"<li><span class='lbl'>Base donde ejecutar:</span> {e(d['base'])}</li>",
           f"<li><span class='lbl'>Servidor:</span> {e(d['servidor'])}</li></ol>",
           "<div class='sub'>Datos de los jobs</div><ol start='9'>",
           f"<li><span class='lbl'>Jobs:</span> {e(imp['jobs'] or 'No aplica')}"
           + (f"<div class='nota'>Jobs que usan los objetos modificados (detectados en el servidor): {e(', '.join(d['jobs_detectados']))}</div>" if d["jobs_detectados"] else "")
           + "</li>",
           f"<li><span class='lbl'>Frecuencia:</span> {e(imp['frecuencia'] or 'No aplica')}</li></ol>"]
    filas.append(("1", "[X] Ejecución de scripts / jobs", "".join(det)))
    # 2. Migración de datos
    if d["migraciones"]:
        mig = "<ol class='rom'>" + "".join(
            f"<li>{e(m['script'])} <span class='nota'>· {e(m['tipo'])} · {e(m['estado'])}"
            + (f" · {m['filas']} fila(s)" if m.get("filas") is not None else "") + "</span>"
            + (f"<div class='nota'>{e(m['descripcion'])}</div>" if m["descripcion"] else "") + "</li>" for m in d["migraciones"]) + "</ol>"
        mig += "<div class='nota'>Cada script se ejecuta una sola vez, en una transacción, y queda registrado en ctl.SCRIPTS_EJECUTADOS. Las filas modificadas o eliminadas se respaldan en ctl.RESPALDO_DATOS.</div>"
    else:
        mig = "<div class='nota'>No aplica: el pase no incluye cambios de datos.</div>"
    filas.append(("2", ("[X]" if d["migraciones"] else "[ ]") + " Actualización de datos (INSERT / UPDATE / DELETE)", mig))
    # 3. Validación post-despliegue
    v = d["validacion"]
    val = (f"<span class='{'ok' if not v['fallas'] else 'ko'}'>{v['ok']} de {v['total']} validaciones conformes</span>"
           "<div class='nota'>Objetos desplegados, vistas consultables, procesos ejecutables y pruebas de calidad de datos.</div>")
    if v["fallas"]:
        val += "<div class='ko'>Observadas: " + e(", ".join(v["fallas"])) + "</div>"
    filas.append(("3", "[X] Validación post-despliegue", val))
    # 4. Reversión
    rev = (f"Reversión a la versión <b>{e(d['version_anterior'] or 'anterior aprobada')}</b> mediante el workflow <i>Rollback</i> "
           "(ejecución exclusiva de TI, con motivo y evidencia). La foto previa de la base queda adjunta al release."
           + ("<div class='nota'>Los cambios de datos se revierten con una nueva migración usando el respaldo de ctl.RESPALDO_DATOS.</div>" if d["migraciones"] else ""))
    filas.append(("4", "[X] Plan de reversión", rev))

    consid = (f"<b>Fecha:</b> {e(d['fecha'])}<br><b>Hora:</b> {e(d['hora'])}<br><b>Ejecutado por:</b> {e(d['ejecutado_por'])}"
              f"<br><b>Versión:</b> {e(d['version'])}<br><b>Estado:</b> <span class='{estado_cls}'>{e(d['estado'])}</span>"
              + (f"<br><b>Aprobado por:</b> {e(d['aprobadores'])}" if d["aprobadores"] else "")
              + (f"<br><a href='{e(d['run_url'])}'>Evidencia de ejecución</a>" if d["run_url"] else ""))
    cuerpo = "".join(
        f"<tr><td style='text-align:center'>{n}</td><td><b>{e(t)}</b></td><td class='det'>{det_}</td>"
        + (f"<td rowspan='{len(filas)}' style='text-align:center'><b>Pipeline DataOps</b><br><span class='nota'>(automático)</span></td>"
           f"<td rowspan='{len(filas)}'>{consid}</td>" if i == 0 else "") + "</tr>"
        for i, (n, t, det_) in enumerate(filas))
    reqs = "".join(
        f"<tr><td>{e(r['requerimiento'] or '—')}</td><td>{('<a href=' + chr(39) + e(r['url']) + chr(39) + '>#' + str(r['pr']) + '</a> ') if r.get('url') else ''}{e(r.get('titulo') or '')}</td>"
        f"<td>{e(r['area'] or '—')}</td><td>{e(r.get('autor') or '')}</td><td>{e(r.get('aprobadores') or '')}</td></tr>"
        for r in imp["requerimientos"])
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(d['numero_acta'])} · Actividades</title><style>{CSS}</style></head><body><div class="hoja">
<div class="cab"><div>[Logo institucional]</div><div class="t">{e(d['aplicacion'])}<br>Acta de Pase a Producción</div><div>Calidad de Software<br>Doc. generado</div></div>
<div class="meta"><span><b>N.º de acta:</b> {e(d['numero_acta'])}</span><span><b>Ambiente:</b> {e(d['ambiente'])} · <b>Riesgo:</b> {e(d['riesgo'])}</span></div>
<h2>D. Actividades del Pase a Producción</h2>
<table><tr><th style="width:44px">Orden</th><th style="width:130px">Tipo de actividad</th><th>Detalle</th><th style="width:90px">Área ejecutante</th><th style="width:140px">Consideración de ejecución</th></tr>{cuerpo}</table>
{"<h2>Requerimientos incluidos</h2><table><tr><th>Código</th><th>Pull Request</th><th>Área</th><th>Autor</th><th>Aprobado por</th></tr>" + reqs + "</table>" if reqs else ""}
<div class="nota">Documento generado automáticamente por el pipeline DataOps el {e(d['generado'])}. La información proviene del repositorio, del plan de despliegue y de los resultados de ejecución; no se edita a mano. (*) en el Anexo 01: campo detectado por nombre, a confirmar por el responsable.</div>
</div></body></html>"""


# ------------------------------------------------------------------ DOCX
def render_docx(d, ruta):
    from docx import Document
    from docx.enum.section import WD_ORIENT  # noqa: F401
    from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Pt, Cm, RGBColor

    def sombra(celda, color):
        tcPr = celda._tc.get_or_add_tcPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), color)
        tcPr.append(shd)

    def bordes(tabla):
        tbl = tabla._tbl
        tblPr = tbl.tblPr
        b = OxmlElement("w:tblBorders")
        for lado in ("top", "left", "bottom", "right", "insideH", "insideV"):
            el = OxmlElement(f"w:{lado}")
            el.set(qn("w:val"), "single"); el.set(qn("w:sz"), "6"); el.set(qn("w:color"), "8C959F")
            b.append(el)
        tblPr.append(b)

    usados = set()

    def anchos_fijos(tabla, anchos):
        tabla.autofit = False
        tblPr = tabla._tbl.tblPr
        layout = OxmlElement("w:tblLayout"); layout.set(qn("w:type"), "fixed"); tblPr.append(layout)
        for gc, ancho in zip(tabla._tbl.tblGrid.findall(qn("w:gridCol")), anchos):
            gc.set(qn("w:w"), str(int(ancho.twips)))
        for fila_ in tabla.rows:
            for celda, ancho in zip(fila_.cells, anchos):
                celda.width = ancho

    def parrafo(celda_o_doc, texto="", negrita=False, tam=9.5, color=None, antes=0, despues=2, sangria=None, alinear=None):
        es_celda = hasattr(celda_o_doc, "_tc")
        if es_celda and id(celda_o_doc._tc) not in usados and len(celda_o_doc.paragraphs) == 1 and not celda_o_doc.paragraphs[0].text:
            usados.add(id(celda_o_doc._tc))
            p = celda_o_doc.paragraphs[0]
        else:
            p = celda_o_doc.add_paragraph()
        pf = p.paragraph_format
        pf.space_before, pf.space_after = Pt(antes), Pt(despues)
        if sangria is not None:
            pf.left_indent = Cm(sangria)
        if alinear:
            p.alignment = alinear
        if texto:
            r = p.add_run(texto); r.bold = negrita; r.font.size = Pt(tam)
            if color:
                r.font.color.rgb = RGBColor.from_string(color)
        return p

    def etiqueta_valor(celda, n, etiqueta, valor, sangria=0.2):
        p = parrafo(celda, sangria=sangria)
        r = p.add_run(f"{n}. " if n else ""); r.font.size = Pt(9.5)
        r = p.add_run(etiqueta); r.bold = True; r.font.size = Pt(9.5)
        r = p.add_run(f" {valor}"); r.font.size = Pt(9.5)

    def lista(celda, titulo, items, formato):
        parrafo(celda, titulo, negrita=True, antes=4, sangria=0.6)
        if not items:
            parrafo(celda, "No aplica.", tam=9, color="57606A", sangria=1.2)
        for i, it in enumerate(items, 1):
            p = parrafo(celda, sangria=1.0, despues=0)
            p.paragraph_format.first_line_indent = Cm(-0.6)
            r = p.add_run(f"{romano(i)}.\t"); r.font.size = Pt(9)
            r = p.add_run(formato(it)); r.font.size = Pt(9)

    doc = Document()
    sec = doc.sections[0]
    sec.page_height, sec.page_width = Cm(29.7), Cm(21.0)
    sec.left_margin = sec.right_margin = Cm(1.8)
    sec.top_margin, sec.bottom_margin = Cm(1.6), Cm(1.6)
    estilo = doc.styles["Normal"]; estilo.font.name = "Calibri"; estilo.font.size = Pt(10)

    # Encabezado de página (como el formato institucional; el logo se coloca en la plantilla oficial)
    cab = sec.header.add_table(rows=1, cols=3, width=Cm(17.4))
    bordes(cab)
    anchos_fijos(cab, [Cm(4.2), Cm(9.0), Cm(4.2)])
    for celda, texto, neg in zip(cab.rows[0].cells, ["[Logo institucional]", f"{d['aplicacion']}\nActa de Pase a Producción", "Calidad de Software\nDoc. generado"],
                                 [False, True, False]):
        celda.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        celda.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = celda.paragraphs[0].add_run(texto); r.bold = neg; r.font.size = Pt(10 if neg else 8)

    p = parrafo(doc, alinear=WD_ALIGN_PARAGRAPH.CENTER, despues=6)
    r = p.add_run("Número de Acta: "); r.bold = True; r.font.size = Pt(12)
    r = p.add_run(d["numero_acta"]); r.font.size = Pt(12)
    parrafo(doc, f"Ambiente: {d['ambiente']}   ·   Riesgo calculado: {d['riesgo']}   ·   Versión: {d['version']}",
            tam=9, color="57606A", alinear=WD_ALIGN_PARAGRAPH.CENTER, despues=8)

    titulo = doc.add_table(rows=1, cols=1); titulo.alignment = WD_TABLE_ALIGNMENT.CENTER
    anchos_fijos(titulo, [Cm(17.6)])
    c = titulo.rows[0].cells[0]; sombra(c, "D9D9D9")
    r = c.paragraphs[0].add_run("D. Actividades del Pase a Producción"); r.bold = True; r.font.size = Pt(13)
    parrafo(doc, despues=4)

    t = doc.add_table(rows=1, cols=5); bordes(t); t.alignment = WD_TABLE_ALIGNMENT.CENTER
    anchos = [Cm(1.3), Cm(2.8), Cm(8.6), Cm(2.0), Cm(2.9)]
    for i, (celda, texto) in enumerate(zip(t.rows[0].cells, ["Orden", "Tipo de actividad", "Detalle", "Área ejecutante", "Consideración de ejecución"])):
        celda.width = anchos[i]; sombra(celda, "EEF0F2")
        celda.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = celda.paragraphs[0].add_run(texto); r.bold = True; r.font.size = Pt(9)

    imp, s = d["impacto"], d["scripts"]
    marca = lambda valor, op: "X" if (valor.lower().startswith(op.lower()[0]) and valor not in ("No indicado", "")) else " "
    filas = []

    def fila(orden, tipo):
        cells = t.add_row().cells
        for i, celda in enumerate(cells):
            celda.width = anchos[i]
        cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        cells[0].paragraphs[0].add_run(orden).font.size = Pt(9.5)
        r = cells[1].paragraphs[0].add_run(tipo); r.bold = True; r.font.size = Pt(9.5)
        filas.append(cells)
        return cells[2]

    # 1. Scripts / jobs
    det = fila("1", "[X] Ejecución de scripts / jobs")
    etiqueta_valor(det, 1, "Afecta cierre diario:", f"Sí [{marca(imp['afecta_cierre'], 'Sí')}]   No [{marca(imp['afecta_cierre'], 'No')}]")
    etiqueta_valor(det, 2, "Afecta performance del sistema:", f"Sí [{marca(imp['afecta_performance'], 'Sí')}]   No [{marca(imp['afecta_performance'], 'No')}]")
    etiqueta_valor(det, 3, "Criticidad:", imp["criticidad"])
    parrafo(det, "Datos de los scripts:", negrita=True, antes=6)
    etiqueta_valor(det, 4, "Nombre de aplicación:", d["aplicacion"])
    etiqueta_valor(det, 5, "Ubicación del script:", d["release_url"] or f"Repositorio · versión {d['version']} · commit {d['commit'][:8]}")
    etiqueta_valor(det, 6, "Listado de scripts:", "")
    fmt = lambda i: f"{i['objeto']}  ({i['tipo']}{i['nota']})"
    lista(det, "-  Crear:", s["crear"], fmt)
    lista(det, "-  Modificar:", s["modificar"], fmt)
    lista(det, "-  Eliminar:", s["eliminar"], fmt)
    etiqueta_valor(det, 7, "Base donde ejecutar:", d["base"])
    etiqueta_valor(det, 8, "Servidor:", d["servidor"])
    parrafo(det, "Datos de los jobs:", negrita=True, antes=6)
    etiqueta_valor(det, 9, "Nombre de los jobs:", imp["jobs"] or "No aplica")
    if d["jobs_detectados"]:
        parrafo(det, "Jobs que usan los objetos modificados (detectados): " + ", ".join(d["jobs_detectados"]), tam=8.5, color="57606A", sangria=0.6)
    etiqueta_valor(det, 10, "Frecuencia:", imp["frecuencia"] or "No aplica")

    # 2. Datos
    det = fila("2", ("[X]" if d["migraciones"] else "[ ]") + " Actualización de datos (INSERT / UPDATE / DELETE)")
    if d["migraciones"]:
        for i, m in enumerate(d["migraciones"], 1):
            texto = f"{romano(i)}.  {m['script']}  ({m['tipo']} · {m['estado']}" + (f" · {m['filas']} fila(s)" if m.get("filas") is not None else "") + ")"
            parrafo(det, texto, tam=9, sangria=0.3, despues=0)
            if m["descripcion"]:
                parrafo(det, m["descripcion"], tam=8.5, color="57606A", sangria=0.9, despues=1)
        parrafo(det, "Cada script se ejecuta una sola vez, en una transacción, y queda registrado en ctl.SCRIPTS_EJECUTADOS. "
                     "Las filas modificadas o eliminadas se respaldan en ctl.RESPALDO_DATOS.", tam=8.5, color="57606A", antes=4)
    else:
        parrafo(det, "No aplica: el pase no incluye cambios de datos.", tam=9, color="57606A")

    # 3. Validación
    v = d["validacion"]
    det = fila("3", "[X] Validación post-despliegue")
    parrafo(det, f"{v['ok']} de {v['total']} validaciones conformes", negrita=True, color="1A7F37" if not v["fallas"] else "CF222E")
    parrafo(det, "Objetos desplegados, vistas consultables, procesos ejecutables y pruebas de calidad de datos.", tam=8.5, color="57606A")
    if v["fallas"]:
        parrafo(det, "Observadas: " + ", ".join(v["fallas"]), tam=9, color="CF222E")

    # 4. Reversión
    det = fila("4", "[X] Plan de reversión")
    parrafo(det, f"Reversión a la versión {d['version_anterior'] or 'anterior aprobada'} mediante el workflow Rollback "
                 "(ejecución exclusiva de TI, con motivo y evidencia). La foto previa de la base queda adjunta al release.", tam=9)
    if d["migraciones"]:
        parrafo(det, "Los cambios de datos se revierten con una nueva migración usando el respaldo de ctl.RESPALDO_DATOS.", tam=8.5, color="57606A")

    anchos_fijos(t, anchos)
    # Área ejecutante y consideración (celdas combinadas en todas las filas)
    area = filas[0][3].merge(filas[-1][3]); cons = filas[0][4].merge(filas[-1][4])
    area.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = area.paragraphs[0].add_run("Pipeline DataOps"); r.bold = True; r.font.size = Pt(9.5)
    parrafo(area, "(automático)", tam=8.5, color="57606A", alinear=WD_ALIGN_PARAGRAPH.CENTER)
    for etiqueta, valor in [("Fecha:", d["fecha"]), ("Hora:", d["hora"]), ("Ejecutado por:", d["ejecutado_por"]),
                            ("Versión:", d["version"]), ("Estado:", d["estado"])] + ([("Aprobado por:", d["aprobadores"])] if d["aprobadores"] else []):
        p = cons.paragraphs[0] if etiqueta == "Fecha:" else parrafo(cons)
        r = p.add_run(etiqueta + " "); r.bold = True; r.font.size = Pt(9)
        r = p.add_run(valor); r.font.size = Pt(9)
        if etiqueta == "Estado:":
            r.font.color.rgb = RGBColor.from_string("1A7F37" if d["estado"] in ("EXITOSO", "BORRADOR") else "CF222E"); r.bold = True
    if d["run_url"]:
        parrafo(cons, "Evidencia: " + d["run_url"], tam=7.5, color="0969DA")

    if d["impacto"]["requerimientos"]:
        parrafo(doc, despues=4)
        titulo = doc.add_table(rows=1, cols=1)
        anchos_fijos(titulo, [Cm(17.6)])
        c = titulo.rows[0].cells[0]; sombra(c, "D9D9D9")
        r = c.paragraphs[0].add_run("Requerimientos incluidos en el pase"); r.bold = True; r.font.size = Pt(11)
        parrafo(doc, despues=2)
        rq = doc.add_table(rows=1, cols=5); bordes(rq)
        anchos_rq = [Cm(2.8), Cm(6.4), Cm(2.8), Cm(2.4), Cm(3.2)]
        for celda, texto in zip(rq.rows[0].cells, ["Código", "Pull Request", "Área", "Autor", "Aprobado por"]):
            sombra(celda, "EEF0F2"); r = celda.paragraphs[0].add_run(texto); r.bold = True; r.font.size = Pt(9)
        for req in d["impacto"]["requerimientos"]:
            valores = [req["requerimiento"] or "—", f"#{req['pr']} {req.get('titulo') or ''}", req["area"] or "—",
                       req.get("autor") or "", req.get("aprobadores") or ""]
            for celda, valor in zip(rq.add_row().cells, valores):
                celda.paragraphs[0].add_run(str(valor)).font.size = Pt(9)
        anchos_fijos(rq, anchos_rq)

    parrafo(doc, f"Documento generado automáticamente por el pipeline DataOps el {d['generado']}. La información proviene del "
                 "repositorio, del plan de despliegue y de los resultados de ejecución; no se edita a mano.",
            tam=8, color="57606A", antes=10)
    doc.save(ruta)


# ------------------------------------------------------------------ Anexo 01 (XLSX)
def render_xlsx(d, ruta):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

    wb = Workbook()
    ws = wb.active
    ws.title = "Anexo 01 - Inventario de Tablas"
    fino = Side(style="thin", color="8C959F")
    borde = Border(left=fino, right=fino, top=fino, bottom=fino)
    gris = PatternFill("solid", fgColor="D9D9D9")
    ws.merge_cells("A1:A3")
    ws["A1"] = "[Logo]"
    ws["B1"] = "TECNOLOGÍA DE LA INFORMACIÓN"; ws.merge_cells("B1:D1")
    ws["B3"] = "FORMATO: INVENTARIO DE TABLAS"; ws.merge_cells("B3:D3")
    ws["E1"] = f"Nro Acta: {d['numero_acta']}"; ws["E2"] = f"Fecha: {d['fecha']}"; ws["E3"] = "Versión 001"
    for celda in ("B1", "B3"):
        ws[celda].font = Font(bold=True, size=12); ws[celda].alignment = Alignment(horizontal="center", vertical="center")
    for fila in range(1, 4):
        for col in "ABCDE":
            ws[f"{col}{fila}"].border = borde
    encabezados = ["Base de Datos", "Tabla", "Descripción", "Contiene Datos Sensibles", "Campos sensibles"]
    for i, texto in enumerate(encabezados, 1):
        c = ws.cell(row=5, column=i, value=texto)
        c.font = Font(bold=True); c.fill = gris; c.border = borde
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    fila = 6
    for t in d["inventario"]:
        for i, valor in enumerate([d["base"], t["tabla"], t["descripcion"], t["sensible"], t["campos"] or "—"], 1):
            c = ws.cell(row=fila, column=i, value=valor)
            c.border = borde; c.alignment = Alignment(vertical="top", wrap_text=True, horizontal="center" if i == 4 else "left")
        fila += 1
    if not d["inventario"]:
        ws.cell(row=fila, column=1, value="El pase no crea ni modifica tablas.").font = Font(italic=True); fila += 1
    ws.cell(row=fila + 1, column=1, value="Generado automáticamente desde el SQL Project (descripciones y propiedad DatoSensible). "
                                         "(*) Campo detectado por el nombre de la columna: confirmar con el responsable.").font = Font(italic=True, size=9, color="57606A")
    for col, ancho in zip("ABCDE", [16, 34, 70, 14, 70]):
        ws.column_dimensions[col].width = ancho
    ws.freeze_panes = "A6"

    ws2 = wb.create_sheet("Lista Campos Sensibles")
    ws2["A1"] = "Campos Sensibles:"; ws2["A1"].font = Font(bold=True)
    for i, cat in enumerate(CATEGORIAS, 2):
        ws2.cell(row=i, column=1, value=cat)
    ws2.column_dimensions["A"].width = 46
    wb.save(ruta)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for x in ("contexto", "riesgo", "migraciones", "jobs", "pruebas", "smoke", "prs", "dacpac"):
        p.add_argument(f"--{x}")
    p.add_argument("--inventario-completo", action="store_true", help="Anexo con todas las tablas, no solo las del pase")
    p.add_argument("--salida", default="acta")
    a = p.parse_args()
    d = construir(a)
    out = Path(a.salida); out.mkdir(parents=True, exist_ok=True)
    (out / "acta.json").write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "actividades.html").write_text(render_html(d), encoding="utf-8")
    render_docx(d, out / f"{d['numero_acta']}_D_Actividades.docx")
    render_xlsx(d, out / f"{d['numero_acta']}_Anexo01_Inventario_Tablas.xlsx")
    print(f"Acta {d['numero_acta']}: {sum(len(v) for v in d['scripts'].values())} objetos, "
          f"{len(d['migraciones'])} migraciones, {len(d['inventario'])} tablas en el anexo -> {out}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback
        tb = traceback.format_exc()
        print(tb, file=sys.stderr)
        print("::error title=Acta del pase::" + tb.replace("%", "%25").replace("\n", "%0A")[-3000:])
        sys.exit(1)
