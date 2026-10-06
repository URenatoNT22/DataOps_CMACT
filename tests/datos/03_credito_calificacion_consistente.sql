-- severidad: ERROR
-- descripcion: La calificación debe ser un valor válido y consistente con los días de atraso.
SELECT TOP (50) [FECHA_CORTE], [COD_CREDITO], [DIAS_ATRASO], [CALIFICACION]
FROM [tab].[TB_CREDITO]
WHERE [CALIFICACION] <> CASE WHEN [DIAS_ATRASO] <= 8   THEN 'NORMAL'
                             WHEN [DIAS_ATRASO] <= 30  THEN 'CPP'
                             WHEN [DIAS_ATRASO] <= 60  THEN 'DEFICIENTE'
                             WHEN [DIAS_ATRASO] <= 120 THEN 'DUDOSO'
                             ELSE 'PERDIDA' END;
