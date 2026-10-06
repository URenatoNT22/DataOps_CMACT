-- severidad: ERROR
-- descripcion: Toda cuota del tablón de cronogramas debe pertenecer a un crédito del tablón de créditos en la misma fecha de corte.
SELECT TOP (50) [c].[FECHA_CORTE], [c].[COD_CREDITO], [c].[NRO_CUOTA]
FROM [tab].[TB_CRONOGRAMA] AS [c]
WHERE NOT EXISTS (SELECT 1 FROM [tab].[TB_CREDITO] AS [t]
                  WHERE [t].[FECHA_CORTE] = [c].[FECHA_CORTE] AND [t].[COD_CREDITO] = [c].[COD_CREDITO]);
