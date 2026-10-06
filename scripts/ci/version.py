#!/usr/bin/env python3
"""
Calcula la siguiente versión semántica a partir de Conventional Commits.

  feat!: / BREAKING CHANGE  -> MAJOR
  feat:                     -> MINOR
  fix:, perf:, refactor:... -> PATCH

Uso:
  version.py siguiente          -> imprime vX.Y.Z (siguiente versión de producción)
  version.py desarrollo N       -> imprime X.Y.Z.N (versión de un build de DEV)
"""
import re
import subprocess
import sys


def git(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def ultimo_tag():
    tags = [t for t in git("tag", "--list", "v*", "--sort=-v:refname").splitlines() if re.fullmatch(r"v\d+\.\d+\.\d+", t)]
    return tags[0] if tags else ""


def siguiente():
    tag = ultimo_tag()
    if not tag:
        return "v1.0.0", tag, []
    mayor, menor, parche = map(int, tag[1:].split("."))
    mensajes = git("log", f"{tag}..HEAD", "--format=%s%n%b%n---fin---").split("---fin---")
    mensajes = [m.strip() for m in mensajes if m.strip()]
    salto = None
    for m in mensajes:
        titulo = m.splitlines()[0]
        if re.match(r"^\w+(\([^)]*\))?!:", titulo) or "BREAKING CHANGE" in m:
            salto = "major"
            break
        if re.match(r"^feat(\([^)]*\))?:", titulo):
            salto = "minor"
        elif salto is None:
            salto = "patch"
    if salto == "major":
        return f"v{mayor + 1}.0.0", tag, mensajes
    if salto == "minor":
        return f"v{mayor}.{menor + 1}.0", tag, mensajes
    return f"v{mayor}.{menor}.{parche + 1}", tag, mensajes


if __name__ == "__main__":
    modo = sys.argv[1] if len(sys.argv) > 1 else "siguiente"
    if modo == "siguiente":
        print(siguiente()[0])
    elif modo == "anterior":
        print(ultimo_tag())
    elif modo == "desarrollo":
        n = sys.argv[2] if len(sys.argv) > 2 else "0"
        base = siguiente()[0][1:]
        print(f"{base}.{n}")
    else:
        sys.exit(__doc__)
