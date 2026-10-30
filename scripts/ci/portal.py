#!/usr/bin/env python3
"""
Portal DataOps: tablero general + secciones conectadas, como sitio estático.

  index.html                Resumen: indicadores, últimos pases, PR en curso y alertas
  pases.html                Pases a producción: un registro por release con su acta (HTML, Word, Excel)
  pases/<version>.html      Sección D del acta de ese pase
  validaciones.html         Resultado de validaciones por pase y riesgo de los PR abiertos
  inventario.html           Inventario de tablas y campos sensibles (modelo vigente)
  diccionario/              Diccionario de datos (lo genera documentar.py)

Entradas (JSON de la API de GitHub y actas de cada release). No necesita conexión a la base.
"""
import argparse
import datetime as dt
import html
import json
import shutil  # noqa: F401
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import acta as acta_mod  # noqa: E402
import modelo_dacpac as md  # noqa: E402

e = lambda x: html.escape(str(x if x is not None else ""))
TZ = dt.timezone(dt.timedelta(hours=-5))

CSS = """
:root{--bg:#f4f6f8;--card:#fff;--tx:#1f2328;--tx2:#59636e;--bd:#d8dee4;--pri:#0b3d6e;--pri2:#e7f0fa;
--ok:#1a7f37;--okbg:#dafbe1;--warn:#9a6700;--warnbg:#fff8c5;--err:#cf222e;--errbg:#ffebe9;--mut:#eef1f4}
@media (prefers-color-scheme:dark){:root{--bg:#0f1318;--card:#171c22;--tx:#e6edf3;--tx2:#9aa5b1;--bd:#2d3540;
--pri:#79b8ff;--pri2:#122a44;--ok:#56d364;--okbg:#12301b;--warn:#e3b341;--warnbg:#3a2d06;--err:#ff7b72;--errbg:#3d1416;--mut:#222a33}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--tx);font:14.5px/1.55 "Segoe UI",system-ui,-apple-system,Roboto,sans-serif}
header.top{background:#0b3d6e;color:#fff}header .in{max-width:1200px;margin:0 auto;padding:16px 20px 0}
header .marca{display:flex;justify-content:space-between;align-items:flex-end;gap:12px;flex-wrap:wrap}
header h1{margin:0;font-size:20px;font-weight:600}header .sub{opacity:.8;font-size:13px}
nav{display:flex;gap:4px;margin-top:14px;overflow-x:auto}nav a{color:#dbe7f3;text-decoration:none;padding:9px 14px;border-radius:8px 8px 0 0;font-size:13.5px;white-space:nowrap}
nav a.act{background:var(--bg);color:var(--tx);font-weight:600}
main{max-width:1200px;margin:0 auto;padding:22px 20px 50px}
h2{font-size:16px;margin:28px 0 10px;font-weight:600}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px}
.kpi{background:var(--card);border:1px solid var(--bd);border-radius:12px;padding:14px 16px}
.kpi .l{font-size:12px;color:var(--tx2)}.kpi .v{font-size:24px;font-weight:650;margin-top:2px}.kpi .s{font-size:12px;color:var(--tx2)}
.kpi.alerta .v{color:var(--err)}.kpi.bien .v{color:var(--ok)}
.card{background:var(--card);border:1px solid var(--bd);border-radius:12px;overflow:hidden}
table{width:100%;border-collapse:collapse;font-size:13.5px}th,td{text-align:left;padding:9px 12px;border-bottom:1px solid var(--bd);vertical-align:top}
th{font-size:12px;color:var(--tx2);font-weight:600;background:var(--mut)}tr:last-child td{border-bottom:0}
.pill{display:inline-block;padding:1px 9px;border-radius:999px;font-size:12px;font-weight:600;white-space:nowrap}
.p-ok{background:var(--okbg);color:var(--ok)}.p-warn{background:var(--warnbg);color:var(--warn)}.p-err{background:var(--errbg);color:var(--err)}
.p-info{background:var(--pri2);color:var(--pri)}.p-mut{background:var(--mut);color:var(--tx2)}
a{color:var(--pri)}.muted{color:var(--tx2)}.vacio{padding:16px;color:var(--tx2)}
.grid2{display:grid;grid-template-columns:1.6fr 1fr;gap:16px}@media(max-width:860px){.grid2{grid-template-columns:1fr}}
.doc a{margin-right:10px;white-space:nowrap}
footer{max-width:1200px;margin:0 auto;padding:0 20px 30px;color:var(--tx2);font-size:12px}
input.q{width:100%;padding:9px 12px;border:1px solid var(--bd);border-radius:8px;background:var(--card);color:var(--tx);margin-bottom:10px}
"""


def leer(ruta, defecto):
    try:
        return json.loads(Path(ruta).read_text(encoding="utf-8")) if ruta and Path(ruta).exists() else defecto
    except Exception:
        return defecto


