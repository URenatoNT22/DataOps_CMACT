#!/usr/bin/env python3
"""
Utilitario de base de datos para el pipeline (pymssql).

Conexión por variables de entorno:
    SQL_SERVER    host,puerto  (ej. 4.tcp.ngrok.io,12345  |  localhost,1433)
    SQL_USER      login SQL (svc_pipeline)
    SQL_PASSWORD  contraseña
    SQL_DATABASE  base por defecto (se puede sobreescribir con --base)

Subcomandos:
    script                 Ejecuta un .sql (separa lotes por GO).
    consulta               Ejecuta una sentencia y muestra el resultado.
    pruebas                Ejecuta las pruebas de datos de una carpeta (cada .sql devuelve filas = falla).
    smoke                  Pruebas de humo post-despliegue (vistas consultables, carga ejecutable con rollback).
    dependencias-jobs      Busca jobs de SQL Agent que referencian los objetos indicados.
    registrar-despliegue   Inserta un registro en ctl.HISTORIAL_DESPLIEGUE.
    version-instalada      Devuelve la última versión registrada en ctl.HISTORIAL_DESPLIEGUE.
"""
import argparse
import json
import os
import re
import sys
import time
from pathlib import Path


def conectar(base=None, autocommit=True):
    import pymssql  # se importa aquí para que --help funcione sin la librería

    servidor = os.environ.get("SQL_SERVER", "")
    if not servidor:
        sys.exit("ERROR: falta la variable SQL_SERVER")
    host, puerto = servidor, "1433"
    servidor = servidor.replace("tcp:", "")
    for sep in (",", ":"):
        if sep in servidor:
            host, puerto = servidor.rsplit(sep, 1)
            break
    else:
        host = servidor
    ultimo_error = None
    for intento in range(1, 6):
        try:
            conn = pymssql.connect(
                server=host.strip(),
                port=int(puerto),
                user=os.environ["SQL_USER"],
                password=os.environ["SQL_PASSWORD"],
                database=base or os.environ.get("SQL_DATABASE", "master"),
                login_timeout=30,
                timeout=0,
                autocommit=autocommit,
                charset="UTF-8",
            )
            return conn
        except Exception as exc:  # reintentos: ngrok o el contenedor pueden tardar en responder
            ultimo_error = exc
            print(f"  conexión intento {intento}/5 falló: {exc}", file=sys.stderr)
            time.sleep(min(5 * intento, 20))
    sys.exit(f"ERROR: no se pudo conectar a {host}:{puerto} -> {ultimo_error}")


def lotes(texto):
    """Divide un script T-SQL en lotes usando las líneas GO."""
    partes, actual = [], []
    for linea in texto.splitlines():
        if re.fullmatch(r"\s*GO\s*(--.*)?", linea, flags=re.IGNORECASE):
            if "".join(actual).strip():
                partes.append("\n".join(actual))
            actual = []
        else:
            actual.append(linea)
    if "".join(actual).strip():
        partes.append("\n".join(actual))
    return partes


def _mensajes(conn):
    """Activa la captura de PRINT / RAISERROR informativos."""
    mensajes = []
    try:
        def manejador(msgstate, severity, srvname, procname, line, msgtext):
            texto = msgtext.decode() if isinstance(msgtext, bytes) else msgtext
            mensajes.append(texto)
            print(f"  [sql] {texto}")
        conn._conn.set_msghandler(manejador)
    except Exception:
        pass
    return mensajes


def cmd_script(args):
    conn = conectar(args.base)
    _mensajes(conn)
    cur = conn.cursor()
    texto = Path(args.archivo).read_text(encoding="utf-8-sig")
    for i, lote in enumerate(lotes(texto), 1):
        inicio = time.time()
        cur.execute(lote)
        while True:  # consumir todos los result sets
            try:
                cur.fetchall()
            except Exception:
                pass
            if not cur.nextset():
                break
        print(f"  lote {i} ok ({time.time() - inicio:.1f}s)")
    conn.close()


def cmd_consulta(args):
    conn = conectar(args.base)
    _mensajes(conn)
    cur = conn.cursor(as_dict=True)
    cur.execute(args.sql)
    filas = []
    try:
        filas = cur.fetchall()
    except Exception:
        pass
    if args.json:
        print(json.dumps(filas, default=str, ensure_ascii=False))
    else:
        for f in filas:
            print(f)
    conn.close()


def _cabecera(texto, clave, defecto=""):
    m = re.search(rf"^--\s*{clave}\s*:\s*(.+)$", texto, flags=re.IGNORECASE | re.MULTILINE)
    return m.group(1).strip() if m else defecto


