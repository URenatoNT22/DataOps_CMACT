-- Vista de consumo: indicadores de cartera por fecha de corte, agencia y tipo de crédito.
CREATE VIEW [rpt].[vw_RESUMEN_CARTERA_AGENCIA]
AS
SELECT
    [t].[FECHA_CORTE],
    [t].[REGION],
    [t].[NOMBRE_AGENCIA],
    [t].[TIPO_CREDITO],
    [t].[MONEDA],
    COUNT_BIG(*)                                                         AS [NRO_CREDITOS],
    SUM([t].[SALDO_CAPITAL])                                             AS [SALDO_CARTERA],
    SUM(CASE WHEN [t].[DIAS_ATRASO] > 30 THEN [t].[SALDO_CAPITAL] ELSE 0 END) AS [SALDO_EN_MORA],
    CAST(SUM(CASE WHEN [t].[DIAS_ATRASO] > 30 THEN [t].[SALDO_CAPITAL] ELSE 0 END)
         / NULLIF(SUM([t].[SALDO_CAPITAL]), 0) AS DECIMAL(9,6))          AS [RATIO_MORA]
FROM [tab].[TB_CREDITO] AS [t]
GROUP BY [t].[FECHA_CORTE], [t].[REGION], [t].[NOMBRE_AGENCIA], [t].[TIPO_CREDITO], [t].[MONEDA];
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description',
    @value = N'Indicadores de cartera (saldo, saldo en mora > 30 días y ratio de mora) por fecha de corte, agencia y tipo de crédito.',
    @level0type = N'SCHEMA', @level0name = N'rpt', @level1type = N'VIEW', @level1name = N'vw_RESUMEN_CARTERA_AGENCIA';
GO
