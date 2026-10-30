<!--
  SOLICITUD DE PASE · Inteligencia de Negocios
  Complete cada sección. Las secciones 1, 3 y 4 alimentan el Acta de Pase a Producción
  que el pipeline genera automáticamente: escriba el valor después de los dos puntos y
  marque las opciones con [x].

  Título del PR (Conventional Commits):  tipo(ámbito): descripción
    feat(rpt): agrega vista de mora por analista
    fix(tab): corrige cálculo de días de atraso en TB_CREDITO
  Tipos: feat · fix · perf · refactor · docs · test · chore · revert  (agregar ! si rompe compatibilidad)
-->

## 1. Identificación del requerimiento

- **Código de requerimiento:** 
- **Área solicitante:** 
- **Módulo / aplicación:** 
- **Tipo de pase:** [ ] Solicitud de negocio  [ ] Corrección de error

## 2. Motivo

<!-- Necesidad de negocio que atiende y resultado esperado. Mínimo una oración. -->


## 3. Alcance técnico

<!-- Los objetos de base de datos (crear / modificar / eliminar) los detecta y lista el pipeline. -->
- **Incluye cambios de datos (carpeta migraciones/):** [ ] Sí  [ ] No
- **Jobs involucrados:** 
- **Frecuencia del job:** [ ] Diaria  [ ] Semanal  [ ] Mensual  [ ] No aplica

## 4. Impacto operativo

- **Afecta cierre diario:** [ ] Sí  [ ] No
- **Afecta performance del sistema:** [ ] Sí  [ ] No
- **Criticidad:** [ ] Alta  [ ] Media  [ ] Baja
- **Ventana de ejecución sugerida:** 

## 5. Prerrequisitos

- [ ] Acta de capacitación a soporte informático
- [ ] Acta de capacitación al usuario líder
- [ ] Acta de validación del usuario líder
- [ ] Acta de validación interna
- Otros: 

## 6. Validación del desarrollador

- [ ] Probé el cambio y los resultados son los esperados
- [ ] Revisé el reporte automático del pipeline (riesgo, impacto y script)
- [ ] Los objetos nuevos o modificados tienen descripción (`MS_Description`) y los campos sensibles están clasificados (`DatoSensible`)
- [ ] Si hay `UPDATE` / `DELETE`, el script respalda las filas en `ctl.RESPALDO_DATOS`

## 7. Plan de reversión

<!-- Por defecto: rollback a la versión anterior por el pipeline (solo TI). Indique aquí si requiere algo adicional. -->
Rollback a la versión anterior mediante el workflow *Rollback*. 

---

### Conformidad del revisor

- [ ] El cambio corresponde al requerimiento y al motivo descrito
- [ ] El riesgo calculado y el impacto aguas abajo son aceptables
- [ ] Las pruebas y validaciones automáticas están conformes
- [ ] (Cambio SENSIBLE) Cuenta con el visto previo de TI
