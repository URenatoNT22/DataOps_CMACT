-- severidad: ERROR
-- descripcion: El tablón TB_CREDITO debe tener filas en su última fecha de corte.
SELECT 'TB_CREDITO sin filas' AS [FALLA]
WHERE NOT EXISTS (SELECT 1 FROM [tab].[TB_CREDITO]);
