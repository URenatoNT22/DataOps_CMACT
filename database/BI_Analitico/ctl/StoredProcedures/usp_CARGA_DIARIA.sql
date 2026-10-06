-- Orquestador de la carga de tablones. Es lo que ejecuta el job de SQL Agent.
-- Si no se indica fecha de corte, procesa el último fin de mes cerrado.
CREATE PROCEDURE [ctl].[usp_CARGA_DIARIA]
    @FECHA_CORTE DATE = NULL
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    IF @FECHA_CORTE IS NULL
        SET @FECHA_CORTE = EOMONTH(SYSDATETIME(), -1);

    EXEC [tab].[usp_CARGA_TB_CREDITO]    @FECHA_CORTE = @FECHA_CORTE;
    EXEC [tab].[usp_CARGA_TB_CRONOGRAMA] @FECHA_CORTE = @FECHA_CORTE;
END
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description',
    @value = N'Orquestador de la carga de tablones (crédito y cronograma). Invocado por el job de SQL Agent.',
    @level0type = N'SCHEMA', @level0name = N'ctl', @level1type = N'PROCEDURE', @level1name = N'usp_CARGA_DIARIA';
GO
