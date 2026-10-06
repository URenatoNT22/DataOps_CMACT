-- Carga el tablón tab.TB_CREDITO para una fecha de corte.
-- Idempotente: borra y vuelve a cargar la fecha de corte indicada.
-- Registra la ejecución en ctl.BITACORA_CARGA.
CREATE PROCEDURE [tab].[usp_CARGA_TB_CREDITO]
    @FECHA_CORTE DATE
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    DECLARE @ID_BITACORA BIGINT, @FILAS INT, @MENSAJE NVARCHAR(4000);

    INSERT INTO [ctl].[BITACORA_CARGA] ([PROCESO], [FECHA_CORTE], [INICIO], [ESTADO])
    VALUES (N'tab.usp_CARGA_TB_CREDITO', @FECHA_CORTE, SYSDATETIME(), 'EN_CURSO');
    SET @ID_BITACORA = SCOPE_IDENTITY();

    BEGIN TRY
        BEGIN TRANSACTION;

        DELETE FROM [tab].[TB_CREDITO] WHERE [FECHA_CORTE] = @FECHA_CORTE;

        WITH [CUOTAS] AS
        (
            SELECT
                [q].[ID_CREDITO],
                SUM(CASE WHEN [q].[FECHA_PAGO] <= @FECHA_CORTE THEN 1 ELSE 0 END)                         AS [CUOTAS_PAGADAS],
                SUM(CASE WHEN [p].[IMPAGA] = 1 AND [q].[FECHA_VENCIMIENTO] < @FECHA_CORTE THEN 1 ELSE 0 END) AS [CUOTAS_VENCIDAS_IMPAGAS],
                SUM(CASE WHEN [p].[IMPAGA] = 1 THEN 1 ELSE 0 END)                                            AS [CUOTAS_PENDIENTES],
                SUM(CASE WHEN [p].[IMPAGA] = 1 THEN [q].[CAPITAL] ELSE 0 END)                                AS [SALDO_CAPITAL],
                SUM(CASE WHEN [p].[IMPAGA] = 1 AND [q].[FECHA_VENCIMIENTO] < @FECHA_CORTE THEN [q].[CAPITAL] ELSE 0 END) AS [CAPITAL_VENCIDO],
                MIN(CASE WHEN [p].[IMPAGA] = 1 AND [q].[FECHA_VENCIMIENTO] < @FECHA_CORTE THEN [q].[FECHA_VENCIMIENTO] END) AS [PRIMER_VENCIMIENTO_IMPAGO],
                MIN(CASE WHEN [p].[IMPAGA] = 1 AND [q].[FECHA_VENCIMIENTO] >= @FECHA_CORTE THEN [q].[FECHA_VENCIMIENTO] END) AS [FECHA_PROXIMO_VENCIMIENTO]
            FROM [src].[CUOTA] AS [q]
            CROSS APPLY (SELECT CASE WHEN [q].[FECHA_PAGO] IS NULL OR [q].[FECHA_PAGO] > @FECHA_CORTE THEN 1 ELSE 0 END AS [IMPAGA]) AS [p]
            GROUP BY [q].[ID_CREDITO]
        ),
        [BASE] AS
        (
            SELECT
                [c].[ID_CREDITO], [c].[COD_CREDITO], [c].[ANALISTA], [c].[FECHA_DESEMBOLSO], [c].[MONTO_DESEMBOLSADO],
                [c].[TASA_ANUAL], [c].[NRO_CUOTAS],
                [cl].[ID_CLIENTE], [cl].[TIPO_DOCUMENTO], [cl].[NRO_DOCUMENTO], [cl].[NOMBRE_COMPLETO], [cl].[SEXO],
                [cl].[FECHA_NACIMIENTO], [cl].[SEGMENTO],
                [a].[ID_AGENCIA], [a].[NOMBRE_AGENCIA], [a].[REGION], [a].[ZONA],
                [pr].[ID_PRODUCTO], [pr].[NOMBRE_PRODUCTO], [pr].[TIPO_CREDITO], [pr].[MONEDA],
                [k].[CUOTAS_PAGADAS], [k].[CUOTAS_VENCIDAS_IMPAGAS], [k].[CUOTAS_PENDIENTES], [k].[SALDO_CAPITAL],
                [k].[CAPITAL_VENCIDO], [k].[FECHA_PROXIMO_VENCIMIENTO],
                ISNULL(DATEDIFF(DAY, [k].[PRIMER_VENCIMIENTO_IMPAGO], @FECHA_CORTE), 0) AS [DIAS_ATRASO]
            FROM [src].[CREDITO]        AS [c]
            INNER JOIN [CUOTAS]         AS [k]  ON [k].[ID_CREDITO]  = [c].[ID_CREDITO]
            INNER JOIN [src].[CLIENTE]  AS [cl] ON [cl].[ID_CLIENTE] = [c].[ID_CLIENTE]
            INNER JOIN [src].[AGENCIA]  AS [a]  ON [a].[ID_AGENCIA]  = [c].[ID_AGENCIA]
            INNER JOIN [src].[PRODUCTO] AS [pr] ON [pr].[ID_PRODUCTO] = [c].[ID_PRODUCTO]
            WHERE [c].[FECHA_DESEMBOLSO] <= @FECHA_CORTE
              AND [k].[CUOTAS_PENDIENTES] > 0
        )
        INSERT INTO [tab].[TB_CREDITO]
        (
            [FECHA_CORTE], [COD_CREDITO], [ID_CREDITO], [ID_CLIENTE], [TIPO_DOCUMENTO], [NRO_DOCUMENTO], [NOMBRE_CLIENTE],
            [SEXO], [EDAD_CLIENTE], [SEGMENTO_CLIENTE], [ID_AGENCIA], [NOMBRE_AGENCIA], [REGION], [ZONA], [ANALISTA],
            [ID_PRODUCTO], [NOMBRE_PRODUCTO], [TIPO_CREDITO], [MONEDA], [FECHA_DESEMBOLSO], [MONTO_DESEMBOLSADO],
            [TASA_ANUAL], [NRO_CUOTAS], [CUOTAS_PAGADAS], [CUOTAS_VENCIDAS_IMPAGAS], [CUOTAS_PENDIENTES],
            [SALDO_CAPITAL], [CAPITAL_VENCIDO], [DIAS_ATRASO], [CALIFICACION], [ESTADO_CREDITO], [FECHA_PROXIMO_VENCIMIENTO], [RANGO_ATRASO]
        )
        SELECT
            @FECHA_CORTE, [b].[COD_CREDITO], [b].[ID_CREDITO], [b].[ID_CLIENTE], [b].[TIPO_DOCUMENTO], [b].[NRO_DOCUMENTO],
            [b].[NOMBRE_COMPLETO], [b].[SEXO],
            CAST(CASE WHEN [b].[FECHA_NACIMIENTO] IS NULL THEN NULL
                      ELSE DATEDIFF(YEAR, [b].[FECHA_NACIMIENTO], @FECHA_CORTE)
                           - CASE WHEN DATEADD(YEAR, DATEDIFF(YEAR, [b].[FECHA_NACIMIENTO], @FECHA_CORTE), [b].[FECHA_NACIMIENTO]) > @FECHA_CORTE THEN 1 ELSE 0 END
                 END AS TINYINT),
            [b].[SEGMENTO], [b].[ID_AGENCIA], [b].[NOMBRE_AGENCIA], [b].[REGION], [b].[ZONA], [b].[ANALISTA],
            [b].[ID_PRODUCTO], [b].[NOMBRE_PRODUCTO], [b].[TIPO_CREDITO], [b].[MONEDA], [b].[FECHA_DESEMBOLSO],
            [b].[MONTO_DESEMBOLSADO], [b].[TASA_ANUAL], [b].[NRO_CUOTAS], [b].[CUOTAS_PAGADAS],
            [b].[CUOTAS_VENCIDAS_IMPAGAS], [b].[CUOTAS_PENDIENTES], [b].[SALDO_CAPITAL], [b].[CAPITAL_VENCIDO],
            [b].[DIAS_ATRASO],
            CASE WHEN [b].[DIAS_ATRASO] <= 8   THEN 'NORMAL'
                 WHEN [b].[DIAS_ATRASO] <= 30  THEN 'CPP'
                 WHEN [b].[DIAS_ATRASO] <= 60  THEN 'DEFICIENTE'
                 WHEN [b].[DIAS_ATRASO] <= 120 THEN 'DUDOSO'
                 ELSE 'PERDIDA' END,
            CASE WHEN [b].[DIAS_ATRASO] > 30 THEN 'VENCIDO' ELSE 'VIGENTE' END,
            [b].[FECHA_PROXIMO_VENCIMIENTO],
            CASE WHEN [b].[DIAS_ATRASO] = 0    THEN 'AL DIA'
                 WHEN [b].[DIAS_ATRASO] <= 8   THEN '1-8'
                 WHEN [b].[DIAS_ATRASO] <= 30  THEN '9-30'
                 WHEN [b].[DIAS_ATRASO] <= 60  THEN '31-60'
                 WHEN [b].[DIAS_ATRASO] <= 120 THEN '61-120'
                 ELSE 'MAS DE 120' END
        FROM [BASE] AS [b];

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
    @value = N'Carga idempotente del tablón tab.TB_CREDITO para una fecha de corte, a partir de las tablas fuente src.*.',
    @level0type = N'SCHEMA', @level0name = N'tab', @level1type = N'PROCEDURE', @level1name = N'usp_CARGA_TB_CREDITO';
GO
