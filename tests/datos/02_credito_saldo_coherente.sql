-- severidad: ERROR
-- descripcion: El saldo de capital no puede ser negativo ni mayor al monto desembolsado; el capital vencido no puede superar al saldo.
SELECT TOP (50) [FECHA_CORTE], [COD_CREDITO], [MONTO_DESEMBOLSADO], [SALDO_CAPITAL], [CAPITAL_VENCIDO]
FROM [tab].[TB_CREDITO]
WHERE [SALDO_CAPITAL] < 0
   OR [SALDO_CAPITAL] > [MONTO_DESEMBOLSADO]
   OR [CAPITAL_VENCIDO] > [SALDO_CAPITAL];
