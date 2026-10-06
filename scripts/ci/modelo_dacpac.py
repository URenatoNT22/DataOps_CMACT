"""
Lectura del modelo de un DACPAC (model.xml) y comparación entre dos versiones.

Un DACPAC es un .zip que contiene model.xml: la descripción completa del esquema
(tablas, columnas, tipos, vistas, procedimientos, dependencias y extended properties).
Con esto se documenta la base SIN conectarse a ella.
"""
import difflib
import re
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

NS = "{http://schemas.microsoft.com/sqlserver/dac/Serialization/2012/02}"

TIPOS_OBJETO = {
    "SqlTable": "Tabla",
    "SqlView": "Vista",
    "SqlProcedure": "Procedimiento",
    "SqlScalarFunction": "Función escalar",
    "SqlInlineTableValuedFunction": "Función de tabla (inline)",
    "SqlMultiStatementTableValuedFunction": "Función de tabla",
    "SqlSchema": "Esquema",
    "SqlSequence": "Secuencia",
    "SqlSynonym": "Sinónimo",
    "SqlIndex": "Índice",
}
TIPOS_DOCUMENTABLES = ("SqlTable", "SqlView", "SqlProcedure", "SqlScalarFunction",
                       "SqlInlineTableValuedFunction", "SqlMultiStatementTableValuedFunction")


@dataclass
class Columna:
    nombre: str
    tipo: str = ""
    nulo: bool = True
    identidad: bool = False
    default: str = ""
    descripcion: str = ""
    calculada: bool = False

    def firma(self):
        return f"{self.tipo} {'NULL' if self.nulo else 'NOT NULL'}{' IDENTITY' if self.identidad else ''}" \
               f"{(' DEFAULT ' + self.default) if self.default else ''}"


@dataclass
class Objeto:
    nombre: str              # [esquema].[objeto]
    tipo_sql: str
    esquema: str = ""
    corto: str = ""
    descripcion: str = ""
    columnas: list = field(default_factory=list)
    parametros: list = field(default_factory=list)
    definicion: str = ""
    clave_primaria: list = field(default_factory=list)
    indices: list = field(default_factory=list)
    depende_de: set = field(default_factory=set)

    @property
    def tipo(self):
        return TIPOS_OBJETO.get(self.tipo_sql, self.tipo_sql)

    @property
    def nombre_simple(self):
        return f"{self.esquema}.{self.corto}"


def _partes(nombre):
    return re.findall(r"\[((?:[^\]]|\]\])*)\]", nombre or "")


def _valor_propiedad(elem, nombre):
    for p in elem.findall(f"{NS}Property"):
        if p.get("Name") == nombre:
            if p.get("Value") is not None:
                return p.get("Value")
            v = p.find(f"{NS}Value")
            return v.text if v is not None else ""
    return None


def _referencias(elem, relacion):
    salida = []
    for r in elem.findall(f"{NS}Relationship"):
        if r.get("Name") == relacion:
            for entry in r.findall(f"{NS}Entry"):
                for ref in entry.findall(f"{NS}References"):
                    salida.append(ref.get("Name"))
    return salida


def _elementos_rel(elem, relacion):
    salida = []
    for r in elem.findall(f"{NS}Relationship"):
        if r.get("Name") == relacion:
            for entry in r.findall(f"{NS}Entry"):
                salida.extend(entry.findall(f"{NS}Element"))
    return salida


def _tipo_dato(elem_col):
    especificadores = [e for e in _elementos_rel(elem_col, "TypeSpecifier") + _elementos_rel(elem_col, "Type")
                       if e.get("Type") == "SqlTypeSpecifier"]
    for ts in especificadores:
        tipo = (_referencias(ts, "Type") or ["?"])[0]
        tipo = _partes(tipo)[-1] if _partes(tipo) else tipo
        if _valor_propiedad(ts, "IsMax") == "True":
            return f"{tipo.upper()}(MAX)"
        largo = _valor_propiedad(ts, "Length")
        prec, esc = _valor_propiedad(ts, "Precision"), _valor_propiedad(ts, "Scale")
        if largo:
            return f"{tipo.upper()}({largo})"
        if prec and tipo.lower() in ("decimal", "numeric"):
            return f"{tipo.upper()}({prec},{esc or 0})"
        if tipo.lower() in ("datetime2", "time", "datetimeoffset"):
            return f"{tipo.upper()}({esc or 0})"
        return tipo.upper()
    return ""


