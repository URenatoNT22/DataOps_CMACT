-- severidad: ERROR
-- descripcion: Indicador de negocio: el saldo de cartera de la vista rpt.vw_RESUMEN_CARTERA_AGENCIA debe cuadrar con el tablón por fecha de corte.
SELECT [t].[FECHA_CORTE], [t].[SALDO_TABLON], [r].[SALDO_VISTA]
FROM (SELECT [FECHA_CORTE], SUM([SALDO_CAPITAL]) AS [SALDO_TABLON] FROM [tab].[TB_CREDITO] GROUP BY [FECHA_CORTE]) AS [t]
LEFT JOIN (SELECT [FECHA_CORTE], SUM([SALDO_CARTERA]) AS [SALDO_VISTA] FROM [rpt].[vw_RESUMEN_CARTERA_AGENCIA] GROUP BY [FECHA_CORTE]) AS [r]
       ON [r].[FECHA_CORTE] = [t].[FECHA_CORTE]
WHERE ABS([t].[SALDO_TABLON] - ISNULL([r].[SALDO_VISTA], 0)) > 0.01;