def fecha(iso):
    if not iso:
        return ""
    try:
        return dt.datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(TZ).strftime("%d/%m/%Y %H:%M")
    except Exception:
        return iso[:10]


def pill_riesgo(nivel):
    cls = {"ESTANDAR": "p-ok", "SENSIBLE": "p-warn", "PROHIBIDO": "p-err"}.get((nivel or "").upper(), "p-mut")
    return f"<span class='pill {cls}'>{e(nivel or '—')}</span>"


def pagina(titulo, activa, cuerpo, app, base_rel=""):
    tabs = [("Resumen", "index.html"), ("Pases a producción", "pases.html"), ("Validaciones", "validaciones.html"),
            ("Inventario de datos sensibles", "inventario.html"), ("Diccionario de datos", "diccionario/index.html")]
    nav = "".join(f"<a href='{base_rel}{href}' class='{'act' if t == activa else ''}'>{t}</a>" for t, href in tabs)
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(titulo)} · Portal DataOps</title><style>{CSS}</style></head><body>
<header class="top"><div class="in"><div class="marca"><div><div class="sub">Inteligencia de Negocios · Portal DataOps</div><h1>{e(app)}</h1></div>
<div class="sub">Actualizado {dt.datetime.now(TZ):%d/%m/%Y %H:%M}</div></div><nav>{nav}</nav></div></header>
<main>{cuerpo}</main><footer>Generado automáticamente por el pipeline a partir del repositorio, los releases y las ejecuciones. No se edita a mano.</footer></body></html>"""


def asset(rel, sufijo):
    for a in rel.get("assets", []):
        if a["name"].endswith(sufijo):
            return a.get("browser_download_url") or a.get("url")
    return ""


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--releases"); p.add_argument("--actas", help="carpeta con <tag>/acta.json")
    p.add_argument("--prs"); p.add_argument("--despliegues"); p.add_argument("--issues")
    p.add_argument("--dacpac"); p.add_argument("--aplicacion", default="BI_ANALITICO")
    p.add_argument("--diccionario", help="carpeta generada por documentar.py sitio")
    p.add_argument("--salida", default="sitio")
    a = p.parse_args()
    out = Path(a.salida); (out / "pases").mkdir(parents=True, exist_ok=True)

    releases = [r for r in leer(a.releases, []) if not r.get("draft")]
    releases.sort(key=lambda r: r.get("published_at") or "", reverse=True)
    actas = {}
    for r in releases:
        d = leer(Path(a.actas or "actas") / r["tag_name"] / "acta.json", None)
        if d:
            actas[r["tag_name"]] = d
    prs = leer(a.prs, [])
    runs = leer(a.despliegues, [])
    issues = [i for i in leer(a.issues, []) if "pull_request" not in i]
    etiquetas = lambda i: {l["name"] for l in i.get("labels", [])}
    aud_pend = [i for i in issues if "auditoria/pendiente" in etiquetas(i)]
    aud_obs = [i for i in issues if "auditoria/observado" in etiquetas(i)]
    drift = [i for i in issues if "drift" in etiquetas(i)]
    incid = [i for i in issues if "incidente" in etiquetas(i)]
    hace30 = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=30)
    rel30 = [r for r in releases if r.get("published_at") and dt.datetime.fromisoformat(r["published_at"].replace("Z", "+00:00")) >= hace30]
    runs_fin = [x for x in runs if x.get("status") == "completed" and x.get("conclusion") in ("success", "failure")]
    exito = round(100 * sum(1 for x in runs_fin if x["conclusion"] == "success") / len(runs_fin)) if runs_fin else None
    objetos = md.cargar(a.dacpac) if a.dacpac and Path(a.dacpac).exists() else {}
    inv = acta_mod.inventario(objetos, {}, todas=True) if objetos else []
    sens = [t for t in inv if t["sensible"] == "Sí"]

    # ---------------- Resumen
    ultima = releases[0] if releases else None
    kpis = [
        ("Versión en producción", ultima["tag_name"] if ultima else "—", fecha(ultima.get("published_at")) if ultima else "", ""),
        ("Pases a PROD (30 días)", len(rel30), f"{len(releases)} en total", ""),
        ("Despliegues exitosos", f"{exito}%" if exito is not None else "—", f"últimas {len(runs_fin)} ejecuciones", "bien" if (exito or 0) >= 90 else ""),
        ("PR en curso", len(prs), f"{sum(1 for x in prs if x.get('base', {}).get('ref') == 'main')} hacia PROD", ""),
        ("Auditorías TI pendientes", len(aud_pend), f"{len(aud_obs)} observadas", "alerta" if aud_obs else ""),
        ("Alertas abiertas", len(drift) + len(incid), f"{len(drift)} drift · {len(incid)} incidentes", "alerta" if drift or incid else "bien"),
        ("Tablas con datos sensibles", len(sens), f"de {len(inv)} tablas", ""),
    ]
    k = "".join(f"<div class='kpi {c}'><div class='l'>{e(l)}</div><div class='v'>{e(v)}</div><div class='s'>{e(s)}</div></div>" for l, v, s, c in kpis)

    def fila_pase(r, completo=False):
        d = actas.get(r["tag_name"], {})
        n_obj = sum(len(v) for v in d.get("scripts", {}).values()) if d else "—"
        aud = "Conforme" if "✅ conforme" in (r.get("body") or "") else ("Observado" if "⚠️ observado" in (r.get("body") or "") else "Pendiente")
        aud_cls = {"Conforme": "p-ok", "Observado": "p-err"}.get(aud, "p-warn")
        docs = [f"<a href='pases/{e(r['tag_name'])}.html'>Acta (web)</a>" if d else ""]
        for etiqueta, suf in (("Word", "_D_Actividades.docx"), ("Anexo Excel", "_Inventario_Tablas.xlsx")):
            url = asset(r, suf)
            if url:
                docs.append(f"<a href='{e(url)}'>{etiqueta}</a>")
        reqs = ", ".join(x["requerimiento"] for x in d.get("impacto", {}).get("requerimientos", []) if x.get("requerimiento")) if d else ""
        celdas = [f"<a href='{e(r.get('html_url'))}'><b>{e(r['tag_name'])}</b></a>", e(fecha(r.get("published_at"))),
                  pill_riesgo(d.get("riesgo")), e(n_obj), e(len(d.get("migraciones", [])) if d else "—"),
                  f"<span class='pill {aud_cls}'>{aud}</span>", f"<span class='doc'>{''.join(docs) or '<span class=muted>—</span>'}</span>"]
        if completo:
            celdas.insert(2, e(reqs or "—"))
        return "<tr>" + "".join(f"<td>{c}</td>" for c in celdas) + "</tr>"

    cab_pases = "<tr><th>Versión</th><th>Fecha</th><th>Riesgo</th><th>Objetos</th><th>Migraciones</th><th>Auditoría TI</th><th>Documentos</th></tr>"
    tabla_pases = (f"<div class='card'><table>{cab_pases}{''.join(fila_pase(r) for r in releases[:8])}</table></div>"
                   if releases else "<div class='card vacio'>Aún no hay pases a producción.</div>")
    PROD, DEV = "<span class='pill p-info'>PROD</span>", "<span class='pill p-mut'>DEV</span>"
    filas_pr = "".join(
        f"<tr><td><a href='{e(x.get('html_url'))}'>#{x['number']}</a> {e(x.get('title'))}</td><td>{e(x.get('user', {}).get('login'))}</td>"
        f"<td>{PROD if x.get('base', {}).get('ref') == 'main' else DEV}</td>"
        f"<td>{pill_riesgo(next((l['name'].split('/')[1].upper() for l in x.get('labels', []) if l['name'] in ('riesgo/estandar', 'riesgo/sensible', 'riesgo/prohibido')), ''))}</td></tr>"
        for x in prs)
    tabla_prs = (f"<div class='card'><table><tr><th>Pull Request</th><th>Autor</th><th>Destino</th><th>Riesgo</th></tr>{filas_pr}</table></div>"
                 if prs else "<div class='card vacio'>No hay PR en curso.</div>")
    alertas = [(i, "Drift") for i in drift] + [(i, "Incidente") for i in incid] + [(i, "Auditoría observada") for i in aud_obs] + [(i, "Auditoría pendiente") for i in aud_pend]
    filas_al = "".join(f"<tr><td><span class='pill {'p-err' if t != 'Auditoría pendiente' else 'p-warn'}'>{t}</span></td>"
                       f"<td><a href='{e(i.get('html_url'))}'>{e(i.get('title'))}</a><div class='muted'>{e(fecha(i.get('created_at')))}</div></td></tr>" for i, t in alertas)
    tabla_al = f"<div class='card'><table>{filas_al}</table></div>" if alertas else "<div class='card vacio'>Sin alertas abiertas.</div>"
    resumen = (f"<div class='kpis'>{k}</div><div class='grid2'><div><h2>Últimos pases a producción</h2>{tabla_pases}</div>"
               f"<div><h2>Alertas y auditoría</h2>{tabla_al}</div></div><h2>Pull Requests en curso</h2>{tabla_prs}")
    (out / "index.html").write_text(pagina("Resumen", "Resumen", resumen, a.aplicacion), encoding="utf-8")

    # ---------------- Pases
    cab_full = "<tr><th>Versión</th><th>Fecha</th><th>Requerimientos</th><th>Riesgo</th><th>Objetos</th><th>Migraciones</th><th>Auditoría TI</th><th>Documentos</th></tr>"
    pases = (f"<h2>Pases a producción</h2><div class='card'><table>{cab_full}{''.join(fila_pase(r, True) for r in releases)}</table></div>"
             if releases else "<h2>Pases a producción</h2><div class='card vacio'>Aún no hay pases a producción.</div>")
    (out / "pases.html").write_text(pagina("Pases a producción", "Pases a producción", pases, a.aplicacion), encoding="utf-8")
    for tag, d in actas.items():
        destino = out / "pases" / f"{tag}.html"
        origen = Path(a.actas or "actas") / tag / "actividades.html"
        contenido = origen.read_text(encoding="utf-8") if origen.exists() else acta_mod.render_html(d)
        volver = ("<div style='max-width:820px;margin:16px auto 0;font-family:Segoe UI,sans-serif'>"
                  "<a href='../pases.html'>← Volver a Pases a producción</a></div>")
        destino.write_text(contenido.replace("<body>", "<body>" + volver, 1), encoding="utf-8")

    # ---------------- Validaciones
    filas_v = []
    for r in releases:
        d = actas.get(r["tag_name"])
        if not d:
            continue
        v = d.get("validacion", {})
        ok = not v.get("fallas")
        filas_v.append(f"<tr><td><b>{e(r['tag_name'])}</b></td><td>{e(fecha(r.get('published_at')))}</td><td>{pill_riesgo(d.get('riesgo'))}</td>"
                       f"<td><span class='pill {'p-ok' if ok else 'p-err'}'>{v.get('ok', 0)} / {v.get('total', 0)}</span></td>"
                       f"<td>{'Sí' if d.get('perdida_datos') else 'No'}</td><td>{e(', '.join(v.get('fallas', [])) or '—')}</td></tr>")
    val = ("<h2>Validación post-despliegue por pase</h2>" +
           (f"<div class='card'><table><tr><th>Versión</th><th>Fecha</th><th>Riesgo</th><th>Validaciones conformes</th><th>Pérdida de datos</th><th>Observadas</th></tr>{''.join(filas_v)}</table></div>"
            if filas_v else "<div class='card vacio'>Sin registros.</div>")
           + "<h2>Riesgo de los Pull Requests en curso</h2>" + tabla_prs)
    (out / "validaciones.html").write_text(pagina("Validaciones", "Validaciones", val, a.aplicacion), encoding="utf-8")

    # ---------------- Inventario
    filas_i = "".join(f"<tr class='it'><td>{e(t['tabla'])}</td><td>{e(t['descripcion'])}</td>"
                      f"<td><span class='pill {'p-warn' if t['sensible'] == 'Sí' else 'p-mut'}'>{t['sensible']}</span></td><td>{e(t['campos'] or '—')}</td></tr>" for t in inv)
    inv_html = ("<h2>Inventario de tablas y campos sensibles</h2>"
                "<input class='q' placeholder='Buscar tabla o campo…' oninput=\"document.querySelectorAll('.it').forEach(f=>f.style.display=f.textContent.toLowerCase().includes(this.value.toLowerCase())?'':'none')\">"
                + (f"<div class='card'><table><tr><th>Tabla</th><th>Descripción</th><th>Datos sensibles</th><th>Campos sensibles</th></tr>{filas_i}</table></div>"
                   if inv else "<div class='card vacio'>Sin información del modelo.</div>")
                + "<p class='muted'>Fuente: SQL Project (propiedad extendida <code>DatoSensible</code>). (*) detectado por el nombre de la columna: confirmar con el responsable.</p>")
    (out / "inventario.html").write_text(pagina("Inventario de datos sensibles", "Inventario de datos sensibles", inv_html, a.aplicacion), encoding="utf-8")

    # ---------------- Diccionario
    if a.diccionario and Path(a.diccionario).exists():
        shutil.copytree(a.diccionario, out / "diccionario", dirs_exist_ok=True)
        idx = out / "diccionario" / "index.html"
        if idx.exists():
            idx.write_text(idx.read_text(encoding="utf-8").replace(
                "<body>", "<body><div style='max-width:1180px;margin:14px auto 0;padding:0 20px;font-family:Segoe UI,sans-serif'>"
                          "<a href='../index.html'>← Volver al portal</a></div>", 1), encoding="utf-8")
    else:
        (out / "diccionario").mkdir(exist_ok=True)
        (out / "diccionario" / "index.html").write_text(pagina("Diccionario", "Diccionario de datos", "<div class='card vacio'>Sin diccionario.</div>", a.aplicacion, "../"), encoding="utf-8")
    print(f"Portal generado en {out} ({len(releases)} pases, {len(prs)} PR, {len(inv)} tablas)")


if __name__ == "__main__":
    main()
