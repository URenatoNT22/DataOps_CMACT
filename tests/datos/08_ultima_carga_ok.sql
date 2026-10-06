-- severidad: ADVERTENCIA
-- descripcion: La última ejecución registrada de cada proceso de carga debe haber terminado en estado OK.
SELECT [b].[PROCESO], [b].[FECHA_CORTE], [b].[ESTADO], [b].[MENSAJE]
FROM [ctl].[BITACORA_CARGA] AS [b]
WHERE [b].[ID_BITACORA] IN (SELECT MAX([ID_BITACORA]) FROM [ctl].[BITACORA_CARGA] GROUP BY [PROCESO])
  AND [b].[ESTADO] <> 'OK';
