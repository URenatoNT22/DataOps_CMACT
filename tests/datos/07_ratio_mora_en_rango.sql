-- severidad: ADVERTENCIA
-- descripcion: Indicador de negocio: el ratio de mora total de la última fecha de corte debería estar entre 0% y 25%. Fuera de ese rango, revisar antes de publicar.
SELECT [FECHA_CORTE], [RATIO_MORA]
FROM
(
    SELECT [FECHA_CORTE],
           SUM([SALDO_EN_MORA]) / NULLIF(SUM([SALDO_CARTERA]), 0) AS [RATIO_MORA]
    FROM [rpt].[vw_RESUMEN_CARTERA_AGENCIA]
    WHERE [FECHA_CORTE] = (SELECT MAX([FECHA_CORTE]) FROM [tab].[TB_CREDITO])
    GROUP BY [FECHA_CORTE]
) AS [x]
WHERE [RATIO_MORA] < 0 OR [RATIO_MORA] > 0.25;
