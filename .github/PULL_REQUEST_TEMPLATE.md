<!--
  Título del PR (obligatorio, Conventional Commits):
    feat(tab): agrega columna SEGMENTO_RIESGO a TB_CREDITO
    fix(rpt): corrige cálculo de ratio de mora en vw_RESUMEN_CARTERA_AGENCIA
    refactor(tab): simplifica carga de TB_CRONOGRAMA
  Tipos: feat | fix | perf | refactor | docs | test | chore | revert   (agregar ! si rompe compatibilidad: feat!: ...)

  Ramas: feature/<ticket>-<descripcion> -> develop (DEV)   |   develop -> main (PROD)
  El pipeline completa automáticamente: qué cambia, impacto, riesgo, script y pruebas.
-->

## Motivo
<!-- ¿Qué necesidad de negocio atiende? ¿Quién lo pidió? Mínimo una oración. -->


## Solicitud / ticket relacionado
<!-- Ej: Relacionado: #12  (issue de solicitud de cambio) -->


## Indicadores, reportes o procesos afectados
<!-- Ej: Reporte de cartera Power BI, indicador de mora por agencia, job de carga diaria -->


## Cómo se validó
- [ ] Probé la consulta / el proceso en mi ambiente
- [ ] Revisé el reporte automático del pipeline (comentario en este PR)
- [ ] Los objetos nuevos o modificados tienen descripción (MS_Description)

## Para el aprobador
- [ ] El cambio corresponde al motivo descrito
- [ ] El riesgo calculado es razonable y el impacto aguas abajo está entendido
- [ ] (Si es SENSIBLE) TI dio su visto previo