def cmd_pruebas(args):
    conn = conectar(args.base)
    cur = conn.cursor(as_dict=True)
    resultados = []
    for archivo in sorted(Path(args.carpeta).glob("*.sql")):
        texto = archivo.read_text(encoding="utf-8-sig")
        severidad = _cabecera(texto, "severidad", "ERROR").upper()
        descripcion = _cabecera(texto, "descripcion", archivo.stem)
        inicio = time.time()
        try:
            cur.execute(texto)
            filas = cur.fetchall()
            estado = "OK" if not filas else ("FALLA" if severidad == "ERROR" else "ADVERTENCIA")
            detalle = filas[:5]
        except Exception as exc:
            estado, detalle = "ERROR_EJECUCION", [{"error": str(exc)[:500]}]
            filas = []
        resultados.append({
            "prueba": archivo.stem, "descripcion": descripcion, "severidad": severidad,
            "estado": estado, "filas_con_falla": len(filas), "muestra": detalle,
            "segundos": round(time.time() - inicio, 2),
        })
        icono = {"OK": "✅", "ADVERTENCIA": "⚠️"}.get(estado, "❌")
        print(f"{icono} {archivo.stem}: {estado} ({len(filas)} filas)")
    conn.close()
    _guardar(args.salida, {"tipo": "pruebas_datos", "base": args.base, "resultados": resultados})
    fallidas = [r for r in resultados if r["estado"] in ("FALLA", "ERROR_EJECUCION")]
    if fallidas and not args.no_fallar:
        sys.exit(f"{len(fallidas)} prueba(s) de datos fallaron")


def cmd_smoke(args):
    conn = conectar(args.base)
    cur = conn.cursor(as_dict=True)
    resultados = []

    cur.execute("""
        SELECT s.name AS esquema, o.name AS objeto, o.type_desc AS tipo
        FROM sys.objects o JOIN sys.schemas s ON s.schema_id = o.schema_id
        WHERE o.is_ms_shipped = 0 AND o.type IN ('V','P','FN','IF','TF','U')
        ORDER BY s.name, o.name""")
    objetos = cur.fetchall()
    resultados.append({"prueba": "objetos_desplegados", "estado": "OK" if objetos else "FALLA",
                       "detalle": f"{len(objetos)} objetos de usuario"})

    for o in [x for x in objetos if x["tipo"] == "VIEW"]:
        nombre = f"[{o['esquema']}].[{o['objeto']}]"
        try:
            cur.execute(f"SELECT TOP (1) * FROM {nombre}")
            cur.fetchall()
            resultados.append({"prueba": f"vista_consultable {nombre}", "estado": "OK", "detalle": ""})
        except Exception as exc:
            resultados.append({"prueba": f"vista_consultable {nombre}", "estado": "FALLA", "detalle": str(exc)[:300]})

    # Ejecuta el orquestador de carga dentro de una transacción y la revierte: valida que los SP
    # compilan y corren contra el esquema nuevo sin alterar los datos.
    if args.probar_carga:
        conn2 = conectar(args.base, autocommit=False)
        cur2 = conn2.cursor()
        try:
            cur2.execute("SELECT MAX(FECHA_CORTE) FROM [tab].[TB_CREDITO]")
            fecha = cur2.fetchone()[0]
            if fecha is None:
                resultados.append({"prueba": "carga_ejecutable", "estado": "OMITIDA", "detalle": "sin datos cargados"})
            else:
                cur2.execute("EXEC [ctl].[usp_CARGA_DIARIA] @FECHA_CORTE = %s", (str(fecha),))
                resultados.append({"prueba": "carga_ejecutable ctl.usp_CARGA_DIARIA", "estado": "OK",
                                   "detalle": f"ejecutada para {fecha} y revertida"})
        except Exception as exc:
            resultados.append({"prueba": "carga_ejecutable ctl.usp_CARGA_DIARIA", "estado": "FALLA", "detalle": str(exc)[:300]})
        finally:
            try:
                conn2.rollback()
            except Exception:
                pass
            conn2.close()

    conn.close()
    for r in resultados:
        icono = {"OK": "✅", "OMITIDA": "➖"}.get(r["estado"], "❌")
        print(f"{icono} {r['prueba']}: {r['estado']} {r['detalle']}")
    _guardar(args.salida, {"tipo": "smoke", "base": args.base, "resultados": resultados})
    if any(r["estado"] == "FALLA" for r in resultados) and not args.no_fallar:
        sys.exit("Pruebas de humo con fallas")