def _limpiar_valor_ep(valor):
    v = (valor or "").strip()
    m = re.fullmatch(r"N?'(.*)'", v, flags=re.S)
    return m.group(1).replace("''", "'") if m else v


def cargar(ruta_dacpac):
    """Devuelve dict nombre -> Objeto, con dependencias resueltas a nivel de objeto."""
    with zipfile.ZipFile(ruta_dacpac) as z:
        raiz = ET.fromstring(z.read("model.xml"))
    modelo = raiz.find(f"{NS}Model")
    objetos, descripciones, defaults, pks = {}, {}, {}, {}
    indices = []

    for el in modelo.findall(f"{NS}Element"):
        tipo, nombre = el.get("Type"), el.get("Name")
        partes = _partes(nombre)
        if tipo in TIPOS_DOCUMENTABLES:
            o = Objeto(nombre=nombre, tipo_sql=tipo, esquema=partes[0], corto=partes[-1])
            for c in _elementos_rel(el, "Columns"):
                cp = _partes(c.get("Name"))
                col = Columna(nombre=cp[-1], tipo=_tipo_dato(c),
                              nulo=_valor_propiedad(c, "IsNullable") != "False",
                              identidad=_valor_propiedad(c, "IsIdentity") == "True",
                              calculada=c.get("Type") == "SqlComputedColumn")
                o.columnas.append(col)
            for prm in _elementos_rel(el, "Parameters"):
                pp = _partes(prm.get("Name"))
                o.parametros.append(f"{pp[-1]} {_tipo_dato(prm)}")
            cuerpo = _valor_propiedad(el, "QueryScript") or _valor_propiedad(el, "BodyScript") or ""
            o.definicion = cuerpo.strip()
            deps = set()
            for rel in ("BodyDependencies", "QueryDependencies", "ExpressionDependencies"):
                deps.update(_referencias(el, rel))
            for c in _elementos_rel(el, "Columns"):
                deps.update(_referencias(c, "ExpressionDependencies"))
            o.depende_de = deps
            objetos[nombre] = o
        elif tipo == "SqlExtendedProperty":
            if partes and partes[-1] == "MS_Description":
                host = (_referencias(el, "Host") or [None])[0]
                if host:
                    descripciones[host] = _limpiar_valor_ep(_valor_propiedad(el, "Value"))
        elif tipo == "SqlDefaultConstraint":
            col = (_referencias(el, "ForColumn") or [None])[0]
            if col:
                defaults[col] = (_valor_propiedad(el, "DefaultExpressionScript") or "").strip()
        elif tipo == "SqlPrimaryKeyConstraint":
            tabla = (_referencias(el, "DefiningTable") or [None])[0]
            cols = []
            for spec in _elementos_rel(el, "ColumnSpecifications"):
                cols.extend(_partes(c)[-1] for c in _referencias(spec, "Column"))
            if tabla:
                pks[tabla] = cols
        elif tipo == "SqlIndex":
            tabla = (_referencias(el, "IndexedObject") or [None])[0]
            cols = []
            for spec in _elementos_rel(el, "ColumnSpecifications"):
                cols.extend(_partes(c)[-1] for c in _referencias(spec, "Column"))
            indices.append((tabla, partes[-1], cols))

    for nombre, o in objetos.items():
        o.descripcion = descripciones.get(nombre, "")
        o.clave_primaria = pks.get(nombre, [])
        for c in o.columnas:
            ref = f"{nombre}.[{c.nombre}]"
            c.descripcion = descripciones.get(ref, "")
            c.default = defaults.get(ref, "")
        # dependencias a nivel de objeto (descarta columnas, tipos y el propio objeto)
        resueltas = set()
        for d in o.depende_de:
            p = _partes(d)
            if len(p) >= 2:
                candidato = f"[{p[0]}].[{p[1]}]"
                if candidato in objetos and candidato != nombre:
                    resueltas.add(candidato)
        o.depende_de = resueltas
    for tabla, nombre_idx, cols in indices:
        if tabla in objetos:
            objetos[tabla].indices.append(f"{nombre_idx} ({', '.join(cols)})")
    return objetos


