-- severidad: ERROR
-- descripcion: El capital de las cuotas no pagadas del cronograma debe ser igual al saldo de capital del tablón de créditos (por crédito y fecha de corte).
SELECT TOP (50) [t].[FECHA_CORTE], [t].[COD_CREDITO], [t].[SALDO_CAPITAL], [c].[CAPITAL_PENDIENTE]
FROM [tab].[TB_CREDITO] AS [t]
LEFT JOIN
(
    SELECT [FECHA_CORTE], [COD_CREDITO], SUM([CAPITAL]) AS [CAPITAL_PENDIENTE]
    FROM [tab].[TB_CRONOGRAMA]
    WHERE [ESTADO_CUOTA] <> 'PAGADA'
    GROUP BY [FECHA_CORTE], [COD_CREDITO]
) AS [c] ON [c].[FECHA_CORTE] = [t].[FECHA_CORTE] AND [c].[COD_CREDITO] = [t].[COD_CREDITO]
WHERE ABS([t].[SALDO_CAPITAL] - ISNULL([c].[CAPITAL_PENDIENTE], 0)) > 0.01;
