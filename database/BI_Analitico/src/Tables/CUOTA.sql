-- Fuente (simulada): plan de pagos y pagos realizados por cuota. Datos ficticios.
CREATE TABLE [src].[CUOTA]
(
    [ID_CREDITO] INT NOT NULL,
    [NRO_CUOTA] SMALLINT NOT NULL,
    [FECHA_VENCIMIENTO] DATE NOT NULL,
    [CAPITAL] DECIMAL(18,2) NOT NULL,
    [INTERES] DECIMAL(18,2) NOT NULL,
    [FECHA_PAGO] DATE NULL,
    [MONTO_PAGADO] DECIMAL(18,2) NULL,
    CONSTRAINT [PK_CUOTA] PRIMARY KEY CLUSTERED ([ID_CREDITO], [NRO_CUOTA])
);
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Fuente (simulada): plan de pagos y pagos realizados por cuota. Datos ficticios.',
    @level0type = N'SCHEMA', @level0name = N'src', @level1type = N'TABLE', @level1name = N'CUOTA';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Crédito al que pertenece la cuota.',
    @level0type = N'SCHEMA', @level0name = N'src', @level1type = N'TABLE', @level1name = N'CUOTA',
    @level2type = N'COLUMN', @level2name = N'ID_CREDITO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Número correlativo de la cuota.',
    @level0type = N'SCHEMA', @level0name = N'src', @level1type = N'TABLE', @level1name = N'CUOTA',
    @level2type = N'COLUMN', @level2name = N'NRO_CUOTA';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Fecha de vencimiento de la cuota.',
    @level0type = N'SCHEMA', @level0name = N'src', @level1type = N'TABLE', @level1name = N'CUOTA',
    @level2type = N'COLUMN', @level2name = N'FECHA_VENCIMIENTO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Amortización de capital de la cuota.',
    @level0type = N'SCHEMA', @level0name = N'src', @level1type = N'TABLE', @level1name = N'CUOTA',
    @level2type = N'COLUMN', @level2name = N'CAPITAL';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Interés de la cuota.',
    @level0type = N'SCHEMA', @level0name = N'src', @level1type = N'TABLE', @level1name = N'CUOTA',
    @level2type = N'COLUMN', @level2name = N'INTERES';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Fecha en que se pagó la cuota; NULL si no está pagada.',
    @level0type = N'SCHEMA', @level0name = N'src', @level1type = N'TABLE', @level1name = N'CUOTA',
    @level2type = N'COLUMN', @level2name = N'FECHA_PAGO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Monto pagado de la cuota; NULL si no está pagada.',
    @level0type = N'SCHEMA', @level0name = N'src', @level1type = N'TABLE', @level1name = N'CUOTA',
    @level2type = N'COLUMN', @level2name = N'MONTO_PAGADO';
GO