def cmd_dependencias_jobs(args):
    objetos = [o.strip() for o in args.objetos.split(",") if o.strip()]
    hallazgos = []
    if objetos:
        conn = conectar("msdb")
        cur = conn.cursor(as_dict=True)
        try:
            cur.execute("""
                SELECT j.name AS job, j.enabled AS habilitado, s.step_id AS paso, s.step_name AS nombre_paso,
                       s.database_name AS base, s.command AS comando
                FROM dbo.sysjobs j JOIN dbo.sysjobsteps s ON s.job_id = j.job_id
                WHERE s.subsystem = 'TSQL'""")
            pasos = cur.fetchall()
        except Exception as exc:
            print(f"Sin acceso a msdb ({exc}); se omite el análisis de jobs", file=sys.stderr)
            pasos = []
        conn.close()
        base_destino = (args.base or os.environ.get("SQL_DATABASE", "")).lower()
        for o in objetos:
            corto = o.replace("[", "").replace("]", "").lower()
            nombre = corto.split(".")[-1]
            for p in pasos:
                comando = (p["comando"] or "").replace("[", "").replace("]", "").lower()
                if base_destino and (p["base"] or "").lower() != base_destino and f"{base_destino}." not in comando:
                    continue
                if corto in comando or re.search(rf"\b{re.escape(nombre)}\b", comando):
                    hallazgos.append({"objeto": o, "job": p["job"], "paso": p["nombre_paso"],
                                      "base": p["base"], "habilitado": bool(p["habilitado"])})
    _guardar(args.salida, {"tipo": "dependencias_jobs", "jobs": hallazgos})
    print(f"{len(hallazgos)} referencia(s) en jobs de SQL Agent")


def cmd_registrar(args):
    conn = conectar(args.base)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO [ctl].[HISTORIAL_DESPLIEGUE]
            ([VERSION],[TIPO],[COMMIT_SHA],[RAMA],[PULL_REQUEST],[RIESGO],[EJECUTADO_POR],[APROBADO_POR],[MOTIVO],[URL_EJECUCION])
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (args.version, args.tipo, args.commit, args.rama, args.pr or None, args.riesgo or None,
                 args.ejecutado_por, args.aprobado_por or None, args.motivo or None, args.url or None))
    conn.close()
    print(f"Despliegue {args.version} registrado en ctl.HISTORIAL_DESPLIEGUE")


def cmd_version(args):
    conn = conectar(args.base)
    cur = conn.cursor(as_dict=True)
    try:
        cur.execute("""SELECT TOP (1) [VERSION], [TIPO], [COMMIT_SHA], [FECHA_DESPLIEGUE]
                       FROM [ctl].[HISTORIAL_DESPLIEGUE] ORDER BY [ID_DESPLIEGUE] DESC""")
        fila = cur.fetchone()
    except Exception:
        fila = None
    conn.close()
    print(json.dumps(fila or {}, default=str))


def _guardar(ruta, datos):
    if ruta:
        Path(ruta).parent.mkdir(parents=True, exist_ok=True)
        Path(ruta).write_text(json.dumps(datos, default=str, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--base", help="Base de datos (por defecto SQL_DATABASE)")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("script"); s.add_argument("--archivo", required=True); s.set_defaults(f=cmd_script)
    s = sub.add_parser("consulta"); s.add_argument("--sql", required=True); s.add_argument("--json", action="store_true"); s.set_defaults(f=cmd_consulta)
    s = sub.add_parser("pruebas"); s.add_argument("--carpeta", default="tests/datos"); s.add_argument("--salida")
    s.add_argument("--no-fallar", action="store_true"); s.set_defaults(f=cmd_pruebas)
    s = sub.add_parser("smoke"); s.add_argument("--salida"); s.add_argument("--probar-carga", action="store_true")
    s.add_argument("--no-fallar", action="store_true"); s.set_defaults(f=cmd_smoke)
    s = sub.add_parser("dependencias-jobs"); s.add_argument("--objetos", default=""); s.add_argument("--salida"); s.set_defaults(f=cmd_dependencias_jobs)
    s = sub.add_parser("registrar-despliegue")
    for a in ("version", "tipo", "commit", "rama", "ejecutado-por"):
        s.add_argument(f"--{a}", required=True)
    for a in ("pr", "riesgo", "aprobado-por", "motivo", "url"):
        s.add_argument(f"--{a}", default="")
    s.set_defaults(f=cmd_registrar)
    s = sub.add_parser("version-instalada"); s.set_defaults(f=cmd_version)

    args = p.parse_args()
    args.f(args)


if __name__ == "__main__":
    main()
