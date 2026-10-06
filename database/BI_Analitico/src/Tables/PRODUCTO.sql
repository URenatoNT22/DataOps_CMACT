-- Fuente (simulada): catálogo de productos de crédito. Datos ficticios.
CREATE TABLE [src].[PRODUCTO]
(
    [ID_PRODUCTO] SMALLINT NOT NULL,
    [NOMBRE_PRODUCTO] VARCHAR(80) NOT NULL,
    [TIPO_CREDITO] VARCHAR(40) NOT NULL,
    [MONEDA] CHAR(3) NOT NULL,
    CONSTRAINT [PK_PRODUCTO] PRIMARY KEY CLUSTERED ([ID_PRODUCTO])
);
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Fuente (simulada): catálogo de productos de crédito. Datos ficticios.',
    @level0type = N'SCHEMA', @level0name = N'src', @level1type = N'TABLE', @level1name = N'PRODUCTO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Identificador del producto.',
    @level0type = N'SCHEMA', @level0name = N'src', @level1type = N'TABLE', @level1name = N'PRODUCTO',
    @level2type = N'COLUMN', @level2name = N'ID_PRODUCTO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Nombre comercial del producto.',
    @level0type = N'SCHEMA', @level0name = N'src', @level1type = N'TABLE', @level1name = N'PRODUCTO',
    @level2type = N'COLUMN', @level2name = N'NOMBRE_PRODUCTO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Tipo de crédito regulatorio (CONSUMO, MICROEMPRESA, PEQUENA EMPRESA, HIPOTECARIO).',
    @level0type = N'SCHEMA', @level0name = N'src', @level1type = N'TABLE', @level1name = N'PRODUCTO',
    @level2type = N'COLUMN', @level2name = N'TIPO_CREDITO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Moneda del producto (PEN, USD).',
    @level0type = N'SCHEMA', @level0name = N'src', @level1type = N'TABLE', @level1name = N'PRODUCTO',
    @level2type = N'COLUMN', @level2name = N'MONEDA';
GO