def usado_por(objetos):
    """Mapa inverso: objeto -> conjunto de objetos que dependen de él."""
    inverso = {n: set() for n in objetos}
    for n, o in objetos.items():
        for d in o.depende_de:
            inverso.setdefault(d, set()).add(n)
    return inverso


def impacto(objetos, cambiados, profundidad=4):
    """Objetos aguas abajo (que dependen directa o indirectamente) de los objetos cambiados."""
    inverso = usado_por(objetos)
    aristas, visitados = set(), set()
    frontera = set(cambiados)
    for _ in range(profundidad):
        nueva = set()
        for n in frontera:
            for dep in inverso.get(n, ()):
                aristas.add((n, dep))
                if dep not in visitados and dep not in cambiados:
                    nueva.add(dep)
        visitados |= nueva
        frontera = nueva
    return visitados, aristas


def _norm(texto):
    return [l.rstrip() for l in (texto or "").strip().splitlines()]


def comparar(base, nuevo):
    """Compara dos modelos. Devuelve lista de cambios por objeto."""
    base = base or {}
    cambios = []
    for nombre in sorted(set(base) | set(nuevo)):
        a, b = base.get(nombre), nuevo.get(nombre)
        if a is None:
            cambios.append({"objeto": nombre, "tipo": b.tipo, "accion": "AGREGADO", "detalle": [],
                            "diff": list(difflib.unified_diff([], _norm(b.definicion), lineterm="", n=3))})
            continue
        if b is None:
            cambios.append({"objeto": nombre, "tipo": a.tipo, "accion": "ELIMINADO", "detalle": [], "diff": []})
            continue
        detalle = []
        ca = {c.nombre: c for c in a.columnas}
        cb = {c.nombre: c for c in b.columnas}
        if a.tipo_sql == "SqlTable":
            for c in cb:
                if c not in ca:
                    detalle.append(f"➕ Columna nueva `{c}` {cb[c].firma()}")
            for c in ca:
                if c not in cb:
                    detalle.append(f"➖ Columna eliminada `{c}` ({ca[c].firma()})")
            for c in cb:
                if c in ca and ca[c].firma() != cb[c].firma():
                    detalle.append(f"✏️ Columna `{c}`: {ca[c].firma()} → {cb[c].firma()}")
            if a.clave_primaria != b.clave_primaria:
                detalle.append(f"🔑 Clave primaria: {', '.join(a.clave_primaria)} → {', '.join(b.clave_primaria)}")
            if a.indices != b.indices:
                detalle.append("Índices modificados")
        elif ca.keys() != cb.keys():
            agregadas = [c for c in cb if c not in ca]
            quitadas = [c for c in ca if c not in cb]
            if agregadas:
                detalle.append("➕ Columnas de salida nuevas: " + ", ".join(f"`{c}`" for c in agregadas))
            if quitadas:
                detalle.append("➖ Columnas de salida eliminadas: " + ", ".join(f"`{c}`" for c in quitadas))
        if a.parametros != b.parametros:
            detalle.append(f"Parámetros: ({', '.join(a.parametros)}) → ({', '.join(b.parametros)})")
        diff = []
        if _norm(a.definicion) != _norm(b.definicion):
            diff = list(difflib.unified_diff(_norm(a.definicion), _norm(b.definicion),
                                             fromfile="actual", tofile="propuesto", lineterm="", n=3))
            if a.tipo_sql != "SqlTable":
                detalle.append("Definición (código) modificada")
        if a.descripcion != b.descripcion:
            detalle.append("Descripción del objeto actualizada")
        desc_cols = [c for c in cb if c in ca and ca[c].descripcion != cb[c].descripcion]
        if desc_cols:
            detalle.append("Descripción actualizada en columnas: " + ", ".join(f"`{c}`" for c in desc_cols))
        if detalle or diff:
            cambios.append({"objeto": nombre, "tipo": b.tipo, "accion": "MODIFICADO", "detalle": detalle, "diff": diff})
    return cambios
