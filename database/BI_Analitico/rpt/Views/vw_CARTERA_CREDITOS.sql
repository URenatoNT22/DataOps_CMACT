-- Vista de consumo: cartera de créditos a la última fecha de corte disponible.
CREATE VIEW [rpt].[vw_CARTERA_CREDITOS]
AS
SELECT
    [t].[FECHA_CORTE],
    [t].[COD_CREDITO],
    [t].[NRO_DOCUMENTO],
    [t].[NOMBRE_CLIENTE],
    [t].[SEGMENTO_CLIENTE],
    [t].[REGION],
    [t].[ZONA],
    [t].[NOMBRE_AGENCIA],
    [t].[ANALISTA],
    [t].[TIPO_CREDITO],
    [t].[NOMBRE_PRODUCTO],
    [t].[MONEDA],
    [t].[FECHA_DESEMBOLSO],
    [t].[MONTO_DESEMBOLSADO],
    [t].[TASA_ANUAL],
    [t].[NRO_CUOTAS],
    [t].[CUOTAS_PAGADAS],
    [t].[CUOTAS_PENDIENTES],
    [t].[SALDO_CAPITAL],
    [t].[CAPITAL_VENCIDO],
    [t].[DIAS_ATRASO],
    [t].[CALIFICACION],
    [t].[ESTADO_CREDITO],
    CAST(CASE WHEN [t].[DIAS_ATRASO] > 30 THEN 1 ELSE 0 END AS BIT) AS [EN_MORA]
FROM [tab].[TB_CREDITO] AS [t]
WHERE [t].[FECHA_CORTE] = (SELECT MAX([FECHA_CORTE]) FROM [tab].[TB_CREDITO]);
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description',
    @value = N'Cartera de créditos con saldo a la última fecha de corte. Fuente para reportes de cartera en Power BI.',
    @level0type = N'SCHEMA', @level0name = N'rpt', @level1type = N'VIEW', @level1name = N'vw_CARTERA_CREDITOS';
GO
