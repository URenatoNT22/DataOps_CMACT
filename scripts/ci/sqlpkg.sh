#!/usr/bin/env bash
# Envoltorio de SqlPackage. Usa SQL_SERVER / SQL_USER / SQL_PASSWORD del entorno.
#   sqlpkg.sh reporte  <dacpac> <base> <salida.xml> [opciones extra]
#   sqlpkg.sh script   <dacpac> <base> <salida.sql> [opciones extra]
#   sqlpkg.sh publicar <dacpac> <base> [opciones extra]
#   sqlpkg.sh extraer  <base> <salida.dacpac>
set -euo pipefail
PERFIL="${PERFIL:-deployment/publicacion.publish.xml}"
: "${SQL_SERVER:?falta SQL_SERVER}" "${SQL_USER:?falta SQL_USER}" "${SQL_PASSWORD:?falta SQL_PASSWORD}"
SERVIDOR="tcp:${SQL_SERVER#tcp:}"

destino() {
  echo "/TargetServerName:$SERVIDOR"; echo "/TargetDatabaseName:$1"; echo "/TargetUser:$SQL_USER"
  echo "/TargetPassword:$SQL_PASSWORD"; echo "/TargetTrustServerCertificate:True"; echo "/TargetEncryptConnection:True"
  echo "/TargetTimeout:60"
}

accion="$1"; shift
case "$accion" in
  reporte|script|publicar)
    dacpac="$1"; base="$2"; shift 2
    mapfile -t dst < <(destino "$base")
    declare -A act=([reporte]=DeployReport [script]=Script [publicar]=Publish)
    salida=()
    if [ "$accion" != "publicar" ]; then salida=("/OutputPath:$1"); shift; mkdir -p "$(dirname "${salida[0]#/OutputPath:}")"; fi
    sqlpackage "/Action:${act[$accion]}" "/SourceFile:$dacpac" "${dst[@]}" "/Profile:$PERFIL" "${salida[@]}" \
      /p:CommandTimeout=0 "$@"
    ;;
  extraer)
    base="$1"; salida="$2"; mkdir -p "$(dirname "$salida")"
    sqlpackage /Action:Extract "/SourceServerName:$SERVIDOR" "/SourceDatabaseName:$base" "/SourceUser:$SQL_USER" \
      "/SourcePassword:$SQL_PASSWORD" /SourceTrustServerCertificate:True /SourceEncryptConnection:True /SourceTimeout:60 \
      "/TargetFile:$salida" /p:ExtractAllTableData=False /p:IgnorePermissions=True /p:IgnoreUserLoginMappings=True \
      /p:VerifyExtraction=False
    ;;
  *) echo "acción desconocida: $accion" >&2; exit 2 ;;
esac
