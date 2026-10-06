-- Carga el tablón tab.TB_CRONOGRAMA para una fecha de corte.
-- Depende de tab.TB_CREDITO de la misma fecha de corte (se ejecuta después de usp_CARGA_TB_CREDITO):
-- solo incluye cuotas de créditos con saldo y toma de ahí los atributos desnormalizados.
CREATE PROCEDURE [tab].[usp_CARGA_TB_CRONOGRAMA]
    @FECHA_CORTE DATE
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    DECLARE @ID_BITACORA BIGINT, @FILAS INT, @MENSAJE NVARCHAR(4000);

    INSERT INTO [ctl].[BITACORA_CARGA] ([PROCESO], [FECHA_CORTE], [INICIO], [ESTADO])
    VALUES (N'tab.usp_CARGA_TB_CRONOGRAMA', @FECHA_CORTE, SYSDATETIME(), 'EN_CURSO');
    SET @ID_BITACORA = SCOPE_IDENTITY();

    BEGIN TRY
        IF NOT EXISTS (SELECT 1 FROM [tab].[TB_CREDITO] WHERE [FECHA_CORTE] = @FECHA_CORTE)
            THROW 50001, N'No existe tab.TB_CREDITO para la fecha de corte. Ejecute primero tab.usp_CARGA_TB_CREDITO.', 1;

        BEGIN TRANSACTION;

        DELETE FROM [tab].[TB_CRONOGRAMA] WHERE [FECHA_CORTE] = @FECHA_CORTE;

        INSERT INTO [tab].[TB_CRONOGRAMA]
        (
            [FECHA_CORTE], [COD_CREDITO], [NRO_CUOTA], [ID_CREDITO], [NRO_DOCUMENTO], [NOMBRE_CLIENTE], [NOMBRE_AGENCIA],
            [NOMBRE_PRODUCTO], [MONEDA], [FECHA_VENCIMIENTO], [CAPITAL], [INTERES], [MONTO_CUOTA], [SALDO_CAPITAL_POST],
            [FECHA_PAGO], [MONTO_PAGADO], [ESTADO_CUOTA], [DIAS_ATRASO_CUOTA]
        )
        SELECT
            @FECHA_CORTE,
            [t].[COD_CREDITO],
            [q].[NRO_CUOTA],
            [q].[ID_CREDITO],
            [t].[NRO_DOCUMENTO],
            [t].[NOMBRE_CLIENTE],
            [t].[NOMBRE_AGENCIA],
            [t].[NOMBRE_PRODUCTO],
            [t].[MONEDA],
            [q].[FECHA_VENCIMIENTO],
            [q].[CAPITAL],
            [q].[INTERES],
            [q].[CAPITAL] + [q].[INTERES],
            SUM([q].[CAPITAL]) OVER (PARTITION BY [q].[ID_CREDITO] ORDER BY [q].[NRO_CUOTA] DESC
                                     ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) - [q].[CAPITAL],
            [e].[FECHA_PAGO],
            [e].[MONTO_PAGADO],
            [e].[ESTADO_CUOTA],
            CASE WHEN [e].[ESTADO_CUOTA] = 'VENCIDA' THEN DATEDIFF(DAY, [q].[FECHA_VENCIMIENTO], @FECHA_CORTE) ELSE 0 END
        FROM [src].[CUOTA] AS [q]
        INNER JOIN [tab].[TB_CREDITO] AS [t]
                ON [t].[ID_CREDITO] = [q].[ID_CREDITO]
               AND [t].[FECHA_CORTE] = @FECHA_CORTE
        CROSS APPLY
        (
            SELECT
                CASE WHEN [q].[FECHA_PAGO] <= @FECHA_CORTE THEN [q].[FECHA_PAGO] END   AS [FECHA_PAGO],
                CASE WHEN [q].[FECHA_PAGO] <= @FECHA_CORTE THEN [q].[MONTO_PAGADO] END AS [MONTO_PAGADO],
                CASE WHEN [q].[FECHA_PAGO] <= @FECHA_CORTE      THEN 'PAGADA'
                     WHEN [q].[FECHA_VENCIMIENTO] < @FECHA_CORTE THEN 'VENCIDA'
                     ELSE 'POR_VENCER' END                                               AS [ESTADO_CUOTA]
        ) AS [e];

        SET @FILAS = @@ROWCOUNT;

        COMMIT TRANSACTION;

        UPDATE [ctl].[BITACORA_CARGA]
           SET [FIN] = SYSDATETIME(), [ESTADO] = 'OK', [FILAS] = @FILAS
         WHERE [ID_BITACORA] = @ID_BITACORA;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;
        SET @MENSAJE = ERROR_MESSAGE();
        UPDATE [ctl].[BITACORA_CARGA]
           SET [FIN] = SYSDATETIME(), [ESTADO] = 'ERROR', [MENSAJE] = @MENSAJE
         WHERE [ID_BITACORA] = @ID_BITACORA;
        THROW;
    END CATCH
END
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description',
    @value = N'Carga idempotente del tablón tab.TB_CRONOGRAMA para una fecha de corte. Requiere tab.TB_CREDITO cargado para esa fecha.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'PROCEDURE', @level1name = N'usp_CARGA_TB_CRONOGRAMA';
GO
