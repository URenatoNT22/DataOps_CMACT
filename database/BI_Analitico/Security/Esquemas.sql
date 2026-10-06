-- Esquemas del ambiente analítico
--   src : réplica simulada de los sistemas fuente (core financiero). En la demo se llena con datos ficticios.
--   tab : tablones desnormalizados (un registro = una entidad de negocio a una fecha de corte).
--   rpt : vistas de consumo para Power BI / usuarios. Nunca se lee un tablón directo desde un reporte.
--   ctl : control de procesos (bitácora de cargas, orquestación, utilitarios de demo).
CREATE SCHEMA [src] AUTHORIZATION [dbo];
GO
CREATE SCHEMA [tab] AUTHORIZATION [dbo];
GO
CREATE SCHEMA [rpt] AUTHORIZATION [dbo];
GO
CREATE SCHEMA [ctl] AUTHORIZATION [dbo];
GO
