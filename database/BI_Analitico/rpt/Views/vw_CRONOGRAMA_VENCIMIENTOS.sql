-- Vista de consumo: cuotas no pagadas (vencidas y por vencer) a la última fecha de corte.
CREATE VIEW [rpt].[vw_CRONOGRAMA_VENCIMIENTOS]
AS
SELECT
    [c].[FECHA_CORTE],
    [c].[COD_CREDITO],
    [c].[NRO_CUOTA],
    [c].[NRO_DOCUMENTO],
    [c].[NOMBRE_CLIENTE],
    [c].[NOMBRE_AGENCIA],
    [c].[NOMBRE_PRODUCTO],
    [c].[MONEDA],
    [c].[FECHA_VENCIMIENTO],
    [c].[MONTO_CUOTA],
    [c].[ESTADO_CUOTA],
    [c].[DIAS_ATRASO_CUOTA]
FROM [tab].[TB_CRONOGRAMA] AS [c]
WHERE [c].[FECHA_CORTE] = (SELECT MAX([FECHA_CORTE]) FROM [tab].[TB_CRONOGRAMA])
  AND [c].[ESTADO_CUOTA] IN ('VENCIDA', 'POR_VENCER');
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description',
    @value = N'Cuotas no pagadas (vencidas y por vencer) a la última fecha de corte, para gestión de cobranza.',
    @level0type = N'SCHEMA', @level0name = N'rpt', @level1type = N'VIEW', @level1name = N'vw_CRONOGRAMA_VENCIMIENTOS';
GO
