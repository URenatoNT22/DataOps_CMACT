-- Fuente (simulada): créditos desembolsados. Datos ficticios.
CREATE TABLE [src].[CREDITO]
(
    [ID_CREDITO] INT NOT NULL,
    [COD_CREDITO] VARCHAR(20) NOT NULL,
    [ID_CLIENTE] INT NOT NULL,
    [ID_AGENCIA] SMALLINT NOT NULL,
    [ID_PRODUCTO] SMALLINT NOT NULL,
    [ANALISTA] VARCHAR(80) NOT NULL,
    [FECHA_DESEMBOLSO] DATE NOT NULL,
    [MONTO_DESEMBOLSADO] DECIMAL(18,2) NOT NULL,
    [TASA_ANUAL] DECIMAL(9,4) NOT NULL,
    [NRO_CUOTAS] SMALLINT NOT NULL,
    CONSTRAINT [PK_CREDITO] PRIMARY KEY CLUSTERED ([ID_CREDITO])
);
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Fuente (simulada): créditos desembolsados. Datos ficticios.',
    @level0type = N'SCHEMA', @level0name = N'src', @level1type = N'TABLE', @level1name = N'CREDITO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Identificador interno del crédito.',
    @level0type = N'SCHEMA', @level0name = N'src', @level1type = N'TABLE', @level1name = N'CREDITO',
    @level2type = N'COLUMN', @level2name = N'ID_CREDITO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Código de negocio del crédito.',
    @level0type = N'SCHEMA', @level0name = N'src', @level1type = N'TABLE', @level1name = N'CREDITO',
    @level2type = N'COLUMN', @level2name = N'COD_CREDITO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Cliente titular del crédito.',
    @level0type = N'SCHEMA', @level0name = N'src', @level1type = N'TABLE', @level1name = N'CREDITO',
    @level2type = N'COLUMN', @level2name = N'ID_CLIENTE';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Agencia que originó el crédito.',
    @level0type = N'SCHEMA', @level0name = N'src', @level1type = N'TABLE', @level1name = N'CREDITO',
    @level2type = N'COLUMN', @level2name = N'ID_AGENCIA';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Producto de crédito.',
    @level0type = N'SCHEMA', @level0name = N'src', @level1type = N'TABLE', @level1name = N'CREDITO',
    @level2type = N'COLUMN', @level2name = N'ID_PRODUCTO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Analista de créditos responsable (ficticio).',
    @level0type = N'SCHEMA', @level0name = N'src', @level1type = N'TABLE', @level1name = N'CREDITO',
    @level2type = N'COLUMN', @level2name = N'ANALISTA';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Fecha de desembolso.',
    @level0type = N'SCHEMA', @level0name = N'src', @level1type = N'TABLE', @level1name = N'CREDITO',
    @level2type = N'COLUMN', @level2name = N'FECHA_DESEMBOLSO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Monto desembolsado en la moneda del producto.',
    @level0type = N'SCHEMA', @level0name = N'src', @level1type = N'TABLE', @level1name = N'CREDITO',
    @level2type = N'COLUMN', @level2name = N'MONTO_DESEMBOLSADO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Tasa efectiva anual pactada, en porcentaje.',
    @level0type = N'SCHEMA', @level0name = N'src', @level1type = N'TABLE', @level1name = N'CREDITO',
    @level2type = N'COLUMN', @level2name = N'TASA_ANUAL';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Número de cuotas pactadas (frecuencia mensual).',
    @level0type = N'SCHEMA', @level0name = N'src', @level1type = N'TABLE', @level1name = N'CREDITO',
    @level2type = N'COLUMN', @level2name = N'NRO_CUOTAS';
GO
